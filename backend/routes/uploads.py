import uuid
import re
import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Request
from starlette.responses import FileResponse

from database import db
from utils.security import get_current_user
from config import (
    USE_CLOUDINARY, USE_S3, UPLOAD_DIR,
    AWS_S3_BUCKET_NAME, AWS_S3_REGION, s3_client,
    MAX_UPLOADS_PER_MINUTE, UPLOAD_WINDOW
)

logger = logging.getLogger(__name__)
router = APIRouter()

_MAGIC_BYTES = {
    b'\x25\x50\x44\x46': 'pdf',
    b'\xff\xd8\xff': 'jpg',
    b'\x89\x50\x4e\x47': 'png',
    b'\x47\x49\x46\x38': 'gif',
    b'\x52\x49\x46\x46': 'webp',
    b'\x50\x4b\x03\x04': 'office',
    b'\xd0\xcf\x11\xe0': 'office_legacy',
}


def _validate_file_content(file_content: bytes, declared_ext: str) -> bool:
    """Validate that file content matches the declared extension."""
    if len(file_content) < 4:
        return False
    header = file_content[:4]
    if declared_ext == 'txt':
        return True
    for magic, file_type in _MAGIC_BYTES.items():
        if header[:len(magic)] == magic:
            if file_type == 'pdf' and declared_ext == 'pdf':
                return True
            elif file_type == 'jpg' and declared_ext in ('jpg', 'jpeg'):
                return True
            elif file_type == 'png' and declared_ext == 'png':
                return True
            elif file_type == 'gif' and declared_ext == 'gif':
                return True
            elif file_type == 'webp' and declared_ext == 'webp':
                return len(file_content) >= 12 and file_content[8:12] == b'WEBP'
            elif file_type == 'office' and declared_ext in ('docx', 'xlsx', 'pptx'):
                return True
            elif file_type == 'office_legacy' and declared_ext in ('doc', 'xls', 'ppt'):
                return True
            return False
    if declared_ext in ('pdf', 'jpg', 'jpeg', 'png', 'gif', 'webp',
                        'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'):
        return False
    return True


_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
_MAX_IMAGE_DIMENSION = 1920
_JPEG_QUALITY = 80


def compress_image(file_content: bytes, filename: str) -> tuple:
    """Compress and optionally resize an image file."""
    from PIL import Image
    import io as _io

    ext = Path(filename).suffix.lower().lstrip(".")
    if ext not in _IMAGE_EXTENSIONS:
        return file_content, filename

    original_size = len(file_content)
    img = Image.open(_io.BytesIO(file_content))
    w, h = img.size
    if w > _MAX_IMAGE_DIMENSION or h > _MAX_IMAGE_DIMENSION:
        img.thumbnail((_MAX_IMAGE_DIMENSION, _MAX_IMAGE_DIMENSION), Image.LANCZOS)

    output = _io.BytesIO()
    stem = Path(filename).stem

    if ext == "png":
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            if img.mode == "P":
                img = img.convert("RGBA")
            img.save(output, format="PNG", optimize=True)
            new_filename = f"{stem}.png"
        else:
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(output, format="JPEG", quality=_JPEG_QUALITY, optimize=True)
            new_filename = f"{stem}.jpg"
    else:
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(output, format="JPEG", quality=_JPEG_QUALITY, optimize=True)
        new_filename = f"{stem}.jpg"

    compressed_bytes = output.getvalue()
    compressed_size = len(compressed_bytes)
    savings = round((1 - compressed_size / original_size) * 100, 1) if original_size else 0
    logger.info(f"Image compressed: {original_size} -> {compressed_size} ({savings}% reduction)")
    return compressed_bytes, new_filename


