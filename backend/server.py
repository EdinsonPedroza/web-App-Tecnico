from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header, UploadFile, File
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import hashlib
import json
import shutil

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'educando_db')]

# JWT Secret
JWT_SECRET = os.environ.get('JWT_SECRET', 'educando_secret_key_2025')
JWT_ALGORITHM = "HS256"

app = FastAPI()
api_router = APIRouter(prefix="/api")

# File upload directory
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# --- Startup Event - Crear datos iniciales ---
@app.on_event("startup")
async def startup_event():
    await create_initial_data()

async def create_initial_data():
    """Crea los usuarios y datos iniciales si no existen"""
    # Verificar si ya existe el admin
    admin = await db.users.find_one({"email": "admin@educando.com"})
    if admin:
        return  # Ya existen datos
    
    print("Creando datos iniciales...")
    
    # Crear programas
    programs = [
        {"id": "prog-admin", "name": "Técnico en Asistencia Administrativa", "description": "Formación técnica en gestión administrativa", "duration": "12 meses", "modules": [], "active": True},
        {"id": "prog-infancia", "name": "Técnico en Atención a la Primera Infancia", "description": "Formación en desarrollo infantil", "duration": "12 meses", "modules": [], "active": True},
        {"id": "prog-sst", "name": "Técnico en Seguridad y Salud en el Trabajo", "description": "Formación en prevención de riesgos", "duration": "12 meses", "modules": [], "active": True},
    ]
    for p in programs:
        await db.programs.update_one({"id": p["id"]}, {"$set": p}, upsert=True)
    
    # Crear usuarios
    users = [
        {"id": "user-admin", "name": "Administrador General", "email": "admin@educando.com", "cedula": None, "password_hash": hash_password("admin123"), "role": "admin", "program_id": None, "phone": "3001234567", "active": True},
        {"id": "user-prof-1", "name": "María García López", "email": "profesor@educando.com", "cedula": None, "password_hash": hash_password("profesor123"), "role": "profesor", "program_id": None, "phone": "3009876543", "active": True},
        {"id": "user-est-1", "name": "Juan Martínez Ruiz", "email": None, "cedula": "1234567890", "password_hash": hash_password("estudiante123"), "role": "estudiante", "program_id": "prog-admin", "phone": "3101234567", "active": True},
        {"id": "user-est-2", "name": "Ana Sofía Hernández", "email": None, "cedula": "0987654321", "password_hash": hash_password("estudiante123"), "role": "estudiante", "program_id": "prog-admin", "phone": "3207654321", "active": True},
    ]
    for u in users:
        await db.users.update_one({"id": u["id"]}, {"$set": u}, upsert=True)
    
    # Crear materias
    subjects = [
        {"id": "subj-1", "name": "Fundamentos de Administración", "program_id": "prog-admin", "module_number": 1, "description": "Bases de la gestión administrativa", "active": True},
        {"id": "subj-2", "name": "Herramientas Ofimáticas", "program_id": "prog-admin", "module_number": 1, "description": "Excel, Word, PowerPoint", "active": True},
    ]
    for s in subjects:
        await db.subjects.update_one({"id": s["id"]}, {"$set": s}, upsert=True)
    
    # Crear curso
    course = {"id": "course-1", "name": "Fundamentos de Administración - Grupo A 2025", "program_id": "prog-admin", "subject_id": "subj-1", "teacher_id": "user-prof-1", "year": 2025, "student_ids": ["user-est-1", "user-est-2"], "active": True}
    await db.courses.update_one({"id": course["id"]}, {"$set": course}, upsert=True)
    
    # Crear actividades
    now = datetime.now(timezone.utc)
    activities = [
        {"id": "act-1", "course_id": "course-1", "title": "Ensayo sobre principios administrativos", "description": "Elaborar un ensayo de 2 páginas sobre los principios fundamentales de la administración", "activity_number": 1, "start_date": now.isoformat(), "due_date": (now + timedelta(days=14)).isoformat(), "files": [], "active": True},
        {"id": "act-2", "course_id": "course-1", "title": "Taller de organización empresarial", "description": "Realizar el taller práctico sobre estructura organizacional", "activity_number": 2, "start_date": now.isoformat(), "due_date": (now + timedelta(days=7)).isoformat(), "files": [], "active": True},
    ]
    for a in activities:
        await db.activities.update_one({"id": a["id"]}, {"$set": a}, upsert=True)
    
    print("Datos iniciales creados exitosamente")
    print("Credenciales:")
    print("  Admin: admin@educando.com / admin123")
    print("  Profesor: profesor@educando.com / profesor123")
    print("  Estudiante: 1234567890 / estudiante123")

