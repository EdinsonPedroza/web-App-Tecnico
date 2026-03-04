import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends

from database import db
from utils.security import get_current_user, safe_object_id
from utils.audit import log_audit
from utils.helpers import (
    derive_estado_from_program_statuses,
    validate_module_dates_order,
    validate_module_dates_recovery_close,
    get_open_enrollment_module,
    get_current_module_from_dates,
    can_enroll_in_module,
)
from models.schemas import CourseCreate, CourseUpdate
from config import (
    MAX_LIMIT, USE_CLOUDINARY, USE_S3, UPLOAD_DIR,
    _ERR_ENROLL_EGRESADO, _ERR_ENROLL_PENDIENTE
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/courses")
async def get_courses(teacher_id: Optional[str] = None, student_id: Optional[str] = None, skip: int = 0, limit: int = 100, fields: Optional[str] = None, user=Depends(get_current_user)):
    conditions = []

    if teacher_id:
        safe_teacher_id = safe_object_id(teacher_id, "teacher_id")
        teacher = await db.users.find_one({"id": safe_teacher_id}, {"_id": 0})
        if teacher and teacher.get("subject_ids"):
            conditions.append({
                "$or": [
                    {"teacher_id": safe_teacher_id},
                    {"subject_ids": {"$in": teacher["subject_ids"]}},
                    {"subject_id": {"$in": teacher["subject_ids"]}}
                ]
            })
        else:
            conditions.append({"teacher_id": safe_teacher_id})

    if student_id:
        conditions.append({"student_ids": safe_object_id(student_id, "student_id")})

    if len(conditions) == 0:
        query = {}
    elif len(conditions) == 1:
        query = conditions[0]
    else:
        query = {"$and": conditions}

    projection = {"_id": 0}
    if fields == "summary":
        projection["student_ids"] = 0
        projection["removed_student_ids"] = 0

    limit = max(1, min(limit, MAX_LIMIT))
    skip = max(0, skip)
    courses = await db.courses.find(query, projection).skip(skip).limit(limit).to_list(limit)
    return courses


@router.get("/courses/{course_id}")
async def get_course(course_id: str, user=Depends(get_current_user)):
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return course


@router.get("/courses/{course_id}/students")
async def get_course_students(course_id: str, include_removed: bool = False, user=Depends(get_current_user)):
    """Return students enrolled in a specific course."""
    if user["role"] not in ["admin", "profesor"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    student_ids = course.get("student_ids") or []
    removed_ids = course.get("removed_student_ids") or []

    all_ids_to_fetch = list(set(student_ids + (removed_ids if include_removed else [])))
    if not all_ids_to_fetch:
        return []
    students = await db.users.find(
        {"id": {"$in": all_ids_to_fetch}, "role": "estudiante"},
        {"_id": 0, "password_hash": 0}
    ).to_list(5000)

    if include_removed:
        removed_set = set(removed_ids) - set(student_ids)
        for s in students:
            if s["id"] in removed_set:
                s["_removed_from_group"] = True
    return students


@router.post("/courses")
async def create_course(req: CourseCreate, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")

    existing_group = await db.courses.find_one({"name": req.name, "program_id": req.program_id}, {"_id": 0, "id": 1})
    if existing_group:
        raise HTTPException(status_code=400, detail="Ya existe un grupo con ese nombre para este programa")

    module_dates = req.module_dates or {}
    date_order_error = validate_module_dates_order(module_dates)
    if date_order_error:
        raise HTTPException(status_code=400, detail=date_order_error)

    recovery_close_error = validate_module_dates_recovery_close(module_dates)
    if recovery_close_error:
        raise HTTPException(status_code=400, detail=recovery_close_error)

    student_ids_to_add = req.student_ids or []
    if student_ids_to_add:
        course_current_module = get_open_enrollment_module(module_dates) or get_current_module_from_dates(module_dates) or 1
        if not can_enroll_in_module(module_dates, course_current_module):
            if req.program_id:
                students_info = await db.users.find(
                    {"id": {"$in": student_ids_to_add}, "role": "estudiante"},
                    {"_id": 0, "id": 1, "program_statuses": 1, "program_modules": 1}
                ).to_list(5000)
                student_map = {s["id"]: s for s in students_info}
                for sid in student_ids_to_add:
                    s = student_map.get(sid)
                    if not s:
                        raise HTTPException(status_code=400, detail=f"Estudiante {sid} no encontrado")
                    prog_statuses = s.get("program_statuses") or {}
                    prog_modules = s.get("program_modules") or {}
                    status = prog_statuses.get(req.program_id)
                    student_module = prog_modules.get(req.program_id)
                    if status == "retirado" and student_module is not None and student_module == course_current_module:
                        continue
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"No se puede matricular estudiantes: el período de matrícula para el "
                            f"Módulo {course_current_module} ha cerrado. Solo se permite reingreso de "
                            "estudiantes retirados en el módulo actual del grupo."
                        )
                    )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"No se puede matricular estudiantes: el período de matrícula para el Módulo {course_current_module} ha cerrado"
                )

        if req.program_id:
            students_mod_info = await db.users.find(
                {"id": {"$in": student_ids_to_add}, "role": "estudiante"},
                {"_id": 0, "id": 1, "program_modules": 1, "module": 1, "program_statuses": 1}
            ).to_list(5000)
            student_mod_map = {s["id"]: s for s in students_mod_info}
            for sid in student_ids_to_add:
                s = student_mod_map.get(sid) or {}
                prog_modules = s.get("program_modules") or {}
                student_mod = prog_modules.get(req.program_id)
                if student_mod is None:
                    student_mod = s.get("module")
                if student_mod is not None and student_mod != course_current_module:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"El estudiante está en el Módulo {student_mod} del programa, pero el grupo "
                            f"corresponde al Módulo {course_current_module}. Solo puede inscribirse en "
                            "grupos del módulo en que se encuentra."
                        )
                    )
                prog_statuses = s.get("program_statuses") or {}
                student_prog_status = prog_statuses.get(req.program_id)
                if student_prog_status == "egresado":
                    raise HTTPException(status_code=400, detail=_ERR_ENROLL_EGRESADO)
                if student_prog_status == "pendiente_recuperacion":
                    raise HTTPException(status_code=400, detail=_ERR_ENROLL_PENDIENTE)

    if student_ids_to_add and req.program_id:
        conflicting_groups = await db.courses.find(
            {"program_id": req.program_id, "student_ids": {"$in": student_ids_to_add}},
            {"_id": 0, "name": 1, "student_ids": 1}
        ).to_list(1000)
        if conflicting_groups:
            conflict_names = [g["name"] for g in conflicting_groups]
            raise HTTPException(
                status_code=400,
                detail=f"Uno o más estudiantes ya están inscritos en otro grupo del mismo programa: {', '.join(conflict_names)}"
            )

    subject_ids = []
    if req.subject_ids:
        subject_ids = req.subject_ids
    elif req.subject_id:
        subject_ids = [req.subject_id]

    course = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "program_id": req.program_id,
        "subject_id": req.subject_id,
        "subject_ids": subject_ids if subject_ids else [],
        "teacher_id": req.teacher_id,
        "year": req.year,
        "student_ids": student_ids_to_add,
        "start_date": req.start_date,
        "end_date": req.end_date,
        "grupo": req.grupo,
        "module_dates": module_dates,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    logger.info(f"Creating course: id={course['id']}, name={course['name']}, subject_ids={course['subject_ids']}, student_ids={len(course['student_ids'])} students")

    await db.courses.insert_one(course)
    del course["_id"]

    if course["student_ids"]:
        program_id = course["program_id"]
        module_number = get_open_enrollment_module(course["module_dates"]) or get_current_module_from_dates(course["module_dates"])
        if module_number is None and course["subject_ids"]:
            subject_docs = await db.subjects.find(
                {"id": {"$in": course["subject_ids"]}}, {"_id": 0, "module_number": 1}
            ).to_list(500)
            valid_modules = [s["module_number"] for s in subject_docs if s.get("module_number")]
            if valid_modules:
                module_number = min(valid_modules)
        if module_number is not None:
            await db.users.update_many(
                {
                    "id": {"$in": course["student_ids"]},
                    "role": "estudiante",
                    "$or": [
                        {f"program_modules.{program_id}": {"$exists": False}},
                        {f"program_modules.{program_id}": None},
                        {f"program_modules.{program_id}": {"$lte": module_number}},
                    ],
                },
                {"$set": {
                    "module": module_number,
                    f"program_modules.{program_id}": module_number
                }}
            )
        if program_id:
            enrolled_docs = await db.users.find(
                {"id": {"$in": course["student_ids"]}, "role": "estudiante"},
                {"_id": 0, "id": 1, "program_statuses": 1}
            ).to_list(5000)
            for s in enrolled_docs:
                ps = s.get("program_statuses") or {}
                if ps.get(program_id) == "reprobado":
                    ps[program_id] = "activo"
                    new_estado = derive_estado_from_program_statuses(ps)
                    await db.users.update_one(
                        {"id": s["id"]},
                        {"$set": {"program_statuses": ps, "estado": new_estado}}
                    )

    await log_audit("course_created", user["id"], user["role"], {"course_id": course["id"], "course_name": course.get("name", "")})
    return course