@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...), user=Depends(get_current_user)):
    if user["role"] not in ["profesor", "admin", "estudiante"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    original_name = file.filename
    MAX_FILE_SIZE = 10 * 1024 * 1024

    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_FILE_SIZE + 1024:
                raise HTTPException(status_code=413, detail="El archivo excede el tamaño máximo permitido (10MB)")
        except ValueError:
            pass

    chunks = []
    total_size = 0
    while True:
        chunk = await file.read(64 * 1024)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="El archivo excede el tamaño máximo permitido (10MB)")
        chunks.append(chunk)
    file_content = b"".join(chunks)
    file_size = total_size

    _ext = Path(original_name).suffix.lower().lstrip(".")

    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "jpg", "jpeg", "png", "gif", "webp"}
    if _ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Tipo de archivo no permitido: .{_ext}")

    if not _validate_file_content(file_content, _ext):
        raise HTTPException(
            status_code=400,
            detail=f"El contenido del archivo no coincide con la extensión .{_ext}"
        )

    _safe_basename = re.sub(r'[^\w\-]', '_', Path(original_name).stem)[:100]

    file_content, original_name = compress_image(file_content, original_name)
    _ext = Path(original_name).suffix.lower().lstrip(".")
    file_size = len(file_content)

    _user_id = user["id"]
    _upload_key = f"upload:{_user_id}"
    _now = datetime.now(timezone.utc)
    _window_start = _now - timedelta(seconds=UPLOAD_WINDOW)
    _upload_count = await db.rate_limits.count_documents({
        "key": _upload_key,
        "timestamp": {"$gte": _window_start}
    })
    if _upload_count >= MAX_UPLOADS_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Demasiadas subidas. Intente de nuevo en un minuto.")
    await db.rate_limits.insert_one({
        "key": _upload_key,
        "timestamp": _now,
        "expires_at": _now + timedelta(seconds=UPLOAD_WINDOW)
    })

    _unique_suffix = str(uuid.uuid4())[:8]

    if USE_S3:
        _content_type_map = {
            "pdf": "application/pdf",
            "doc": "application/msword",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "xls": "application/vnd.ms-excel",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "ppt": "application/vnd.ms-powerpoint",
            "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "txt": "text/plain",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp",
        }
        _content_type = _content_type_map.get(_ext, "application/octet-stream")

        if _ext == "pdf":
            _folder = "uploads/pdf"
        elif _ext in {"jpg", "jpeg", "png", "gif", "webp"}:
            _folder = "uploads/images"
        else:
            _folder = "uploads/docs"

        _s3_key = f"{_folder}/{_safe_basename}_{_unique_suffix}.{_ext}"

        try:
            logger.info(f"Attempting S3 upload: bucket={AWS_S3_BUCKET_NAME}, region={AWS_S3_REGION}, key={_s3_key}")
            s3_client.put_object(
                Bucket=AWS_S3_BUCKET_NAME,
                Key=_s3_key,
                Body=file_content,
                ContentType=_content_type,
                ContentDisposition=f'inline; filename="{original_name}"',
            )
            _file_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_REGION}.amazonaws.com/{_s3_key}"
            logger.info(f"File uploaded to S3: {_file_url}")
            return {
                "filename": original_name,
                "stored_name": _s3_key,
                "url": _file_url,
                "size": file_size,
                "storage": "s3",
                "resource_type": "raw"
            }
        except Exception as e:
            logger.error(f"S3 upload failed for key={_s3_key}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Error al subir el archivo. Intente de nuevo más tarde."
            )

    if USE_CLOUDINARY:
        import cloudinary.uploader
        import io as _io
        if _ext in {"jpg", "jpeg", "png", "gif", "webp", "bmp", "svg"}:
            _resource_type = "image"
        elif _ext in {"mp4", "avi", "mov", "mkv", "webm"}:
            _resource_type = "video"
        else:
            _resource_type = "raw"
        _public_id = f"educando/uploads/{_safe_basename}_{_unique_suffix}.{_ext}"
        result = cloudinary.uploader.upload(
            _io.BytesIO(file_content),
            public_id=_public_id,
            resource_type=_resource_type,
            overwrite=False,
        )
        return {
            "filename": original_name,
            "stored_name": result["public_id"],
            "url": result["secure_url"],
            "size": file_size,
            "storage": "cloudinary",
            "resource_type": _resource_type
        }

    _file_id = str(uuid.uuid4())
    _ext_with_dot = Path(original_name).suffix
    safe_name = f"{_file_id}{_ext_with_dot}"
    file_path = UPLOAD_DIR / safe_name
    with open(file_path, "wb") as f:
        f.write(file_content)
    return {
        "filename": original_name,
        "stored_name": safe_name,
        "url": f"/api/files/{safe_name}",
        "size": os.path.getsize(file_path),
        "storage": "local"
    }


@router.get("/files/{filename}")
async def get_file(filename: str, user=Depends(get_current_user)):
    if any(c in filename for c in ('..', '/', '\\', '\x00')):
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido")
    safe_filename = Path(filename).name
    file_path = UPLOAD_DIR / safe_filename
    try:
        if not file_path.resolve().is_relative_to(UPLOAD_DIR.resolve()):
            raise HTTPException(status_code=400, detail="Nombre de archivo inválido")
    except ValueError:
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    ext = safe_filename.rsplit('.', 1)[-1].lower() if '.' in safe_filename else ''
    mime_map = {
        'pdf': 'application/pdf',
        'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
        'png': 'image/png', 'gif': 'image/gif', 'webp': 'image/webp',
        'txt': 'text/plain',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'ppt': 'application/vnd.ms-powerpoint',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    }
    media_type = mime_map.get(ext, 'application/octet-stream')
    if ext in ('pdf', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'txt'):
        disposition = f'inline; filename="{safe_filename}"'
    else:
        disposition = f'attachment; filename="{safe_filename}"'
    return FileResponse(
        file_path,
        media_type=media_type,
        headers={"Content-Disposition": disposition}
    )
