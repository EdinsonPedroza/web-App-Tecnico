from fastapi import APIRouter
from routes.auth import router as auth_router
from routes.users import router as users_router
from routes.courses import router as courses_router
from routes.subjects import router as subjects_router
from routes.activities import router as activities_router
from routes.grades import router as grades_router
from routes.submissions import router as submissions_router
from routes.videos import router as videos_router
from routes.recovery import router as recovery_router
from routes.admin import router as admin_router
from routes.programs import router as programs_router
from routes.dashboard import router as dashboard_router
from routes.uploads import router as uploads_router

router = APIRouter(prefix="/api")
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(courses_router)
router.include_router(subjects_router)
router.include_router(activities_router)
router.include_router(grades_router)
router.include_router(submissions_router)
router.include_router(videos_router)
router.include_router(recovery_router)
router.include_router(admin_router)
router.include_router(programs_router)
router.include_router(dashboard_router)
router.include_router(uploads_router)
