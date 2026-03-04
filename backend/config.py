import os
import logging
import re
from pathlib import Path
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env.local')
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

BOGOTA_TZ = ZoneInfo("America/Bogota")

# Error messages for enrollment prerequisite validation
_ERR_ENROLL_EGRESADO = "No se puede inscribir a un estudiante que ya egresó del programa."
_ERR_ENROLL_PENDIENTE = (
    "No se puede inscribir a un estudiante que tiene recuperaciones pendientes. "
    "Debe resolver su proceso de recuperación antes de matricularse en un nuevo grupo."
)

# JWT
JWT_SECRET = os.environ.get('JWT_SECRET')
_JWT_DEFAULT = 'educando_secret_key_2025_CHANGE_ME'
if not JWT_SECRET:
    logger.warning("⚠️ JWT_SECRET not set! Using insecure default. SET THIS IN PRODUCTION!")
    JWT_SECRET = _JWT_DEFAULT
if any(os.environ.get(env) for env in ['RENDER', 'RAILWAY_ENVIRONMENT', 'DYNO']) and JWT_SECRET == _JWT_DEFAULT:
    raise RuntimeError(
        "🚫 FATAL: JWT_SECRET is set to the insecure default value. "
        "Cannot start server in production. Set the JWT_SECRET environment variable to a strong random secret."
    )
JWT_ALGORITHM = "HS256"

# Rate limiting
MAX_LOGIN_ATTEMPTS_PER_IP = 50
MAX_LOGIN_ATTEMPTS_PER_USER = 5
LOGIN_ATTEMPT_WINDOW = 300

MAX_UPLOADS_PER_MINUTE = 20
UPLOAD_WINDOW = 60

# Module validation
MIN_MODULE_NUMBER = 1

def validate_module_number(module_num, field_name="module"):
    """Validate that a module number is a positive integer."""
    if not isinstance(module_num, int) or module_num < MIN_MODULE_NUMBER:
        raise ValueError(f"{field_name} must be >= {MIN_MODULE_NUMBER}, got {module_num}")
    return True

# Pagination limits
MAX_LIMIT = 500
MAX_LIMIT_GRADES = 1000

# File upload
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Cloudinary
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
USE_CLOUDINARY = bool(CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET)

if USE_CLOUDINARY:
    try:
        import cloudinary
        import cloudinary.uploader
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True
        )
        logger.info("Cloudinary configured – uploads will use persistent cloud storage.")
    except ImportError:
        USE_CLOUDINARY = False
        logger.warning("cloudinary package not installed. Falling back to local disk storage.")
else:
    if os.environ.get('RENDER') or os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('DYNO'):
        logger.warning(
            "⚠️  PRODUCTION WARNING: Files are stored on ephemeral disk storage. "
            "Uploaded files will be LOST on redeployment. "
            "Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET to use persistent storage."
        )

# AWS S3
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME')
AWS_S3_REGION = os.environ.get('AWS_S3_REGION', 'us-east-1')
USE_S3 = bool(AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_S3_BUCKET_NAME)

s3_client = None
if USE_S3:
    import boto3
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION
    )
    logger.info("AWS S3 configured – PDFs will use persistent S3 storage.")
else:
    logger.warning("AWS S3 not configured – PDFs stored on ephemeral local disk.")

# Production detection
IS_PRODUCTION = any(os.environ.get(env) for env in ['RENDER', 'RAILWAY_ENVIRONMENT', 'DYNO'])

# CORS
cors_origins_str = os.environ.get('CORS_ORIGINS', '*')
cors_origins = cors_origins_str.split(',') if ',' in cors_origins_str else [cors_origins_str]
allow_credentials = "*" not in cors_origins

if (IS_PRODUCTION or JWT_SECRET != _JWT_DEFAULT) and '*' in cors_origins:
    logger.warning(
        "⚠️  SECURITY WARNING: CORS_ORIGINS is set to '*' in production! "
        "Restrict CORS_ORIGINS to your frontend domain to improve security."
    )

def redact_mongo_url(url: str) -> str:
    """Redact sensitive information from MongoDB URL for logging"""
    if 'localhost' in url or '127.0.0.1' in url:
        return "localhost"
    return "cloud/remote"
