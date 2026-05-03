import uuid
import asyncio
import logging
import os
import io
import csv
import re
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from pymongo import UpdateOne

try:
    import openpyxl
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

from database import db
from utils.security import get_current_user, hash_password
from utils.audit import log_audit, _make_audit_record
from utils.helpers import derive_estado_from_program_statuses
from config import BOGOTA_TZ, MAX_OVERDUE_BEFORE_RECOVERY, AUTO_RECOVERY_ENABLED_AT
from scheduler.cleanup import acquire_scheduler_lock, release_scheduler_lock

logger = logging.getLogger(__name__)
router = APIRouter()


async def check_and_close_modules():
    """
    Check all programs and courses for module close dates that have passed and automatically close them.
    This function runs daily at 00:01 AM.
    Also checks recovery close dates: students who haven't passed recovery by the deadline are removed.
    """
    # Distributed lock: only one worker across all instances should run this job
    if not await acquire_scheduler_lock("auto_close_modules", ttl_seconds=1800):
        logger.info("Module closure already running on another worker, skipping.")
        return
    try:
        logger.info("Running automatic module closure check...")
        now = datetime.now(timezone.utc)
        # Use Bogotá timezone for date comparisons so scheduler results are
        # consistent with the dates configured by administrators (UTC-5).
        today_str = datetime.now(BOGOTA_TZ).strftime("%Y-%m-%d")
        
        # Get all programs; check all moduleN_close_date fields in Python for N-module support.
        # (Business rule 2026-02-25: no longer hardcoded to 2 modules)
        programs = await db.programs.find({}, {"_id": 0}).to_list(100)
        
        if not programs:
            logger.info("No programs with close dates to process")
        else:
            for program in programs:
                program_id = program["id"]
                program_name = program["name"]
                
                # Determine how many modules this program defines (minimum 2 for backwards compatibility)
                program_modules_list = program.get("modules") or []
                max_modules = max(len(program_modules_list), 2)
                
                # Check all modules for this program dynamically (supports N modules)
                for mod_num in range(1, max_modules + 1):
                    close_date_field = f"module{mod_num}_close_date"
                    close_date = program.get(close_date_field)
                    if not close_date or close_date > today_str:
                        continue

                    closure_check = await db.module_closures.find_one({
                        "program_id": program_id,
                        "module_number": mod_num,
                        "closed_date": close_date
                    })

                    if not closure_check:
                        logger.info(f"Auto-closing Module {mod_num} for program {program_name} (date: {close_date})")
                        try:
                            result = await close_module_internal(module_number=mod_num, program_id=program_id)

                            await db.module_closures.insert_one({
                                "id": str(uuid.uuid4()),
                                "program_id": program_id,
                                "module_number": mod_num,
                                "closed_date": close_date,
                                "closed_at": now.isoformat(),
                                "result": result
                            })
                            logger.info(
                                f"Module {mod_num} closed for {program_name}: "
                                f"{result['promoted_count']} promoted, {result['graduated_count']} graduated, "
                                f"{result['recovery_pending_count']} in recovery"
                            )
                        except Exception as e:
                            logger.error(f"Error auto-closing Module {mod_num} for {program_name}: {e}", exc_info=True)
        
        # Check course-level recovery close dates: promote winners, remove losers
        all_courses = await db.courses.find({}, {"_id": 0}).to_list(5000)
        all_subjects = await db.subjects.find({}, {"_id": 0, "id": 1, "module_number": 1}).to_list(5000)
        subject_module_map = {s["id"]: (s.get("module_number") or 1) for s in all_subjects}
        # Pre-load programs indexed by id for fallback module_dates construction
        all_programs_map = {p["id"]: p for p in programs} if programs else {}
        removed_count = 0
        promoted_recovery_count = 0
        skipped_no_grades_recovery = 0
        total_courses = len(all_courses)
        for i, course in enumerate(all_courses):
            # Log progress and yield to event loop periodically to avoid blocking other requests
            if i % 10 == 0:
                logger.info(f"Scheduler progress: processing course {i + 1}/{total_courses}")
                await asyncio.sleep(0)
            module_dates = course.get("module_dates") or {}
            prog_id_for_course = course.get("program_id", "")

            # --- Causa 1: fallback module_dates from program when course has none ---
            if not module_dates and prog_id_for_course:
                prog = all_programs_map.get(prog_id_for_course)
                if prog:
                    prog_modules_list = prog.get("modules") or []
                    max_mod = max(len(prog_modules_list), 2)
                    for mn in range(1, max_mod + 1):
                        close_field = f"module{mn}_close_date"
                        close_val = prog.get(close_field)
                        if close_val:
                            # Use moduleN_close_date as a proxy recovery_close when no
                            # per-course module_dates are configured.
                            module_dates[str(mn)] = {"recovery_close": close_val}
                if module_dates:
                    logger.warning(
                        f"Course {course['id']} has no module_dates; synthesized fallback "
                        f"from program {prog_id_for_course}: {list(module_dates.keys())}"
                    )
                else:
                    logger.warning(
                        f"Course {course['id']} has no module_dates and program "
                        f"{prog_id_for_course!r} has no moduleN_close_date fields – "
                        "skipping recovery check for this course."
                    )
                    continue

            # Pre-load course grades once per course (not once per module_key).
            # Uses aggregation to compute per-(student, subject) averages in MongoDB,
            # avoiding loading up to 200k raw grade documents into memory.
            subject_ids = course.get("subject_ids") or []
            if not subject_ids and course.get("subject_id"):
                subject_ids = [course["subject_id"]]
            _grade_pipeline = [
                {"$match": {"course_id": course["id"], "value": {"$ne": None}}},
                {"$group": {
                    "_id": {"student_id": "$student_id", "subject_id": "$subject_id"},
                    "avg": {"$avg": "$value"},
                    "count": {"$sum": 1}
                }}
            ]
            _grade_aggs = await db.grades.aggregate(_grade_pipeline).to_list(100000)
            # grades_index: (student_id, subject_id) -> (avg, count)
            grades_index = {}
            # student_all_grades_avg: student_id -> {"wsum": float, "n": int} for no-subjects fallback
            student_all_grades_avg: dict = {}
            for _g in _grade_aggs:
                _sid = _g["_id"]["student_id"]
                _subj = _g["_id"]["subject_id"]
                _avg, _cnt = float(_g["avg"]), int(_g["count"])
                grades_index[(_sid, _subj)] = (_avg, _cnt)
                _sagg = student_all_grades_avg.setdefault(_sid, {"wsum": 0.0, "n": 0})
                _sagg["wsum"] += _avg * _cnt
                _sagg["n"] += _cnt

            for module_key, dates in module_dates.items():
                recovery_close = dates.get("recovery_close") if dates else None
                if not recovery_close or recovery_close > today_str:
                    continue  # Recovery period not closed yet
                
                # --- Causa 3: retroactively run close_module_internal if it was never executed ---
                # Check whether failed_subjects records already exist for this course/module.
                existing_any = await db.failed_subjects.find_one(
                    {"course_id": course["id"], "module_number": int(module_key)},
                    {"_id": 0, "id": 1}
                )
                if not existing_any:
                    # Check if close_module_internal was already recorded for this program/module.
                    closure_exists = await db.module_closures.find_one({
                        "program_id": prog_id_for_course,
                        "module_number": int(module_key),
                    }) if prog_id_for_course else None
                    if not closure_exists and prog_id_for_course:
                        logger.warning(
                            f"Recovery close passed for course {course['id']} module {module_key} "
                            "but no failed_subjects records found and no module closure recorded – "
                            "running close_module_internal retroactively."
                        )
                        try:
                            retro_result = await close_module_internal(
                                module_number=int(module_key),
                                program_id=prog_id_for_course
                            )
                            await db.module_closures.insert_one({
                                "id": str(uuid.uuid4()),
                                "program_id": prog_id_for_course,
                                "module_number": int(module_key),
                                "closed_date": recovery_close,
                                "closed_at": now.isoformat(),
                                "result": retro_result,
                                "retroactive": True
                            })
                            logger.info(
                                f"Retroactive close_module_internal for program {prog_id_for_course} "
                                f"module {module_key}: {retro_result}"
                            )
                            # Re-fetch records after the retroactive closure
                            existing_any = await db.failed_subjects.find_one(
                                {"course_id": course["id"], "module_number": int(module_key)},
                                {"_id": 0, "id": 1}
                            )
                        except Exception as retro_err:
                            logger.error(
                                f"Error in retroactive close_module_internal for course "
                                f"{course['id']} module {module_key}: {retro_err}",
                                exc_info=True
                            )

                # Find ALL failed_subjects for this course/module that haven't been processed yet.
                # Ceiling of 5000: a single course cannot realistically have more students.
                all_records = await db.failed_subjects.find({
                    "course_id": course["id"],
                    "module_number": int(module_key),
                    "recovery_expired": {"$ne": True},
                    "recovery_processed": {"$ne": True}
                }, {"_id": 0}).to_list(5000)
                
                prog_id = course.get("program_id", "")

                # Group recovery records by student
                students_records = {}
                for record in all_records:
                    sid = record["student_id"]
                    students_records.setdefault(sid, []).append(record)

                # Skip only when there are no recovery records AND no enrolled students.
                # We still need to process courses with no recovery records if they have
                # direct-pass students whose promotion was deferred to recovery_close.
                if not all_records and not course.get("student_ids"):
                    continue

                # Filter course subjects to those belonging to this module_key.
                # grades_index and student_all_grades_avg are pre-loaded once per course above.
                module_subject_ids = [sid for sid in subject_ids if subject_module_map.get(sid, 1) == int(module_key)]
                
                # Pre-load all student docs and the program in bulk before the loop
                _rec_student_ids = list(students_records.keys())
                if _rec_student_ids:
                    _rec_student_docs = await db.users.find(
                        {"id": {"$in": _rec_student_ids}},
                        {"_id": 0, "id": 1, "program_modules": 1, "program_statuses": 1}
                    ).to_list(5000)
                    students_map = {s["id"]: s for s in _rec_student_docs}
                else:
                    students_map = {}
                prog_doc = await db.programs.find_one({"id": prog_id}, {"_id": 0}) if prog_id else None
                user_bulk_ops: list = []
                fs_bulk_ops: list = []
                _records_unenroll_ids: list = []
                _audit_log_batch: list = []

                for student_id, records in students_records.items():
                    # Business rule: at recovery_close, any habilitación left without admin or
                    # teacher confirmation is treated as reprobado. If the admin took no action
                    # on any recovery record, remove the student from the group and mark reprobado.
                    # If admin approved at least one but another was left "en espera" (unapproved),
                    # the all_passed check below handles it: partial approval ≠ full pass.
                    has_admin_action = any(
                        r.get("recovery_approved") is True or r.get("recovery_completed") is True
                        for r in records
                    )
                    if not has_admin_action:
                        logger.info(
                            f"Recovery close: no admin action for student {student_id} in course "
                            f"{course['id']} – applying fail flow (removing from group, marking reprobado)"
                        )
                        # Remove student only from the course where recovery was not passed.
                        _records_unenroll_ids.append(student_id)
                        student_doc = students_map.get(student_id)
                        _ps = (student_doc or {}).get("program_statuses") or {}
                        if prog_id:
                            _ps[prog_id] = "reprobado"
                        _new_estado = derive_estado_from_program_statuses(_ps)
                        _upd: dict = {"estado": _new_estado}
                        if prog_id:
                            _upd["program_statuses"] = _ps
                            # Bug-1 fix: a previous erroneous advancement (e.g. only partial
                            # records were found when all_passed was evaluated) could have set
                            # program_modules to module_key+1.  Pinning it back to module_key
                            # here ensures the student stays at the module they failed.
                            _upd[f"program_modules.{prog_id}"] = int(module_key)
                        user_bulk_ops.append(UpdateOne({"id": student_id, "role": "estudiante"}, {"$set": _upd}))
                        logger.info(
                            f"Student {student_id} marked reprobado for program {prog_id} "
                            "(recovery_close passed with no admin action)"
                        )
                        await log_audit(
                            "student_removed_from_group", "system", "system",
                            {"student_id": student_id, "course_id": course["id"],
                             "program_id": prog_id, "trigger": "recovery_close_no_admin_action"}
                        )
                        removed_count += 1
                        for record in records:
                            fs_bulk_ops.append(UpdateOne(
                                {"id": record["id"]},
                                {"$set": {"recovery_processed": True, "processed_at": now.isoformat()}}
                            ))
                        continue

                    # A student passes only if ALL their records are approved by admin AND completed AND approved by teacher
                    all_passed = all(
                        r.get("recovery_approved") is True and
                        r.get("recovery_completed") is True and
                        r.get("teacher_graded_status") == "approved"
                        for r in records
                    )

                    # Bug-2 fix: even when all *existing* records show "passed", also verify that
                    # every failing subject in this course/module has a corresponding record.
                    # When admin only enables *some* subjects via the recovery panel (leaving others
                    # "en espera"), those unenabled subjects never get failed_subjects records.
                    # Without this guard the scheduler would only see the admin-enabled records and
                    # could incorrectly promote the student even though other subjects were never
                    # addressed.  Any subject with a failing average (<3.0) and no record is treated
                    # as not-approved, overriding all_passed to False.
                    if all_passed and module_subject_ids:
                        tracked_subject_ids = {r.get("subject_id") for r in records if r.get("subject_id")}
                        for sid in module_subject_ids:
                            if sid in tracked_subject_ids:
                                continue  # This subject has a record – already considered above
                            _gd = grades_index.get((student_id, sid))
                            if _gd is None:
                                # Subject has no grades — teacher may have forgotten to grade
                                skipped_no_grades_recovery += 1
                                logger.debug(
                                    f"Recovery close: student {student_id} has no grades for "
                                    f"subject {sid} in course {course['id']} module {module_key} – skipping subject"
                                )
                            else:  # Only flag if grades exist (skip ungraded subjects)
                                avg = _gd[0]
                                if avg < 3.0:
                                    all_passed = False
                                    logger.info(
                                        f"Recovery close: student {student_id} has unrecorded failing "
                                        f"subject {sid} (avg {avg:.2f}) in course {course['id']} "
                                        f"module {module_key} – overriding all_passed to False"
                                    )
                                    break
                    
                    if all_passed:
                        # Promote to next module or graduate
                        student = students_map.get(student_id)
                        if student:
                            program_modules = student.get("program_modules") or {}
                            program_statuses = student.get("program_statuses") or {}
                            program = prog_doc
                            max_modules = max(len(program.get("modules", [])) if program and program.get("modules") else 2, 2)
                            # Use the module being closed (not the student's potentially stale field)
                            # to decide between promotion and graduation
                            if int(module_key) >= max_modules:
                                program_statuses[prog_id] = "egresado"
                                new_global_estado = derive_estado_from_program_statuses(program_statuses)
                                user_bulk_ops.append(UpdateOne(
                                    {"id": student_id},
                                    {
                                        "$set": {"program_statuses": program_statuses, "estado": new_global_estado},
                                        "$unset": {f"program_promotion_pending.{prog_id}": ""}
                                    }
                                ))
                                logger.info(f"Student {student_id} graduated (recovery passed all subjects in course {course['id']})")
                                _audit_log_batch.append(_make_audit_record("student_graduated", "system", "system", {"student_id": student_id, "course_id": course["id"], "trigger": "recovery_close"}))
                            else:
                                next_module = int(module_key) + 1
                                program_statuses[prog_id] = "activo"
                                new_global_estado = derive_estado_from_program_statuses(program_statuses)
                                update_fields = {
                                    "estado": new_global_estado,
                                    "program_statuses": program_statuses
                                }
                                if prog_id:
                                    update_fields[f"program_modules.{prog_id}"] = next_module
                                user_bulk_ops.append(UpdateOne(
                                    {"id": student_id},
                                    {
                                        "$set": update_fields,
                                        "$unset": {f"program_promotion_pending.{prog_id}": ""}
                                    }
                                ))
                                logger.info(f"Student {student_id} promoted to module {next_module} (recovery passed in course {course['id']})")
                                _audit_log_batch.append(_make_audit_record("student_promoted", "system", "system", {"student_id": student_id, "course_id": course["id"], "next_module": next_module, "trigger": "recovery_close"}))
                            promoted_recovery_count += 1
                    else:
                        # Not all subjects passed: admin left some habilitaciones "en espera"
                        # (unapproved) or teacher did not grade them. Treat as reprobado.
                        logger.info(f"Recovery close: student {student_id} did not pass all subjects in course {course['id']} – removing from group")
                        # Remove student only from the course where recovery was not passed.
                        _records_unenroll_ids.append(student_id)
                        student_doc = students_map.get(student_id)
                        student_program_statuses = (student_doc or {}).get("program_statuses") or {}
                        if prog_id:
                            student_program_statuses[prog_id] = "reprobado"
                        new_estado = derive_estado_from_program_statuses(student_program_statuses)
                        update_fields = {"estado": new_estado}
                        if prog_id:
                            update_fields["program_statuses"] = student_program_statuses
                            # Bug-1 fix (same guard as in the no_admin_action path above):
                            # pin program_modules to the module being closed so the student
                            # does not appear at an incorrectly advanced module number.
                            update_fields[f"program_modules.{prog_id}"] = int(module_key)
                        user_bulk_ops.append(UpdateOne({"id": student_id, "role": "estudiante"}, {"$set": update_fields}))
                        logger.info(f"Student {student_id} marked as reprobado for program {prog_id} (recovery closed, did not pass)")
                        _audit_log_batch.append(_make_audit_record("student_removed_from_group", "system", "system", {"student_id": student_id, "course_id": course["id"], "program_id": prog_id, "trigger": "recovery_close_failed"}))
                        removed_count += 1
                    
                    # Mark all records for this student in this course/module as processed
                    for record in records:
                        fs_bulk_ops.append(UpdateOne(
                            {"id": record["id"]},
                            {"$set": {"recovery_processed": True, "processed_at": now.isoformat()}}
                        ))

                if user_bulk_ops:
                    await db.users.bulk_write(user_bulk_ops, ordered=False)
                if fs_bulk_ops:
                    await db.failed_subjects.bulk_write(fs_bulk_ops, ordered=False)
                if _audit_log_batch:
                    try:
                        await db.audit_logs.insert_many(_audit_log_batch, ordered=False)
                    except Exception as _audit_exc:
                        logger.error(f"Failed to batch write recovery audit logs: {_audit_exc}")
                # Batch unenroll for students_records loop: one course update instead of N
                if _records_unenroll_ids:
                    await db.courses.update_one(
                        {"id": course["id"]},
                        {
                            "$pull": {"student_ids": {"$in": _records_unenroll_ids}},
                            "$addToSet": {"removed_student_ids": {"$each": _records_unenroll_ids}}
                        }
                    )
                    _still_enrolled_docs = await db.courses.find(
                        {"student_ids": {"$in": _records_unenroll_ids}},
                        {"_id": 0, "student_ids": 1}
                    ).to_list(1000)
                    _still_enrolled_set: set = set()
                    for _c in _still_enrolled_docs:
                        _still_enrolled_set.update(_c.get("student_ids") or [])
                    for _sid in _records_unenroll_ids:
                        if _sid not in _still_enrolled_set:
                            await db.users.update_one(
                                {"id": _sid, "role": "estudiante"},
                                {"$unset": {"grupo": ""}}
                            )
                
                # Also promote students who passed the module directly (no failed subjects),
                # whose promotion was deferred to recovery_close by close_module_internal.
                # Pre-load student docs and reuse prog_doc for direct_pass loop
                _direct_ids = [sid for sid in course.get("student_ids", []) if sid not in students_records]
                if _direct_ids:
                    _direct_docs = await db.users.find(
                        {"id": {"$in": _direct_ids}},
                        {"_id": 0, "id": 1, "program_modules": 1, "program_statuses": 1}
                    ).to_list(5000)
                    direct_students_map = {s["id"]: s for s in _direct_docs}
                    # Pre-fetch all pending failed_subjects for direct-pass students in one query
                    _direct_pending_list = await db.failed_subjects.find({
                        "student_id": {"$in": _direct_ids},
                        "program_id": prog_id,
                        "module_number": int(module_key),
                        "recovery_processed": {"$ne": True},
                        "recovery_expired": {"$ne": True},
                    }, {"_id": 0, "student_id": 1}).to_list(5000)
                    _direct_pending_set = {rec["student_id"] for rec in _direct_pending_list}
                else:
                    direct_students_map = {}
                    _direct_pending_set = set()
                direct_user_bulk_ops: list = []
                _direct_unenroll_ids: list = []
                _direct_audit_log_batch: list = []

                for student_id in course.get("student_ids", []):
                    if student_id in students_records:
                        continue  # Already handled above as a recovery student
                    direct_student = direct_students_map.get(student_id)
                    if not direct_student:
                        continue
                    direct_prog_modules = direct_student.get("program_modules") or {}
                    # Only process if still in the module being closed (idempotency guard)
                    if direct_prog_modules.get(prog_id) != int(module_key):
                        continue
                    # Check if student has unresolved failed_subjects in OTHER courses
                    # for the same program and module. If so, skip promotion — the student
                    # must resolve all recovery subjects before advancing.
                    # Use pre-fetched set instead of individual find_one per student.
                    if student_id in _direct_pending_set:
                        continue

                    # Defensive rule: never promote at recovery_close when the student still
                    # has failing averages in this course/module, even if failed_subjects is
                    # missing or incomplete. Students with NO grades are skipped – they may be
                    # newly enrolled in this group and have not been graded yet; removing them
                    # would incorrectly mark them as reprobado.
                    if module_subject_ids:
                        has_grades_for_module = False
                        has_failing = False
                        for sid in module_subject_ids:
                            _gd = grades_index.get((student_id, sid))
                            if _gd:
                                has_grades_for_module = True
                                avg = _gd[0]
                                if avg < 3.0:
                                    has_failing = True
                                    break
                        if not has_grades_for_module:
                            continue  # No grades for this module; skip (likely newly enrolled)
                    else:
                        _all = student_all_grades_avg.get(student_id)
                        if not _all or _all["n"] == 0:
                            continue  # No grades in this course; skip (likely newly enrolled)
                        avg = _all["wsum"] / _all["n"]
                        has_failing = avg < 3.0

                    if has_failing:
                        logger.info(
                            f"Recovery close: student {student_id} has failing averages in "
                            f"course {course['id']} module {module_key} without full recovery pass "
                            "– removing from group instead of promoting"
                        )
                        _direct_unenroll_ids.append(student_id)
                        removed_count += 1
                        student_doc = direct_students_map.get(student_id)
                        ps = (student_doc or {}).get("program_statuses") or {}
                        if prog_id:
                            ps[prog_id] = "reprobado"
                        new_estado = derive_estado_from_program_statuses(ps)
                        upd = {"estado": new_estado}
                        if prog_id:
                            upd["program_statuses"] = ps
                        direct_user_bulk_ops.append(UpdateOne({"id": student_id, "role": "estudiante"}, {"$set": upd}))
                        await log_audit(
                            "student_removed_from_group", "system", "system",
                            {"student_id": student_id, "course_id": course["id"],
                             "program_id": prog_id, "trigger": "recovery_close_direct_pass_failing_guard"}
                        )
                        continue

                    direct_prog_statuses = direct_student.get("program_statuses") or {}
                    # A student can be reprobado or still pendiente_recuperacion here when they
                    # were not processed by the students_records loop (either removed from a
                    # different course earlier in this scheduler run, or their failed_subjects
                    # records are missing/stale). Remove them instead of promoting them.
                    # pendiente_recuperacion at recovery_close without resolved records means
                    # admin/teacher never confirmed the habilitación – treat as reprobado.
                    if direct_prog_statuses.get(prog_id) in ("reprobado", "pendiente_recuperacion"):
                        logger.info(
                            f"Recovery close: student {student_id} has status "
                            f"'{direct_prog_statuses.get(prog_id)}' for program {prog_id} "
                            f"– removing from course {course['id']} (no confirmed recovery)"
                        )
                        _direct_unenroll_ids.append(student_id)
                        _upd: dict = {"estado": "reprobado"}
                        if prog_id:
                            direct_prog_statuses[prog_id] = "reprobado"
                            _upd["estado"] = derive_estado_from_program_statuses(direct_prog_statuses)
                            _upd["program_statuses"] = direct_prog_statuses
                            _upd[f"program_modules.{prog_id}"] = int(module_key)
                        direct_user_bulk_ops.append(UpdateOne(
                            {"id": student_id, "role": "estudiante"}, {"$set": _upd}
                        ))
                        removed_count += 1
                        _direct_audit_log_batch.append(_make_audit_record(
                            "student_removed_from_group", "system", "system",
                            {"student_id": student_id, "course_id": course["id"],
                             "program_id": prog_id, "trigger": "recovery_close_unconfirmed_recovery"}
                        ))
                        continue
                    program = prog_doc
                    max_modules = max(len(program.get("modules", [])) if program and program.get("modules") else 2, 2)
                    if int(module_key) >= max_modules:
                        direct_prog_statuses[prog_id] = "egresado"
                        new_global_estado = derive_estado_from_program_statuses(direct_prog_statuses)
                        direct_user_bulk_ops.append(UpdateOne(
                            {"id": student_id},
                            {
                                "$set": {"program_statuses": direct_prog_statuses, "estado": new_global_estado},
                                "$unset": {f"program_promotion_pending.{prog_id}": ""}
                            }
                        ))
                        logger.info(f"Student {student_id} graduated (direct pass, deferred to recovery_close for course {course['id']})")
                        _direct_audit_log_batch.append(_make_audit_record("student_graduated", "system", "system", {"student_id": student_id, "course_id": course["id"], "trigger": "recovery_close_direct_pass"}))
                    else:
                        next_module = int(module_key) + 1
                        direct_prog_statuses[prog_id] = "activo"
                        new_global_estado = derive_estado_from_program_statuses(direct_prog_statuses)
                        update_fields = {
                            "estado": new_global_estado,
                            "program_statuses": direct_prog_statuses
                        }
                        if prog_id:
                            update_fields[f"program_modules.{prog_id}"] = next_module
                        direct_user_bulk_ops.append(UpdateOne(
                            {"id": student_id},
                            {
                                "$set": update_fields,
                                "$unset": {f"program_promotion_pending.{prog_id}": ""}
                            }
                        ))
                        logger.info(f"Student {student_id} promoted to module {next_module} (direct pass, deferred to recovery_close for course {course['id']})")
                        _direct_audit_log_batch.append(_make_audit_record("student_promoted", "system", "system", {"student_id": student_id, "course_id": course["id"], "next_module": next_module, "trigger": "recovery_close_direct_pass"}))
                    promoted_recovery_count += 1

                if direct_user_bulk_ops:
                    await db.users.bulk_write(direct_user_bulk_ops, ordered=False)
                if _direct_audit_log_batch:
                    try:
                        await db.audit_logs.insert_many(_direct_audit_log_batch, ordered=False)
                    except Exception as _audit_exc:
                        logger.error(f"Failed to batch write direct_pass audit logs: {_audit_exc}")
                # Batch unenroll for direct_pass loop: one course update instead of N
                if _direct_unenroll_ids:
                    await db.courses.update_one(
                        {"id": course["id"]},
                        {
                            "$pull": {"student_ids": {"$in": _direct_unenroll_ids}},
                            "$addToSet": {"removed_student_ids": {"$each": _direct_unenroll_ids}}
                        }
                    )
                    _still_enrolled_docs = await db.courses.find(
                        {"student_ids": {"$in": _direct_unenroll_ids}},
                        {"_id": 0, "student_ids": 1}
                    ).to_list(1000)
                    _still_enrolled_set = set()
                    for _c in _still_enrolled_docs:
                        _still_enrolled_set.update(_c.get("student_ids") or [])
                    for _sid in _direct_unenroll_ids:
                        if _sid not in _still_enrolled_set:
                            await db.users.update_one(
                                {"id": _sid, "role": "estudiante"},
                                {"$unset": {"grupo": ""}}
                            )

                # Strict fallback at recovery_close: if a student still has failing averages
                # in this course/module and did not fully pass recovery records, remove them.
                # This covers edge cases where failed_subjects records are missing/stale.
                # Pre-load current course doc and all student docs in 2 queries (instead of 2 per student)
                current_course_doc = await db.courses.find_one({"id": course["id"]}, {"_id": 0, "student_ids": 1})
                _fallback_ids = list(course.get("student_ids", []))
                if _fallback_ids:
                    _fb_docs = await db.users.find(
                        {"id": {"$in": _fallback_ids}},
                        {"_id": 0, "id": 1, "program_modules": 1, "program_statuses": 1}
                    ).to_list(5000)
                    fallback_students_map = {s["id"]: s for s in _fb_docs}
                else:
                    fallback_students_map = {}
                fallback_user_bulk_ops: list = []
                fallback_fs_bulk_ops: list = []
                _fallback_unenroll_ids: list = []

                # Pre-load ALL failed_subjects for all fallback students in ONE query
                # instead of one query per student inside the loop (N queries → 1 query)
                if _fallback_ids:
                    _fallback_fs_docs = await db.failed_subjects.find({
                        "student_id": {"$in": _fallback_ids},
                        "course_id": course["id"],
                        "module_number": int(module_key),
                        "recovery_processed": {"$ne": True},
                        "recovery_expired": {"$ne": True},
                    }, {"_id": 0}).to_list(5000)
                    _fallback_fs_by_student: dict = {}
                    for _fsr in _fallback_fs_docs:
                        _fsid = _fsr.get("student_id")
                        if _fsid:
                            _fallback_fs_by_student.setdefault(_fsid, []).append(_fsr)
                else:
                    _fallback_fs_by_student = {}

                for student_id in _fallback_ids:
                    # Skip if already unenrolled in previous steps
                    if not current_course_doc or student_id not in (current_course_doc.get("student_ids") or []):
                        continue

                    # Only enforce for students still in the module being closed
                    stud = fallback_students_map.get(student_id)
                    if not stud:
                        continue
                    if prog_id and (stud.get("program_modules") or {}).get(prog_id) != int(module_key):
                        continue

                    # Determine if student has failing performance in this course/module.
                    # Students with NO grades are skipped – they may be newly enrolled
                    # and have not been graded yet; removing them would be incorrect.
                    if module_subject_ids:
                        has_grades_for_module = False
                        has_failing = False
                        for sid in module_subject_ids:
                            _gd = grades_index.get((student_id, sid))
                            if _gd:
                                has_grades_for_module = True
                                avg = _gd[0]
                                if avg < 3.0:
                                    has_failing = True
                                    break
                        if not has_grades_for_module:
                            continue  # No grades for this module; skip (likely newly enrolled)
                    else:
                        _all = student_all_grades_avg.get(student_id)
                        if not _all or _all["n"] == 0:
                            continue  # No grades in this course; skip (likely newly enrolled)
                        avg = _all["wsum"] / _all["n"]
                        has_failing = avg < 3.0

                    if not has_failing:
                        continue

                    unresolved_records = _fallback_fs_by_student.get(student_id, [])

                    # If all unresolved records are fully approved+graded, let normal pass flow apply
                    if unresolved_records and all(
                        r.get("recovery_approved") is True and
                        r.get("recovery_completed") is True and
                        r.get("teacher_graded_status") == "approved"
                        for r in unresolved_records
                    ):
                        continue

                    _fallback_unenroll_ids.append(student_id)
                    removed_count += 1
                    student_doc = fallback_students_map.get(student_id)
                    ps = (student_doc or {}).get("program_statuses") or {}
                    if prog_id:
                        ps[prog_id] = "reprobado"
                    new_estado = derive_estado_from_program_statuses(ps)
                    upd = {"estado": new_estado}
                    if prog_id:
                        upd["program_statuses"] = ps
                    fallback_user_bulk_ops.append(UpdateOne({"id": student_id, "role": "estudiante"}, {"$set": upd}))

                    if unresolved_records:
                        for rec in unresolved_records:
                            fallback_fs_bulk_ops.append(UpdateOne(
                                {"id": rec["id"]},
                                {"$set": {"recovery_processed": True, "processed_at": now.isoformat()}}
                            ))

                    await log_audit(
                        "student_removed_from_group", "system", "system",
                        {"student_id": student_id, "course_id": course["id"],
                         "program_id": prog_id, "trigger": "recovery_close_strict_fallback_failed"}
                    )

                if fallback_user_bulk_ops:
                    await db.users.bulk_write(fallback_user_bulk_ops, ordered=False)
                if fallback_fs_bulk_ops:
                    await db.failed_subjects.bulk_write(fallback_fs_bulk_ops, ordered=False)
                # Batch unenroll for fallback loop: one course update instead of N
                if _fallback_unenroll_ids:
                    await db.courses.update_one(
                        {"id": course["id"]},
                        {
                            "$pull": {"student_ids": {"$in": _fallback_unenroll_ids}},
                            "$addToSet": {"removed_student_ids": {"$each": _fallback_unenroll_ids}}
                        }
                    )
                    _still_enrolled_docs = await db.courses.find(
                        {"student_ids": {"$in": _fallback_unenroll_ids}},
                        {"_id": 0, "student_ids": 1}
                    ).to_list(1000)
                    _still_enrolled_set = set()
                    for _c in _still_enrolled_docs:
                        _still_enrolled_set.update(_c.get("student_ids") or [])
                    for _sid in _fallback_unenroll_ids:
                        if _sid not in _still_enrolled_set:
                            await db.users.update_one(
                                {"id": _sid, "role": "estudiante"},
                                {"$unset": {"grupo": ""}}
                            )

        if removed_count > 0:
            logger.info(f"Recovery check: removed {removed_count} students from groups due to failed recovery")
        if promoted_recovery_count > 0:
            logger.info(f"Recovery check: promoted/graduated {promoted_recovery_count} students after passing recovery")
        if skipped_no_grades_recovery > 0:
            logger.warning(
                f"WARNING: {skipped_no_grades_recovery} student-subject instances skipped during recovery check "
                "due to missing grades — teachers may have forgotten to grade some subjects"
            )
        
        logger.info("Automatic module closure check completed")

        # Run auto-recovery check (overdue submissions) if the feature is enabled
        if AUTO_RECOVERY_ENABLED_AT:
            try:
                reverted = await revert_stale_auto_recoveries()
                if reverted:
                    logger.info(f"Scheduler: reverted {reverted} stale auto-recovery records")
            except Exception as rev_err:
                logger.error(f"Scheduler: error reverting stale auto-recoveries: {rev_err}")
            try:
                created = await check_overdue_auto_recovery()
                if created:
                    logger.info(f"Auto-recovery (overdue): {created} new failed_subjects records created")
            except Exception as ar_err:
                logger.error(f"Error in overdue auto-recovery check: {ar_err}", exc_info=True)
    except Exception as e:
        logger.error(f"Error in automatic module closure check: {e}", exc_info=True)
    finally:
        await release_scheduler_lock("auto_close_modules")


