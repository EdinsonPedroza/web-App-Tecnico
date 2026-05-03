import asyncio
import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from database import db
from utils.security import get_current_user, safe_object_id
from utils.audit import log_audit, log_security_event
from models.schemas import ActivityCreate, ActivityUpdate
from config import MAX_LIMIT, MAX_ACTIVITIES_PER_WEEK_PER_SUBJECT

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/activities")
async def get_activities(course_id: Optional[str] = None, subject_id: Optional[str] = None, skip: int = 0, limit: int = 500, user=Depends(get_current_user)):
    query = {}
    if course_id:
        query["course_id"] = safe_object_id(course_id, "course_id")
    if subject_id:
        query["subject_id"] = safe_object_id(subject_id, "subject_id")
    # Students only see activities whose start_date has already passed
    if user["role"] == "estudiante":
        now_iso = datetime.now(timezone.utc).isoformat()
        query["$or"] = [
            {"start_date": {"$exists": False}},
            {"start_date": None},
            {"start_date": ""},
            {"start_date": {"$lte": now_iso}},
        ]
    limit = max(1, min(limit, MAX_LIMIT))
    skip = max(0, skip)
    total_count, activities = await asyncio.gather(
        db.activities.count_documents(query),
        db.activities.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    )

    if user["role"] == "estudiante" and course_id:
        approved_records = await db.failed_subjects.find({
            "student_id": user["id"],
            "course_id": course_id,
            "recovery_approved": True,
            "recovery_processed": {"$ne": True},
            "recovery_rejected": {"$ne": True},
        }, {"_id": 0, "subject_id": 1}).to_list(100)
        approved_subject_ids = {r.get("subject_id") for r in approved_records if r.get("subject_id")}
        has_course_level_approval = any(not r.get("subject_id") for r in approved_records)

        filtered_activities = []
        for a in activities:
            if not a.get("is_recovery"):
                filtered_activities.append(a)
                continue
            act_sid = a.get("subject_id")
            if (act_sid and act_sid in approved_subject_ids) or (not act_sid and has_course_level_approval):
                filtered_activities.append(a)
        activities = filtered_activities

    response = JSONResponse(content=activities)
    response.headers["X-Total-Count"] = str(total_count)
    response.headers["X-Has-More"] = str((skip + limit) < total_count).lower()
    return response


