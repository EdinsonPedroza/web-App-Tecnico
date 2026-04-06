import re
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends

from database import db
from utils.security import get_current_user, hash_password
from utils.audit import log_audit, log_security_event
from utils.helpers import derive_estado_from_program_statuses
from models.schemas import UserCreate, UserUpdate, AdminCreateByEditor, AdminUpdateByEditor

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/users")
async def get_users(
    role: Optional[str] = None,
    estado: Optional[str] = None,
    search: Optional[str] = None,
    program_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    user=Depends(get_current_user)
):
    if user["role"] not in ["admin", "profesor"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    if page < 1:
        page = 1
    if page_size < 1 or page_size > 200:
        page_size = 50

    query = {}
    if role:
        query["role"] = role
    if estado:
        if estado == 'activo':
            query["$or"] = [{"estado": "activo"}, {"estado": None}, {"estado": {"$exists": False}}]
        else:
            query["estado"] = estado

    if program_id:
        program_filter = {"$or": [{"program_id": program_id}, {"program_ids": program_id}]}
        if "$or" in query:
            estado_or = query.pop("$or")
            query["$and"] = [{"$or": estado_or}, program_filter]
        else:
            query["$or"] = [{"program_id": program_id}, {"program_ids": program_id}]

    if search and search.strip():
        # Escape regex metacharacters to prevent ReDoS (CWE-943).
        search_regex = {"$regex": re.escape(search.strip()), "$options": "i"}
        search_cond = {"$or": [{"name": search_regex}, {"cedula": search_regex}]}
        if "$and" in query:
            query["$and"].append(search_cond)
        elif "$or" in query:
            existing_or = query.pop("$or")
            query["$and"] = [{"$or": existing_or}, search_cond]
        else:
            query.update(search_cond)

    total = await db.users.count_documents(query)
    skip = (page - 1) * page_size
    users = await db.users.find(query, {"_id": 0, "password_hash": 0}).sort("name", 1).skip(skip).limit(page_size).to_list(page_size)

    if role == "estudiante" and users:
        user_ids = [u["id"] for u in users]
        enrolled_courses = await db.courses.find(
            {"student_ids": {"$in": user_ids}},
            {"_id": 0, "id": 1, "name": 1, "student_ids": 1, "program_id": 1}
        ).to_list(1000)
        for u in users:
            u["course_ids"] = [c["id"] for c in enrolled_courses if u["id"] in (c.get("student_ids") or [])]
            u["enrolled_courses"] = [{"id": c["id"], "name": c["name"], "program_id": c.get("program_id")} for c in enrolled_courses if u["id"] in (c.get("student_ids") or [])]

    return {
        "users": users,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size)
    }


@router.post("/users")
async def create_user(req: UserCreate, user=Depends(get_current_user)):
    if user["role"] != "admin":
        log_security_event("UNAUTHORIZED_USER_CREATE_ATTEMPT", {
            "attempted_by": user["id"],
            "attempted_role": user["role"]
        })
        raise HTTPException(status_code=403, detail="Solo admin puede crear usuarios")

    if req.role in ["admin", "profesor"] and req.email:
        existing = await db.users.find_one({"email": req.email})
        if existing:
            log_security_event("DUPLICATE_EMAIL_ATTEMPT", {
                "email": req.email,
                "attempted_by": user["id"]
            })
            raise HTTPException(status_code=400, detail="Email ya existe")

    if req.role == "estudiante" and req.cedula:
        existing = await db.users.find_one({"cedula": req.cedula})
        if existing:
            log_security_event("DUPLICATE_CEDULA_ATTEMPT", {
                "cedula": req.cedula,
                "attempted_by": user["id"]
            })
            raise HTTPException(status_code=400, detail="Cédula ya existe")

    program_ids = []
    if req.program_ids:
        program_ids = req.program_ids
    elif req.program_id:
        program_ids = [req.program_id]

    if req.role == "estudiante" and not program_ids:
        raise HTTPException(status_code=400, detail="El estudiante debe estar inscrito en al menos un programa técnico")

    subject_ids = req.subject_ids if req.subject_ids else []

    if req.role == "profesor" and subject_ids:
        for subject_id in subject_ids:
            conflict = await db.users.find_one(
                {"role": "profesor", "subject_ids": subject_id},
                {"_id": 0, "id": 1, "name": 1}
            )
            if conflict:
                raise HTTPException(
                    status_code=400,
                    detail=f"La materia ya está asignada al profesor '{conflict['name']}'. Desasígnela primero antes de asignarla a otro profesor."
                )

    estado = req.estado if req.estado else ("activo" if req.role == "estudiante" else None)

    if req.program_modules:
        program_modules = req.program_modules
    elif req.module and program_ids:
        program_modules = {prog_id: req.module for prog_id in program_ids}
    else:
        program_modules = None

    if req.role == "estudiante":
        if req.program_statuses:
            program_statuses = req.program_statuses
        elif program_ids:
            program_statuses = {prog_id: "activo" for prog_id in program_ids}
        else:
            program_statuses = None
        if program_statuses and not req.estado:
            estado = derive_estado_from_program_statuses(program_statuses)
    else:
        program_statuses = None

    new_user = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "cedula": req.cedula,
        "password_hash": hash_password(req.password),
        "role": req.role,
        "program_id": req.program_id,
        "program_ids": program_ids,
        "subject_ids": subject_ids,
        "phone": req.phone,
        "module": req.module,
        "program_modules": program_modules,
        "program_statuses": program_statuses,
        "estado": estado,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    if req.email is not None:
        new_user["email"] = req.email
    try:
        await db.users.insert_one(new_user)
    except Exception as exc:
        logger.error(f"Error inserting user into database: {exc}")
        raise HTTPException(status_code=500, detail="No se pudo crear el usuario. Inténtelo de nuevo.")

    logger.info(f"User created: id={new_user['id']}, role={req.role}, by={user['id']}")
    await log_audit("student_created" if req.role == "estudiante" else "user_created", user["id"], user["role"], {"new_user_id": new_user["id"], "new_user_role": req.role, "new_user_name": req.name})

    del new_user["_id"]
    del new_user["password_hash"]
    return new_user