async def check_overdue_auto_recovery(dry_run: bool = False) -> int:
    """
    Place students in recovery when they accumulate >= MAX_OVERDUE_BEFORE_RECOVERY
    activities with past due_date and no submission in a single subject.

    Only activities with due_date >= AUTO_RECOVERY_ENABLED_AT are counted so the
    feature is not applied retroactively to pre-deployment workshops.

    Returns the number of new failed_subjects records created (or would-be created in dry_run).
    """
    if not AUTO_RECOVERY_ENABLED_AT:
        return 0

    now_iso = datetime.now(timezone.utc).isoformat()
    threshold = MAX_OVERDUE_BEFORE_RECOVERY
    created_count = 0
    candidates: list = []  # only used in dry_run mode

    # Load subjects once for name/module lookup
    all_subjects = await db.subjects.find({}, {"_id": 0, "id": 1, "name": 1, "module_number": 1}).to_list(2000)
    subject_info = {s["id"]: s for s in all_subjects}

    # Process course by course to keep memory bounded
    async for course in db.courses.find(
        {"student_ids": {"$exists": True, "$not": {"$size": 0}}}, {"_id": 0}
    ):
        course_id = course["id"]
        enrolled_ids = course.get("student_ids") or []
        if not enrolled_ids:
            continue

        subject_ids = list(set(
            (course.get("subject_ids") or []) +
            ([course["subject_id"]] if course.get("subject_id") else [])
        ))
        if not subject_ids:
            continue

        program_id = course.get("program_id", "")

        # Overdue non-recovery activities in this course since feature was enabled
        overdue_acts = await db.activities.find({
            "course_id": course_id,
            "is_recovery": {"$ne": True},
            "due_date": {"$lt": now_iso, "$gte": AUTO_RECOVERY_ENABLED_AT},
        }, {"_id": 0, "id": 1, "subject_id": 1}).to_list(2000)

        if not overdue_acts:
            continue

        activity_ids = [a["id"] for a in overdue_acts]

        # Submissions for these activities (only students in this course)
        subs = await db.submissions.find(
            {"activity_id": {"$in": activity_ids}, "student_id": {"$in": enrolled_ids}},
            {"_id": 0, "activity_id": 1, "student_id": 1}
        ).to_list(len(activity_ids) * len(enrolled_ids) + 1)
        submitted_pairs = {(s["student_id"], s["activity_id"]) for s in subs}

        # Build per-subject activity sets for fast lookup
        acts_by_subject: dict = {}
        for a in overdue_acts:
            sid = a.get("subject_id")
            if sid:
                acts_by_subject.setdefault(sid, []).append(a["id"])

        # Bulk-load all enrolled students for this course (one query per course, not one per student)
        enrolled_docs = await db.users.find(
            {"id": {"$in": enrolled_ids}, "role": "estudiante"},
            {"_id": 0, "id": 1, "estado": 1, "name": 1, "program_statuses": 1}
        ).to_list(len(enrolled_ids) + 1)
        enrolled_map = {s["id"]: s for s in enrolled_docs}

        # Bulk-load existing open recovery records for this course to avoid find_one per student
        existing_recoveries = await db.failed_subjects.find(
            {"course_id": course_id, "recovery_processed": {"$ne": True}, "recovery_rejected": {"$ne": True}},
            {"_id": 0, "student_id": 1, "subject_id": 1}
        ).to_list(5000)
        existing_recovery_set = {(r["student_id"], r.get("subject_id")) for r in existing_recoveries}

        for student_id in enrolled_ids:
            student = enrolled_map.get(student_id)
            if not student:
                continue
            if student.get("estado") in ("retirado", "egresado"):
                continue

            for subject_id, act_ids_for_subject in acts_by_subject.items():
                if subject_id not in subject_ids:
                    continue

                missing = sum(
                    1 for aid in act_ids_for_subject
                    if (student_id, aid) not in submitted_pairs
                )
                if missing < threshold:
                    continue

                # Skip if recovery already exists (use pre-loaded set, no extra query)
                if (student_id, subject_id) in existing_recovery_set:
                    continue

                subj_meta = subject_info.get(subject_id, {})
                prev_status = (student.get("program_statuses") or {}).get(program_id, "activo")
                record = {
                    "id": str(uuid.uuid4()),
                    "student_id": student_id,
                    "student_name": student.get("name", ""),
                    "course_id": course_id,
                    "course_name": course.get("name", ""),
                    "subject_id": subject_id,
                    "subject_name": subj_meta.get("name", ""),
                    "program_id": program_id,
                    "module_number": subj_meta.get("module_number", 1),
                    "average_grade": 0.0,
                    "recovery_approved": False,
                    "recovery_completed": False,
                    "recovery_processed": False,
                    "recovery_reason": "overdue_submissions",
                    "overdue_count": missing,
                    "previous_program_status": prev_status,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }

                if dry_run:
                    candidates.append(record)
                else:
                    await db.failed_subjects.insert_one(record)
                    del record["_id"]
                    # Update student program_statuses to pendiente_recuperacion
                    if program_id:
                        prog_statuses = student.get("program_statuses") or {}
                        if prog_statuses.get(program_id) == "activo":
                            await db.users.update_one(
                                {"id": student_id},
                                {
                                    "$set": {
                                        f"program_statuses.{program_id}": "pendiente_recuperacion",
                                        "estado": "pendiente_recuperacion",
                                    }
                                }
                            )
                    logger.info(
                        f"Auto-recovery (overdue): student={student_id} subject={subject_id} "
                        f"course={course_id} overdue={missing}"
                    )

                created_count += 1

    if dry_run:
        return candidates  # type: ignore[return-value]
    return created_count


