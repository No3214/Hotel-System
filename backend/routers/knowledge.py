from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from models import KnowledgeCreate

router = APIRouter(tags=["knowledge"])


@router.get("/knowledge")
async def list_knowledge(category: Optional[str] = None, search: Optional[str] = None, limit: int = 50):
    query = {}
    if category:
        query["category"] = category
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"content": {"$regex": search, "$options": "i"}},
        ]
    items = await db.knowledge.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    total = await db.knowledge.count_documents(query)
    return {"items": items, "total": total}


@router.post("/knowledge")
async def create_knowledge(data: KnowledgeCreate):
    item = {
        "id": new_id(),
        **data.model_dump(),
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.knowledge.insert_one(item)
    return clean_doc(item)


@router.delete("/knowledge/{item_id}")
async def delete_knowledge(item_id: str):
    result = await db.knowledge.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Bilgi bulunamadi")
    return {"success": True}
