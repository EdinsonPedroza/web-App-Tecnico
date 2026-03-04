# Entry point - kept minimal for compatibility with gunicorn and tests
from app import app  # noqa: F401

__all__ = ["app"]
