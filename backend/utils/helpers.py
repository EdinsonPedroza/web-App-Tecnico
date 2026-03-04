import logging
from typing import Optional
from datetime import datetime, timezone
from pymongo import UpdateOne

from database import db
from utils.audit import log_audit

logger = logging.getLogger(__name__)


def sanitize_string(input_str: str, max_length: int = 500) -> str:
    """Sanitize string input to prevent injection attacks"""
    import re
    if not input_str or not isinstance(input_str, str):
        return ""
    sanitized = re.sub(r'[<>{}()\'"\[\]\\;`]', '', input_str)
    sanitized = ''.join(char for char in sanitized if char.isprintable())
    return sanitized[:max_length]


def get_current_module_from_dates(module_dates: dict) -> Optional[int]:
    """Determine the current module number based on today's date and module_dates."""
    if not module_dates:
        return None
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sorted_keys = sorted(module_dates.keys(), key=lambda k: int(k) if str(k).isdigit() else 0)
    for mod_key in sorted_keys:
        dates = module_dates.get(mod_key) or {}
        start = dates.get("start")
        end = dates.get("recovery_close") or dates.get("end")
        if start and end and start <= today <= end:
            return int(mod_key)
    modules_with_start = [(int(k), (module_dates.get(k) or {}).get("start")) for k in sorted_keys if (module_dates.get(k) or {}).get("start")]
    if not modules_with_start:
        return None
    modules_with_start.sort()
    if today < modules_with_start[0][1]:
        return modules_with_start[0][0]
    current = modules_with_start[0][0]
    for mod_num, start in modules_with_start:
        if start <= today:
            current = mod_num
    return current


def can_enroll_in_course(course: dict) -> bool:
    """Check if enrollment is still open for a course."""
    module_dates = course.get("module_dates") or {}
    mod1_dates = module_dates.get("1") or module_dates.get(1) or {}
    mod1_start = mod1_dates.get("start")
    if not mod1_start:
        return True
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return today < mod1_start


def can_enroll_in_module(module_dates: dict, module_number: int) -> bool:
    """Check if enrollment window is open for a specific module number."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    mod_key = str(module_number)
    mod_dates = module_dates.get(mod_key) or module_dates.get(module_number) or {}
    mod_start = mod_dates.get("start")

    if module_number == 1:
        if not mod_start:
            return True
        return today < mod_start

    prev_key = str(module_number - 1)
    prev_dates = module_dates.get(prev_key) or module_dates.get(module_number - 1) or {}
    prev_recovery_close = prev_dates.get("recovery_close") or prev_dates.get("end")

    if not prev_recovery_close and not mod_start:
        return True
    if prev_recovery_close and today < prev_recovery_close:
        return False
    if mod_start and today >= mod_start:
        return False
    return True


def get_open_enrollment_module(module_dates: dict) -> Optional[int]:
    """Return the module currently accepting enrollments based on date windows."""
    if not module_dates:
        return None
    mod_numbers = sorted(
        int(k) for k in module_dates.keys() if str(k).isdigit()
    )
    if not mod_numbers:
        return None
    mods_to_check = mod_numbers + [mod_numbers[-1] + 1]
    for mod_num in mods_to_check:
        if can_enroll_in_module(module_dates, mod_num):
            return mod_num
    return None


def validate_module_dates_order(module_dates: dict) -> Optional[str]:
    """Validate that module N+1 starts after module N's recovery_close (or end) date."""
    if not module_dates or len(module_dates) < 2:
        return None
    sorted_keys = sorted(module_dates.keys(), key=lambda k: int(k) if str(k).isdigit() else 0)
    for i in range(len(sorted_keys) - 1):
        curr_key = sorted_keys[i]
        next_key = sorted_keys[i + 1]
        curr_dates = module_dates.get(curr_key) or {}
        next_dates = module_dates.get(next_key) or {}
        curr_boundary = curr_dates.get("recovery_close") or curr_dates.get("end")
        next_start = next_dates.get("start")
        if curr_boundary and next_start and next_start <= curr_boundary:
            return (f"La fecha de inicio del Módulo {next_key} ({next_start}) debe ser "
                    f"posterior al cierre de recuperaciones del Módulo {curr_key} ({curr_boundary})")
    return None


def validate_module_dates_recovery_close(module_dates: dict) -> Optional[str]:
    """Validate that every module_dates entry includes a recovery_close date."""
    for mod_key, dates in (module_dates or {}).items():
        if not (dates or {}).get("recovery_close"):
            return (
                f"El Módulo {mod_key} no tiene fecha de cierre de recuperaciones "
                "(recovery_close). Todas las entradas de fechas de módulo deben incluirla."
            )
    return None


