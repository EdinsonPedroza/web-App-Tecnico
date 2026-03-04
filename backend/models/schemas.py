import re
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

from utils.helpers import sanitize_string
from config import validate_module_number


class LoginRequest(BaseModel):
    email: Optional[str] = None
    cedula: Optional[str] = None
    password: str = Field(..., min_length=1, max_length=200)
    role: str = Field(..., pattern="^(estudiante|profesor|admin|editor)$")

    @field_validator('email')
    @classmethod
    def sanitize_email(cls, v):
        if v:
            v = v.strip()[:200]
            v = ''.join(char for char in v if char.isprintable())
            if v and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', v):
                raise ValueError("Formato de email inválido")
            return v
        return v

    @field_validator('cedula')
    @classmethod
    def sanitize_cedula(cls, v):
        if v:
            return re.sub(r'\D', '', v)[:50]
        return v


class AdminCreateByEditor(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=6, max_length=200)

    @field_validator('name', 'email')
    @classmethod
    def sanitize_fields(cls, v):
        return sanitize_string(v, 200)


class AdminUpdateByEditor(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[str] = Field(None, min_length=1, max_length=200)
    password: Optional[str] = Field(None, min_length=6, max_length=200)
    active: Optional[bool] = None

    @field_validator('name', 'email')
    @classmethod
    def sanitize_fields(cls, v):
        if v is not None:
            return sanitize_string(v, 200)
        return v


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[str] = Field(None, max_length=200)
    cedula: Optional[str] = Field(None, max_length=50)
    password: str = Field(..., min_length=6, max_length=200)
    role: str = Field(..., pattern="^(estudiante|profesor|admin)$")
    program_id: Optional[str] = None
    program_ids: Optional[List[str]] = None
    course_ids: Optional[List[str]] = None
    subject_ids: Optional[List[str]] = None
    phone: Optional[str] = Field(None, max_length=50)
    module: Optional[int] = Field(None, ge=1)
    program_modules: Optional[dict] = None
    program_statuses: Optional[dict] = None
    estado: Optional[str] = Field(None, pattern="^(activo|egresado|pendiente_recuperacion|retirado)$")

    @field_validator('name', 'email', 'phone')
    @classmethod
    def sanitize_text_fields(cls, v):
        if v:
            return sanitize_string(v, 200)
        return v

    @field_validator('cedula')
    @classmethod
    def sanitize_cedula(cls, v):
        if v:
            cleaned = re.sub(r'\D', '', v)[:50]
            if not cleaned:
                raise ValueError('La cédula debe contener al menos un número')
            return cleaned
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v:
            email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_pattern, v):
                raise ValueError('El correo electrónico debe contener @ y un dominio válido')
        return v

    @field_validator('program_modules')
    @classmethod
    def validate_program_modules(cls, v):
        if v is not None:
            for prog_id, module_num in v.items():
                validate_module_number(module_num, f"Module number for program {prog_id}")
        return v


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=200)
    cedula: Optional[str] = Field(None, max_length=50)
    password: Optional[str] = Field(None, min_length=6, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    program_id: Optional[str] = None
    program_ids: Optional[List[str]] = None
    subject_ids: Optional[List[str]] = None
    active: Optional[bool] = None
    module: Optional[int] = Field(None, ge=1)
    program_modules: Optional[dict] = None
    program_statuses: Optional[dict] = None
    estado: Optional[str] = Field(None, pattern="^(activo|egresado|pendiente_recuperacion|retirado)$")

    @field_validator('name', 'email', 'phone')
    @classmethod
    def sanitize_text_fields(cls, v):
        if v:
            return sanitize_string(v, 200)
        return v

    @field_validator('cedula')
    @classmethod
    def sanitize_cedula(cls, v):
        if v:
            cleaned = re.sub(r'\D', '', v)[:50]
            if not cleaned:
                raise ValueError('La cédula debe contener al menos un número')
            return cleaned
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v:
            email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_pattern, v):
                raise ValueError('El correo electrónico debe contener @ y un dominio válido')
        return v

    @field_validator('program_modules')
    @classmethod
    def validate_program_modules(cls, v):
        if v is not None:
            for prog_id, module_num in v.items():
                validate_module_number(module_num, f"Module number for program {prog_id}")
        return v


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
    module1_close_date: Optional[str] = None
    module2_close_date: Optional[str] = None


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
    subject_id: Optional[str] = None
    subject_ids: Optional[List[str]] = []
    teacher_id: Optional[str] = None
    year: int = datetime.now().year
    student_ids: Optional[List[str]] = []
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grupo: Optional[str] = None
    module_dates: Optional[dict] = {}


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    subject_id: Optional[str] = None
    subject_ids: Optional[List[str]] = None
    teacher_id: Optional[str] = None
    student_ids: Optional[List[str]] = None
    active: Optional[bool] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grupo: Optional[str] = None
    module_dates: Optional[dict] = None


class ActivityCreate(BaseModel):
    course_id: str
    subject_id: Optional[str] = None
    title: str
    description: Optional[str] = ""
    start_date: Optional[str] = None
    due_date: str
    files: Optional[list] = []
    is_recovery: Optional[bool] = False


class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    due_date: Optional[str] = None
    files: Optional[list] = None
    active: Optional[bool] = None
    is_recovery: Optional[bool] = None
    subject_id: Optional[str] = None


class GradeCreate(BaseModel):
    student_id: str
    course_id: str
    activity_id: Optional[str] = None
    subject_id: Optional[str] = None
    value: Optional[float] = Field(None, ge=0.0, le=5.0)
    comments: Optional[str] = ""
    recovery_status: Optional[str] = None


class GradeUpdate(BaseModel):
    value: Optional[float] = Field(None, ge=0.0, le=5.0)
    comments: Optional[str] = None
    recovery_status: Optional[str] = None


class ClassVideoCreate(BaseModel):
    course_id: str
    subject_id: Optional[str] = None
    title: str
    url: str
    description: Optional[str] = ""
    available_from: Optional[str] = None

    @field_validator('url')
    @classmethod
    def validate_youtube_url(cls, v):
        if not v or not v.strip():
            raise ValueError('URL requerida')
        pattern = r'^(https?://)?(www\.)?(youtube\.com/(watch\?.*v=|embed/|shorts/)|youtu\.be/)[\w\-]{11}'
        if not re.search(pattern, v.strip()):
            raise ValueError('La URL debe ser un enlace válido de YouTube')
        return v.strip()


class ClassVideoUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    available_from: Optional[str] = None

    @field_validator('url')
    @classmethod
    def validate_youtube_url(cls, v):
        if v is None:
            return v
        if not v.strip():
            return v
        pattern = r'^(https?://)?(www\.)?(youtube\.com/(watch\?.*v=|embed/|shorts/)|youtu\.be/)[\w\-]{11}'
        if not re.search(pattern, v.strip()):
            raise ValueError('La URL debe ser un enlace válido de YouTube')
        return v.strip()


class SubmissionCreate(BaseModel):
    activity_id: str
    content: Optional[str] = ""
    files: Optional[list] = []


class RecoveryEnableRequest(BaseModel):
    student_id: str
    course_id: str
    subject_id: Optional[str] = None


class ModuleCloseDateUpdate(BaseModel):
    module1_close_date: Optional[str] = None
    module2_close_date: Optional[str] = None
