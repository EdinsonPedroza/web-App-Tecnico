import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends

from database import db
from utils.security import get_current_user
from utils.audit import log_audit
from utils.helpers import derive_estado_from_program_statuses
from models.schemas import RecoveryEnableRequest

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/recovery/enable")
async def enable_recovery(req: RecoveryEnableRequest, user=Depends(get_current_user)):
    """Admin enables recovery for a specific student in a course"""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede habilitar recuperaciones")

    recovery = {
        "id": str(uuid.uuid4()),
        "student_id": req.student_id,
        "course_id": req.course_id,
        "subject_id": req.subject_id,
        "enabled": True,
        "enabled_by": user["id"],
        "enabled_at": datetime.now(timezone.utc).isoformat()
    }

    existing = await db.recovery_enabled.find_one({
        "student_id": req.student_id,
        "course_id": req.course_id,
        "subject_id": req.subject_id
    })

    if existing:
        await db.recovery_enabled.update_one(
            {"id": existing["id"]},
            {"$set": {"enabled": True, "enabled_by": user["id"], "enabled_at": datetime.now(timezone.utc).isoformat()}}
        )
        return {"message": "Recuperación actualizada"}

    await db.recovery_enabled.insert_one(recovery)
    return {"message": "Recuperación habilitada para el estudiante"}


@router.get("/recovery/enabled")
async def get_recovery_enabled(student_id: Optional[str] = None, course_id: Optional[str] = None, user=Depends(get_current_user)):
    """Get list of students with recovery enabled"""
    fs_query = {
        "recovery_approved": True,
        "recovery_completed": {"$ne": True},
        "recovery_processed": {"$ne": True},
        "recovery_rejected": {"$ne": True},
    }
    if student_id:
        fs_query["student_id"] = student_id
    if course_id:
        fs_query["course_id"] = course_id

    active_records = await db.failed_subjects.find(fs_query, {"_id": 0, "student_id": 1, "course_id": 1, "subject_id": 1}).to_list(1000)
    if active_records:
        seen = set()
        enabled = []
        for r in active_records:
            key = (r.get("student_id"), r.get("course_id"), r.get("subject_id"))
            if key in seen:
                continue
            seen.add(key)
            enabled.append({
                "student_id": r.get("student_id"),
                "course_id": r.get("course_id"),
                "subject_id": r.get("subject_id"),
                "enabled": True,
                "source": "failed_subjects"
            })
        return enabled

    query = {}
    if student_id:
        query["student_id"] = student_id
    if course_id:
        query["course_id"] = course_id
    return await db.recovery_enabled.find(query, {"_id": 0}).to_list(500)


@router.get("/student/my-recoveries")
async def get_student_recoveries(user=Depends(get_current_user)):
    """Get recovery subjects for the current student."""
    if user["role"] != "estudiante":
        raise HTTPException(status_code=403, detail="Solo estudiantes pueden acceder a sus recuperaciones")

    student_id = user["id"]
    program_modules = user.get("program_modules") or {}

    failed_subjects = await db.failed_subjects.find({
        "student_id": student_id,
        "recovery_processed": {"$ne": True}
    }, {"_id": 0}).to_list(100)

    all_subject_docs = await db.subjects.find({}, {"_id": 0, "id": 1, "module_number": 1}).to_list(1000)
    db_subject_module_map = {s["id"]: (s.get("module_number") or 1) for s in all_subject_docs}

    filtered = []
    for subject in failed_subjects:
        prog_id = subject.get("program_id", "")
        sid = subject.get("subject_id")
        if sid and sid in db_subject_module_map:
            subject_module = db_subject_module_map[sid]
        else:
            subject_module = subject.get("module_number")
        if subject_module is None:
            filtered.append(subject)
            continue
        current_module = program_modules.get(prog_id)
        if current_module is None:
            current_module = user.get("module") or 1
        if subject_module == current_module:
            filtered.append(subject)
    failed_subjects = filtered

    programs = await db.programs.find({}, {"_id": 0}).to_list(100)
    program_map = {p["id"]: p["name"] for p in programs}

    missing_subject_ids = [s["subject_id"] for s in failed_subjects if s.get("subject_id") and not s.get("subject_name")]
    subject_name_lookup = {}
    if missing_subject_ids:
        subj_docs = await db.subjects.find({"id": {"$in": missing_subject_ids}}, {"_id": 0, "id": 1, "name": 1}).to_list(500)
        subject_name_lookup = {s["id"]: s["name"] for s in subj_docs}

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Pre-load all courses needed to avoid N+1 queries inside the loop
    course_ids = list({s["course_id"] for s in failed_subjects if s.get("course_id")})
    if course_ids:
        course_docs = await db.courses.find(
            {"id": {"$in": course_ids}},
            {"_id": 0, "id": 1, "module_dates": 1}
        ).to_list(500)
        course_map_for_dates = {c["id"]: c for c in course_docs}
    else:
        course_map_for_dates = {}

    for subject in failed_subjects:
        subject["program_name"] = program_map.get(subject["program_id"], "Desconocido")
        if not subject.get("subject_name") and subject.get("subject_id"):
            subject["subject_name"] = subject_name_lookup.get(subject["subject_id"], "")
        course = course_map_for_dates.get(subject["course_id"])
        recovery_close = None
        if course and course.get("module_dates"):
            module_key = str(subject.get("module_number", ""))
            module_dates = course["module_dates"].get(module_key)
            if module_dates:
                recovery_close = module_dates.get("recovery_close")
        subject["recovery_close_date"] = recovery_close
        subject["recovery_closed"] = bool(recovery_close and recovery_close < today_str)
        subject.setdefault("recovery_approved", False)
        teacher_status = subject.get("teacher_graded_status")
        if subject.get("recovery_completed") and teacher_status == "rejected":
            subject["status_label"] = "reprobado"
        elif subject.get("recovery_completed") and teacher_status == "approved":
            subject["status_label"] = "aprobado"
        elif subject.get("recovery_approved"):
            subject["status_label"] = "habilitada"
        else:
            subject["status_label"] = "pendiente_aprobacion"

    return {
        "recoveries": failed_subjects,
        "total": len(failed_subjects)
    }
