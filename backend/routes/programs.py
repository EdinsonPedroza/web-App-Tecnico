import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends

from database import db
from utils.security import get_current_user
from utils.audit import log_audit
from models.schemas import ProgramCreate, ProgramUpdate
from cache import programs_cache

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/programs")
async def get_programs(user=Depends(get_current_user)):
    cached = programs_cache.get("all")
    if cached is not None:
        return cached
    programs = await db.programs.find({}, {"_id": 0}).to_list(100)
    programs_cache.set("all", programs)
    return programs


@router.post("/programs")
async def create_program(req: ProgramCreate, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede crear programas")
    program = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "description": req.description,
        "duration": req.duration,
        "modules": req.modules,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.programs.insert_one(program)
    del program["_id"]
    programs_cache.invalidate()
    await log_audit("program_created", user["id"], user["role"], {"program_id": program["id"], "program_name": req.name})
    return program


@router.put("/programs/{program_id}")
async def update_program(program_id: str, req: ProgramUpdate, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    result = await db.programs.update_one({"id": program_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Programa no encontrado")
    programs_cache.invalidate()
    updated = await db.programs.find_one({"id": program_id}, {"_id": 0})
    return updated


@router.delete("/programs/{program_id}")
async def delete_program(program_id: str, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")
    await db.programs.delete_one({"id": program_id})
    programs_cache.invalidate()
    await log_audit("program_deleted", user["id"], user["role"], {"program_id": program_id})
    return {"message": "Programa eliminado"}


@router.get("/student/programs")
async def get_student_programs(user=Depends(get_current_user)):
    """Get programs that a student is enrolled in"""
    if user["role"] != "estudiante":
        raise HTTPException(status_code=403, detail="Solo estudiantes")

    program_ids = user.get("program_ids", [])
    if not program_ids and user.get("program_id"):
        program_ids = [user.get("program_id")]

    if not program_ids:
        return []

    programs = await db.programs.find({"id": {"$in": program_ids}}, {"_id": 0}).to_list(100)
    return programs