# --- Utility Functions ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_token(user_id: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No autorizado")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

# --- Pydantic Models ---
class LoginRequest(BaseModel):
    email: Optional[str] = None
    cedula: Optional[str] = None
    password: str
    role: str

class UserCreate(BaseModel):
    name: str
    email: Optional[str] = None
    cedula: Optional[str] = None
    password: str
    role: str
    program_id: Optional[str] = None
    phone: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    cedula: Optional[str] = None
    phone: Optional[str] = None
    program_id: Optional[str] = None
    active: Optional[bool] = None

class ProgramCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    duration: Optional[str] = "12 meses"
    modules: Optional[list] = []

class ProgramUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None
    modules: Optional[list] = None
    active: Optional[bool] = None

class SubjectCreate(BaseModel):
    name: str
    program_id: str
    module_number: int = 1
    description: Optional[str] = ""

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    module_number: Optional[int] = None
    program_id: Optional[str] = None
    active: Optional[bool] = None

class CourseCreate(BaseModel):
    name: str
    program_id: str
    subject_id: str
    teacher_id: str
    year: int = 2025
    student_ids: Optional[List[str]] = []

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    teacher_id: Optional[str] = None
    student_ids: Optional[List[str]] = None
    active: Optional[bool] = None

class ActivityCreate(BaseModel):
    course_id: str
    title: str
    description: Optional[str] = ""
    start_date: Optional[str] = None
    due_date: str
    files: Optional[list] = []

class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    due_date: Optional[str] = None
    files: Optional[list] = None
    active: Optional[bool] = None

class GradeCreate(BaseModel):
    student_id: str
    course_id: str
    activity_id: Optional[str] = None
    value: float
    comments: Optional[str] = ""

class GradeUpdate(BaseModel):
    value: Optional[float] = None
    comments: Optional[str] = None

class ClassVideoCreate(BaseModel):
    course_id: str
    title: str
    url: str
    description: Optional[str] = ""

class SubmissionCreate(BaseModel):
    activity_id: str
    content: Optional[str] = ""
    files: Optional[list] = []