async def revert_stale_auto_recoveries() -> int:
    """
    Revert auto-recovery records that are no longer valid due to date changes.

    Specifically handles two scenarios:
    1. AUTO_RECOVERY_ENABLED_AT was moved to the future (feature not yet active).
    2. The student no longer has >= threshold overdue submissions because activities
       or dates changed since the record was created.

    Only reverts records that are still pending admin approval (recovery_approved=False,
    recovery_processed=False, recovery_rejected!=True). Approved or completed records
    are never touched — the admin already acted on them.

    Returns the count of reverted records.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    reverted = 0

    # Find all pending auto-recovery records
    pending = await db.failed_subjects.find(
        {
            "recovery_reason": "overdue_submissions",
            "recovery_approved": False,
            "recovery_processed": {"$ne": True},
            "recovery_rejected": {"$ne": True},
        },
        {"_id": 0}
    ).to_list(5000)

    if not pending:
        return 0

    # If AUTO_RECOVERY_ENABLED_AT is not set or is in the future, revert ALL pending records
    if not AUTO_RECOVERY_ENABLED_AT or AUTO_RECOVERY_ENABLED_AT > now_iso:
        ids_to_revert = [r["id"] for r in pending]
        for record in pending:
            await _revert_single_auto_recovery(record)
        logger.info(
            f"revert_stale_auto_recoveries: AUTO_RECOVERY_ENABLED_AT is future/unset — "
            f"reverted {len(ids_to_revert)} records"
        )
        return len(ids_to_revert)

    # Otherwise check each record individually: does the student still qualify?
    threshold = MAX_OVERDUE_BEFORE_RECOVERY

    # Group by course to batch activity/submission queries
    by_course: dict = {}
    for r in pending:
        by_course.setdefault(r["course_id"], []).append(r)

    for course_id, records in by_course.items():
        # Overdue non-recovery activities since feature was enabled
        overdue_acts = await db.activities.find({
            "course_id": course_id,
            "is_recovery": {"$ne": True},
            "due_date": {"$lt": now_iso, "$gte": AUTO_RECOVERY_ENABLED_AT},
        }, {"_id": 0, "id": 1, "subject_id": 1}).to_list(2000)

        if not overdue_acts:
            # No overdue activities → all records for this course no longer valid
            for record in records:
                await _revert_single_auto_recovery(record)
                reverted += 1
            continue

        activity_ids = [a["id"] for a in overdue_acts]
        acts_by_subject = {}
        for a in overdue_acts:
            if a.get("subject_id"):
                acts_by_subject.setdefault(a["subject_id"], []).append(a["id"])

        student_ids = list({r["student_id"] for r in records})
        subs = await db.submissions.find(
            {"activity_id": {"$in": activity_ids}, "student_id": {"$in": student_ids}},
            {"_id": 0, "activity_id": 1, "student_id": 1}
        ).to_list(len(activity_ids) * len(student_ids) + 1)
        submitted_pairs = {(s["student_id"], s["activity_id"]) for s in subs}

        for record in records:
            sid = record["student_id"]
            subj_id = record["subject_id"]
            act_ids_for_subject = acts_by_subject.get(subj_id, [])
            missing = sum(
                1 for aid in act_ids_for_subject
                if (sid, aid) not in submitted_pairs
            )
            if missing < threshold:
                await _revert_single_auto_recovery(record)
                reverted += 1

    if reverted:
        logger.info(f"revert_stale_auto_recoveries: reverted {reverted} records that no longer qualify")
    return reverted


async def _revert_single_auto_recovery(record: dict):
    """Remove a single pending auto-recovery record and restore the student's previous status."""
    student_id = record["student_id"]
    program_id = record.get("program_id")
    prev_status = record.get("previous_program_status", "activo")

    await db.failed_subjects.delete_one({"id": record["id"]})

    if program_id:
        # Only restore if the student is still in pendiente_recuperacion for this program
        # (they might have other reasons to be in recovery — don't blindly overwrite)
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
    logger.info(
        f"Reverted auto-recovery: student={student_id} subject={record.get('subject_id')} "
        f"course={record.get('course_id')} restored_status={prev_status}"
    )


