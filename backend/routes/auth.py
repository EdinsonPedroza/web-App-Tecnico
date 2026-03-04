import uuid
import logging
import json
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request

from database import db
from utils.security import (
    get_current_user, check_rate_limit, create_token,
    hash_password, verify_password, mask_identifier
)
from utils.audit import log_audit, log_security_event
from models.schemas import LoginRequest
from config import LOGIN_ATTEMPT_WINDOW

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/auth/login")
async def login(req: LoginRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"

    identifier = req.cedula if req.role == "estudiante" else req.email
    if not await check_rate_limit(client_ip, identifier):
        log_security_event("RATE_LIMIT_EXCEEDED", {
            "ip": client_ip,
            "role": req.role,
            "identifier": mask_identifier(req.email or req.cedula or "")
        })
        raise HTTPException(
            status_code=429,
            detail="Demasiados intentos de inicio de sesión. Por favor, intente más tarde."
        )

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=LOGIN_ATTEMPT_WINDOW)
    docs = [{"key": f"login_ip:{client_ip}", "timestamp": now, "expires_at": expires_at}]
    if identifier:
        docs.append({"key": f"login_id:{identifier}", "timestamp": now, "expires_at": expires_at})
    await db.rate_limits.insert_many(docs)

    if req.role == "estudiante":
        if not req.cedula:
            raise HTTPException(status_code=400, detail="Cédula requerida")
        user = await db.users.find_one(
            {"cedula": req.cedula, "role": "estudiante"},
            {"_id": 0}
        )
        identifier = req.cedula
    elif req.role in ["profesor", "admin", "editor"]:
        if not req.email:
            raise HTTPException(status_code=400, detail="Correo requerido")
        role_filter = {"$in": ["profesor", "admin", "editor"]} if req.role == "profesor" else req.role
        user = await db.users.find_one({"email": req.email, "role": role_filter}, {"_id": 0})
        identifier = req.email
    else:
        log_security_event("INVALID_ROLE", {"role": req.role, "ip": client_ip})
        raise HTTPException(status_code=400, detail="Rol inválido")

    if not user:
        log_security_event("LOGIN_FAILED_USER_NOT_FOUND", {
            "ip": client_ip,
            "role": req.role,
            "identifier": mask_identifier(identifier)
        })
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    is_valid, needs_rehash = verify_password(req.password, user["password_hash"])
    if not is_valid:
        log_security_event("LOGIN_FAILED_WRONG_PASSWORD", {
            "ip": client_ip,
            "role": req.role,
            "user_id": user["id"],
            "identifier": mask_identifier(identifier)
        })
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    if not user.get("active", True):
        log_security_event("LOGIN_FAILED_INACTIVE_ACCOUNT", {
            "ip": client_ip,
            "user_id": user["id"],
            "identifier": mask_identifier(identifier)
        })
        raise HTTPException(status_code=403, detail="Cuenta desactivada")

    if needs_rehash:
        try:
            await db.users.update_one(
                {"id": user["id"]},
                {"$set": {"password_hash": hash_password(req.password)}}
            )
            logger.info(f"Password re-hashed to bcrypt for user_id={user['id']}")
        except Exception as rehash_err:
            logger.error(f"Failed to re-hash password for user_id={user['id']}: {rehash_err}")

    if identifier:
        await db.rate_limits.delete_many({"key": f"login_id:{identifier}"})

    logger.info(f"Successful login: user_id={user['id']}, role={user['role']}, ip={client_ip}")
    await log_audit("login_success", user["id"], user["role"], {"ip": client_ip})

    token = create_token(user["id"], user["role"])
    await db.refresh_tokens.delete_many({"user_id": user["id"]})
    refresh_token_str = str(uuid.uuid4())
    await db.refresh_tokens.insert_one({
        "token": refresh_token_str,
        "user_id": user["id"],
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7)
    })
    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    return {"token": token, "refresh_token": refresh_token_str, "user": user_data}


@router.post("/auth/refresh")
async def refresh_token(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    refresh_key = f"refresh_ip:{client_ip}"
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=300)
    count = await db.rate_limits.count_documents({
        "key": refresh_key,
        "timestamp": {"$gte": window_start}
    })
    if count >= 30:
        raise HTTPException(status_code=429, detail="Demasiadas solicitudes de renovación de sesión")
    await db.rate_limits.insert_one({
        "key": refresh_key,
        "timestamp": now,
        "expires_at": now + timedelta(seconds=300)
    })

    try:
        body = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Body JSON inválido")
    old_token = body.get("refresh_token")
    if not old_token:
        raise HTTPException(status_code=400, detail="refresh_token requerido")

    token_doc = await db.refresh_tokens.find_one_and_delete({"token": old_token})
    if not token_doc:
        raise HTTPException(status_code=401, detail="Refresh token inválido o ya utilizado")

    if token_doc.get("expires_at") and token_doc["expires_at"] < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expirado")

    user_id = token_doc["user_id"]
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user or not user.get("active", True):
        raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")

    new_refresh_token = str(uuid.uuid4())
    await db.refresh_tokens.insert_one({
        "token": new_refresh_token,
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7)
    })

    new_access_token = create_token(user_id, user["role"])
    return {
        "token": new_access_token,
        "refresh_token": new_refresh_token
    }


@router.post("/auth/logout")
async def logout(request: Request, user=Depends(get_current_user)):
    body = {}
    try:
        body = await request.json()
    except (ValueError, Exception) as e:
        logger.debug(f"Logout: could not parse request body: {type(e).__name__}")
    refresh_token_value = body.get("refresh_token") if body else None
    if refresh_token_value:
        await db.refresh_tokens.delete_one({"token": refresh_token_value, "user_id": user["id"]})
    else:
        await db.refresh_tokens.delete_many({"user_id": user["id"]})
    return {"message": "Sesión cerrada exitosamente"}


@router.get("/auth/me")
async def get_me(user=Depends(get_current_user)):
    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    return user_data


@router.get("/me/subjects")
async def get_my_subjects(user=Depends(get_current_user)):
    """Return the full Subject objects assigned to the authenticated teacher."""
    if user["role"] not in ["profesor", "admin"]:
        raise HTTPException(status_code=403, detail="Solo profesores pueden acceder a sus materias")
    subject_ids = user.get("subject_ids") or []
    if not subject_ids:
        return []
    subjects = await db.subjects.find({"id": {"$in": subject_ids}}, {"_id": 0}).to_list(500)
    return subjects
