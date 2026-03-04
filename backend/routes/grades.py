import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse

from database import db
from utils.security import get_current_user, safe_object_id
from utils.audit import log_audit, log_security_event
from utils.helpers import (
    _check_and_update_recovery_completion,
    _check_and_update_recovery_rejection,
)
from models.schemas import GradeCreate, GradeUpdate
from config import MAX_LIMIT, MAX_LIMIT_GRADES

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/grades")
async def get_grades(course_id: Optional[str] = None, student_id: Optional[str] = None, subject_id: Optional[str] = None, activity_id: Optional[str] = None, skip: int = 0, limit: int = 100, user=Depends(get_current_user), request: Request = None):
    if user["role"] == "estudiante":
        student_id = user["id"]
    query = {}
    if course_id:
        query["course_id"] = safe_object_id(course_id, "course_id")
    if student_id:
        query["student_id"] = safe_object_id(student_id, "student_id")
    if subject_id:
        query["subject_id"] = safe_object_id(subject_id, "subject_id")
    if activity_id:
        query["activity_id"] = safe_object_id(activity_id, "activity_id")
    if course_id and request and "limit" not in request.query_params:
        limit = MAX_LIMIT_GRADES
    effective_max = MAX_LIMIT_GRADES if course_id else MAX_LIMIT
    limit = max(1, min(limit, effective_max))
    skip = max(0, skip)
    total_count = await db.grades.count_documents(query)
    grades = await db.grades.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    response = JSONResponse(content=grades)
    response.headers["X-Total-Count"] = str(total_count)
    response.headers["X-Has-More"] = str((skip + limit) < total_count).lower()
    return response