async def close_module_internal(module_number: int, program_id: Optional[str] = None):
    """
    Internal function to close a module for a program. 
    Reviews all student grades and:
    - If student passed all subjects: promote to next module or graduate
    - If student failed any subject: mark as 'pendiente_recuperacion'
    
    This function can be called both by the API endpoint and the automatic scheduler.
    """
    # Business rule (2026-02-25): no longer restricting to modules 1-2; supports N modules.
    if not isinstance(module_number, int) or module_number < 1:
        raise ValueError(f"Número de módulo inválido: debe ser un entero >= 1, got {module_number}")
    
    # Get students enrolled in this program who are currently activo for that program.
    # Business rule (2026-02-25): filter by per-program status (not global estado) so that
    # multi-program students in pendiente_recuperacion for another program are not incorrectly
    # included in this module's closure.
    # Dual-filter rationale: program_statuses.{program_id}=="activo" ensures per-program
    # correctness; the $or on program_id/program_ids restricts to students enrolled in the
    # target program (supports both legacy single-program and multi-program data shapes).
    query: dict = {"role": "estudiante"}
    if program_id:
        query[f"program_statuses.{program_id}"] = "activo"
        query["$or"] = [
            {"program_id": program_id},
            {"program_ids": program_id}
        ]
    else:
        query["estado"] = "activo"
    
    students = await db.users.find(query, {
        "_id": 0, "id": 1, "name": 1, "module": 1, "program_modules": 1,
        "program_statuses": 1, "program_id": 1, "program_ids": 1, "estado": 1
    }).to_list(5000)
    
    promoted_count = 0
    graduated_count = 0
    recovery_count = 0
    skipped_no_grades = 0
    failed_subjects_records = []
    promotion_pending_ops: list = []
    user_bulk_ops: list = []

    # Get courses/groups — filter by program_id when known to reduce data loaded
    courses_query = {"program_id": program_id} if program_id else {}
    courses = await db.courses.find(courses_query, {"_id": 0}).to_list(5000)
    
    # Load subjects for per-subject grade calculations
    all_subjects = await db.subjects.find({}, {"_id": 0, "id": 1, "name": 1, "module_number": 1}).to_list(1000)
    subject_name_map = {s["id"]: s["name"] for s in all_subjects}
    subject_module_map = {s["id"]: (s.get("module_number") or 1) for s in all_subjects}
    
    # Pre-load programs for N-module max_modules determination
    all_programs = await db.programs.find({}, {"_id": 0, "id": 1, "modules": 1}).to_list(100)
    program_max_modules_map = {
        p["id"]: max(len(p.get("modules") or []), 2)
        for p in all_programs
    }
    
    # Cargar TODAS las grades de todos los cursos en UNA sola query (optimización crítica)
    all_course_ids = [c["id"] for c in courses]
    # Compute grade averages in MongoDB to avoid loading all grade documents into memory
    pipeline = [
        {"$match": {"course_id": {"$in": all_course_ids}, "value": {"$ne": None}}},
        {"$group": {
            "_id": {
                "student_id": "$student_id",
                "course_id": "$course_id",
                "subject_id": "$subject_id"
            },
            "avg_value": {"$avg": "$value"},
            "count": {"$sum": 1}
        }}
    ]
    aggregated_grades = await db.grades.aggregate(pipeline).to_list(200000)
    # Build index: (student_id, course_id, subject_id) -> {"avg": float, "count": int}
    grades_avg_index = {}
    # Secondary index: (student_id, course_id) -> list of {"avg", "count"} for fallback path
    course_grades_index: dict = {}
    student_graded_courses = {}
    for g in aggregated_grades:
        key = (g["_id"]["student_id"], g["_id"]["course_id"], g["_id"]["subject_id"])
        entry = {"avg": g["avg_value"], "count": g["count"]}
        grades_avg_index[key] = entry
        course_grades_index.setdefault((g["_id"]["student_id"], g["_id"]["course_id"]), []).append(entry)
        student_graded_courses.setdefault(g["_id"]["student_id"], set()).add(g["_id"]["course_id"])

    for student in students:
        student_id = student["id"]
        student_program_modules = student.get("program_modules", {})
        
        # Check if student is in the specified module for any of their programs
        programs_in_module = []
        if program_id:
            # Check specific program
            if student_program_modules.get(program_id) == module_number:
                programs_in_module.append(program_id)
        else:
            # Check all programs
            for prog_id, mod_num in student_program_modules.items():
                if mod_num == module_number:
                    programs_in_module.append(prog_id)
        
        if not programs_in_module:
            continue  # Student not in this module
        
        # Get all courses for this student in the specified programs
        student_courses = [c for c in courses if student_id in c.get("student_ids", []) and c["program_id"] in programs_in_module]
        
        # Skip students with no grades in any of their module courses — teacher may have
        # forgotten to grade them. Count and log them instead of processing with 0.0 averages.
        graded_course_ids = student_graded_courses.get(student_id, set())
        if student_courses and not any(c["id"] in graded_course_ids for c in student_courses):
            skipped_no_grades += 1
            logger.debug(
                f"Student {student_id} skipped in module {module_number} closure: "
                "no grades found in any enrolled course"
            )
            continue
        
        # Group grades by course; detect failing subjects individually
        failed_courses = []
        for course in student_courses:
            subject_ids = course.get("subject_ids") or []
            if not subject_ids and course.get("subject_id"):
                subject_ids = [course["subject_id"]]
            
            course_has_failing = False
            if subject_ids:
                # Create one record per failing subject (only subjects belonging to the module being closed)
                for subject_id in subject_ids:
                    # Only process subjects that belong to the module being closed.
                    # Default to module 1 for subjects without module_number, so they're
                    # included in module 1 closures but excluded from module 2+ closures.
                    if subject_module_map.get(subject_id, 1) != module_number:
                        continue
                    grade_info = grades_avg_index.get((student_id, course["id"], subject_id))
                    subject_avg = grade_info["avg"] if grade_info else 0.0
                    
                    if subject_avg < 3.0:
                        course_has_failing = True
                        subject_name = subject_name_map.get(subject_id, "Desconocido")
                        failed_subjects_records.append({
                            "id": str(uuid.uuid4()),
                            "student_id": student_id,
                            "student_name": student["name"],
                            "course_id": course["id"],
                            "course_name": course["name"],
                            "subject_id": subject_id,
                            "subject_name": subject_name,
                            "program_id": course["program_id"],
                            "module_number": module_number,
                            "average_grade": round(subject_avg, 2),
                            "recovery_approved": False,
                            "recovery_completed": False,
                            "previous_program_status": (student.get("program_statuses") or {}).get(course["program_id"], "activo"),
                            "created_at": datetime.now(timezone.utc).isoformat()
                        })
            else:
                # Fallback: no subjects defined, use course-level average (weighted by count)
                course_entries = course_grades_index.get((student_id, course["id"]), [])
                total_sum = sum(e["avg"] * e["count"] for e in course_entries)
                total_count = sum(e["count"] for e in course_entries)
                average = total_sum / total_count if total_count > 0 else 0.0
                
                if average < 3.0:
                    course_has_failing = True
                    failed_subjects_records.append({
                        "id": str(uuid.uuid4()),
                        "student_id": student_id,
                        "student_name": student["name"],
                        "course_id": course["id"],
                        "course_name": course["name"],
                        "program_id": course["program_id"],
                        "module_number": module_number,
                        "average_grade": round(average, 2),
                        "recovery_approved": False,
                        "recovery_completed": False,
                        "previous_program_status": (student.get("program_statuses") or {}).get(course["program_id"], "activo"),
                        "created_at": datetime.now(timezone.utc).isoformat()
                    })
            
            if course_has_failing:
                failed_courses.append({
                    "course_id": course["id"],
                    "course_name": course["name"],
                    "program_id": course["program_id"],
                })
        
        # Determine student status
        if failed_courses:
            # Student failed some subjects - mark as pending recovery per-program
            recovery_count += 1
            
            # Collect programs where student failed
            failed_program_ids = list({f["program_id"] for f in failed_courses})
            
            # Update program_statuses per-program and derive global estado
            student_program_statuses = student.get("program_statuses") or {}
            for prog_id in failed_program_ids:
                student_program_statuses[prog_id] = "pendiente_recuperacion"
            new_global_estado = derive_estado_from_program_statuses(student_program_statuses)
            user_bulk_ops.append(UpdateOne(
                {"id": student_id},
                {"$set": {
                    "program_statuses": student_program_statuses,
                    "estado": new_global_estado
                }}
            ))
        else:
            # Student passed all courses.
            # If any of the student's courses in this module has a recovery_close date
            # configured, defer the promotion/graduation to recovery_close processing.
            # This ensures students advance exactly when the recovery period closes,
            # not at the module close date.
            any_recovery_close = any(
                (c.get("module_dates") or {}).get(str(module_number), {}).get("recovery_close")
                for c in student_courses
            )
            if any_recovery_close:
                # Promotion deferred; the scheduler's recovery_close section will handle it.
                # Business rule (2026-02-25): set program_promotion_pending so the frontend
                # can show "Aprobado (pend. avance)" and the field is cleared at recovery_close.
                pending_set = {f"program_promotion_pending.{p}": True for p in programs_in_module}
                if pending_set:
                    promotion_pending_ops.append(UpdateOne({"id": student_id}, {"$set": pending_set}))
                promoted_count += 1
            else:
                # No recovery period configured: promote immediately (backward compatibility).
                student_program_statuses = student.get("program_statuses") or {}
                for prog_id in programs_in_module:
                    current_module = student_program_modules.get(prog_id, 1)
                    prog_max_modules = program_max_modules_map.get(prog_id, 2)

                    if current_module < prog_max_modules:
                        # Promote to next module
                        student_program_modules[prog_id] = current_module + 1
                        student_program_statuses[prog_id] = "activo"
                        promoted_count += 1
                    else:
                        # Last module completed - graduate
                        graduated_count += 1
                        student_program_statuses[prog_id] = "egresado"
                
                new_global_estado = derive_estado_from_program_statuses(student_program_statuses)
                # Update program_modules and program_statuses
                user_bulk_ops.append(UpdateOne(
                    {"id": student_id},
                    {"$set": {
                        "program_modules": student_program_modules,
                        "program_statuses": student_program_statuses,
                        "estado": new_global_estado
                    }}
                ))
    
    # Bulk write deferred program_promotion_pending updates
    if promotion_pending_ops:
        await db.users.bulk_write(promotion_pending_ops, ordered=False)

    # Bulk write status updates for failed/promoted/graduated students
    if user_bulk_ops:
        await db.users.bulk_write(user_bulk_ops, ordered=False)

    # Bulk insert failed subjects records
    if failed_subjects_records:
        await db.failed_subjects.insert_many(failed_subjects_records)
    
    if skipped_no_grades > 0:
        logger.warning(
            f"WARNING: {skipped_no_grades} students skipped due to missing grades in module {module_number}"
        )
    
    return {
        "message": "Cierre de módulo completado",
        "module_number": module_number,
        "program_id": program_id,
        "promoted_count": promoted_count,
        "graduated_count": graduated_count,
        "recovery_pending_count": recovery_count,
        "failed_subjects_count": len(failed_subjects_records),
        "skipped_no_grades_count": skipped_no_grades
    }


