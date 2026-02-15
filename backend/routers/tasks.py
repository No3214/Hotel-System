from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from models import TaskCreate, TaskUpdate, TaskStatus

router = APIRouter(tags=["tasks"])


@router.get("/tasks")
async def list_tasks(status: Optional[str] = None, priority: Optional[str] = None, limit: int = 50, skip: int = 0):
    query = {}
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    tasks = await db.tasks.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.tasks.count_documents(query)
    return {"tasks": tasks, "total": total}


@router.post("/tasks")
async def create_task(data: TaskCreate):
    task = {
        "id": new_id(),
        **data.model_dump(),
        "status": TaskStatus.PENDING,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.tasks.insert_one(task)
    return clean_doc(task)


@router.patch("/tasks/{task_id}")
async def update_task(task_id: str, data: TaskUpdate):
    update = {k: v for k, v in data.model_dump().items() if v is not None}
    update["updated_at"] = utcnow()
    if data.status == TaskStatus.COMPLETED:
        update["completed_at"] = utcnow()
    result = await db.tasks.update_one({"id": task_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(404, "Gorev bulunamadi")
    return {"success": True}


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    result = await db.tasks.delete_one({"id": task_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Gorev bulunamadi")
    return {"success": True}
