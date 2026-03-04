import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends

from database import db
from utils.security import get_current_user
from models.schemas import SubjectCreate, SubjectUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/subjects")
async def get_subjects(program_id: Optional[str] = None, teacher_id: Optional[str] = None, user=Depends(get_current_user)):
    query = {}
    if program_id:
        query["program_id"] = program_id
    if teacher_id:
        teacher = await db.users.find_one({"id": teacher_id, "role": "profesor"}, {"_id": 0})
        if teacher and teacher.get("subject_ids"):
            query["id"] = {"$in": teacher["subject_ids"]}
        else:
            return []
    subjects = await db.subjects.find(query, {"_id": 0}).to_list(500)
    return subjects


@router.get("/subjects/teachers")
async def get_subjects_teachers(user=Depends(get_current_user)):
    """Return a map of subject_id -> comma-separated teacher names for all teachers."""
    teachers = await db.users.find(
        {"role": "profesor"},
        {"_id": 0, "id": 1, "name": 1, "subject_ids": 1}
    ).to_list(500)
    names_by_subject: dict = {}
    for t in teachers:
        for sid in (t.get("subject_ids") or []):
            names_by_subject.setdefault(sid, []).append(t["name"])
    return {sid: ", ".join(names) for sid, names in names_by_subject.items()}


@router.post("/subjects")
async def create_subject(req: SubjectCreate, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")
    subject = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "program_id": req.program_id,
        "module_number": req.module_number,
        "description": req.description,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.subjects.insert_one(subject)
    del subject["_id"]
    return subject


@router.get("/subjects/{subject_id}")
async def get_subject(subject_id: str, user=Depends(get_current_user)):
    subject = await db.subjects.find_one({"id": subject_id}, {"_id": 0})
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    return subject


@router.put("/subjects/{subject_id}")
async def update_subject(subject_id: str, req: SubjectUpdate, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    result = await db.subjects.update_one({"id": subject_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    updated = await db.subjects.find_one({"id": subject_id}, {"_id": 0})
    return updated


@router.delete("/subjects/{subject_id}")
async def delete_subject(subject_id: str, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")
    await db.subjects.delete_one({"id": subject_id})
    return {"message": "Materia eliminada"}