def derive_estado_from_program_statuses(program_statuses: dict) -> str:
    """Derive the global 'estado' from per-program statuses."""
    if not program_statuses:
        return "activo"
    statuses = list(program_statuses.values())
    if "activo" in statuses:
        return "activo"
    if all(s == "egresado" for s in statuses):
        return "egresado"
    if "pendiente_recuperacion" in statuses:
        return "pendiente_recuperacion"
    if "egresado" in statuses:
        return "egresado"
    if "reprobado" in statuses:
        return "reprobado"
    return "retirado"


async def _get_program_courses_for_student(
    student_id: str, prog_id: str, fallback_course_id: str
) -> list:
    """Return all courses for prog_id where student_id is still enrolled."""
    if prog_id:
        courses = await db.courses.find(
            {"program_id": prog_id, "student_ids": student_id},
            {"_id": 0, "id": 1},
        ).to_list(1000)
        return courses or [{"id": fallback_course_id}]
    return [{"id": fallback_course_id}]


async def _unenroll_student_from_course(
    student_id: str, course_id: str
) -> list:
    """Unenroll student only from the specified course and clear stale group label."""
    await db.courses.update_one(
        {"id": course_id},
        {
            "$pull": {"student_ids": student_id},
            "$addToSet": {"removed_student_ids": student_id}
        }
    )

    still_enrolled_anywhere = await db.courses.find_one(
        {"student_ids": student_id},
        {"_id": 0, "id": 1}
    )
    if not still_enrolled_anywhere:
        await db.users.update_one(
            {"id": student_id, "role": "estudiante"},
            {"$unset": {"grupo": ""}}
        )

    return [course_id]


async def _check_and_update_recovery_completion(student_id: str, course_id: str):
    """Check if all recovery subjects for a student in a course are now completed and approved."""
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        return
    prog_id = course.get("program_id", "")

    all_records = await db.failed_subjects.find(
        {
            "student_id": student_id,
            "course_id": course_id,
            "recovery_processed": {"$ne": True},
            "recovery_expired": {"$ne": True},
        },
        {"_id": 0},
    ).to_list(200)

    if not all_records:
        return

    all_passed = all(
        r.get("recovery_approved") is True and
        r.get("recovery_completed") is True and r.get("teacher_graded_status") == "approved"
        for r in all_records
    )
    if not all_passed:
        return

    student = await db.users.find_one({"id": student_id}, {"_id": 0})
    if not student:
        return

    program_statuses = student.get("program_statuses") or {}

    if program_statuses.get(prog_id) != "pendiente_recuperacion":
        return

    module_number = (
        (student.get("program_modules") or {}).get(prog_id)
        or student.get("module")
        or all_records[0].get("module_number", 1)
    )
    program = await db.programs.find_one({"id": prog_id}, {"_id": 0}) if prog_id else None
    max_modules = max(len(program.get("modules", [])) if program else 2, 2)

    if module_number >= max_modules:
        program_statuses[prog_id] = "egresado"
    else:
        program_statuses[prog_id] = "activo"

    new_estado = derive_estado_from_program_statuses(program_statuses)
    await db.users.update_one(
        {"id": student_id},
        {"$set": {"estado": new_estado, "program_statuses": program_statuses}},
    )
    logger.info(
        f"Student {student_id} status updated to {program_statuses.get(prog_id)} "
        f"after all recovery subjects approved in course {course_id}"
    )
    await log_audit(
        "recovery_all_approved",
        "system",
        "system",
        {
            "student_id": student_id,
            "course_id": course_id,
            "new_status": program_statuses.get(prog_id),
            "trigger": "all_recoveries_graded_approved",
        },
    )


async def _check_and_update_recovery_rejection(student_id: str, course_id: str):
    """Mark recovery records as rejected when a teacher rejects a recovery subject."""
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        return
    prog_id = course.get("program_id", "")

    approved_records = await db.failed_subjects.find(
        {
            "student_id": student_id,
            "course_id": course_id,
            "recovery_approved": True,
            "recovery_processed": {"$ne": True},
            "recovery_expired": {"$ne": True},
        },
        {"_id": 0},
    ).to_list(200)

    if not approved_records:
        return

    any_rejected = any(r.get("teacher_graded_status") == "rejected" for r in approved_records)
    if not any_rejected:
        return

    now = datetime.now(timezone.utc)
    bulk_reject_ops = [
        UpdateOne(
            {"id": record["id"]},
            {"$set": {
                "recovery_rejected": True,
                "rejected_at": now.isoformat(),
                "rejected_by": "teacher"
            }}
        )
        for record in approved_records
    ]
    await db.failed_subjects.bulk_write(bulk_reject_ops, ordered=False)
    logger.info(
        f"Student {student_id} marked for deferred expulsion from group {course_id} "
        f"(teacher rejected recovery subject; scheduler will process at recovery_close)"
    )
    await log_audit(
        "recovery_rejected_by_teacher_deferred", "system", "system",
        {"student_id": student_id, "course_id": course_id,
         "program_id": prog_id, "trigger": "teacher_rejected_recovery"}
    )