@router.post("/admin/set-all-students-module-1")
async def set_all_students_module_1(user=Depends(get_current_user)):
    """Admin endpoint to set all existing students to Module 1"""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede realizar esta operación")
    
    # Update all students to module 1
    result = await db.users.update_many(
        {"role": "estudiante"},
        {"$set": {"module": 1}}
    )
    
    return {
        "message": f"Se actualizaron {result.modified_count} estudiantes al Módulo 1",
        "modified_count": result.modified_count
    }

@router.post("/admin/close-module")
async def close_module(module_number: int, program_id: Optional[str] = None, user=Depends(get_current_user)):
    """
    Admin manually closes a module for a program. 
    Reviews all student grades and:
    - If student passed all subjects: promote to next module or graduate
    - If student failed any subject: mark as 'pendiente_recuperacion'
    
    NOTE: This is a manual endpoint. Module closure also happens automatically
    when the configured close date is reached.
    """
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede cerrar módulos")
    
    try:
        result = await close_module_internal(module_number, program_id)
        await log_audit("module_closed", user["id"], user["role"], {"module_number": module_number, "program_id": program_id or "all", "promoted": result.get("promoted_count", 0), "graduated": result.get("graduated_count", 0), "recovery": result.get("recovery_count", 0)})
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/admin/force-recovery-check")
async def force_recovery_check(user=Depends(get_current_user)):
    """
    Manually trigger the automatic recovery-close check and expulsion logic
    (same logic that the daily scheduler runs at 02:00 AM).

    Use this endpoint when the scheduler may not have run at the expected time
    or when you need to immediately apply expulsions after recovery deadlines have passed.
    Only accessible by admin users.
    """
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede forzar la verificación de recuperaciones")
    try:
        await check_and_close_modules()
        await log_audit(
            "force_recovery_check", user["id"], user["role"],
            {"trigger": "manual_admin"}
        )
        return {"message": "Verificación de recuperaciones ejecutada exitosamente"}
    except Exception as e:
        logger.error(f"Error in force_recovery_check endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error ejecutando verificación: {str(e)}")

@router.get("/admin/auto-recovery-candidates")
async def get_auto_recovery_candidates(user=Depends(get_current_user)):
    """
    Dry-run of the overdue auto-recovery check.
    Returns the list of (student, subject, course) combinations that WOULD enter recovery
    if the scheduler ran right now, without creating any records.
    Requires AUTO_RECOVERY_ENABLED_AT to be set.
    """
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")
    if not AUTO_RECOVERY_ENABLED_AT:
        return {
            "enabled": False,
            "message": "AUTO_RECOVERY_ENABLED_AT no está configurado. La función está desactivada.",
            "candidates": [],
        }
    candidates = await check_overdue_auto_recovery(dry_run=True)
    return {
        "enabled": True,
        "threshold": MAX_OVERDUE_BEFORE_RECOVERY,
        "enabled_at": AUTO_RECOVERY_ENABLED_AT,
        "candidate_count": len(candidates),
        "candidates": candidates,
    }


@router.post("/admin/revert-auto-recoveries")
async def trigger_revert_auto_recoveries(user=Depends(get_current_user)):
    """
    Manually trigger the reversal of stale auto-recovery records.
    Useful when module dates or AUTO_RECOVERY_ENABLED_AT are changed and the admin
    wants to immediately restore affected students without waiting for the nightly scheduler.
    Only pending (not yet approved) records are reverted.
    """
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")
    reverted = await revert_stale_auto_recoveries()
    return {
        "reverted": reverted,
        "message": (
            f"Se revirtieron {reverted} recuperaciones automáticas que ya no aplican. "
            "Los estudiantes fueron restaurados a su estado anterior."
            if reverted > 0
            else "No se encontraron recuperaciones automáticas para revertir."
        ),
    }


