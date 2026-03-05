import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import (
    BOGOTA_TZ, cors_origins, allow_credentials,
    UPLOAD_DIR, USE_S3, AWS_S3_BUCKET_NAME, AWS_S3_REGION,
    s3_client
)
from database import db, client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app):
    # === STARTUP ===
    try:
        logger.info("Starting application initialization...")

        await db.command('ping')
        logger.info("MongoDB connection successful")

        try:
            from create_indexes import create_indexes
            await create_indexes(db)
            logger.info("Índices MongoDB verificados/creados exitosamente")
        except Exception as e:
            logger.warning(f"No se pudieron crear índices automáticamente: {e}")

        try:
            await db.rate_limits.create_index("expires_at", expireAfterSeconds=0, name="rate_limits_ttl")
        except Exception as idx_err:
            logger.warning(f"rate_limits_ttl index could not be created: {idx_err}")
        try:
            await db.rate_limits.create_index(
                [("key", 1), ("timestamp", -1)], name="rate_limits_key_timestamp"
            )
        except Exception as idx_err:
            # If there is an IndexKeySpecsConflict (code 86), the old index was created
            # with a different sort direction. Drop and recreate it — this is safe because
            # rate_limits is a performance-only index with no unique data; no documents
            # are deleted when dropping an index.
            if "IndexKeySpecsConflict" in str(idx_err) or getattr(idx_err, "code", None) == 86:
                try:
                    await db.rate_limits.drop_index("rate_limits_key_timestamp")
                    await db.rate_limits.create_index(
                        [("key", 1), ("timestamp", -1)], name="rate_limits_key_timestamp"
                    )
                    logger.info("rate_limits_key_timestamp index recreated with correct sort direction")
                except Exception as recreate_err:
                    logger.warning(f"rate_limits_key_timestamp index could not be recreated: {recreate_err}")
            else:
                logger.warning(f"rate_limits_key_timestamp index could not be created: {idx_err}")
        try:
            await db.scheduler_locks.create_index("expires_at", expireAfterSeconds=0, name="scheduler_locks_ttl")
        except Exception as idx_err:
            logger.debug(f"scheduler_locks_ttl index already exists or could not be created: {idx_err}")
        try:
            await db.scheduler_locks.create_index("lock_name", unique=True, name="scheduler_locks_unique")
        except Exception as idx_err:
            logger.debug(f"scheduler_locks_unique index already exists or could not be created: {idx_err}")
        try:
            await db.grade_changes.create_index(
                [("student_id", 1), ("changed_at", -1)],
                name="grade_changes_student_date"
            )
        except Exception as idx_err:
            logger.debug(f"grade_changes_student_date index already exists or could not be created: {idx_err}")
        try:
            await db.refresh_tokens.create_index("expires_at", expireAfterSeconds=0, name="refresh_tokens_ttl")
        except Exception as idx_err:
            logger.debug(f"refresh_tokens_ttl index already exists or could not be created: {idx_err}")
        try:
            await db.refresh_tokens.create_index("token", unique=True, name="refresh_tokens_token_unique")
        except Exception as idx_err:
            logger.debug(f"refresh_tokens_token_unique index already exists or could not be created: {idx_err}")
        try:
            await db.refresh_tokens.create_index("user_id", name="refresh_tokens_user_id")
        except Exception as idx_err:
            logger.debug(f"refresh_tokens_user_id index already exists or could not be created: {idx_err}")

        await create_initial_data()

        worker_id = os.environ.get("WORKER_ID")
        should_start_scheduler = worker_id is None or worker_id == "0"
        if should_start_scheduler:
            from routes.admin import check_and_close_modules
            from scheduler.cleanup import cleanup_expired_data

            scheduler.add_job(
                check_and_close_modules,
                CronTrigger(hour=2, minute=0, timezone=BOGOTA_TZ),
                id='auto_close_modules',
                name='Automatic Module Closure',
                replace_existing=True
            )
            scheduler.add_job(
                cleanup_expired_data,
                CronTrigger(hour=3, minute=0, timezone=BOGOTA_TZ),
                id='cleanup_expired_data',
                name='Cleanup Expired Tokens and Rate Limits',
                replace_existing=True
            )
            scheduler.start()
            logger.info("Automatic module closure scheduler started (runs daily at 02:00 AM Bogotá time / UTC-5)")
        else:
            logger.info(f"Worker {worker_id}: skipping scheduler start (only worker 0 runs the scheduler)")

        if USE_S3:
            try:
                s3_client.head_bucket(Bucket=AWS_S3_BUCKET_NAME)
                logger.info(f"✅ AWS S3 bucket '{AWS_S3_BUCKET_NAME}' is accessible.")
            except Exception as e:
                logger.error(f"❌ AWS S3 bucket verification failed: {e}. PDF uploads will fail!")

        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Startup failed: {e}", exc_info=True)
        if "auth" in str(e).lower() or "connection" in str(e).lower() or "ServerSelectionTimeoutError" in type(e).__name__:
            logger.error(
                "MongoDB connection failed. Please check your MONGO_URL environment variable."
            )
        logger.warning(
            "Application started WITHOUT database connection. "
            "API endpoints requiring MongoDB will not work until the connection is restored."
        )

    yield  # Application runs here

    # === SHUTDOWN ===
    logger.info("Application shutting down...")
    try:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler shut down gracefully")
    except Exception as e:
        logger.warning(f"Error shutting down scheduler: {e}")
    client.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        content_type = response.headers.get("content-type", "")
        if "text/html" in content_type:
            csp_directives = [
                "default-src 'self'",
                "script-src 'self'",
                "style-src 'self' 'unsafe-inline'",
                "img-src 'self' data: blob: https://*.amazonaws.com",
                "font-src 'self' data:",
                "connect-src 'self' https://*.onrender.com",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
            ]
            response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        if request.url.path.startswith("/api/auth/"):
            response.headers["Cache-Control"] = "no-store"
        return response


