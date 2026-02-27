"""
Script para crear índices en MongoDB.
Ejecutar una vez antes de ir a producción:
    python create_indexes.py

También se llama automáticamente al iniciar la aplicación.
"""
import asyncio
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


async def create_indexes(db):
    """Crea todos los índices necesarios para rendimiento óptimo."""
    indexes = [
        # users — email uniqueness only applies to non-null values (partialFilterExpression
        # excludes documents where email is missing or null from the unique constraint,
        # allowing multiple users such as students who have no email address).
        ("users", [("email", 1)], {"unique": True, "partialFilterExpression": {"email": {"$type": "string"}}, "name": "users_email_unique"}),
        ("users", [("cedula", 1)], {"sparse": True, "name": "users_cedula"}),
        ("users", [("role", 1)], {"name": "users_role"}),
        ("users", [("estado", 1)], {"name": "users_estado"}),
        ("users", [("role", 1), ("estado", 1)], {"name": "users_role_estado"}),
        ("users", [("name", 1)], {"name": "users_name"}),
        # courses
        ("courses", [("teacher_id", 1)], {"name": "courses_teacher_id"}),
        ("courses", [("program_id", 1)], {"name": "courses_program_id"}),
        ("courses", [("student_ids", 1)], {"name": "courses_student_ids"}),
        # grades
        ("grades", [("student_id", 1)], {"name": "grades_student_id"}),
        ("grades", [("course_id", 1)], {"name": "grades_course_id"}),
        ("grades", [("activity_id", 1)], {"name": "grades_activity_id"}),
        ("grades", [("student_id", 1), ("course_id", 1)], {"name": "grades_student_course"}),
        ("grades", [("student_id", 1), ("course_id", 1), ("activity_id", 1)], {"name": "grades_student_course_activity"}),
        # submissions
        ("submissions", [("student_id", 1)], {"name": "submissions_student_id"}),
        ("submissions", [("activity_id", 1)], {"name": "submissions_activity_id"}),
        ("submissions", [("activity_id", 1), ("student_id", 1)], {"unique": True, "name": "submissions_activity_student_unique"}),
        # activities
        ("activities", [("course_id", 1)], {"name": "activities_course_id"}),
        ("activities", [("course_id", 1), ("subject_id", 1)], {"name": "activities_course_subject"}),
        ("activities", [("due_date", 1)], {"name": "activities_due_date"}),
        # programs
        ("programs", [("active", 1)], {"name": "programs_active"}),
        # subjects
        ("subjects", [("program_id", 1)], {"name": "subjects_program_id"}),
        ("subjects", [("program_id", 1), ("module_number", 1)], {"name": "subjects_program_module"}),
        # module_closures
        ("module_closures", [("program_id", 1), ("module_number", 1)], {"name": "module_closures_program_module"}),
        # recovery_enabled
        ("recovery_enabled", [("student_id", 1), ("course_id", 1)], {"name": "recovery_enabled_student_course"}),
        # failed_subjects
        ("failed_subjects", [("student_id", 1)], {"name": "failed_subjects_student_id"}),
        ("failed_subjects", [("student_id", 1), ("course_id", 1)], {"name": "failed_subjects_student_course"}),
        ("failed_subjects", [("course_id", 1), ("module_number", 1), ("recovery_processed", 1)], {"name": "failed_subjects_course_module_processed"}),
        ("failed_subjects", [("recovery_approved", 1), ("recovery_completed", 1), ("recovery_processed", 1), ("recovery_rejected", 1)], {"name": "failed_subjects_recovery_state"}),
    ]

    created = 0
    skipped = 0
    errors = 0

    for collection_name, keys, options in indexes:
        try:
            background_options = {**options, "background": True}
            await db[collection_name].create_index(keys, **background_options)
            logger.info(f"Índice creado/verificado: {collection_name}.{options.get('name', str(keys))}")
            created += 1
        except Exception as e:
            if "IndexOptionsConflict" in type(e).__name__ or "IndexOptionsConflict" in str(e):
                # Index exists with different options — drop and recreate so the new
                # options (e.g. partialFilterExpression) take effect.
                index_name = options.get("name")
                try:
                    if index_name:
                        await db[collection_name].drop_index(index_name)
                    background_options = {**options, "background": True}
                    await db[collection_name].create_index(keys, **background_options)
                    logger.info(f"Índice recreado con nuevas opciones: {collection_name}.{index_name}")
                    created += 1
                except Exception as recreate_e:
                    logger.error(f"Error recreando índice en {collection_name}.{index_name}: {recreate_e}")
                    errors += 1
            elif "already exists" in str(e).lower():
                skipped += 1
            else:
                logger.error(f"Error creando índice en {collection_name}: {e}")
                errors += 1

    logger.info(f"Índices: {created} creados/verificados, {skipped} ya existían, {errors} errores")
    return {"created": created, "skipped": skipped, "errors": errors}


async def main():
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.environ.get("DB_NAME", "WebApp")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    print(f"Conectando a MongoDB: {db_name}")
    result = await create_indexes(db)
    print(f"Resultado: {result}")
    client.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