@router.get("/admin/recovery-panel")
async def get_recovery_panel(user=Depends(get_current_user)):
    """
    Get all students with failed subjects pending recovery approval.
    Returns detailed information for admin to review and approve recoveries.
    Only shows in-process records: not yet decided, or approved-but-not-completed.
    Excluded: recovery_rejected=True or (recovery_approved=True and recovery_completed=True).
    Also detects students in courses where the module close date has passed
    and they have failing averages, even if they haven't been explicitly processed.
    Only shows entries where the group's recovery period (recovery_close) is still open.
    """
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede acceder al panel de recuperaciones")
    
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Pre-load all courses and subjects for efficient lookups
    all_courses = await db.courses.find({}, {"_id": 0}).to_list(1000)
    course_map = {c["id"]: c for c in all_courses}
    all_subjects = await db.subjects.find({}, {"_id": 0, "id": 1, "name": 1, "module_number": 1}).to_list(1000)
    subject_map = {s["id"]: s["name"] for s in all_subjects}
    subject_module_map = {s["id"]: (s.get("module_number") or 1) for s in all_subjects}

    def get_subject_names(course_doc):
        """Return list of ALL subject names for a course (fallback)."""
        sids = course_doc.get("subject_ids") or []
        if not sids and course_doc.get("subject_id"):
            sids = [course_doc["subject_id"]]
        names = [subject_map[sid] for sid in sids if sid in subject_map]
        return names if names else [course_doc.get("name", "Sin nombre")]

    def get_failing_subject_names(student_id, course_id, course_doc, grades_index):
        """Return only the subject names where the student's average is < 3.0.
        Falls back to all course subjects if per-subject data is unavailable."""
        sids = course_doc.get("subject_ids") or []
        if not sids and course_doc.get("subject_id"):
            sids = [course_doc["subject_id"]]
        if not sids:
            return [course_doc.get("name", "Sin nombre")]
        failing = []
        for sid in sids:
            values = grades_index.get((student_id, course_id, sid), [])
            # No grades or average < 3.0 → consider failed
            avg = sum(values) / len(values) if values else 0.0
            if avg < 3.0 and sid in subject_map:
                failing.append(subject_map[sid])
        return failing if failing else get_subject_names(course_doc)

    def get_failing_subjects_with_ids(student_id, course_id, course_doc, grades_index, filter_module=None):
        """Return list of (subject_id, subject_name, avg) for each failing subject.
        If filter_module is provided, only subjects belonging to that module are returned."""
        sids = course_doc.get("subject_ids") or []
        if not sids and course_doc.get("subject_id"):
            sids = [course_doc["subject_id"]]
        if not sids:
            return []
        failing = []
        for sid in sids:
            if filter_module is not None and subject_module_map.get(sid, 1) != filter_module:
                continue
            values = grades_index.get((student_id, course_id, sid), [])
            avg = sum(values) / len(values) if values else 0.0
            if avg < 3.0 and sid in subject_map:
                failing.append((sid, subject_map[sid], round(avg, 2)))
        return failing

    def get_recovery_close(course_doc, module_number):
        """Return the recovery_close date string for a given module in a course, or None."""
        module_dates = course_doc.get("module_dates") or {}
        dates = module_dates.get(str(module_number)) or {}
        return dates.get("recovery_close")

    def get_next_module_start(course_doc, module_number):
        """Return the start date of the next module in a course, or None."""
        module_dates = course_doc.get("module_dates") or {}
        next_dates = module_dates.get(str(module_number + 1)) or {}
        return next_dates.get("start")

    # Fetch only records still in-process for admin action.
    failed_records = await db.failed_subjects.find(
        {"recovery_processed": {"$ne": True}},
        {"_id": 0}
    ).to_list(1000)
    
    # Build a lookup of student cedulas for human-readable IDs
    student_ids_in_records = list({r["student_id"] for r in failed_records})
    students_lookup = {}
    if student_ids_in_records:
        student_docs = await db.users.find(
            {"id": {"$in": student_ids_in_records}},
            {"_id": 0, "id": 1, "cedula": 1, "name": 1}
        ).to_list(5000)
        students_lookup = {s["id"]: s for s in student_docs}
    
    # Pre-load grades via aggregation (one query, not N docs) for per-subject averages
    course_ids_in_records = list({r["course_id"] for r in failed_records})
    grades_index: dict = {}
    teacher_graded_index: dict = {}
    if student_ids_in_records and course_ids_in_records:
        grade_agg = await db.grades.aggregate([
            {"$match": {
                "student_id": {"$in": student_ids_in_records},
                "course_id": {"$in": course_ids_in_records},
            }},
            {"$group": {
                "_id": {"student_id": "$student_id", "course_id": "$course_id", "subject_id": "$subject_id"},
                "values": {"$push": {"$cond": [{"$ne": ["$value", None]}, "$value", "$$REMOVE"]}},
                "last_recovery_status": {"$last": "$recovery_status"},
            }}
        ]).to_list(50000)
        for _g in grade_agg:
            key = (_g["_id"]["student_id"], _g["_id"]["course_id"], _g["_id"].get("subject_id"))
            if _g["values"]:
                grades_index[key] = _g["values"]
            if _g.get("last_recovery_status"):
                teacher_graded_index[key] = _g["last_recovery_status"]

    # Get all programs for reference
    programs = await db.programs.find({}, {"_id": 0}).to_list(100)
    program_map = {p["id"]: p["name"] for p in programs}
    program_close_map = {}
    for p in programs:
        pid = p.get("id")
        if not pid:
            continue
        max_mod = max(len(p.get("modules") or []), 2)
        for mn in range(1, max_mod + 1):
            close_val = p.get(f"module{mn}_close_date")
            if close_val:
                program_close_map[(pid, mn)] = close_val
    
    # Organize by student; only include records whose recovery period is still open
    students_map = {}
    for record in failed_records:
        course_doc = course_map.get(record["course_id"]) or {}
        module_num = record.get("module_number", 1)
        recovery_close = get_recovery_close(course_doc, module_num)
        if not recovery_close:
            recovery_close = program_close_map.get((record.get("program_id", ""), module_num))
        # Skip records whose recovery period has already closed
        if recovery_close and recovery_close <= today_str:
            continue
        next_module_start = get_next_module_start(course_doc, module_num)

        student_id = record["student_id"]
        if student_id not in students_map:
            student_doc = students_lookup.get(student_id) or {}
            students_map[student_id] = {
                "student_id": student_id,
                "student_name": record["student_name"],
                "student_cedula": student_doc.get("cedula") or "",
                "failed_subjects": []
            }
        
        subject_name = record.get("subject_name") or record.get("course_name", "Sin nombre")
        subject_id_for_record = record.get("subject_id")
        teacher_status = teacher_graded_index.get((student_id, record["course_id"], subject_id_for_record))
        if not teacher_status:
            teacher_status = teacher_graded_index.get((student_id, record["course_id"], None))

        # Compute a human-readable status for the record
        ts = record.get("teacher_graded_status") if record.get("teacher_graded_status") is not None else teacher_status
        if record.get("recovery_completed"):
            rec_status = "teacher_approved" if ts == "approved" else "teacher_rejected"
        else:
            # Not yet graded by teacher (may or may not be admin-approved)
            rec_status = "pending"

        students_map[student_id]["failed_subjects"].append({
            "id": record["id"],
            "course_id": record["course_id"],
            "course_name": record["course_name"],
            "subject_name": subject_name,
            "program_id": record["program_id"],
            "program_name": program_map.get(record["program_id"], "Desconocido"),
            "module_number": record["module_number"],
            "average_grade": next((v for v in (record.get("average_grade"), record.get("avg"), 0.0) if v is not None), 0.0),
            "recovery_approved": record["recovery_approved"],
            "recovery_completed": record["recovery_completed"],
            "recovery_processed": record.get("recovery_processed", False),
            "processed_at": record.get("processed_at"),
            "recovery_close": recovery_close,
            "next_module_start": next_module_start,
            "teacher_graded_status": ts,
            "status": rec_status,
            "recovery_reason": record.get("recovery_reason"),
            "overdue_count": record.get("overdue_count"),
        })
    
    # Also detect students in courses with past module close dates who have failing averages
    # but are not yet in the failed_subjects collection.
    # Show entries where the recovery period is still open.

    # Track which (student_id, course_id, subject_id) combos already have a persisted record
    already_tracked = set()
    for record in failed_records:
        already_tracked.add((record["student_id"], record["course_id"], record.get("subject_id")))

    # Program close-date fallback map (program_id, module_number) -> close_date
    program_close_map = {}
    for p in programs:
        pid = p.get("id")
        if not pid:
            continue
        max_mod = max(len(p.get("modules") or []), 2)
        for mn in range(1, max_mod + 1):
            close_val = p.get(f"module{mn}_close_date")
            if close_val:
                program_close_map[(pid, mn)] = close_val

    # --- Pass 1: identify courses that need auto-detection (no DB queries) ---
    autodetect_work: list = []  # list of (course, module_number, recovery_close)
    for course in all_courses:
        module_dates = course.get("module_dates") or {}
        if not module_dates:
            pid = course.get("program_id", "")
            module_dates = {
                str(mn): {"end": close_val, "recovery_close": close_val}
                for (prog_id, mn), close_val in program_close_map.items()
                if prog_id == pid
            }
        for module_key, dates in module_dates.items():
            module_number = int(module_key) if str(module_key).isdigit() else None
            if not module_number:
                continue
            close_date = (dates or {}).get("end") or program_close_map.get(
                (course.get("program_id", ""), module_number)
            )
            if not close_date or close_date > today_str:
                continue
            recovery_close = (dates or {}).get("recovery_close")
            if recovery_close and recovery_close <= today_str:
                continue
            autodetect_work.append((course, module_number, recovery_close))

    if autodetect_work:
        # --- Pass 2: bulk-load grades and students (2 queries total, not N) ---
        autodetect_course_ids = list({c["id"] for c, _, _ in autodetect_work})

        # Use aggregation to get per-(student, course, subject) averages instead of raw docs
        autodetect_pipeline = [
            {"$match": {"course_id": {"$in": autodetect_course_ids}, "value": {"$ne": None}}},
            {"$group": {
                "_id": {"student_id": "$student_id", "course_id": "$course_id", "subject_id": "$subject_id"},
                "avg": {"$avg": "$value"},
                "count": {"$sum": 1}
            }}
        ]
        autodetect_agg = await db.grades.aggregate(autodetect_pipeline).to_list(200000)

        # Build indexes
        # (student_id, course_id, subject_id) -> [avg]  — reuse existing grades_index format
        autodetect_grades_index: dict = {}
        autodetect_graded_ids: dict = {}  # course_id -> set of student_ids with any grade
        for _g in autodetect_agg:
            _sid = _g["_id"]["student_id"]
            _cid = _g["_id"]["course_id"]
            _subj = _g["_id"]["subject_id"]
            _avg = float(_g["avg"])
            autodetect_grades_index.setdefault((_sid, _cid, _subj), []).append(_avg)
            autodetect_graded_ids.setdefault(_cid, set()).add(_sid)

        # Collect all candidate student IDs across all relevant courses
        all_candidate_ids: set = set()
        for course, _, _ in autodetect_work:
            enrolled = set(course.get("student_ids") or [])
            removed = set(course.get("removed_student_ids") or [])
            graded = autodetect_graded_ids.get(course["id"], set())
            all_candidate_ids.update((enrolled | graded) - removed)

        # Bulk-load student docs (one query)
        autodetect_students: dict = {}
        if all_candidate_ids:
            student_docs = await db.users.find(
                {"id": {"$in": list(all_candidate_ids)}, "role": "estudiante"},
                {"_id": 0, "id": 1, "name": 1, "cedula": 1}
            ).to_list(10000)
            autodetect_students = {s["id"]: s for s in student_docs}

        # --- Pass 3: process each (course, module) using pre-loaded data ---
        for course, module_number, recovery_close in autodetect_work:
            enrolled_ids = set(course.get("student_ids") or [])
            removed_ids = set(course.get("removed_student_ids") or [])
            graded_ids = autodetect_graded_ids.get(course["id"], set())
            candidate_student_ids = list((enrolled_ids | graded_ids) - removed_ids)
            if not candidate_student_ids:
                continue

            for student_id in candidate_student_ids:
                student = autodetect_students.get(student_id)
                if not student:
                    continue

                failing_subjects = get_failing_subjects_with_ids(
                    student_id, course["id"], course,
                    autodetect_grades_index, module_number
                )

                # Fallback course-level average when no subjects defined
                all_avgs = [
                    v
                    for key, vals in autodetect_grades_index.items()
                    if key[0] == student_id and key[1] == course["id"]
                    for v in vals
                ]
                average = sum(all_avgs) / len(all_avgs) if all_avgs else 0.0

                if not failing_subjects and average >= 3.0:
                    continue

                if student_id not in students_map:
                    students_map[student_id] = {
                        "student_id": student_id,
                        "student_name": student.get("name", "Desconocido"),
                        "student_cedula": student.get("cedula") or "",
                        "failed_subjects": []
                    }

                if failing_subjects:
                    for subj_id, subj_name, subj_avg in failing_subjects:
                        if (student_id, course["id"], subj_id) in already_tracked:
                            continue
                        temp_record_id = f"auto-{student_id}-{course['id']}-{subj_id}-{module_number}"
                        teacher_status = teacher_graded_index.get((student_id, course["id"], subj_id)) or \
                                         teacher_graded_index.get((student_id, course["id"], None))
                        students_map[student_id]["failed_subjects"].append({
                            "id": temp_record_id,
                            "course_id": course["id"],
                            "course_name": course.get("name", "Sin nombre"),
                            "subject_id": subj_id,
                            "subject_name": subj_name,
                            "program_id": course.get("program_id", ""),
                            "program_name": program_map.get(course.get("program_id", ""), "Desconocido"),
                            "module_number": module_number,
                            "average_grade": subj_avg,
                            "recovery_approved": False,
                            "recovery_completed": False,
                            "recovery_close": recovery_close,
                            "next_module_start": get_next_module_start(course, module_number),
                            "auto_detected": True,
                            "teacher_graded_status": teacher_status,
                            "status": "pending"
                        })
                        already_tracked.add((student_id, course["id"], subj_id))
                else:
                    if (student_id, course["id"], None) in already_tracked:
                        continue
                    temp_record_id = f"auto-{student_id}-{course['id']}-{module_number}"
                    students_map[student_id]["failed_subjects"].append({
                        "id": temp_record_id,
                        "course_id": course["id"],
                        "course_name": course.get("name", "Sin nombre"),
                        "subject_name": course.get("name", "Sin nombre"),
                        "program_id": course.get("program_id", ""),
                        "program_name": program_map.get(course.get("program_id", ""), "Desconocido"),
                        "module_number": module_number,
                        "average_grade": round(average, 2),
                        "recovery_approved": False,
                        "recovery_completed": False,
                        "recovery_close": recovery_close,
                        "next_module_start": get_next_module_start(course, module_number),
                        "auto_detected": True,
                        "teacher_graded_status": teacher_graded_index.get((student_id, course["id"], None)),
                        "status": "pending"
                    })
                    already_tracked.add((student_id, course["id"], None))
    
    filtered_students = [s for s in students_map.values() if s.get("failed_subjects")]

    return {
        "students": filtered_students,
        "total_students": len(filtered_students),
        "total_failed_subjects": sum(len(s["failed_subjects"]) for s in filtered_students)
    }

