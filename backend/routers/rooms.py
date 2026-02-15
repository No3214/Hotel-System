from fastapi import APIRouter, HTTPException
from database import db
from helpers import utcnow
from hotel_data import ROOMS

router = APIRouter(tags=["rooms"])


@router.get("/rooms")
async def list_rooms():
    db_rooms = await db.rooms.find({}, {"_id": 0}).to_list(100)
    if not db_rooms:
        return {"rooms": ROOMS}
    return {"rooms": db_rooms}


@router.get("/rooms/{room_id}")
async def get_room(room_id: str):
    room = await db.rooms.find_one({"room_id": room_id}, {"_id": 0})
    if not room:
        for r in ROOMS:
            if r["room_id"] == room_id:
                return r
        raise HTTPException(404, "Oda bulunamadi")
    return room
