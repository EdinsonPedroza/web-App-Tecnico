import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from database import db
from utils.security import get_current_user
from models.schemas import SubmissionCreate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/submissions")
async def get_submissions(activity_id: Optional[str] = None, student_id: Optional[str] = None, skip: int = 0, limit: int = 200, user=Depends(get_current_user)):
    if user["role"] == "estudiante":
        student_id = user["id"]
    query = {}
    if activity_id:
        query["activity_id"] = activity_id
    if student_id:
        query["student_id"] = student_id
    max_limit = 200 if activity_id else 500
    limit = max(1, min(limit, max_limit))
    skip = max(0, skip)
    total_count = await db.submissions.count_documents(query)
    submissions = await db.submissions.find(query, {"_id": 0}).sort("submitted_at", -1).skip(skip).limit(limit).to_list(limit)
    response = JSONResponse(content=submissions)
    response.headers["X-Total-Count"] = str(total_count)
    response.headers["X-Has-More"] = str((skip + limit) < total_count).lower()
    return response


@router.post("/submissions")
async def create_submission(req: SubmissionCreate, user=Depends(get_current_user)):
    if user["role"] != "estudiante":
        raise HTTPException(status_code=403, detail="Solo estudiantes")

    activity = await db.activities.find_one({"id": req.activity_id}, {"_id": 0})
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")

    course = await db.courses.find_one({"id": activity["course_id"]}, {"_id": 0, "student_ids": 1, "program_id": 1})
    if not course or user["id"] not in (course.get("student_ids") or []):
        raise HTTPException(status_code=403, detail="No estás inscrito en este curso")

    now = datetime.now(timezone.utc)

    if activity.get("is_recovery"):
        failed_filter = {
            "student_id": user["id"],
            "course_id": activity["course_id"],
            "recovery_approved": True,
            "recovery_processed": {"$ne": True},
            "recovery_rejected": {"$ne": True},
        }
        if activity.get("subject_id"):
            failed_filter["subject_id"] = activity["subject_id"]
        failed_record = await db.failed_subjects.find_one(failed_filter)
        if not failed_record:
            raise HTTPException(
                status_code=400,
                detail="Tu recuperación debe ser aprobada por el administrador antes de poder entregar actividades"
            )

    if activity.get("start_date"):
        start_date = datetime.fromisoformat(activity["start_date"].replace("Z", "+00:00"))
        if now < start_date:
            raise HTTPException(status_code=400, detail="La actividad aún no está disponible.")

    due_date = datetime.fromisoformat(activity["due_date"].replace("Z", "+00:00"))
    if now > due_date:
        raise HTTPException(status_code=400, detail="La fecha límite ha pasado. No se puede entregar.")

    if req.files and len(req.files) > 3:
        raise HTTPException(status_code=400, detail="Máximo 3 archivos por entrega")

    if activity.get("subject_id"):
        subject = await db.subjects.find_one({"id": activity["subject_id"]}, {"_id": 0, "module_number": 1})
        if subject and subject.get("module_number") is not None:
            subject_module = subject["module_number"]
            if course and course.get("program_id"):
                program_id = course["program_id"]
                student_module = (user.get("program_modules") or {}).get(program_id)
                if student_module is None:
                    student_module = user.get("module")
                if student_module is not None and int(student_module) != int(subject_module):
                    raise HTTPException(
                        status_code=403,
                        detail=f"Esta actividad pertenece al Módulo {int(subject_module)}, pero estás actualmente en el Módulo {int(student_module)}. Solo puedes entregar actividades de tu módulo actual."
                    )

    existing = await db.submissions.find_one({
        "activity_id": req.activity_id,
        "student_id": user["id"]
    })
    if existing:
        if existing.get("edited", False):
            raise HTTPException(status_code=400, detail="Esta actividad ya ha sido editada. Solo se permite una edición por actividad.")

        # Si el contenido y archivos son idénticos, no contar como edición
        existing_files = existing.get("files") or []
        new_files = req.files or []
        existing_content = (existing.get("content") or "").strip()
        new_content = (req.content or "").strip()

        def files_equal(f1, f2):
            if len(f1) != len(f2):
                return False
            for a, b in zip(f1, f2):
                if isinstance(a, dict) and isinstance(b, dict):
                    if a.get("url") != b.get("url") or a.get("name") != b.get("name"):
                        return False
                else:
                    if a != b:
                        return False
            return True

        if existing_content == new_content and files_equal(existing_files, new_files):
            logger.info("Duplicate submission detected for activity %s by student %s — returning existing without modification", req.activity_id, user["id"])
            return existing

        await db.submissions.update_one(
            {"id": existing["id"]},
            {"$set": {"content": req.content, "files": req.files, "submitted_at": datetime.now(timezone.utc).isoformat(), "edited": True}}
        )
        updated = await db.submissions.find_one({"id": existing["id"]}, {"_id": 0})
        return updated

    submission = {
        "id": str(uuid.uuid4()),
        "activity_id": req.activity_id,
        "student_id": user["id"],
        "content": req.content,
        "files": req.files,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "edited": False
    }
    await db.submissions.insert_one(submission)
    del submission["_id"]
    return submission
