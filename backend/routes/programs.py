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


async def _revert_module_recoveries(program_id: str, module_number: int):
    """
    Called when a module close date is moved to the future.
    Finds all pending failed_subjects for this (program, module) and reverts them:
      - Deletes the failed_subjects record
      - Restores the student's program_status to their previous state
    Only touches records that have NOT been approved or completed by the admin.
    """
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    pending = await db.failed_subjects.find(
        {
            "program_id": program_id,
            "module_number": module_number,
            "recovery_approved": False,
            "recovery_processed": {"$ne": True},
            "recovery_rejected": {"$ne": True},
        },
        {"_id": 0}
    ).to_list(5000)

    if not pending:
        return 0

    reverted = 0
    for record in pending:
        student_id = record["student_id"]
        prev_status = record.get("previous_program_status", "activo")

        await db.failed_subjects.delete_one({"id": record["id"]})

        # Only restore status if the student has no other open recovery records for this program
        other_open = await db.failed_subjects.find_one({
            "student_id": student_id,
            "program_id": program_id,
            "recovery_approved": False,
            "recovery_processed": {"$ne": True},
            "recovery_rejected": {"$ne": True},
        })
        if not other_open:
            await db.users.update_one(
                {"id": student_id},
                {"$set": {
                    f"program_statuses.{program_id}": prev_status,
                    "estado": prev_status,
                }}
            )
        reverted += 1
        logger.info(
            f"Reverted module closure recovery: student={student_id} "
            f"program={program_id} module={module_number} restored_status={prev_status}"
        )

    logger.info(
        f"_revert_module_recoveries: program={program_id} module={module_number} "
        f"reverted={reverted} records (close date moved to future)"
    )
    return reverted


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

    # Read current program BEFORE updating to compare close dates
    current = await db.programs.find_one({"id": program_id}, {"_id": 0})
    if not current:
        raise HTTPException(status_code=404, detail="Programa no encontrado")

    result = await db.programs.update_one({"id": program_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Programa no encontrado")

    programs_cache.invalidate()
    updated = await db.programs.find_one({"id": program_id}, {"_id": 0})

    # Detect if any module close date was moved to the future.
    # If so, revert pending recovery records for those students so they
    # continue in their course as if the module had never closed.
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for mod_num in range(1, 10):
        field = f"module{mod_num}_close_date"
        new_date = update_data.get(field)
        if not new_date:
            continue
        old_date = current.get(field)
        # Only revert when the new date is in the future AND it changed (or was set for first time)
        if new_date > today_str and (old_date != new_date):
            try:
                reverted = await _revert_module_recoveries(program_id, mod_num)
                if reverted:
                    logger.info(
                        f"update_program: {field} moved to future ({old_date} → {new_date}), "
                        f"reverted {reverted} recovery records for program={program_id}"
                    )
            except Exception as e:
                logger.error(f"update_program: error reverting module {mod_num} recoveries: {e}")

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
