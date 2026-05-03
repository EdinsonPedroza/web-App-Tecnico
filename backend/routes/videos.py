import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from database import db
from utils.security import get_current_user, safe_object_id
from models.schemas import ClassVideoCreate, ClassVideoUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


async def _verify_video_course_ownership(video_id: str, user: dict):
    """Raise HTTP 403/404 if professor is not assigned to the video's course.
    Mirrors the same ownership pattern used in activities and grades."""
    video = await db.class_videos.find_one({"id": video_id}, {"_id": 0})
    if not video:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    course = await db.courses.find_one({"id": video.get("course_id")}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    teacher_ids = list(course.get("teacher_ids") or [])
    if course.get("teacher_id"):
        teacher_ids.append(course["teacher_id"])
    if user["id"] not in teacher_ids:
        user_subject_ids = set(user.get("subject_ids") or [])
        course_subject_ids = set(course.get("subject_ids") or [])
        if not user_subject_ids.intersection(course_subject_ids):
            raise HTTPException(status_code=403, detail="No tienes permiso para modificar videos de este curso")
    return video


@router.get("/class-videos")
async def get_class_videos(course_id: Optional[str] = None, subject_id: Optional[str] = None, skip: int = 0, limit: int = 100, user=Depends(get_current_user)):
    query = {}
    if course_id:
        query["course_id"] = safe_object_id(course_id, "course_id")
    if subject_id:
        query["subject_id"] = safe_object_id(subject_id, "subject_id")
    if user["role"] == "estudiante":
        now_iso = datetime.now(timezone.utc).isoformat()
        query["$or"] = [
            {"available_from": {"$exists": False}},
            {"available_from": None},
            {"available_from": ""},
            {"available_from": {"$lte": now_iso}}
        ]
    total_count = await db.class_videos.count_documents(query)
    limit = max(1, min(limit, 500))
    skip = max(0, skip)
    videos = await db.class_videos.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    response = JSONResponse(content=videos)
    response.headers["X-Total-Count"] = str(total_count)
    response.headers["X-Has-More"] = str((skip + limit) < total_count).lower()
    return response


@router.post("/class-videos")
async def create_class_video(req: ClassVideoCreate, user=Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")
    course = await db.courses.find_one({"id": req.course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    teacher_ids = list(course.get("teacher_ids") or [])
    if course.get("teacher_id"):
        teacher_ids.append(course["teacher_id"])
    if user["id"] not in teacher_ids:
        user_subject_ids = set(user.get("subject_ids") or [])
        course_subject_ids = set(course.get("subject_ids") or [])
        if not user_subject_ids.intersection(course_subject_ids):
            raise HTTPException(status_code=403, detail="No tienes permiso para crear videos en este curso")

    # Multi-group: publish to multiple courses at once
    target_course_ids = list(dict.fromkeys(req.course_ids)) if req.course_ids else [req.course_id]
    if req.course_id not in target_course_ids:
        target_course_ids.insert(0, req.course_id)

    group_id = str(uuid.uuid4()) if len(target_course_ids) > 1 else None
    now_iso = datetime.now(timezone.utc).isoformat()
    created_videos = []

    for cid in target_course_ids:
        video = {
            "id": str(uuid.uuid4()),
            "course_id": cid,
            "subject_id": req.subject_id,
            "title": req.title,
            "url": req.url,
            "description": req.description,
            "available_from": req.available_from or None,
            "created_by": user["id"],
            "created_at": now_iso,
        }
        if group_id:
            video["video_group_id"] = group_id
        await db.class_videos.insert_one(video)
        del video["_id"]
        created_videos.append(video)

    if len(created_videos) == 1:
        return created_videos[0]
    return {
        "video_group_id": group_id,
        "course_count": len(created_videos),
        "videos": created_videos,
    }


@router.delete("/class-videos/group/{group_id}")
async def delete_class_video_group(group_id: str, user=Depends(get_current_user)):
    """Delete all videos that share the same video_group_id."""
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")
    videos_in_group = await db.class_videos.find(
        {"video_group_id": group_id}, {"_id": 0, "id": 1}
    ).to_list(500)
    if not videos_in_group:
        raise HTTPException(status_code=404, detail="Grupo de videos no encontrado")
    await db.class_videos.delete_many({"video_group_id": group_id})
    return {"message": f"Grupo eliminado: {len(videos_in_group)} videos"}


@router.delete("/class-videos/{video_id}")
async def delete_class_video(video_id: str, user=Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")
    await _verify_video_course_ownership(video_id, user)
    await db.class_videos.delete_one({"id": video_id})
    return {"message": "Video eliminado"}


@router.put("/class-videos/{video_id}")
async def update_class_video(video_id: str, req: ClassVideoUpdate, user=Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")
    await _verify_video_course_ownership(video_id, user)
    raw = req.model_dump()
    update_data = {k: v for k, v in raw.items() if v is not None}
    if raw.get("available_from") in ("", None) and "available_from" in raw:
        update_data["available_from"] = None
    result = await db.class_videos.update_one({"id": video_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    updated = await db.class_videos.find_one({"id": video_id}, {"_id": 0})
    return updated
