import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends

from database import db
from utils.security import get_current_user, safe_object_id
from utils.audit import log_audit, log_security_event
from models.schemas import ActivityCreate, ActivityUpdate
from config import MAX_LIMIT

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/activities")
async def get_activities(course_id: Optional[str] = None, subject_id: Optional[str] = None, skip: int = 0, limit: int = 500, user=Depends(get_current_user)):
    query = {}
    if course_id:
        query["course_id"] = safe_object_id(course_id, "course_id")
    if subject_id:
        query["subject_id"] = safe_object_id(subject_id, "subject_id")
    limit = max(1, min(limit, MAX_LIMIT))
    skip = max(0, skip)
    activities = await db.activities.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)

    if user["role"] == "estudiante" and course_id:
        approved_records = await db.failed_subjects.find({
            "student_id": user["id"],
            "course_id": course_id,
            "recovery_approved": True,
            "recovery_processed": {"$ne": True},
            "recovery_rejected": {"$ne": True},
        }, {"_id": 0, "subject_id": 1}).to_list(50000)
        approved_subject_ids = {r.get("subject_id") for r in approved_records if r.get("subject_id")}
        has_course_level_approval = any(not r.get("subject_id") for r in approved_records)

        filtered_activities = []
        for a in activities:
            if not a.get("is_recovery"):
                filtered_activities.append(a)
                continue
            act_sid = a.get("subject_id")
            if (act_sid and act_sid in approved_subject_ids) or (not act_sid and has_course_level_approval):
                filtered_activities.append(a)
        activities = filtered_activities

    return activities


@router.post("/activities")
async def create_activity(req: ActivityCreate, user=Depends(get_current_user)):
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
            log_security_event("UNAUTHORIZED_ACTIVITY_CREATE", {
                "professor_id": user["id"],
                "course_id": req.course_id,
            })
            raise HTTPException(status_code=403, detail="No tienes permiso para crear actividades en este curso")
    if req.is_recovery:
        recovery_query = {"course_id": req.course_id, "is_recovery": True}
        if req.subject_id:
            recovery_query["subject_id"] = req.subject_id
        existing_recovery = await db.activities.find_one(recovery_query)
        if existing_recovery:
            raise HTTPException(
                status_code=400,
                detail="Ya existe una actividad de recuperación para esta materia. Solo se permite una por materia."
            )
    activity_number_query = {"course_id": req.course_id}
    if req.subject_id:
        activity_number_query["subject_id"] = req.subject_id
    agg_result = await db.activities.aggregate([
        {"$match": activity_number_query},
        {"$group": {"_id": None, "max_num": {"$max": "$activity_number"}}}
    ]).to_list(1)
    max_num = agg_result[0]["max_num"] if agg_result else 0
    activity_number = (max_num or 0) + 1
    activity = {
        "id": str(uuid.uuid4()),
        "course_id": req.course_id,
        "subject_id": req.subject_id,
        "activity_number": activity_number,
        "title": req.title,
        "description": req.description,
        "start_date": req.start_date,
        "due_date": req.due_date,
        "files": req.files,
        "is_recovery": req.is_recovery or False,
        "active": True,
        "created_by": user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.activities.insert_one(activity)
    del activity["_id"]
    await log_audit("activity_created", user["id"], user["role"], {"activity_id": activity["id"], "course_id": req.course_id, "title": req.title})
    return activity


async def _verify_professor_course_ownership(activity_id: str, user: dict):
    """Raise HTTP 403/404 if the professor is not assigned to the activity's course."""
    activity = await db.activities.find_one({"id": activity_id}, {"_id": 0})
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    course = await db.courses.find_one({"id": activity.get("course_id")}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    teacher_ids = list(course.get("teacher_ids") or [])
    if course.get("teacher_id"):
        teacher_ids.append(course["teacher_id"])
    if user["id"] not in teacher_ids:
        user_subject_ids = set(user.get("subject_ids") or [])
        course_subject_ids = set(course.get("subject_ids") or [])
        if not user_subject_ids.intersection(course_subject_ids):
            raise HTTPException(status_code=403, detail="No tienes permiso para modificar actividades de este curso")
    return activity


@router.put("/activities/{activity_id}")
async def update_activity(activity_id: str, req: ActivityUpdate, user=Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")

    await _verify_professor_course_ownership(activity_id, user)

    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    result = await db.activities.update_one({"id": activity_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    updated = await db.activities.find_one({"id": activity_id}, {"_id": 0})
    return updated


@router.delete("/activities/{activity_id}")
async def delete_activity(activity_id: str, user=Depends(get_current_user)):
    if user["role"] not in ["profesor", "admin"]:
        raise HTTPException(status_code=403, detail="Solo profesores o admin")

    if user["role"] == "profesor":
        await _verify_professor_course_ownership(activity_id, user)
    else:
        activity = await db.activities.find_one({"id": activity_id}, {"_id": 0})
        if not activity:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")

    await db.grades.delete_many({"activity_id": activity_id})
    await db.submissions.delete_many({"activity_id": activity_id})
    await db.activities.delete_one({"id": activity_id})
    await log_audit("activity_deleted", user["id"], user["role"], {"activity_id": activity_id})
    return {"message": "Actividad eliminada con sus notas y entregas"}