@router.post("/admin/approve-recovery")
async def approve_recovery_for_subject(failed_subject_id: str, approve: bool, user=Depends(get_current_user)):
    """
    Admin approves or rejects recovery for a specific failed subject.
    If approved (approve=True), student can see and complete recovery activities.
    If rejected (approve=False), student is immediately removed from all program courses
    and marked as 'reprobado'.
    Handles both persisted records and auto-detected entries (id starts with 'auto-').
    """
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede aprobar recuperaciones")

    now = datetime.now(timezone.utc)

    # Handle auto-detected entries (not persisted yet).
    # Formats:
    #   Old: auto-{student_id}-{course_id}-{module_number}           (sc_part = 73 chars)
    #   New: auto-{student_id}-{course_id}-{subject_id}-{module_number} (sc_part = 110 chars)
    if failed_subject_id.startswith("auto-"):
        # UUIDs are always exactly 36 chars. Strip 'auto-' prefix then parse fixed-length fields.
        remainder = failed_subject_id[5:]  # strip 'auto-'
        # last '-' separates the module_number (an integer, no dashes)
        last_dash = remainder.rfind("-")
        if last_dash == -1:
            raise HTTPException(status_code=404, detail="Registro de materia reprobada no encontrado")
        module_str = remainder[last_dash + 1:]
        sc_part = remainder[:last_dash]
        # sc_part is either:
        #   "{student_id}-{course_id}"                   → 36 + 1 + 36 = 73 chars (old)
        #   "{student_id}-{course_id}-{subject_id}"      → 36 + 1 + 36 + 1 + 36 = 110 chars (new)
        subject_id = None
        # UUIDs are 36 chars each. sc_part lengths:
        #   old: 36 (student) + 1 (-) + 36 (course)          = 73
        #   new: 36 (student) + 1 (-) + 36 (course) + 1 (-) + 36 (subject) = 110
        if len(sc_part) == 73:
            student_id = sc_part[:36]
            course_id = sc_part[37:]
        elif len(sc_part) == 110:
            student_id = sc_part[:36]
            course_id = sc_part[37:73]
            subject_id = sc_part[74:]
        else:
            raise HTTPException(status_code=404, detail="Registro de materia reprobada no encontrado")

        # Validate that both IDs exist in the database
        student = await db.users.find_one({"id": student_id, "role": "estudiante"}, {"_id": 0})
        course = await db.courses.find_one({"id": course_id}, {"_id": 0})
        if not student or not course:
            raise HTTPException(status_code=404, detail="Estudiante o grupo no encontrado")

        prog_id = course.get("program_id", "")
        student_module = (student.get("program_modules") or {}).get(prog_id) or student.get("module")
        module_number = int(module_str) if module_str.isdigit() else 1

        all_grades = await db.grades.find({"student_id": student_id, "course_id": course_id}, {"_id": 0}).to_list(100)

        # Compute average: per-subject if subject_id available, otherwise course-level
        if subject_id:
            subject_grade_values = [g["value"] for g in all_grades if g.get("subject_id") == subject_id and g.get("value") is not None]
            average = sum(subject_grade_values) / len(subject_grade_values) if subject_grade_values else 0.0
        else:
            grade_values = [g["value"] for g in all_grades if g.get("value") is not None]
            average = sum(grade_values) / len(grade_values) if grade_values else 0.0

        if not approve:
            # Admin explicitly rejects this auto-detected recovery: create a rejection record
            # marked for deferred expulsion at recovery_close.
            rejection_record = {
                "id": str(uuid.uuid4()),
                "student_id": student_id,
                "student_name": student.get("name", "Desconocido"),
                "course_id": course_id,
                "course_name": course.get("name", "Sin nombre"),
                "program_id": prog_id,
                "module_number": module_number,
                "average_grade": round(average, 2),
                "recovery_approved": False,
                "recovery_rejected": True,
                "recovery_completed": False,
                "recovery_processed": False,
                "rejected_by": user["id"],
                "rejected_at": now.isoformat(),
                "created_at": now.isoformat()
            }
            if subject_id:
                subject_doc = await db.subjects.find_one({"id": subject_id}, {"_id": 0, "name": 1})
                rejection_record["subject_id"] = subject_id
                rejection_record["subject_name"] = subject_doc.get("name", "Desconocido") if subject_doc else "Desconocido"
            await db.failed_subjects.insert_one(rejection_record)
            logger.info(
                f"Admin {user['id']} rejected recovery for student {student_id} "
                f"in course {course_id} (auto-detected entry); deferred to recovery_close"
            )
            await log_audit(
                "recovery_rejected_by_admin_deferred", user["id"], user["role"],
                {"student_id": student_id, "course_id": course_id, "program_id": prog_id,
                 "module_number": module_number}
            )
            return {"message": "Recuperación rechazada. El estudiante será retirado del grupo al cierre del período de recuperaciones."}

        # Module alignment: recovery can only be approved for the student's current module
        if student_module is not None and student_module != module_number:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"No se puede aprobar: la recuperación es del Módulo {module_number} "
                    f"pero el estudiante está en el Módulo {student_module}."
                )
            )

        new_record = {
            "id": str(uuid.uuid4()),
            "student_id": student_id,
            "student_name": student.get("name", "Desconocido"),
            "course_id": course_id,
            "course_name": course.get("name", "Sin nombre"),
            "program_id": course.get("program_id", ""),
            "module_number": module_number,
            "average_grade": round(average, 2),
            "recovery_approved": True,
            "recovery_rejected": False,
            "recovery_completed": False,
            "approved_by": user["id"],
            "approved_at": now.isoformat(),
            "created_at": now.isoformat()
        }
        if subject_id:
            subject_doc = await db.subjects.find_one({"id": subject_id}, {"_id": 0, "name": 1})
            new_record["subject_id"] = subject_id
            new_record["subject_name"] = subject_doc.get("name", "Desconocido") if subject_doc else "Desconocido"
        # Deduplication: check if a matching unprocessed/unrejected record already exists
        # (prevents duplicate records when admin clicks approve multiple times on the same entry)
        dup_filter: dict = {
            "student_id": student_id,
            "course_id": course_id,
            "module_number": module_number,
            "recovery_processed": {"$ne": True},
            "recovery_rejected": {"$ne": True},
        }
        if subject_id:
            dup_filter["subject_id"] = subject_id
        else:
            dup_filter["subject_id"] = {"$exists": False}
        existing_dup = await db.failed_subjects.find_one(dup_filter, {"_id": 0, "id": 1, "recovery_approved": 1})
        if existing_dup:
            # Record already exists; ensure it is marked as approved (idempotent)
            if not existing_dup.get("recovery_approved"):
                await db.failed_subjects.update_one(
                    {"id": existing_dup["id"]},
                    {"$set": {"recovery_approved": True, "approved_by": user["id"], "approved_at": now.isoformat()}}
                )
            new_record["id"] = existing_dup["id"]
        else:
            await db.failed_subjects.insert_one(new_record)

        # Enable recovery activities for this student/course
        existing = await db.recovery_enabled.find_one({"student_id": student_id, "course_id": course_id, "subject_id": subject_id})
        if not existing:
            await db.recovery_enabled.insert_one({
                "id": str(uuid.uuid4()),
                "student_id": student_id,
                "course_id": course_id,
                "subject_id": subject_id,
                "enabled": True,
                "enabled_by": user["id"],
                "enabled_at": now.isoformat()
            })
        else:
            await db.recovery_enabled.update_one(
                {"id": existing["id"]},
                {"$set": {"enabled": True, "enabled_by": user["id"], "enabled_at": now.isoformat()}}
            )
        # Update program_statuses per-program and derive global estado
        prog_id = course.get("program_id", "")
        student_doc = await db.users.find_one({"id": student_id}, {"_id": 0, "program_statuses": 1})
        student_program_statuses = (student_doc or {}).get("program_statuses") or {}
        if prog_id:
            student_program_statuses[prog_id] = "pendiente_recuperacion"
        new_estado = derive_estado_from_program_statuses(student_program_statuses)
        update_fields = {"estado": new_estado}
        if prog_id:
            update_fields["program_statuses"] = student_program_statuses
        await db.users.update_one({"id": student_id}, {"$set": update_fields})

        return {"message": "Recuperación aprobada exitosamente"}

    # Find the failed subject record
    failed_record = await db.failed_subjects.find_one({"id": failed_subject_id}, {"_id": 0})
    if not failed_record:
        raise HTTPException(status_code=404, detail="Registro de materia reprobada no encontrado")

    if not approve:
        # Admin explicitly rejects this persisted recovery record.
        # Mark the record as rejected but leave recovery_processed=False so the
        # scheduler can handle expulsion at recovery_close.
        rej_student_id = failed_record["student_id"]
        rej_course_id = failed_record["course_id"]
        rej_prog_id = failed_record.get("program_id", "")
        # Mark this record as rejected, keeping it unprocessed for the scheduler
        await db.failed_subjects.update_one(
            {"id": failed_subject_id},
            {"$set": {
                "recovery_approved": False,
                "recovery_rejected": True,
                "recovery_processed": False,
                "rejected_by": user["id"],
                "rejected_at": now.isoformat(),
            }}
        )
        logger.info(
            f"Admin {user['id']} rejected recovery for student {rej_student_id} "
            f"in course {rej_course_id} (record {failed_subject_id}); deferred to recovery_close"
        )
        await log_audit(
            "recovery_rejected_by_admin_deferred", user["id"], user["role"],
            {"student_id": rej_student_id, "failed_subject_id": failed_subject_id,
             "course_id": rej_course_id, "program_id": rej_prog_id}
        )
        return {"message": "Recuperación rechazada. El estudiante será retirado del grupo al cierre del período de recuperaciones."}

    # Module alignment: reject approval if subject module doesn't match student's current module
    record_module = failed_record.get("module_number")
    if record_module is not None:
        stud_doc = await db.users.find_one({"id": failed_record["student_id"]}, {"_id": 0, "program_modules": 1, "module": 1})
        if stud_doc:
            rec_prog_id = failed_record.get("program_id", "")
            stud_mod = (stud_doc.get("program_modules") or {}).get(rec_prog_id) or stud_doc.get("module")
            if stud_mod is not None and stud_mod != record_module:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"No se puede aprobar: la recuperación es del Módulo {record_module} "
                        f"pero el estudiante está en el Módulo {stud_mod}."
                    )
                )
    
    # Update approval status
    await db.failed_subjects.update_one(
        {"id": failed_subject_id},
        {"$set": {
            "recovery_approved": True,
            "recovery_rejected": False,
            "approved_by": user["id"],
            "approved_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Enable recovery in the recovery_enabled collection
    recovery = {
        "id": str(uuid.uuid4()),
        "student_id": failed_record["student_id"],
        "course_id": failed_record["course_id"],
        "subject_id": failed_record.get("subject_id"),
        "enabled": True,
        "enabled_by": user["id"],
        "enabled_at": datetime.now(timezone.utc).isoformat()
    }
    
    existing = await db.recovery_enabled.find_one({
        "student_id": failed_record["student_id"],
        "course_id": failed_record["course_id"],
        "subject_id": failed_record.get("subject_id")
    })
    
    if not existing:
        await db.recovery_enabled.insert_one(recovery)
    else:
        await db.recovery_enabled.update_one(
            {"id": existing["id"]},
            {"$set": {"enabled": True, "enabled_by": user["id"], "enabled_at": datetime.now(timezone.utc).isoformat()}}
        )
    # Update program_statuses per-program and derive global estado
    prog_id = failed_record.get("program_id", "")
    student_doc = await db.users.find_one({"id": failed_record["student_id"]}, {"_id": 0, "program_statuses": 1})
    student_program_statuses = (student_doc or {}).get("program_statuses") or {}
    if prog_id:
        student_program_statuses[prog_id] = "pendiente_recuperacion"
    new_estado = derive_estado_from_program_statuses(student_program_statuses)
    update_fields = {"estado": new_estado}
    if prog_id:
        update_fields["program_statuses"] = student_program_statuses
    await db.users.update_one({"id": failed_record["student_id"]}, {"$set": update_fields})
    await log_audit("recovery_approved", user["id"], user["role"], {"student_id": failed_record["student_id"], "failed_subject_id": failed_subject_id, "subject_name": failed_record.get("subject_name", ""), "course_id": failed_record.get("course_id", "")})
    return {"message": "Recuperación aprobada exitosamente"}

@router.get("/admin/graduated-students-count")
async def get_graduated_students_count(user=Depends(get_current_user)):
    """
    Get count of graduated students for display purposes.
    """
    if user["role"] not in ["admin", "editor"]:
        raise HTTPException(status_code=403, detail="Solo admin/editor pueden ver esta información")
    
    count = await db.users.count_documents({"role": "estudiante", "estado": "egresado"})
    
    return {
        "count": count
    }

@router.post("/admin/reset-users")
async def reset_users(confirm_token: str = None):
    """
    DANGER: Deletes ALL users and creates fresh default users.
    Creates: 2 admins, 1 editor, 2 professors, 2 students
    
    Requires confirmation token: 'RESET_ALL_USERS_CONFIRM'
    
    This endpoint should be disabled or protected in production.
    Set environment variable ALLOW_USER_RESET=false to disable.
    """
    # Check if running in production environment
    if os.environ.get('RENDER') or os.environ.get('RAILWAY_ENVIRONMENT'):
        raise HTTPException(status_code=403, detail="This endpoint is disabled in production")

    # Check if endpoint is allowed (can be disabled via env var)
    allow_reset = os.environ.get('ALLOW_USER_RESET', 'true').lower() == 'true'
    if not allow_reset:
        raise HTTPException(
            status_code=403, 
            detail="Este endpoint está deshabilitado en producción"
        )
    
    # Require confirmation token
    if confirm_token != "RESET_ALL_USERS_CONFIRM":
        raise HTTPException(
            status_code=400,
            detail="Token de confirmación requerido. Parámetro: confirm_token='RESET_ALL_USERS_CONFIRM'"
        )
    
    # Delete ALL users
    deleted_count = await db.users.delete_many({})
    
    # Create new default users
    default_users = [
        # 2 Admins
        {
            "id": str(uuid.uuid4()),
            "name": "Admin Principal",
            "email": "admin@educando.com",
            "cedula": None,
            "password_hash": hash_password("Admin2026"),
            "role": "admin",
            "program_id": None,
            "phone": "3001234567",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Admin Secundario",
            "email": "admin2@educando.com",
            "cedula": None,
            "password_hash": hash_password("Admin2026"),
            "role": "admin",
            "program_id": None,
            "phone": "3001234568",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        # 1 Editor (logs in through profesor login)
        {
            "id": str(uuid.uuid4()),
            "name": "Editor Principal",
            "email": "editor@educando.com",
            "cedula": None,
            "password_hash": hash_password("Editor2026"),
            "role": "editor",
            "program_id": None,
            "phone": "3002222222",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        # 2 Professors
        {
            "id": str(uuid.uuid4()),
            "name": "María García",
            "email": "profesor@educando.com",
            "cedula": None,
            "password_hash": hash_password("Profe2026"),
            "role": "profesor",
            "program_id": None,
            "phone": "3007654321",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Carlos Rodríguez",
            "email": "profesor2@educando.com",
            "cedula": None,
            "password_hash": hash_password("Profe2026"),
            "role": "profesor",
            "program_id": None,
            "phone": "3009876543",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        # 2 Students
        {
            "id": str(uuid.uuid4()),
            "name": "Juan Martínez",
            "email": None,
            "cedula": "1001",
            "password_hash": hash_password("1001"),
            "role": "estudiante",
            "program_id": None,
            "phone": "3101234567",
            "active": True,
            "estado": "activo",
            "current_module": 1,
            "program_ids": [],
            "curso_ids": [],
            "program_modules": {},
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Ana Hernández",
            "email": None,
            "cedula": "1002",
            "password_hash": hash_password("1002"),
            "role": "estudiante",
            "program_id": None,
            "phone": "3207654321",
            "active": True,
            "estado": "activo",
            "current_module": 1,
            "program_ids": [],
            "curso_ids": [],
            "program_modules": {},
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.users.insert_many(default_users)
    
    return {
        "message": "Usuarios reiniciados exitosamente",
        "deleted_count": deleted_count.deleted_count,
        "created_count": len(default_users),
        "users": [
            {"role": "admin", "login": "admin@educando.com", "password": "Admin2026"},
            {"role": "admin", "login": "admin2@educando.com", "password": "Admin2026"},
            {"role": "editor", "login": "editor@educando.com (usar login de profesor)", "password": "Editor2026"},
            {"role": "profesor", "login": "profesor@educando.com", "password": "Profe2026"},
            {"role": "profesor", "login": "profesor2@educando.com", "password": "Profe2026"},
            {"role": "estudiante", "login": "1001 (cédula)", "password": "1001"},
            {"role": "estudiante", "login": "1002 (cédula)", "password": "1002"}
        ]
    }

# --- Seed Data Route ---
@router.post("/seed")
async def seed_data():
    # Block in production
    if os.environ.get('RENDER') or os.environ.get('RAILWAY_ENVIRONMENT'):
        raise HTTPException(status_code=403, detail="Este endpoint está deshabilitado en producción")
    # Check if already seeded
    existing_admin = await db.users.find_one({"email": "admin@educando.com"})
    if existing_admin:
        return {"message": "Base de datos ya tiene datos iniciales"}
    
    # Check for protected production users that must never be re-created
    protected_emails = ["laura.torres@educando.com", "diana.silva@educando.com"]
    protected_cedulas = ["1001234567"]
    for email in protected_emails:
        if await db.users.find_one({"email": email}):
            return {"message": "Datos de producción ya existen. No se recrearán usuarios existentes."}
    for cedula in protected_cedulas:
        if await db.users.find_one({"cedula": cedula}):
            return {"message": "Datos de producción ya existen. No se recrearán usuarios existentes."}
    
    # Create Programs
    programs = [
        {
            "id": "prog-admin",
            "name": "Técnico en Asistencia Administrativa",
            "description": "Formación técnica en gestión administrativa, contabilidad, ofimática y gestión documental.",
            "duration": "12 meses (2 módulos de 6 meses)",
            "modules": [
                {"number": 1, "name": "MÓDULO 1", "subjects": [
                    "Fundamentos de Administración",
                    "Herramientas Ofimáticas",
                    "Gestión Documental y Archivo",
                    "Atención al Cliente y Comunicación Organizacional",
                    "Legislación Laboral y Ética Profesional"
                ]},
                {"number": 2, "name": "MÓDULO 2", "subjects": [
                    "Contabilidad Básica",
                    "Nómina y Seguridad Social Aplicada",
                    "Control de Inventarios y Logística",
                    "Inglés Técnico / Competencias Ciudadanas",
                    "Proyecto Integrador Virtual"
                ]}
            ],
            "module1_close_date": None,
            "module2_close_date": None,
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "prog-infancia",
            "name": "Técnico Laboral en Atención a la Primera Infancia",
            "description": "Formación para el cuidado y educación de niños en primera infancia.",
            "duration": "12 meses (2 módulos de 6 meses)",
            "modules": [
                {"number": 1, "name": "MÓDULO 1", "subjects": [
                    "Inglés I",
                    "Proyecto de vida",
                    "Construcción social de la infancia",
                    "Perspectiva del desarrollo infantil",
                    "Salud y nutrición",
                    "Lenguaje y educación infantil",
                    "Juego y otras formas de comunicación",
                    "Educación y pedagogía"
                ]},
                {"number": 2, "name": "MÓDULO 2", "subjects": [
                    "Inglés II",
                    "Construcción del mundo Matemático",
                    "Dificultades en el aprendizaje",
                    "Estrategias del aula",
                    "Trabajo de grado",
                    "Investigación",
                    "Práctica - Informe"
                ]}
            ],
            "module1_close_date": None,
            "module2_close_date": None,
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "prog-sst",
            "name": "Técnico en Seguridad y Salud en el Trabajo",
            "description": "Formación en prevención de riesgos laborales, medicina preventiva y gestión ambiental.",
            "duration": "12 meses (2 módulos)",
            "modules": [
                {"number": 1, "name": "MÓDULO 1", "subjects": [
                    "Fundamentos en Seguridad y Salud en el Trabajo",
                    "Administración en salud",
                    "Condiciones de seguridad",
                    "Matemáticas",
                    "Psicología del Trabajo"
                ]},
                {"number": 2, "name": "MÓDULO 2", "subjects": [
                    "Comunicación oral y escrita",
                    "Sistema de gestión de seguridad y salud del trabajo",
                    "Anatomía y fisiología",
                    "Medicina preventiva del trabajo",
                    "Ética profesional",
                    "Gestión ambiental",
                    "Proyecto de grado"
                ]}
            ],
            "module1_close_date": None,
            "module2_close_date": None,
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.programs.insert_many(programs)
    
    # Create Subjects
    subjects = []
    for prog in programs:
        for module in prog["modules"]:
            for subj_name in module["subjects"]:
                subjects.append({
                    "id": str(uuid.uuid4()),
                    "name": subj_name,
                    "program_id": prog["id"],
                    "module_number": module["number"],
                    "description": "",
                    "active": True,
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
    await db.subjects.insert_many(subjects)
    
    # Create Users
    admin_id = "user-admin"
    editor_id = "user-editor-2"
    teacher1_id = "user-teacher1"
    teacher2_id = "user-teacher2"
    student1_id = "user-student1"
    student2_id = "user-student2"
    student3_id = "user-student3"
    
    users = [
        {
            "id": editor_id,
            "name": "Editor General",
            "email": "editorgeneral@educando.com",
            "cedula": None,
            "password_hash": hash_password("EditorSeguro2025"),
            "role": "editor",
            "program_id": None,
            "phone": "3002222222",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": admin_id,
            "name": "Administrador General",
            "email": "admin@educando.com",
            "cedula": None,
            "password_hash": hash_password("Admin2026*Seed"),
            "role": "admin",
            "program_id": None,
            "phone": "3001234567",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": teacher1_id,
            "name": "María García López",
            "email": "profesor@educando.com",
            "cedula": None,
            "password_hash": hash_password("Profe2026*Seed1"),
            "role": "profesor",
            "program_id": None,
            "phone": "3007654321",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": teacher2_id,
            "name": "Carlos Rodríguez Pérez",
            "email": "profesor2@educando.com",
            "cedula": None,
            "password_hash": hash_password("Profe2026*Seed2"),
            "role": "profesor",
            "program_id": None,
            "phone": "3009876543",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": student1_id,
            "name": "Juan Martínez Ruiz",
            "email": None,
            "cedula": "1234567890",
            "password_hash": hash_password("Estud2026*Seed1"),
            "role": "estudiante",
            "program_id": "prog-admin",
            "phone": "3101234567",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": student2_id,
            "name": "Ana Sofía Hernández",
            "email": None,
            "cedula": "0987654321",
            "password_hash": hash_password("Estud2026*Seed2"),
            "role": "estudiante",
            "program_id": "prog-infancia",
            "phone": "3207654321",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": student3_id,
            "name": "Pedro López Castro",
            "email": None,
            "cedula": "1122334455",
            "password_hash": hash_password("Estud2026*Seed3"),
            "role": "estudiante",
            "program_id": "prog-sst",
            "phone": "3159876543",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    await db.users.insert_many(users)
    
    return {
        "message": "Datos iniciales creados exitosamente",
        "users_created": 7,
        "programs_created": 3
    }

# --- Stats Route ---
@router.delete("/admin/purge-group-data")
async def purge_all_group_data(user=Depends(get_current_user)):
    """Delete ALL courses/groups and every dependent record (activities, grades,
    submissions, videos, recovery_enabled, failed_subjects). Admin only."""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")

    courses_deleted = await db.courses.delete_many({})
    activities_deleted = await db.activities.delete_many({})
    grades_deleted = await db.grades.delete_many({})
    submissions_deleted = await db.submissions.delete_many({})
    videos_deleted = await db.class_videos.delete_many({})
    recovery_deleted = await db.recovery_enabled.delete_many({})
    failed_deleted = await db.failed_subjects.delete_many({})

    await log_audit(
        "purge_group_data",
        user["id"],
        user["role"],
        {
            "courses_deleted": courses_deleted.deleted_count,
            "activities_deleted": activities_deleted.deleted_count,
            "grades_deleted": grades_deleted.deleted_count,
            "submissions_deleted": submissions_deleted.deleted_count,
            "videos_deleted": videos_deleted.deleted_count,
            "recovery_deleted": recovery_deleted.deleted_count,
            "failed_subjects_deleted": failed_deleted.deleted_count,
        }
    )

    logger.info(
        f"Admin {user['id']} purged all group data: "
        f"{courses_deleted.deleted_count} courses, "
        f"{activities_deleted.deleted_count} activities, "
        f"{grades_deleted.deleted_count} grades, "
        f"{submissions_deleted.deleted_count} submissions, "
        f"{videos_deleted.deleted_count} videos"
    )

    return {
        "message": "Todos los grupos y sus datos dependientes fueron eliminados",
        "courses_deleted": courses_deleted.deleted_count,
        "activities_deleted": activities_deleted.deleted_count,
        "grades_deleted": grades_deleted.deleted_count,
        "submissions_deleted": submissions_deleted.deleted_count,
        "videos_deleted": videos_deleted.deleted_count,
        "recovery_enabled_deleted": recovery_deleted.deleted_count,
        "failed_subjects_deleted": failed_deleted.deleted_count,
    }