app.add_middleware(SecurityHeadersMiddleware)


@app.get("/api/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring systems."""
    try:
        await db.command('ping')
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy"}
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
    if debug_mode:
        logger.warning("DEBUG mode is enabled - detailed errors are exposed to clients")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if debug_mode else "An unexpected error occurred"
        }
    )


# Mount static files for local uploads
try:
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
except Exception:
    pass

# Include all API routes
from routes import router as api_router  # noqa: E402
app.include_router(api_router)


@app.get("/")
async def app_root():
    return {"message": "Corporación Social Educando API"}


async def create_initial_data():
    """Crea los usuarios y datos iniciales si no existen"""
    import uuid
    from datetime import datetime, timezone
    from pymongo import UpdateOne
    from utils.security import hash_password

    logger.info("Verificando y creando datos iniciales...")

    programs = [
        {
            "id": "prog-admin",
            "name": "Técnico en Asistencia Administrativa",
            "description": "Formación técnica en gestión administrativa",
            "duration": "12 meses",
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
            "active": True
        },
        {
            "id": "prog-infancia",
            "name": "Técnico Laboral en Atención a la Primera Infancia",
            "description": "Formación en desarrollo infantil",
            "duration": "12 meses",
            "modules": [
                {"number": 1, "name": "MÓDULO 1", "subjects": [
                    "Inglés I", "Proyecto de vida",
                    "Construcción social de la infancia",
                    "Perspectiva del desarrollo infantil", "Salud y nutrición",
                    "Lenguaje y educación infantil",
                    "Juego y otras formas de comunicación", "Educación y pedagogía"
                ]},
                {"number": 2, "name": "MÓDULO 2", "subjects": [
                    "Inglés II", "Construcción del mundo Matemático",
                    "Dificultades en el aprendizaje", "Estrategias del aula",
                    "Trabajo de grado", "Investigación", "Práctica - Informe"
                ]}
            ],
            "module1_close_date": None,
            "module2_close_date": None,
            "active": True
        },
        {
            "id": "prog-sst",
            "name": "Técnico en Seguridad y Salud en el Trabajo",
            "description": "Formación en prevención de riesgos",
            "duration": "12 meses",
            "modules": [
                {"number": 1, "name": "MÓDULO 1", "subjects": [
                    "Fundamentos en Seguridad y Salud en el Trabajo",
                    "Administración en salud", "Condiciones de seguridad",
                    "Matemáticas", "Psicología del Trabajo"
                ]},
                {"number": 2, "name": "MÓDULO 2", "subjects": [
                    "Comunicación oral y escrita",
                    "Sistema de gestión de seguridad y salud del trabajo",
                    "Anatomía y fisiología", "Medicina preventiva del trabajo",
                    "Ética profesional", "Gestión ambiental", "Proyecto de grado"
                ]}
            ],
            "module1_close_date": None,
            "module2_close_date": None,
            "active": True
        },
    ]

    programs_created = 0
    for p in programs:
        result = await db.programs.update_one(
            {"id": p["id"]},
            {"$setOnInsert": p},
            upsert=True
        )
        if result.upserted_id:
            programs_created += 1
    if programs_created > 0:
        logger.info(f"Creados {programs_created} programas nuevos")
    else:
        logger.info("Todos los programas ya existen - no se sobrescribieron")

    for prog in programs:
        for module in prog["modules"]:
            for subj_name in module["subjects"]:
                subject_data = {
                    "id": str(uuid.uuid4()),
                    "name": subj_name,
                    "program_id": prog["id"],
                    "module_number": module["number"],
                    "description": "",
                    "active": True
                }
                await db.subjects.update_one(
                    {"name": subj_name, "program_id": prog["id"], "module_number": module["number"]},
                    {"$setOnInsert": subject_data},
                    upsert=True
                )

    legacy_id_map = {
        "user-editor-1": str(uuid.uuid5(uuid.NAMESPACE_OID, "user-editor-1")),
        "user-prof-1":   str(uuid.uuid5(uuid.NAMESPACE_OID, "user-prof-1")),
        "user-prof-2":   str(uuid.uuid5(uuid.NAMESPACE_OID, "user-prof-2")),
    }
    for old_id, new_id in legacy_id_map.items():
        result = await db.users.update_one({"id": old_id}, {"$set": {"id": new_id}})
        if result.modified_count > 0:
            logger.info(f"Migrated legacy user ID: {old_id} -> {new_id}")

    reset_users = os.environ.get('RESET_USERS', 'false').lower() == 'true'
    if reset_users:
        logger.warning("⚠️  RESET_USERS=true: Eliminando TODOS los usuarios existentes...")
        deleted_result = await db.users.delete_many({})
        logger.info(f"Eliminados {deleted_result.deleted_count} usuarios")

    existing_user_count = await db.users.count_documents({})
    if existing_user_count > 0:
        logger.info(f"Base de datos tiene {existing_user_count} usuarios. Verificando usuarios semilla...")
    else:
        logger.info("Base de datos vacía. Creando usuarios iniciales...")

    create_seed_users = os.environ.get('CREATE_SEED_USERS', 'false').lower() == 'true'

    if not create_seed_users:
        logger.info("CREATE_SEED_USERS=false: Omitiendo creación de usuarios semilla (modo producción)")
    else:
        _is_dev = os.environ.get("ENVIRONMENT", "development").lower() in ("development", "dev", "local")

        editor_password = os.environ.get("SEED_EDITOR_PASSWORD", "Editor2024!" if _is_dev else None)
        prof1_password = os.environ.get("SEED_PROF1_PASSWORD", "Profesor1!" if _is_dev else None)
        prof2_password = os.environ.get("SEED_PROF2_PASSWORD", "Profesor2!" if _is_dev else None)

        if not editor_password:
            logger.warning("SEED_EDITOR_PASSWORD not set. Skipping editor seed user.")
        if not prof1_password:
            logger.warning("SEED_PROF1_PASSWORD not set. Skipping seed user prof-1.")
        if not prof2_password:
            logger.warning("SEED_PROF2_PASSWORD not set. Skipping seed user prof-2.")

        seed_users = []
        if editor_password:
            seed_users.append(
                {"id": str(uuid.uuid5(uuid.NAMESPACE_OID, "user-editor-1")), "name": "Editor Principal",
                 "email": "editor@tecnico.com", "cedula": None, "password_hash": hash_password(editor_password),
                 "role": "editor", "program_id": None, "program_ids": [], "subject_ids": [],
                 "phone": None, "active": True, "module": None, "grupo": None, "estado": "activo"}
            )
        if prof1_password:
            seed_users.append(
                {"id": str(uuid.uuid5(uuid.NAMESPACE_OID, "user-prof-1")), "name": "Ana Martínez",
                 "email": "ana.martinez@profesor.com", "cedula": None, "password_hash": hash_password(prof1_password),
                 "role": "profesor", "program_id": None, "program_ids": [], "subject_ids": [],
                 "phone": None, "active": True, "module": None, "grupo": None, "estado": "activo"}
            )
        if prof2_password:
            seed_users.append(
                {"id": str(uuid.uuid5(uuid.NAMESPACE_OID, "user-prof-2")), "name": "Juan Rodríguez",
                 "email": "juan.rodriguez@profesor.com", "cedula": None, "password_hash": hash_password(prof2_password),
                 "role": "profesor", "program_id": None, "program_ids": [], "subject_ids": [],
                 "phone": None, "active": True, "module": None, "grupo": None, "estado": "activo"}
            )

        created_count = 0
        if seed_users:
            ops = [UpdateOne({"id": u["id"]}, {"$setOnInsert": u}, upsert=True) for u in seed_users]
            result = await db.users.bulk_write(ops, ordered=False)
            created_count = result.upserted_count

        if created_count > 0:
            logger.info(f"Creados {created_count} usuarios semilla nuevos")
        else:
            logger.info("Todos los usuarios semilla ya existen - no se sobrescribieron")

    logger.info(f"Total usuarios en sistema: {await db.users.count_documents({})}")

    logger.info("Checking and fixing course subject_ids field...")
    courses_to_fix = await db.courses.find(
        {"$or": [
            {"subject_ids": {"$exists": False}},
            {"subject_ids": None},
            {"subject_ids": []}
        ]},
        {"_id": 0}
    ).to_list(1000)

    fixed_count = 0
    for course in courses_to_fix:
        if course.get("subject_id") and (not course.get("subject_ids") or len(course.get("subject_ids", [])) == 0):
            await db.courses.update_one(
                {"id": course["id"]},
                {"$set": {"subject_ids": [course["subject_id"]]}}
            )
            fixed_count += 1

    if fixed_count > 0:
        logger.info(f"Fixed {fixed_count} courses with missing subject_ids field")

    logger.info("Checking and fixing user subject_ids field...")
    users_to_fix = await db.users.find(
        {"$or": [
            {"subject_ids": {"$exists": False}},
            {"subject_ids": None}
        ]},
        {"_id": 0}
    ).to_list(1000)

    fixed_user_count = 0
    for user in users_to_fix:
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {"subject_ids": []}}
        )
        fixed_user_count += 1

    if fixed_user_count > 0:
        logger.info(f"Fixed {fixed_user_count} users with missing subject_ids field")

    logger.info("Checking and migrating student program_statuses field...")
    students_to_migrate = await db.users.find(
        {"role": "estudiante", "program_statuses": {"$exists": False}},
        {"_id": 0, "id": 1, "program_ids": 1, "program_id": 1, "estado": 1}
    ).to_list(5000)

    migrated_count = 0
    for student in students_to_migrate:
        program_ids_list = student.get("program_ids") or []
        if not program_ids_list and student.get("program_id"):
            program_ids_list = [student["program_id"]]
        if not program_ids_list:
            continue
        global_estado = student.get("estado", "activo") or "activo"
        program_statuses = {pid: global_estado for pid in program_ids_list}
        await db.users.update_one(
            {"id": student["id"]},
            {"$set": {"program_statuses": program_statuses}}
        )
        migrated_count += 1

    if migrated_count > 0:
        logger.info(f"Migrated {migrated_count} students: initialized program_statuses field")

    logger.info("Checking for orphaned group/course data...")
    existing_course_ids = [c["id"] for c in await db.courses.find({}, {"_id": 0, "id": 1}).to_list(5000)]
    if not existing_course_ids:
        logger.warning(
            "Orphan purge skipped: no courses found in DB. "
            "This is safe on first startup. If courses exist and this warning persists, "
            "check MongoDB connectivity."
        )
    else:
        orphan_filter = {"course_id": {"$nin": existing_course_ids}}
        orphan_activities = await db.activities.delete_many(orphan_filter)
        orphan_grades = await db.grades.delete_many(orphan_filter)
        orphan_submissions = await db.submissions.delete_many(orphan_filter)
        orphan_videos = await db.class_videos.delete_many(orphan_filter)
        orphan_recovery = await db.recovery_enabled.delete_many(orphan_filter)
        orphan_failed = await db.failed_subjects.delete_many(orphan_filter)
        total_purged = (orphan_activities.deleted_count + orphan_grades.deleted_count +
                        orphan_submissions.deleted_count + orphan_videos.deleted_count +
                        orphan_recovery.deleted_count + orphan_failed.deleted_count)
        if total_purged > 0:
            logger.info(
                f"Purged {total_purged} orphaned records: "
                f"{orphan_activities.deleted_count} activities, "
                f"{orphan_grades.deleted_count} grades, "
                f"{orphan_submissions.deleted_count} submissions, "
                f"{orphan_videos.deleted_count} videos, "
                f"{orphan_recovery.deleted_count} recovery_enabled, "
                f"{orphan_failed.deleted_count} failed_subjects"
            )
        else:
            logger.info("No orphaned group/course data found")

    logger.info("Datos iniciales verificados/creados exitosamente")
