from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from models import EventCreate

router = APIRouter(tags=["events"])


@router.get("/events")
async def list_events(active_only: bool = False):
    query = {"is_active": True} if active_only else {}
    events = await db.events.find(query, {"_id": 0}).sort("event_date", 1).to_list(100)
    return {"events": events}


@router.post("/events")
async def create_event(data: EventCreate):
    event = {
        "id": new_id(),
        **data.model_dump(),
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "registrations": 0,
    }
    await db.events.insert_one(event)
    return clean_doc(event)


@router.patch("/events/{event_id}")
async def update_event(event_id: str, data: dict):
    data["updated_at"] = utcnow()
    result = await db.events.update_one({"id": event_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(404, "Etkinlik bulunamadi")
    return {"success": True}


@router.delete("/events/{event_id}")
async def delete_event(event_id: str):
    result = await db.events.delete_one({"id": event_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Etkinlik bulunamadi")
    return {"success": True}