# --- Auth Routes ---
@api_router.post("/auth/login")
async def login(req: LoginRequest):
    query = {}
    if req.role == "estudiante":
        if not req.cedula:
            raise HTTPException(status_code=400, detail="Cédula requerida")
        query = {"cedula": req.cedula, "role": "estudiante"}
    else:
        if not req.email:
            raise HTTPException(status_code=400, detail="Correo requerido")
        query = {"email": req.email, "role": req.role}
    
    user = await db.users.find_one(query, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    if not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    if not user.get("active", True):
        raise HTTPException(status_code=403, detail="Cuenta desactivada")
    
    token = create_token(user["id"], user["role"])
    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    return {"token": token, "user": user_data}

@api_router.get("/auth/me")
async def get_me(user=Depends(get_current_user)):
    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    return user_data

# --- Users Routes ---
@api_router.get("/users")
async def get_users(role: Optional[str] = None, user=Depends(get_current_user)):
    if user["role"] not in ["admin", "profesor"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    query = {}
    if role:
        query["role"] = role
    users = await db.users.find(query, {"_id": 0, "password_hash": 0}).to_list(1000)
    return users

@api_router.post("/users")
async def create_user(req: UserCreate, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede crear usuarios")
    
    if req.role in ["admin", "profesor"] and req.email:
        existing = await db.users.find_one({"email": req.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email ya existe")
    
    if req.role == "estudiante" and req.cedula:
        existing = await db.users.find_one({"cedula": req.cedula})
        if existing:
            raise HTTPException(status_code=400, detail="Cédula ya existe")
    
    new_user = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "email": req.email,
        "cedula": req.cedula,
        "password_hash": hash_password(req.password),
        "role": req.role,
        "program_id": req.program_id,
        "phone": req.phone,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(new_user)
    del new_user["_id"]
    del new_user["password_hash"]
    return new_user

@api_router.put("/users/{user_id}")
async def update_user(user_id: str, req: UserUpdate, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede editar usuarios")
    
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    result = await db.users.update_one({"id": user_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    updated = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    return updated

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede eliminar usuarios")
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario eliminado"}

# --- Programs Routes ---
@api_router.get("/programs")
async def get_programs():
    programs = await db.programs.find({}, {"_id": 0}).to_list(100)
    return programs

@api_router.post("/programs")
async def create_program(req: ProgramCreate, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede crear programas")
    program = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "description": req.description,
        "duration": req.duration,
        "modules": req.modules,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.programs.insert_one(program)
    del program["_id"]
    return program

@api_router.put("/programs/{program_id}")
async def update_program(program_id: str, req: ProgramUpdate, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    result = await db.programs.update_one({"id": program_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Programa no encontrado")
    updated = await db.programs.find_one({"id": program_id}, {"_id": 0})
    return updated

@api_router.delete("/programs/{program_id}")
async def delete_program(program_id: str, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")
    await db.programs.delete_one({"id": program_id})
    return {"message": "Programa eliminado"}

# --- Subjects Routes ---
@api_router.get("/subjects")
async def get_subjects(program_id: Optional[str] = None):
    query = {}
    if program_id:
        query["program_id"] = program_id
    subjects = await db.subjects.find(query, {"_id": 0}).to_list(500)
    return subjects

@api_router.post("/subjects")
async def create_subject(req: SubjectCreate, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")
    subject = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "program_id": req.program_id,
        "module_number": req.module_number,
        "description": req.description,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.subjects.insert_one(subject)
    del subject["_id"]
    return subject

@api_router.put("/subjects/{subject_id}")
async def update_subject(subject_id: str, req: SubjectUpdate, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    result = await db.subjects.update_one({"id": subject_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    updated = await db.subjects.find_one({"id": subject_id}, {"_id": 0})
    return updated

@api_router.delete("/subjects/{subject_id}")
async def delete_subject(subject_id: str, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")
    await db.subjects.delete_one({"id": subject_id})
    return {"message": "Materia eliminada"}

# --- Courses Routes ---
@api_router.get("/courses")
async def get_courses(teacher_id: Optional[str] = None, student_id: Optional[str] = None, user=Depends(get_current_user)):
    query = {}
    if teacher_id:
        query["teacher_id"] = teacher_id
    if student_id:
        query["student_ids"] = student_id
    courses = await db.courses.find(query, {"_id": 0}).to_list(500)
    return courses

@api_router.get("/courses/{course_id}")
async def get_course(course_id: str, user=Depends(get_current_user)):
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return course

@api_router.post("/courses")
async def create_course(req: CourseCreate, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")
    course = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "program_id": req.program_id,
        "subject_id": req.subject_id,
        "teacher_id": req.teacher_id,
        "year": req.year,
        "student_ids": req.student_ids,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.courses.insert_one(course)
    del course["_id"]
    return course

@api_router.put("/courses/{course_id}")
async def update_course(course_id: str, req: CourseUpdate, user=Depends(get_current_user)):
    if user["role"] not in ["admin", "profesor"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    result = await db.courses.update_one({"id": course_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    updated = await db.courses.find_one({"id": course_id}, {"_id": 0})
    return updated

@api_router.delete("/courses/{course_id}")
async def delete_course(course_id: str, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")
    await db.courses.delete_one({"id": course_id})
    return {"message": "Curso eliminado"}

# --- Activities Routes ---
@api_router.get("/activities")
async def get_activities(course_id: Optional[str] = None, user=Depends(get_current_user)):
    query = {}
    if course_id:
        query["course_id"] = course_id
    activities = await db.activities.find(query, {"_id": 0}).to_list(500)
    return activities

@api_router.post("/activities")
async def create_activity(req: ActivityCreate, user=Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")
    # Auto-number: count existing activities for this course
    count = await db.activities.count_documents({"course_id": req.course_id})
    activity_number = count + 1
    activity = {
        "id": str(uuid.uuid4()),
        "course_id": req.course_id,
        "activity_number": activity_number,
        "title": req.title,
        "description": req.description,
        "start_date": req.start_date,
        "due_date": req.due_date,
        "files": req.files,
        "active": True,
        "created_by": user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.activities.insert_one(activity)
    del activity["_id"]
    return activity

@api_router.put("/activities/{activity_id}")
async def update_activity(activity_id: str, req: ActivityUpdate, user=Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    result = await db.activities.update_one({"id": activity_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    updated = await db.activities.find_one({"id": activity_id}, {"_id": 0})
    return updated

@api_router.delete("/activities/{activity_id}")
async def delete_activity(activity_id: str, user=Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")
    await db.activities.delete_one({"id": activity_id})
    return {"message": "Actividad eliminada"}

# --- Grades Routes ---
@api_router.get("/grades")
async def get_grades(course_id: Optional[str] = None, student_id: Optional[str] = None, user=Depends(get_current_user)):
    query = {}
    if course_id:
        query["course_id"] = course_id
    if student_id:
        query["student_id"] = student_id
    grades = await db.grades.find(query, {"_id": 0}).to_list(5000)
    return grades

@api_router.post("/grades")
async def create_grade(req: GradeCreate, user=Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")
    
    existing = await db.grades.find_one({
        "student_id": req.student_id,
        "course_id": req.course_id,
        "activity_id": req.activity_id
    })
    
    if existing:
        await db.grades.update_one(
            {"id": existing["id"]},
            {"$set": {"value": req.value, "comments": req.comments, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        updated = await db.grades.find_one({"id": existing["id"]}, {"_id": 0})
        return updated
    
    grade = {
        "id": str(uuid.uuid4()),
        "student_id": req.student_id,
        "course_id": req.course_id,
        "activity_id": req.activity_id,
        "value": req.value,
        "comments": req.comments,
        "graded_by": user["id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.grades.insert_one(grade)
    del grade["_id"]
    return grade

@api_router.put("/grades/{grade_id}")
async def update_grade(grade_id: str, req: GradeUpdate, user=Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.grades.update_one({"id": grade_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    updated = await db.grades.find_one({"id": grade_id}, {"_id": 0})
    return updated

# --- Class Videos Routes ---
@api_router.get("/class-videos")
async def get_class_videos(course_id: Optional[str] = None, user=Depends(get_current_user)):
    query = {}
    if course_id:
        query["course_id"] = course_id
    videos = await db.class_videos.find(query, {"_id": 0}).to_list(500)
    return videos

@api_router.post("/class-videos")
async def create_class_video(req: ClassVideoCreate, user=Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")
    video = {
        "id": str(uuid.uuid4()),
        "course_id": req.course_id,
        "title": req.title,
        "url": req.url,
        "description": req.description,
        "created_by": user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.class_videos.insert_one(video)
    del video["_id"]
    return video

@api_router.delete("/class-videos/{video_id}")
async def delete_class_video(video_id: str, user=Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")
    await db.class_videos.delete_one({"id": video_id})
    return {"message": "Video eliminado"}

class ClassVideoUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None

@api_router.put("/class-videos/{video_id}")
async def update_class_video(video_id: str, req: ClassVideoUpdate, user=Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    result = await db.class_videos.update_one({"id": video_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    updated = await db.class_videos.find_one({"id": video_id}, {"_id": 0})
    return updated

# --- File Upload Route ---
@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    if user["role"] not in ["profesor", "admin", "estudiante"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    file_id = str(uuid.uuid4())
    ext = Path(file.filename).suffix
    safe_name = f"{file_id}{ext}"
    file_path = UPLOAD_DIR / safe_name
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    return {
        "filename": file.filename,
        "stored_name": safe_name,
        "url": f"/api/files/{safe_name}",
        "size": os.path.getsize(file_path)
    }

@api_router.get("/files/{filename}")
async def get_file(filename: str):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    from starlette.responses import FileResponse
    return FileResponse(file_path)

# --- Submissions Routes ---
@api_router.get("/submissions")
async def get_submissions(activity_id: Optional[str] = None, student_id: Optional[str] = None, user=Depends(get_current_user)):
    query = {}
    if activity_id:
        query["activity_id"] = activity_id
    if student_id:
        query["student_id"] = student_id
    submissions = await db.submissions.find(query, {"_id": 0}).to_list(5000)
    return submissions

@api_router.post("/submissions")
async def create_submission(req: SubmissionCreate, user=Depends(get_current_user)):
    if user["role"] != "estudiante":
        raise HTTPException(status_code=403, detail="Solo estudiantes")
    
    activity = await db.activities.find_one({"id": req.activity_id}, {"_id": 0})
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    
    now = datetime.now(timezone.utc)
    
    # Check start_date
    if activity.get("start_date"):
        start_date = datetime.fromisoformat(activity["start_date"].replace("Z", "+00:00"))
        if now < start_date:
            raise HTTPException(status_code=400, detail="La actividad aún no está disponible.")
    
    due_date = datetime.fromisoformat(activity["due_date"].replace("Z", "+00:00"))
    if now > due_date:
        raise HTTPException(status_code=400, detail="La fecha límite ha pasado. No se puede entregar.")
    
    existing = await db.submissions.find_one({
        "activity_id": req.activity_id,
        "student_id": user["id"]
    })
    if existing:
        await db.submissions.update_one(
            {"id": existing["id"]},
            {"$set": {"content": req.content, "files": req.files, "submitted_at": datetime.now(timezone.utc).isoformat()}}
        )
        updated = await db.submissions.find_one({"id": existing["id"]}, {"_id": 0})
        return updated
    
    submission = {
        "id": str(uuid.uuid4()),
        "activity_id": req.activity_id,
        "student_id": user["id"],
        "content": req.content,
        "files": req.files,
        "submitted_at": datetime.now(timezone.utc).isoformat()
    }
    await db.submissions.insert_one(submission)
    del submission["_id"]
    return submission

# --- Seed Data Route ---
@api_router.post("/seed")
async def seed_data():
    # Check if already seeded
    existing_admin = await db.users.find_one({"email": "admin@educando.com"})
    if existing_admin:
        return {"message": "Base de datos ya tiene datos iniciales"}
    
    # Create Programs
    programs = [
        {
            "id": "prog-admin",
            "name": "Técnico en Asistencia Administrativa",
            "description": "Formación técnica en gestión administrativa, contabilidad, ofimática y gestión documental.",
            "duration": "12 meses (2 módulos de 6 meses)",
            "modules": [
                {"number": 1, "name": "Módulo 1 - Teórico Práctico", "subjects": [
                    "Fundamentos de Administración", "Herramientas Ofimáticas",
                    "Gestión Documental y Archivo", "Atención al Cliente y Comunicación Organizacional",
                    "Legislación Laboral y Ética Profesional"
                ]},
                {"number": 2, "name": "Módulo 2 - Teórico Práctico", "subjects": [
                    "Contabilidad Básica", "Nómina y Seguridad Social Aplicada",
                    "Control de Inventarios y Logística", "Inglés Técnico / Competencias Ciudadanas",
                    "Proyecto Integrador Virtual"
                ]}
            ],
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "prog-infancia",
            "name": "Técnico Laboral en Atención a la Primera Infancia",
            "description": "Formación para el cuidado y educación de niños en primera infancia.",
            "duration": "12 meses (2 módulos de 6 meses)",
            "modules": [
                {"number": 1, "name": "Módulo 1", "subjects": [
                    "Inglés I", "Proyecto de vida", "Construcción social de la infancia",
                    "Perspectiva del desarrollo infantil", "Salud y nutrición",
                    "Lenguaje y educación infantil", "Juego y otras formas de comunicación",
                    "Educación y pedagogía"
                ]},
                {"number": 2, "name": "Módulo 2", "subjects": [
                    "Inglés II", "Construcción del mundo Matemático",
                    "Dificultades en el aprendizaje", "Estrategias del aula",
                    "Trabajo de grado - Investigación", "Práctica - Informe"
                ]}
            ],
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "prog-sst",
            "name": "Técnico en Seguridad y Salud en el Trabajo",
            "description": "Formación en prevención de riesgos laborales, medicina preventiva y gestión ambiental.",
            "duration": "12 meses (2 módulos)",
            "modules": [
                {"number": 1, "name": "Módulo 1", "subjects": [
                    "Fundamentos en Seguridad y Salud en el Trabajo",
                    "Administración en salud", "Condiciones de seguridad",
                    "Matemáticas", "Psicología del Trabajo"
                ]},
                {"number": 2, "name": "Módulo 2", "subjects": [
                    "Comunicación oral y escrita", "Sistema de gestión de SST",
                    "Anatomía y fisiología", "Medicina preventiva del trabajo",
                    "Ética profesional", "Gestión ambiental", "Proyecto de grado"
                ]}
            ],
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.programs.insert_many(programs)
    
    # Create Subjects
    subjects = []
    for prog in programs:
        for module in prog["modules"]:
            for subj_name in module["subjects"]:
                subjects.append({
                    "id": str(uuid.uuid4()),
                    "name": subj_name,
                    "program_id": prog["id"],
                    "module_number": module["number"],
                    "description": "",
                    "active": True,
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
    await db.subjects.insert_many(subjects)
    
    # Create Users
    admin_id = "user-admin"
    teacher1_id = "user-teacher1"
    teacher2_id = "user-teacher2"
    student1_id = "user-student1"
    student2_id = "user-student2"
    student3_id = "user-student3"
    
    users = [
        {
            "id": admin_id,
            "name": "Administrador General",
            "email": "admin@educando.com",
            "cedula": None,
            "password_hash": hash_password("admin123"),
            "role": "admin",
            "program_id": None,
            "phone": "3001234567",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": teacher1_id,
            "name": "María García López",
            "email": "profesor@educando.com",
            "cedula": None,
            "password_hash": hash_password("profesor123"),
            "role": "profesor",
            "program_id": None,
            "phone": "3007654321",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": teacher2_id,
            "name": "Carlos Rodríguez Pérez",
            "email": "profesor2@educando.com",
            "cedula": None,
            "password_hash": hash_password("profesor123"),
            "role": "profesor",
            "program_id": None,
            "phone": "3009876543",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": student1_id,
            "name": "Juan Martínez Ruiz",
            "email": None,
            "cedula": "1234567890",
            "password_hash": hash_password("estudiante123"),
            "role": "estudiante",
            "program_id": "prog-admin",
            "phone": "3101234567",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": student2_id,
            "name": "Ana Sofía Hernández",
            "email": None,
            "cedula": "0987654321",
            "password_hash": hash_password("estudiante123"),
            "role": "estudiante",
            "program_id": "prog-infancia",
            "phone": "3207654321",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": student3_id,
            "name": "Pedro López Castro",
            "email": None,
            "cedula": "1122334455",
            "password_hash": hash_password("estudiante123"),
            "role": "estudiante",
            "program_id": "prog-sst",
            "phone": "3159876543",
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    await db.users.insert_many(users)
    
    # Create sample subjects references for courses
    admin_subj = await db.subjects.find_one({"program_id": "prog-admin", "name": "Fundamentos de Administración"}, {"_id": 0})
    infancia_subj = await db.subjects.find_one({"program_id": "prog-infancia", "name": "Educación y pedagogía"}, {"_id": 0})
    sst_subj = await db.subjects.find_one({"program_id": "prog-sst", "name": "Fundamentos en Seguridad y Salud en el Trabajo"}, {"_id": 0})
    
    # Create Courses
    course1_id = "course-1"
    course2_id = "course-2"
    course3_id = "course-3"
    
    courses = [
        {
            "id": course1_id,
            "name": "Fundamentos de Administración - Grupo A 2025",
            "program_id": "prog-admin",
            "subject_id": admin_subj["id"] if admin_subj else "",
            "teacher_id": teacher1_id,
            "year": 2025,
            "student_ids": [student1_id],
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": course2_id,
            "name": "Educación y Pedagogía - Grupo A 2025",
            "program_id": "prog-infancia",
            "subject_id": infancia_subj["id"] if infancia_subj else "",
            "teacher_id": teacher1_id,
            "year": 2025,
            "student_ids": [student2_id],
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": course3_id,
            "name": "Fundamentos SST - Grupo A 2025",
            "program_id": "prog-sst",
            "subject_id": sst_subj["id"] if sst_subj else "",
            "teacher_id": teacher2_id,
            "year": 2025,
            "student_ids": [student3_id],
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    await db.courses.insert_many(courses)
    
    # Create sample Activities
    activities = [
        {
            "id": "act-1",
            "course_id": course1_id,
            "activity_number": 1,
            "title": "Ensayo sobre principios administrativos",
            "description": "Elaborar un ensayo de 2 páginas sobre los principios fundamentales de la administración según Henri Fayol.",
            "start_date": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
            "due_date": (datetime.now(timezone.utc) + timedelta(days=14)).isoformat(),
            "files": [],
            "active": True,
            "created_by": teacher1_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "act-2",
            "course_id": course1_id,
            "activity_number": 2,
            "title": "Taller de organización empresarial",
            "description": "Realizar el taller práctico sobre estructura organizacional. Descargar el archivo adjunto.",
            "start_date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "due_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "files": [{"name": "taller_organizacion.pdf", "url": "#"}],
            "active": True,
            "created_by": teacher1_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "act-3",
            "course_id": course2_id,
            "activity_number": 1,
            "title": "Observación pedagógica",
            "description": "Realizar una observación de clase virtual y presentar un informe de 3 páginas.",
            "start_date": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
            "due_date": (datetime.now(timezone.utc) + timedelta(days=21)).isoformat(),
            "files": [],
            "active": True,
            "created_by": teacher1_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    await db.activities.insert_many(activities)
    
    # Create sample grades
    grades = [
        {
            "id": "grade-1",
            "student_id": student1_id,
            "course_id": course1_id,
            "activity_id": "act-1",
            "value": 4.2,
            "comments": "Buen trabajo, falta profundizar en algunos conceptos.",
            "graded_by": teacher1_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    await db.grades.insert_many(grades)
    
    # Create sample class videos
    videos = [
        {
            "id": "video-1",
            "course_id": course1_id,
            "title": "Clase 1: Introducción a la Administración",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "description": "Primera clase del módulo. Conceptos básicos de administración.",
            "created_by": teacher1_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "video-2",
            "course_id": course1_id,
            "title": "Clase 2: Principios de Fayol",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "description": "Los 14 principios de la administración de Henri Fayol.",
            "created_by": teacher1_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    await db.class_videos.insert_many(videos)
    
    return {
        "message": "Datos iniciales creados exitosamente",
        "credentials": {
            "admin": {"email": "admin@educando.com", "password": "admin123"},
            "profesor": {"email": "profesor@educando.com", "password": "profesor123"},
            "profesor2": {"email": "profesor2@educando.com", "password": "profesor123"},
            "estudiante1": {"cedula": "1234567890", "password": "estudiante123"},
            "estudiante2": {"cedula": "0987654321", "password": "estudiante123"},
            "estudiante3": {"cedula": "1122334455", "password": "estudiante123"}
        }
    }

# --- Stats Route ---
@api_router.get("/stats")
async def get_stats(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin")
    
    students = await db.users.count_documents({"role": "estudiante", "active": True})
    teachers = await db.users.count_documents({"role": "profesor", "active": True})
    programs = await db.programs.count_documents({"active": True})
    courses = await db.courses.count_documents({"active": True})
    activities = await db.activities.count_documents({"active": True})
    
    return {
        "students": students,
        "teachers": teachers,
        "programs": programs,
        "courses": courses,
        "activities": activities
    }

@api_router.get("/")
async def root():
    return {"message": "Corporación Social Educando API"}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
