from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc, escape_regex
from models import GuestCreate

router = APIRouter(tags=["guests"])


@router.get("/guests")
async def list_guests(search: Optional[str] = None, limit: int = 50, skip: int = 0):
    query = {}
    if search:
        safe_search = escape_regex(search)
        query["$or"] = [
            {"name": {"$regex": safe_search, "$options": "i"}},
            {"email": {"$regex": safe_search, "$options": "i"}},
            {"phone": {"$regex": safe_search, "$options": "i"}},
        ]
    guests = await db.guests.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.guests.count_documents(query)
    return {"guests": guests, "total": total}


@router.post("/guests")
async def create_guest(data: GuestCreate):
    guest = {
        "id": new_id(),
        **data.model_dump(),
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "total_stays": 0,
        "vip": False,
    }
    await db.guests.insert_one(guest)
    return clean_doc(guest)


@router.get("/guests/{guest_id}")
async def get_guest(guest_id: str):
    guest = await db.guests.find_one({"id": guest_id}, {"_id": 0})
    if not guest:
        raise HTTPException(404, "Misafir bulunamadi")
    return guest


@router.patch("/guests/{guest_id}")
async def update_guest(guest_id: str, data: dict):
    data["updated_at"] = utcnow()
    result = await db.guests.update_one({"id": guest_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(404, "Misafir bulunamadi")
    return {"success": True}
