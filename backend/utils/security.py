import logging
import hashlib
import jwt
import bcrypt as _bcrypt
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import HTTPException, Header

from database import db
from config import (
    JWT_SECRET, JWT_ALGORITHM,
    MAX_LOGIN_ATTEMPTS_PER_IP, MAX_LOGIN_ATTEMPTS_PER_USER, LOGIN_ATTEMPT_WINDOW
)

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> tuple:
    """Verify password against bcrypt hash, SHA256, or plain text.
    Returns a tuple (is_valid: bool, needs_rehash: bool)."""
    if hashed_password.startswith(('$2a$', '$2b$', '$2y$')):
        try:
            return (_bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8')), False)
        except Exception as e:
            logger.error(f"Bcrypt verification error: {type(e).__name__}")
            return (False, False)
    elif len(hashed_password) == 64 and all(c in '0123456789abcdef' for c in hashed_password.lower()):
        try:
            is_valid = hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
            return (is_valid, is_valid)
        except Exception:
            return (False, False)
    else:
        logger.warning("Plain text password detected in database — will be re-hashed on successful login")
        is_valid = plain_password == hashed_password
        return (is_valid, is_valid)


def safe_object_id(value: str, field_name: str = "id") -> str:
    """Validate that a string parameter is safe for MongoDB queries."""
    if not isinstance(value, str) or not value or value.startswith('$') or '{' in value or len(value) > 200:
        raise HTTPException(status_code=400, detail=f"{field_name} inválido")
    return value


def create_token(user_id: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def check_rate_limit(ip_address: str, identifier: str = None) -> bool:
    """Verifica límite por IP (50) y por identificador de usuario (5)."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=LOGIN_ATTEMPT_WINDOW)
    ip_key = f"login_ip:{ip_address}"
    ip_count = await db.rate_limits.count_documents({
        "key": ip_key,
        "timestamp": {"$gte": window_start}
    })
    if ip_count >= MAX_LOGIN_ATTEMPTS_PER_IP:
        return False
    if identifier:
        id_key = f"login_id:{identifier}"
        id_count = await db.rate_limits.count_documents({
            "key": id_key,
            "timestamp": {"$gte": window_start}
        })
        if id_count >= MAX_LOGIN_ATTEMPTS_PER_USER:
            return False
    return True


async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No autorizado")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id", "")
        if not isinstance(user_id, str) or not user_id or user_id.startswith('$'):
            raise HTTPException(status_code=401, detail="Token inválido")
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        if not user.get("active", True):
            raise HTTPException(status_code=403, detail="Cuenta desactivada")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")


def mask_identifier(value: str) -> str:
    """Mask personal identifiers for safe logging."""
    if not value or len(value) < 4:
        return "****"
    return value[:2] + "*" * (len(value) - 4) + value[-2:]
