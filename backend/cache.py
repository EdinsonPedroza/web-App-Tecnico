import time
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

class TTLCache:
    """Simple in-memory TTL cache for data that changes rarely."""
    
    def __init__(self, ttl_seconds: int = 300):
        self._cache: dict[str, tuple[float, Any]] = {}
        self._ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            timestamp, value = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return value
            del self._cache[key]
        return None
    
    def set(self, key: str, value: Any):
        self._cache[key] = (time.time(), value)
    
    def invalidate(self, key: str = None):
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()

# Cache instances
programs_cache = TTLCache(ttl_seconds=300)   # 5 minutes
subjects_cache = TTLCache(ttl_seconds=300)   # 5 minutes
recovery_panel_cache = TTLCache(ttl_seconds=45)  # 45 seconds — invalidated on any approval/rejection
