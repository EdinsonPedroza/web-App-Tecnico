import uuid
import logging
from datetime import datetime, timezone, timedelta
from database import db

logger = logging.getLogger(__name__)


def sanitize_string(input_str: str, max_length: int = 500) -> str:
    """Sanitize string input to prevent injection attacks"""
    import re
    if not input_str or not isinstance(input_str, str):
        return ""
    sanitized = re.sub(r'[<>{}()\'"\[\]\\;`]', '', input_str)
    sanitized = ''.join(char for char in sanitized if char.isprintable())
    return sanitized[:max_length]


def _make_audit_record(action: str, user_id: str, user_role: str, details: dict) -> dict:
    """Build an audit log record dict without inserting it (for batch inserts)."""
    now = datetime.now(timezone.utc)
    return {
        "id": str(uuid.uuid4()),
        "action": action,
        "user_id": user_id,
        "user_role": user_role,
        "details": details,
        "timestamp": now.isoformat(),
        "expires_at": now + timedelta(days=90)
    }


async def log_audit(action: str, user_id: str, user_role: str, details: dict):
    """Insert an audit log record into the audit_logs collection."""
    try:
        record = _make_audit_record(action, user_id, user_role, details)
        await db.audit_logs.insert_one(record)
    except Exception as exc:
        logger.error(f"Failed to write audit log (action={action}): {exc}")


def log_security_event(event_type: str, details: dict):
    """Log security-related events with sanitized details"""
    import json
    sanitized_details = {}
    for key, value in details.items():
        if isinstance(value, str):
            sanitized_details[key] = sanitize_string(value, 200)
        else:
            sanitized_details[key] = str(value)[:200]
    logger.warning(f"SECURITY: {event_type} - {json.dumps(sanitized_details)}")
