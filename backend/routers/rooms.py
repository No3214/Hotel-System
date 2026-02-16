from fastapi import APIRouter, HTTPException
from database import db
from helpers import utcnow
from hotel_data import ROOMS
from services.cache_service import cache_get, cache_set, cache_invalidate

router = APIRouter(tags=["rooms"])


@router.get("/rooms")
async def list_rooms():
    cached = cache_get("rooms:list", "medium")
    if cached is not None:
        return cached
    db_rooms = await db.rooms.find({}, {"_id": 0}).to_list(100)
    result = {"rooms": db_rooms} if db_rooms else {"rooms": ROOMS}
    cache_set("rooms:list", result, "medium")
    return result


@router.get("/rooms/{room_id}")
async def get_room(room_id: str):
    room = await db.rooms.find_one({"room_id": room_id}, {"_id": 0})
    if not room:
        for r in ROOMS:
            if r["room_id"] == room_id:
                return r
        raise HTTPException(404, "Oda bulunamadi")
    return room
