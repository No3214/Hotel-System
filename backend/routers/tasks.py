from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from models import TaskCreate, TaskUpdate, TaskStatus, TaskPriority

router = APIRouter(tags=["tasks"])

class AITaskRequest(BaseModel):
    text: str


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


@router.post("/tasks/ai-auto-assign")
async def ai_auto_assign_task(data: AITaskRequest):
    """Metin tabanli ariza/talep bildirimlerini yapay zeka ile analiz et ve gorev olustur."""
    from gemini_service import get_chat_response
    import json
    import re

    prompt = f"""
    Sen luks 'Kozbeyli Konagi' otelinin Operasyon Yapay Zekasisin.
    Gelen su ariza/talep bildirimini metnini analiz et: "{data.text}"

    Gorevi uygun departmana (teknik_servis, kat_hizmetleri, resepsiyon, mutfak, guvenlik) ata,
    Onceligini (low, normal, high, urgent) belirle,
    ve kisa bir aciklama ile tahmini onarım suresini yaz.

    Lutfen SADECE asagidaki JSON formatinda sonuc don. (Markdown icinde)
    {{
      "title": "Analiz edilmis kisa baslik (Orn: 201 Nolu Oda Klima Arizasi)",
      "description": "Detayli yorum ve tahmini cozum suresi.",
      "assignee_role": "teknik_servis",
      "priority": "urgent"
    }}
    """
    try:
        ai_response = await get_chat_response("Gorev Ata", new_id(), prompt)
        json_match = re.search(r'```(?:json)?(.*?)```', ai_response, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_response
        parsed_task = json.loads(res_str)

        task = {
            "id": new_id(),
            "title": parsed_task.get("title", data.text[:50]),
            "description": parsed_task.get("description", data.text),
            "assignee_role": parsed_task.get("assignee_role", "general"),
            "priority": parsed_task.get("priority", "normal"),
            "status": TaskStatus.PENDING,
            "source": "ai_auto",
            "created_at": utcnow(),
            "updated_at": utcnow(),
        }
        await db.tasks.insert_one(task)
        return {"success": True, "task": clean_doc(task)}

    except Exception as e:
        return {"error": f"AI Gorev olustururken hata olustu: {str(e)}"}