@router.put("/users/{user_id}")
async def update_user(user_id: str, req: UserUpdate, user=Depends(get_current_user)):
    if user["role"] != "admin":
        log_security_event("UNAUTHORIZED_USER_UPDATE_ATTEMPT", {
            "attempted_by": user["id"],
            "target_user": user_id
        })
        raise HTTPException(status_code=403, detail="Solo admin puede editar usuarios")

    update_data = {k: v for k, v in req.model_dump().items() if v is not None}

    FORBIDDEN_UPDATE_FIELDS = {"id", "role", "password_hash", "created_at"}
    update_data = {k: v for k, v in update_data.items() if k not in FORBIDDEN_UPDATE_FIELDS}

    if "password" in update_data:
        password = update_data.pop("password")
        if password is not None and password.strip():
            update_data["password_hash"] = hash_password(password)
            logger.info(f"Password updated for user: {user_id} by admin: {user['id']}")

    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")

    if "cedula" in update_data and update_data["cedula"]:
        existing = await db.users.find_one({"cedula": update_data["cedula"], "id": {"$ne": user_id}})
        if existing:
            log_security_event("DUPLICATE_CEDULA_UPDATE_ATTEMPT", {
                "cedula": update_data["cedula"],
                "attempted_by": user["id"],
                "target_user": user_id
            })
            raise HTTPException(status_code=400, detail="Esta cédula ya está registrada")

    if "email" in update_data and update_data["email"]:
        existing = await db.users.find_one({"email": update_data["email"], "id": {"$ne": user_id}})
        if existing:
            log_security_event("DUPLICATE_EMAIL_UPDATE_ATTEMPT", {
                "email": update_data["email"],
                "attempted_by": user["id"],
                "target_user": user_id
            })
            raise HTTPException(status_code=400, detail="Este correo ya está registrado")

    if "subject_ids" in update_data and update_data["subject_ids"]:
        target_user = await db.users.find_one({"id": user_id}, {"_id": 0, "role": 1})
        if target_user and target_user.get("role") == "profesor":
            for subject_id in update_data["subject_ids"]:
                conflict = await db.users.find_one(
                    {"role": "profesor", "subject_ids": subject_id, "id": {"$ne": user_id}},
                    {"_id": 0, "id": 1, "name": 1}
                )
                if conflict:
                    raise HTTPException(
                        status_code=400,
                        detail=f"La materia ya está asignada al profesor '{conflict['name']}'. Desasígnela primero antes de asignarla a otro profesor."
                    )

    if "program_ids" in update_data and update_data["program_ids"] is not None:
        current_student = await db.users.find_one({"id": user_id, "role": "estudiante"}, {"_id": 0, "program_ids": 1, "program_id": 1, "program_statuses": 1, "program_modules": 1})
        if current_student:
            current_program_ids = current_student.get("program_ids") or (
                [current_student["program_id"]] if current_student.get("program_id") else []
            )
            new_program_ids = update_data["program_ids"]
            added_programs = [p for p in new_program_ids if p not in current_program_ids]
            if added_programs:
                stored_statuses = current_student.get("program_statuses") or {}
                stored_modules = current_student.get("program_modules") or {}
                sent_statuses = update_data.get("program_statuses") if update_data.get("program_statuses") is not None else {}
                sent_modules = update_data.get("program_modules") if update_data.get("program_modules") is not None else {}
                merged_statuses = {**stored_statuses, **sent_statuses}
                merged_modules = {**stored_modules, **sent_modules}
                for prog_id in added_programs:
                    if prog_id not in merged_statuses:
                        merged_statuses[prog_id] = "activo"
                    if prog_id not in merged_modules:
                        merged_modules[prog_id] = 1
                update_data["program_statuses"] = merged_statuses
                update_data["program_modules"] = merged_modules

    if update_data.get("program_statuses"):
        update_data["estado"] = derive_estado_from_program_statuses(update_data["program_statuses"])

    result = await db.users.update_one({"id": user_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if "subject_ids" in update_data:
        logger.info(f"User subject assignment updated: user_id={user_id}, subject_ids={update_data['subject_ids']}, by={user['id']}")

    logger.info(f"User updated: id={user_id}, by={user['id']}, fields={list(update_data.keys())}")

    updated = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    await log_audit("user_updated", user["id"], user["role"], {"target_user_id": user_id})
    return updated


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede eliminar usuarios")
    if user_id == user["id"]:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta")
    target = await db.users.find_one({"id": user_id}, {"_id": 0, "name": 1, "role": 1})
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    await db.courses.update_many(
        {"student_ids": user_id},
        {"$pull": {"student_ids": user_id}}
    )
    await db.grades.delete_many({"student_id": user_id})
    await db.submissions.delete_many({"student_id": user_id})
    await db.failed_subjects.delete_many({"student_id": user_id})
    await db.recovery_enabled.delete_many({"student_id": user_id})
    await log_audit("user_deleted", user["id"], user["role"], {"deleted_user_id": user_id, "deleted_user_name": (target or {}).get("name", ""), "deleted_user_role": (target or {}).get("role", "")})
    return {"message": "Usuario eliminado"}


# --- Editor Routes ---
@router.post("/editor/create-admin")
async def editor_create_admin(req: AdminCreateByEditor, user=Depends(get_current_user)):
    if user["role"] != "editor":
        raise HTTPException(status_code=403, detail="Solo editor puede crear administradores")

    if not req.email or not req.password or not req.name:
        raise HTTPException(status_code=400, detail="Email, password y nombre son requeridos")

    existing = await db.users.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email ya existe")

    new_admin = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "email": req.email,
        "cedula": None,
        "password_hash": hash_password(req.password),
        "role": "admin",
        "program_id": None,
        "program_ids": [],
        "subject_ids": [],
        "phone": None,
        "module": None,
        "grupo": None,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(new_admin)
    del new_admin["_id"]
    del new_admin["password_hash"]
    return new_admin


@router.get("/editor/admins")
async def editor_get_admins(user=Depends(get_current_user)):
    if user["role"] != "editor":
        raise HTTPException(status_code=403, detail="Solo editor puede ver administradores")
    admins = await db.users.find({"role": "admin"}, {"_id": 0, "password_hash": 0}).to_list(1000)
    return admins


@router.put("/editor/admins/{admin_id}")
async def editor_update_admin(admin_id: str, req: AdminUpdateByEditor, user=Depends(get_current_user)):
    if user["role"] != "editor":
        raise HTTPException(status_code=403, detail="Solo editor puede editar administradores")

    target_user = await db.users.find_one({"id": admin_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")

    if target_user["role"] != "admin":
        raise HTTPException(status_code=400, detail="El usuario no es un administrador")

    update_data = {k: v for k, v in req.model_dump().items() if v is not None}

    FORBIDDEN_UPDATE_FIELDS = {"id", "role", "password_hash", "created_at"}
    update_data = {k: v for k, v in update_data.items() if k not in FORBIDDEN_UPDATE_FIELDS}

    if "password" in update_data:
        password = update_data.pop("password")
        if password and password.strip():
            update_data["password_hash"] = hash_password(password)
            logger.info(f"Password updated for admin: {admin_id} by editor: {user['id']}")

    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")

    if "email" in update_data and update_data["email"]:
        existing = await db.users.find_one({"email": update_data["email"], "id": {"$ne": admin_id}})
        if existing:
            log_security_event("DUPLICATE_EMAIL_UPDATE_ATTEMPT", {
                "email": update_data["email"],
                "attempted_by": user["id"],
                "target_user": admin_id
            })
            raise HTTPException(status_code=400, detail="Este correo ya está registrado")

    await db.users.update_one({"id": admin_id}, {"$set": update_data})
    logger.info(f"Admin updated: id={admin_id}, by={user['id']}, fields={list(update_data.keys())}")
    updated_admin = await db.users.find_one({"id": admin_id}, {"_id": 0, "password_hash": 0})
    return updated_admin


@router.delete("/editor/admins/{admin_id}")
async def editor_delete_admin(admin_id: str, user=Depends(get_current_user)):
    if user["role"] != "editor":
        raise HTTPException(status_code=403, detail="Solo editor puede eliminar administradores")

    target_user = await db.users.find_one({"id": admin_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")

    if target_user["role"] != "admin":
        raise HTTPException(status_code=400, detail="El usuario no es un administrador")

    result = await db.users.delete_one({"id": admin_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")

    logger.info(f"Admin deleted: id={admin_id}, by editor={user['id']}")
    log_security_event("ADMIN_DELETED_BY_EDITOR", {
        "deleted_admin_id": admin_id,
        "deleted_admin_email": target_user.get("email"),
        "editor_id": user["id"]
    })

    return {"message": "Administrador eliminado exitosamente"}


@router.put("/users/{user_id}/promote")
async def promote_student(user_id: str, program_id: Optional[str] = None, user=Depends(get_current_user)):
    """Admin promotes a student to the next module."""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede promover estudiantes")

    student = await db.users.find_one({"id": user_id, "role": "estudiante"}, {"_id": 0})
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    program_modules = student.get("program_modules") or {}
    program_statuses = student.get("program_statuses") or {}
    current_module = student.get("module", 1)

    if program_id:
        all_prog_ids = student.get("program_ids") or ([student.get("program_id")] if student.get("program_id") else [])
        if program_id not in all_prog_ids:
            raise HTTPException(status_code=400, detail=f"El estudiante no pertenece al programa {program_id}")
        target_programs = [program_id]
    else:
        target_programs = student.get("program_ids") or ([student.get("program_id")] if student.get("program_id") else [])

    if not target_programs:
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"module": current_module + 1}}
        )
        updated = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
        return updated

    prog_docs = await db.programs.find(
        {"id": {"$in": target_programs}}, {"_id": 0, "id": 1, "modules": 1}
    ).to_list(100)
    prog_max_map = {p["id"]: max(len(p.get("modules") or []), 2) for p in prog_docs}

    set_fields: dict = {}
    for pid in target_programs:
        prog_current = program_modules.get(pid, current_module)
        prog_max = prog_max_map.get(pid, 2)
        if prog_current >= prog_max:
            raise HTTPException(
                status_code=400,
                detail=f"El estudiante ya está en el módulo final del programa {pid}"
            )
        next_mod = prog_current + 1
        program_modules[pid] = next_mod
        program_statuses[pid] = "activo"
        set_fields[f"program_modules.{pid}"] = next_mod

    new_estado = derive_estado_from_program_statuses(program_statuses)
    set_fields["program_statuses"] = program_statuses
    set_fields["estado"] = new_estado
    set_fields["module"] = program_modules.get(target_programs[0], current_module)

    await db.users.update_one({"id": user_id}, {"$set": set_fields})
    updated = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    return updated


@router.put("/users/{user_id}/graduate")
async def graduate_student(user_id: str, program_id: Optional[str] = None, user=Depends(get_current_user)):
    """Admin marks a student as graduated (egresado)."""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede graduar estudiantes")

    student = await db.users.find_one({"id": user_id, "role": "estudiante"}, {"_id": 0})
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    program_modules = student.get("program_modules") or {}
    program_statuses = student.get("program_statuses") or {}
    current_module = student.get("module", 1)

    if program_id:
        all_prog_ids = student.get("program_ids") or ([student.get("program_id")] if student.get("program_id") else [])
        if program_id not in all_prog_ids:
            raise HTTPException(status_code=400, detail=f"El estudiante no pertenece al programa {program_id}")
        target_programs = [program_id]
    else:
        target_programs = student.get("program_ids") or ([student.get("program_id")] if student.get("program_id") else [])

    if not target_programs:
        if current_module < 2:
            raise HTTPException(status_code=400, detail="El estudiante debe estar en el módulo final para graduarse")
        await db.users.update_one({"id": user_id}, {"$set": {"estado": "egresado"}})
        updated = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
        return updated

    prog_docs = await db.programs.find(
        {"id": {"$in": target_programs}}, {"_id": 0, "id": 1, "modules": 1}
    ).to_list(100)
    prog_max_map = {p["id"]: max(len(p.get("modules") or []), 2) for p in prog_docs}

    for pid in target_programs:
        prog_current = program_modules.get(pid, current_module)
        prog_max = prog_max_map.get(pid, 2)
        if prog_current < prog_max:
            raise HTTPException(
                status_code=400,
                detail=f"El estudiante debe estar en el módulo final del programa {pid} para graduarse"
            )
        program_statuses[pid] = "egresado"

    new_estado = derive_estado_from_program_statuses(program_statuses)
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"estado": new_estado, "program_statuses": program_statuses}}
    )
    updated = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    return updated
