import logging
from datetime import datetime, timezone, timedelta
import os

from database import db

logger = logging.getLogger(__name__)


async def acquire_scheduler_lock(lock_name: str, ttl_seconds: int = 300) -> bool:
    """Try to acquire a distributed lock using MongoDB."""
    try:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=ttl_seconds)
        result = await db.scheduler_locks.update_one(
            {
                "lock_name": lock_name,
                "$or": [
                    {"expires_at": {"$lt": now}},
                    {"expires_at": {"$exists": False}}
                ]
            },
            {
                "$set": {
                    "lock_name": lock_name,
                    "locked_by": f"worker-{os.environ.get('WORKER_ID', 'unknown')}-{os.getpid()}",
                    "locked_at": now,
                    "expires_at": expires_at
                }
            },
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
    except Exception as e:
        logger.error(f"Failed to acquire scheduler lock '{lock_name}': {e}")
        return False


async def release_scheduler_lock(lock_name: str):
    """Release a distributed lock."""
    try:
        await db.scheduler_locks.delete_one({"lock_name": lock_name})
    except Exception as e:
        logger.error(f"Failed to release scheduler lock '{lock_name}': {e}")


async def cleanup_expired_data():
    """Safety-net cleanup for expired tokens and rate limits."""
    try:
        if not await acquire_scheduler_lock("cleanup_expired_data", ttl_seconds=600):
            logger.info("cleanup_expired_data: another worker holds the lock, skipping")
            return
        cutoff = datetime.now(timezone.utc)
        r1 = await db.refresh_tokens.delete_many({"expires_at": {"$lt": cutoff}})
        r2 = await db.rate_limits.delete_many({"expires_at": {"$lt": cutoff}})
        if r1.deleted_count or r2.deleted_count:
            logger.info(f"Cleanup: removed {r1.deleted_count} expired refresh tokens, {r2.deleted_count} expired rate limits")
    except Exception as e:
        logger.error(f"cleanup_expired_data failed: {e}")