@router.post("/grades")
async def create_grade(req: GradeCreate, user=Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")

    course = await db.courses.find_one({"id": req.course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    teacher_ids_list = list(course.get("teacher_ids") or [])
    if course.get("teacher_id"):
        teacher_ids_list.append(course["teacher_id"])
    if user["id"] not in teacher_ids_list:
        user_subject_ids = set(user.get("subject_ids") or [])
        course_subject_ids = set(course.get("subject_ids") or [])
        if not user_subject_ids.intersection(course_subject_ids):
            log_security_event("UNAUTHORIZED_GRADE_ATTEMPT", {
                "professor_id": user["id"],
                "course_id": req.course_id,
                "course_teacher_id": course.get("teacher_id")
            })
            raise HTTPException(status_code=403, detail="No eres el profesor asignado a este curso")

    if req.activity_id:
        activity_doc = await db.activities.find_one({"id": req.activity_id}, {"_id": 0, "is_recovery": 1, "course_id": 1, "subject_id": 1})
        if activity_doc and activity_doc.get("is_recovery"):
            if req.value is not None and not req.recovery_status:
                raise HTTPException(
                    status_code=400,
                    detail="Las actividades de recuperación no admiten nota numérica. Use Aprobar o Rechazar."
                )
            if req.recovery_status not in ("approved", "rejected", None):
                raise HTTPException(status_code=400, detail="Estado de recuperación inválido")
            rec_subject_id = req.subject_id or activity_doc.get("subject_id")
            failed_filter = {
                "student_id": req.student_id,
                "course_id": req.course_id,
                "recovery_approved": True,
                "recovery_processed": {"$ne": True},
                "recovery_rejected": {"$ne": True},
            }
            if rec_subject_id:
                failed_filter["subject_id"] = rec_subject_id
            failed_record = await db.failed_subjects.find_one(failed_filter)
            if not failed_record:
                raise HTTPException(
                    status_code=400,
                    detail="La recuperación debe ser aprobada por el administrador antes de poder calificar"
                )

    existing = await db.grades.find_one({
        "student_id": req.student_id,
        "course_id": req.course_id,
        "activity_id": req.activity_id
    })

    grade_value = req.value
    if req.recovery_status:
        rec_subject_id = req.subject_id
        if req.activity_id:
            _act = await db.activities.find_one({"id": req.activity_id}, {"_id": 0, "subject_id": 1})
            rec_subject_id = rec_subject_id or (_act or {}).get("subject_id")

        fs_filter = {
            "student_id": req.student_id,
            "course_id": req.course_id,
            "recovery_approved": True,
            "recovery_processed": {"$ne": True},
            "recovery_rejected": {"$ne": True},
        }
        if rec_subject_id:
            fs_filter["subject_id"] = rec_subject_id

        if req.recovery_status == "approved":
            # Replace ALL grades for the failed subject with 3.0
            subject_filter = {
                "student_id": req.student_id,
                "course_id": req.course_id,
            }
            if rec_subject_id:
                subject_filter["subject_id"] = rec_subject_id

            # Update all existing grades for this subject to 3.0
            update_result = await db.grades.update_many(
                subject_filter,
                {"$set": {
                    "value": 3.0,
                    "recovery_status": "approved",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )

            grade_value = 3.0

            logger.info(
                f"Recovery approved: updated {update_result.modified_count} grades to 3.0 "
                f"for student {req.student_id}, course {req.course_id}, subject {rec_subject_id}"
            )

            await db.failed_subjects.update_one(
                fs_filter,
                {"$set": {
                    "recovery_completed": True,
                    "teacher_graded_status": "approved",
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            await _check_and_update_recovery_completion(req.student_id, req.course_id)
        else:
            await db.failed_subjects.update_one(
                fs_filter,
                {"$set": {
                    "recovery_completed": True,
                    "teacher_graded_status": "rejected",
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            await _check_and_update_recovery_rejection(req.student_id, req.course_id)

            if existing:
                await db.grades.update_one(
                    {"id": existing["id"]},
                    {"$set": {"recovery_status": req.recovery_status, "updated_at": datetime.now(timezone.utc).isoformat()}}
                )
                updated = await db.grades.find_one({"id": existing["id"]}, {"_id": 0})
                await log_audit("recovery_graded", user["id"], user["role"], {"student_id": req.student_id, "course_id": req.course_id, "subject_id": req.subject_id, "result": "rejected"})
                return updated
            grade = {
                "id": str(uuid.uuid4()),
                "student_id": req.student_id,
                "course_id": req.course_id,
                "activity_id": req.activity_id,
                "subject_id": req.subject_id,
                "value": None,
                "comments": req.comments,
                "recovery_status": req.recovery_status,
                "graded_by": user["id"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await db.grades.insert_one(grade)
            await log_audit("recovery_graded", user["id"], user["role"], {"student_id": req.student_id, "course_id": req.course_id, "subject_id": req.subject_id, "result": "rejected"})
            grade.pop("_id", None)
            return grade

    if existing:
        update_data = {
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        if grade_value is not None:
            update_data["value"] = grade_value
        if req.comments:
            update_data["comments"] = req.comments
        if req.recovery_status:
            update_data["recovery_status"] = req.recovery_status

        if grade_value is not None and existing.get("value") is not None and existing["value"] != grade_value:
            await db.grade_changes.insert_one({
                "id": str(uuid.uuid4()),
                "grade_id": existing["id"],
                "student_id": req.student_id,
                "course_id": req.course_id,
                "activity_id": req.activity_id,
                "subject_id": req.subject_id,
                "old_value": existing["value"],
                "new_value": grade_value,
                "changed_by": user["id"],
                "changed_at": datetime.now(timezone.utc).isoformat()
            })

        await db.grades.update_one(
            {"id": existing["id"]},
            {"$set": update_data}
        )
        updated = await db.grades.find_one({"id": existing["id"]}, {"_id": 0})
        return updated

    grade = {
        "id": str(uuid.uuid4()),
        "student_id": req.student_id,
        "course_id": req.course_id,
        "activity_id": req.activity_id,
        "subject_id": req.subject_id,
        "value": grade_value if grade_value is not None else 0.0,
        "comments": req.comments,
        "recovery_status": req.recovery_status,
        "graded_by": user["id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.grades.insert_one(grade)
    del grade["_id"]
    if req.recovery_status == "approved":
        await log_audit("recovery_graded", user["id"], user["role"], {"student_id": req.student_id, "course_id": req.course_id, "subject_id": req.subject_id, "result": "approved"})
    else:
        await log_audit("grade_assigned", user["id"], user["role"], {"student_id": req.student_id, "course_id": req.course_id, "subject_id": req.subject_id, "activity_id": req.activity_id})
    return grade


@router.put("/grades/{grade_id}")
async def update_grade(grade_id: str, req: GradeUpdate, user=Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.grades.update_one({"id": grade_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    updated = await db.grades.find_one({"id": grade_id}, {"_id": 0})
    return updated