@router.put("/courses/{course_id}")
async def update_course(course_id: str, req: CourseUpdate, user=Depends(get_current_user)):
    if user["role"] not in ["admin", "profesor"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    module_dates_updated = "module_dates" in update_data

    if "module_dates" in update_data and update_data["module_dates"]:
        date_order_error = validate_module_dates_order(update_data["module_dates"])
        if date_order_error:
            raise HTTPException(status_code=400, detail=date_order_error)
        recovery_close_error = validate_module_dates_recovery_close(update_data["module_dates"])
        if recovery_close_error:
            raise HTTPException(status_code=400, detail=recovery_close_error)

    if "subject_ids" in update_data and update_data["subject_ids"]:
        if "subject_id" not in update_data:
            update_data["subject_id"] = update_data["subject_ids"][0]
    elif "subject_id" in update_data and update_data["subject_id"]:
        if "subject_ids" not in update_data:
            update_data["subject_ids"] = [update_data["subject_id"]]

    newly_added_ids = []
    pre_update_student_ids: set = set()
    if req.student_ids is not None and user["role"] == "admin":
        current_course = await db.courses.find_one({"id": course_id}, {"_id": 0, "program_id": 1, "student_ids": 1, "module_dates": 1, "removed_student_ids": 1})
        if current_course:
            current_student_ids = set(current_course.get("student_ids") or [])
            pre_update_student_ids = current_student_ids
            newly_added_ids = list(set(req.student_ids) - current_student_ids)
            course_module_dates = (req.module_dates if req.module_dates is not None else current_course.get("module_dates")) or {}
            course_current_module = get_open_enrollment_module(course_module_dates) or get_current_module_from_dates(course_module_dates) or 1
            if newly_added_ids and not can_enroll_in_module(course_module_dates, course_current_module):
                prog_id = current_course.get("program_id")
                if prog_id:
                    students_info = await db.users.find(
                        {"id": {"$in": newly_added_ids}, "role": "estudiante"},
                        {"_id": 0, "id": 1, "program_statuses": 1, "program_modules": 1}
                    ).to_list(5000)
                    student_map = {s["id"]: s for s in students_info}
                    for sid in newly_added_ids:
                        s = student_map.get(sid)
                        if not s:
                            raise HTTPException(status_code=400, detail=f"Estudiante {sid} no encontrado")
                        prog_statuses = s.get("program_statuses") or {}
                        prog_modules = s.get("program_modules") or {}
                        status = prog_statuses.get(prog_id)
                        student_module = prog_modules.get(prog_id)
                        if status == "retirado" and student_module is not None and student_module == course_current_module:
                            continue
                        raise HTTPException(
                            status_code=400,
                            detail=(
                                f"No se puede matricular estudiantes: el período de matrícula para el "
                                f"Módulo {course_current_module} ha cerrado. Solo se permite reingreso de "
                                "estudiantes retirados en el módulo actual del grupo."
                            )
                        )
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No se puede matricular estudiantes: el período de matrícula para el Módulo {course_current_module} ha cerrado"
                    )

            program_id = current_course.get("program_id")
            if program_id and req.student_ids:
                conflicting_groups = await db.courses.find(
                    {"program_id": program_id, "id": {"$ne": course_id}, "student_ids": {"$in": req.student_ids}},
                    {"_id": 0, "name": 1, "student_ids": 1}
                ).to_list(1000)
                if conflicting_groups:
                    conflict_names = [g["name"] for g in conflicting_groups]
                    raise HTTPException(
                        status_code=400,
                        detail=f"Uno o más estudiantes ya están inscritos en otro grupo del mismo programa: {', '.join(conflict_names)}"
                    )

            removed_ids = set(current_course.get("removed_student_ids") or [])
            if removed_ids and newly_added_ids:
                blocked = [sid for sid in newly_added_ids if sid in removed_ids]
                if blocked:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"No se puede re-matricular a {len(blocked)} estudiante(s) que fueron retirados "
                            "de este grupo por no pasar la recuperación. Deben inscribirse en un nuevo grupo."
                        )
                    )

            if program_id and newly_added_ids:
                students_mod_info = await db.users.find(
                    {"id": {"$in": newly_added_ids}, "role": "estudiante"},
                    {"_id": 0, "id": 1, "program_modules": 1, "module": 1, "program_statuses": 1}
                ).to_list(5000)
                for s in students_mod_info:
                    prog_modules = s.get("program_modules") or {}
                    student_mod = prog_modules.get(program_id)
                    if student_mod is None:
                        student_mod = s.get("module")
                    if student_mod is not None and student_mod != course_current_module:
                        raise HTTPException(
                            status_code=400,
                            detail=(
                                f"El estudiante está en el Módulo {student_mod} del programa, pero el grupo "
                                f"corresponde al Módulo {course_current_module}. Solo puede inscribirse en "
                                "grupos del módulo en que se encuentra."
                            )
                        )
                    prog_statuses = s.get("program_statuses") or {}
                    student_prog_status = prog_statuses.get(program_id)
                    if student_prog_status == "egresado":
                        raise HTTPException(status_code=400, detail=_ERR_ENROLL_EGRESADO)
                    if student_prog_status == "pendiente_recuperacion":
                        raise HTTPException(status_code=400, detail=_ERR_ENROLL_PENDIENTE)

    result = await db.courses.update_one({"id": course_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    updated = await db.courses.find_one({"id": course_id}, {"_id": 0})

    if updated and req.student_ids is not None:
        program_id = updated.get("program_id", "")
        student_ids = updated.get("student_ids") or []
        if student_ids:
            module_number = get_open_enrollment_module(updated.get("module_dates") or {}) or get_current_module_from_dates(updated.get("module_dates") or {})
            if module_number is None:
                subject_ids_for_module = updated.get("subject_ids") or []
                if subject_ids_for_module:
                    subject_docs = await db.subjects.find(
                        {"id": {"$in": subject_ids_for_module}}, {"_id": 0, "module_number": 1}
                    ).to_list(500)
                    valid_modules = [s["module_number"] for s in subject_docs if s.get("module_number")]
                    if valid_modules:
                        module_number = min(valid_modules)
            if module_number is not None:
                await db.users.update_many(
                    {
                        "id": {"$in": student_ids},
                        "role": "estudiante",
                        "$or": [
                            {f"program_modules.{program_id}": {"$exists": False}},
                            {f"program_modules.{program_id}": None},
                            {f"program_modules.{program_id}": {"$lte": module_number}},
                        ],
                    },
                    {"$set": {
                        "module": module_number,
                        f"program_modules.{program_id}": module_number
                    }}
                )

    if req.student_ids is not None and pre_update_student_ids:
        program_id_for_removed = updated.get("program_id", "") if updated else ""
        manually_removed = pre_update_student_ids - set(req.student_ids)
        if manually_removed:
            await db.courses.update_one(
                {"id": course_id},
                {"$addToSet": {"removed_student_ids": {"$each": list(manually_removed)}}}
            )

    if newly_added_ids:
        program_id_for_new = updated.get("program_id", "") if updated else ""
        if program_id_for_new:
            added_student_docs = await db.users.find(
                {"id": {"$in": newly_added_ids}, "role": "estudiante"},
                {"_id": 0, "id": 1, "program_statuses": 1}
            ).to_list(5000)
            for s in added_student_docs:
                ps = s.get("program_statuses") or {}
                if ps.get(program_id_for_new) == "reprobado":
                    ps[program_id_for_new] = "activo"
                    new_estado = derive_estado_from_program_statuses(ps)
                    await db.users.update_one(
                        {"id": s["id"]},
                        {"$set": {"program_statuses": ps, "estado": new_estado}}
                    )

    if module_dates_updated:
        from routes.admin import check_and_close_modules
        await check_and_close_modules()

    return updated


@router.delete("/courses/{course_id}")
async def delete_course(course_id: str, force: bool = False, delete_students: bool = False, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")

    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")

    program_id = course.get("program_id", "")
    student_ids_in_course = course.get("student_ids", [])

    if student_ids_in_course:
        students = await db.users.find(
            {"id": {"$in": student_ids_in_course}, "role": "estudiante"},
            {"_id": 0, "id": 1, "program_statuses": 1, "estado": 1}
        ).to_list(5000)
        blocking_students = []
        for s in students:
            program_statuses = s.get("program_statuses") or {}
            status = program_statuses.get(program_id) if program_id else s.get("estado")
            if not status:
                status = s.get("estado", "activo")
            if status != "egresado":
                blocking_students.append(s["id"])
        if blocking_students and not force and not delete_students:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"No se puede eliminar el grupo: contiene {len(blocking_students)} estudiante(s) "
                    "que aún no han egresado. Use force=true para desmatricularlos y eliminar el grupo, "
                    "o delete_students=true para eliminar también las cuentas de estudiantes."
                )
            )
        if delete_students:
            all_student_ids = student_ids_in_course
            if all_student_ids:
                await db.grades.delete_many({"student_id": {"$in": all_student_ids}})
                await db.submissions.delete_many({"student_id": {"$in": all_student_ids}})
                await db.failed_subjects.delete_many({"student_id": {"$in": all_student_ids}})
                await db.recovery_enabled.delete_many({"student_id": {"$in": all_student_ids}})
                deleted_students_result = await db.users.delete_many(
                    {"id": {"$in": all_student_ids}, "role": "estudiante"}
                )
                await db.courses.update_many(
                    {"student_ids": {"$in": all_student_ids}},
                    {"$pullAll": {"student_ids": all_student_ids}}
                )
                logger.info(
                    f"Deleted {deleted_students_result.deleted_count} student account(s) "
                    f"along with course {course_id}"
                )
                await log_audit(
                    "students_deleted_with_course", user["id"], user["role"],
                    {"course_id": course_id, "student_count": deleted_students_result.deleted_count}
                )
        elif blocking_students:
            await db.users.update_many(
                {"id": {"$in": blocking_students}},
                {"$unset": {"grupo": ""}}
            )
            logger.info(
                f"Force-deleted course {course_id}: unenrolled {len(blocking_students)} active student(s)"
            )

    activities_for_files = await db.activities.find(
        {"course_id": course_id}, {"_id": 0, "id": 1, "files": 1}
    ).to_list(10000)
    activity_ids = [a["id"] for a in activities_for_files if a.get("id")]
    if activity_ids:
        submissions_for_files = await db.submissions.find(
            {"activity_id": {"$in": activity_ids}}, {"_id": 0, "files": 1}
        ).to_list(50000)
    else:
        submissions_for_files = []

    await db.courses.delete_one({"id": course_id})

    activities_deleted = await db.activities.delete_many({"course_id": course_id})
    grades_deleted = await db.grades.delete_many({"course_id": course_id})
    if activity_ids:
        submissions_deleted = await db.submissions.delete_many({"activity_id": {"$in": activity_ids}})
    else:
        submissions_deleted = type("_DeleteResult", (), {"deleted_count": 0})()
    failed_subjects_deleted = await db.failed_subjects.delete_many({"course_id": course_id})
    recovery_enabled_deleted = await db.recovery_enabled.delete_many({"course_id": course_id})
    videos_deleted = await db.class_videos.delete_many({"course_id": course_id})

    cloudinary_deleted_count = 0
    for doc in activities_for_files + submissions_for_files:
        for f in (doc.get("files") or []):
            stored_name = f.get("stored_name") if isinstance(f, dict) else None
            if not stored_name:
                continue
            storage = f.get("storage") if isinstance(f, dict) else None
            is_cloudinary_file = (
                USE_CLOUDINARY and (
                    storage == "cloudinary" or
                    (isinstance(stored_name, str) and stored_name.startswith("educando/"))
                )
            )
            if is_cloudinary_file:
                try:
                    import cloudinary.uploader
                    _rt = f.get("resource_type") if isinstance(f, dict) else None
                    if not _rt:
                        _fext = Path(stored_name).suffix.lower().lstrip(".")
                        if _fext in {"jpg", "jpeg", "png", "gif", "webp", "bmp", "svg"}:
                            _rt = "image"
                        elif _fext in {"mp4", "avi", "mov", "mkv", "webm"}:
                            _rt = "video"
                        else:
                            _rt = "raw"
                    cloudinary.uploader.destroy(stored_name, resource_type=_rt)
                    cloudinary_deleted_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete Cloudinary file {stored_name}: {e}")
            else:
                file_path = UPLOAD_DIR / stored_name
                if file_path.exists():
                    try:
                        file_path.unlink()
                    except Exception as e:
                        logger.warning(f"Failed to delete file {stored_name}: {e}")

    logger.info(
        f"Course {course_id} deleted: "
        f"{activities_deleted.deleted_count} activities, {grades_deleted.deleted_count} grades, "
        f"{submissions_deleted.deleted_count} submissions"
    )
    await log_audit("course_deleted", user["id"], user["role"], {"course_id": course_id, "course_name": course.get("name", "")})

    return {
        "message": "Grupo eliminado con todos sus datos asociados",
        "deleted": {
            "activities": activities_deleted.deleted_count,
            "grades": grades_deleted.deleted_count,
            "submissions": submissions_deleted.deleted_count,
            "failed_subjects": failed_subjects_deleted.deleted_count,
            "recovery_enabled": recovery_enabled_deleted.deleted_count,
            "videos": videos_deleted.deleted_count
        }
    }