@router.post("/activities")
async def create_activity(req: ActivityCreate, user=Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")
    course = await db.courses.find_one({"id": req.course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    teacher_ids_list = list(course.get("teacher_ids") or [])
    if course.get("teacher_id"):
        teacher_ids_list.append(course["teacher_id"])
    if user["id"] not in teacher_ids_list:
        user_subject_ids = set(user.get("subject_ids") or [])
        course_subject_ids = set(course.get("subject_ids") or [])
        if not user_subject_ids.intersection(course_subject_ids):
            log_security_event("UNAUTHORIZED_ACTIVITY_CREATE", {
                "professor_id": user["id"],
                "course_id": req.course_id,
            })
            raise HTTPException(status_code=403, detail="No tienes permiso para crear actividades en este curso")
    # Validate start_date < due_date when both are present
    if req.start_date and req.due_date:
        try:
            _start = datetime.fromisoformat(req.start_date.replace("Z", "+00:00"))
            _due = datetime.fromisoformat(req.due_date.replace("Z", "+00:00"))
            if _start >= _due:
                raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de entrega")
        except ValueError:
            pass  # Invalid date format handled elsewhere

    if req.is_recovery:
        recovery_query = {"course_id": req.course_id, "is_recovery": True}
        if req.subject_id:
            recovery_query["subject_id"] = req.subject_id
        existing_recovery = await db.activities.find_one(recovery_query)
        if existing_recovery:
            raise HTTPException(
                status_code=400,
                detail="Ya existe una actividad de recuperación para esta materia. Solo se permite una por materia."
            )
    # Validate max activities per week per subject (3 entregas semanales por materia)
    if not req.is_recovery and req.subject_id and req.due_date:
        try:
            due = datetime.fromisoformat(req.due_date.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            due = None
        if due:
            # Normalize to UTC date for consistent week boundary calculation
            due_date_only = due.astimezone(timezone.utc).date()
            week_start_date = due_date_only - timedelta(days=due_date_only.weekday())
            week_end_date = week_start_date + timedelta(days=7)
            week_start_str = f"{week_start_date.isoformat()}T00:00:00"
            week_end_str = f"{week_end_date.isoformat()}T00:00:00"
            # Count existing non-recovery activities in the same week for this course+subject
            week_count = await db.activities.count_documents({
                "course_id": req.course_id,
                "subject_id": req.subject_id,
                "is_recovery": {"$ne": True},
                "due_date": {
                    "$gte": week_start_str,
                    "$lt": week_end_str
                }
            })
            if week_count >= MAX_ACTIVITIES_PER_WEEK_PER_SUBJECT:
                raise HTTPException(
                    status_code=400,
                    detail=f"Se ha alcanzado el máximo de {MAX_ACTIVITIES_PER_WEEK_PER_SUBJECT} entregas por semana para esta materia. Elija otra fecha."
                )
    # Determine target courses: use course_ids if provided (multi-group), else single course_id
    target_course_ids = list(dict.fromkeys(req.course_ids)) if req.course_ids else [req.course_id]
    if req.course_id not in target_course_ids:
        target_course_ids.insert(0, req.course_id)

    group_id = str(uuid.uuid4()) if len(target_course_ids) > 1 else None
    now_iso = datetime.now(timezone.utc).isoformat()
    created_activities = []

    for cid in target_course_ids:
        act_num_agg = await db.activities.aggregate([
            {"$match": {"course_id": cid, **({"subject_id": req.subject_id} if req.subject_id else {})}},
            {"$group": {"_id": None, "max_num": {"$max": "$activity_number"}}}
        ]).to_list(1)
        activity_number = ((act_num_agg[0]["max_num"] if act_num_agg else 0) or 0) + 1
        activity = {
            "id": str(uuid.uuid4()),
            "course_id": cid,
            "subject_id": req.subject_id,
            "activity_number": activity_number,
            "title": req.title,
            "description": req.description,
            "start_date": req.start_date,
            "due_date": req.due_date,
            "files": req.files,
            "is_recovery": req.is_recovery or False,
            "active": True,
            "created_by": user["id"],
            "created_at": now_iso,
        }
        if group_id:
            activity["activity_group_id"] = group_id
        await db.activities.insert_one(activity)
        del activity["_id"]
        created_activities.append(activity)

    await log_audit("activity_created", user["id"], user["role"], {
        "activity_ids": [a["id"] for a in created_activities],
        "course_ids": target_course_ids,
        "title": req.title,
        "group_id": group_id,
    })
    # Return the activity for the requested course_id (first in list)
    return created_activities[0] if len(created_activities) == 1 else {
        "activity_group_id": group_id,
        "course_count": len(created_activities),
        "activities": created_activities,
    }


@router.put("/activities/group/{group_id}")
async def update_activity_group(group_id: str, req: ActivityUpdate, user=Depends(get_current_user)):
    """Update all activities that share the same activity_group_id."""
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")
    activities_in_group = await db.activities.find(
        {"activity_group_id": group_id}, {"_id": 0, "id": 1, "course_id": 1}
    ).to_list(500)
    if not activities_in_group:
        raise HTTPException(status_code=404, detail="Grupo de actividades no encontrado")
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    # Validate dates on the first activity as a representative
    if update_data:
        sample = await db.activities.find_one({"activity_group_id": group_id}, {"_id": 0})
        if sample:
            merged_start = update_data.get("start_date") or sample.get("start_date")
            merged_due = update_data.get("due_date") or sample.get("due_date")
            if merged_start and merged_due:
                try:
                    if datetime.fromisoformat(merged_start.replace("Z", "+00:00")) >= \
                       datetime.fromisoformat(merged_due.replace("Z", "+00:00")):
                        raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de entrega")
                except ValueError:
                    pass
        await db.activities.update_many({"activity_group_id": group_id}, {"$set": update_data})
    await log_audit("activity_group_updated", user["id"], user["role"], {
        "group_id": group_id, "course_count": len(activities_in_group)
    })
    updated = await db.activities.find({"activity_group_id": group_id}, {"_id": 0}).to_list(500)
    return {"activity_group_id": group_id, "updated": len(updated), "activities": updated}


@router.delete("/activities/group/{group_id}")
async def delete_activity_group(group_id: str, user=Depends(get_current_user)):
    """Delete all activities that share the same activity_group_id."""
    if user["role"] not in ["profesor", "admin"]:
        raise HTTPException(status_code=403, detail="Solo profesores o admin")
    activities_in_group = await db.activities.find(
        {"activity_group_id": group_id}, {"_id": 0, "id": 1}
    ).to_list(500)
    if not activities_in_group:
        raise HTTPException(status_code=404, detail="Grupo de actividades no encontrado")
    activity_ids = [a["id"] for a in activities_in_group]
    await asyncio.gather(
        db.grades.delete_many({"activity_id": {"$in": activity_ids}}),
        db.submissions.delete_many({"activity_id": {"$in": activity_ids}}),
        db.activities.delete_many({"activity_group_id": group_id}),
    )
    await log_audit("activity_group_deleted", user["id"], user["role"], {
        "group_id": group_id, "deleted_count": len(activity_ids)
    })
    return {"message": f"Grupo eliminado: {len(activity_ids)} actividades y sus entregas"}


async def _verify_professor_course_ownership(activity_id: str, user: dict):
    """Raise HTTP 403/404 if the professor is not assigned to the activity's course."""
    activity = await db.activities.find_one({"id": activity_id}, {"_id": 0})
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    course = await db.courses.find_one({"id": activity.get("course_id")}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    teacher_ids = list(course.get("teacher_ids") or [])
    if course.get("teacher_id"):
        teacher_ids.append(course["teacher_id"])
    if user["id"] not in teacher_ids:
        user_subject_ids = set(user.get("subject_ids") or [])
        course_subject_ids = set(course.get("subject_ids") or [])
        if not user_subject_ids.intersection(course_subject_ids):
            raise HTTPException(status_code=403, detail="No tienes permiso para modificar actividades de este curso")
    return activity


@router.put("/activities/{activity_id}")
async def update_activity(activity_id: str, req: ActivityUpdate, user=Depends(get_current_user)):
    if user["role"] != "profesor":
        raise HTTPException(status_code=403, detail="Solo profesores")

    activity = await _verify_professor_course_ownership(activity_id, user)

    update_data = {k: v for k, v in req.model_dump().items() if v is not None}

    # Validate start_date < due_date using the merged result (update may supply only one of them)
    merged_start = update_data.get("start_date") or activity.get("start_date")
    merged_due = update_data.get("due_date") or activity.get("due_date")
    if merged_start and merged_due:
        try:
            if datetime.fromisoformat(merged_start.replace("Z", "+00:00")) >= \
               datetime.fromisoformat(merged_due.replace("Z", "+00:00")):
                raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de entrega")
        except ValueError:
            pass
    result = await db.activities.update_one({"id": activity_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    updated = await db.activities.find_one({"id": activity_id}, {"_id": 0})
    return updated


@router.delete("/activities/{activity_id}")
async def delete_activity(activity_id: str, user=Depends(get_current_user)):
    if user["role"] not in ["profesor", "admin"]:
        raise HTTPException(status_code=403, detail="Solo profesores o admin")

    if user["role"] == "profesor":
        await _verify_professor_course_ownership(activity_id, user)
    else:
        activity = await db.activities.find_one({"id": activity_id}, {"_id": 0})
        if not activity:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")

    await asyncio.gather(
        db.grades.delete_many({"activity_id": activity_id}),
        db.submissions.delete_many({"activity_id": activity_id}),
        db.activities.delete_one({"id": activity_id}),
    )
    await log_audit("activity_deleted", user["id"], user["role"], {"activity_id": activity_id})
    return {"message": "Actividad eliminada con sus notas y entregas"}
