from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from hotel_data import ROOMS
from services.cache_service import cache_get, cache_set, cache_invalidate

router = APIRouter(tags=["rooms"])


class RoomStatusUpdate(BaseModel):
    status: str  # available, occupied, cleaning, maintenance, blocked
    note: Optional[str] = None


class RoomPriceUpdate(BaseModel):
    base_price: Optional[float] = None
    weekend_price: Optional[float] = None


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


@router.patch("/rooms/{room_id}/status")
async def update_room_status(room_id: str, data: RoomStatusUpdate):
    """Oda durumunu guncelle (musait, dolu, temizlik, bakim, bloke)"""
    valid_statuses = ["available", "occupied", "cleaning", "maintenance", "blocked"]
    if data.status not in valid_statuses:
        raise HTTPException(400, f"Gecersiz durum. Gecerli: {', '.join(valid_statuses)}")

    result = await db.rooms.update_one(
        {"room_id": room_id},
        {"$set": {
            "status": data.status,
            "status_note": data.note or "",
            "status_updated_at": utcnow(),
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Oda bulunamadi")

    # Log status change
    await db.room_status_log.insert_one({
        "id": new_id(),
        "room_id": room_id,
        "status": data.status,
        "note": data.note,
        "created_at": utcnow(),
    })

    cache_invalidate("rooms:list")
    room = await db.rooms.find_one({"room_id": room_id}, {"_id": 0})
    return room


@router.patch("/rooms/{room_id}/price")
async def update_room_price(room_id: str, data: RoomPriceUpdate):
    """Oda fiyatini guncelle"""
    updates = {}
    if data.base_price is not None:
        updates["base_price"] = data.base_price
    if data.weekend_price is not None:
        updates["weekend_price"] = data.weekend_price
    if not updates:
        raise HTTPException(400, "Guncellenecek fiyat bilgisi yok")

    updates["price_updated_at"] = utcnow()
    result = await db.rooms.update_one({"room_id": room_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(404, "Oda bulunamadi")

    cache_invalidate("rooms:list")
    room = await db.rooms.find_one({"room_id": room_id}, {"_id": 0})
    return room


@router.get("/rooms/availability/summary")
async def get_availability_summary():
    """Tum odalarin musaitlik ozeti"""
    rooms = await db.rooms.find({}, {"_id": 0}).to_list(100)
    if not rooms:
        rooms = ROOMS

    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Get today's reservations
    today_reservations = await db.reservations.find({
        "check_in": {"$lte": today},
        "check_out": {"$gt": today},
        "status": {"$in": ["confirmed", "checked_in"]},
    }, {"_id": 0, "room_id": 1, "guest_name": 1, "check_out": 1}).to_list(100)

    occupied_rooms = {r["room_id"]: r for r in today_reservations}

    summary = []
    for room in rooms:
        rid = room.get("room_id")
        reservation = occupied_rooms.get(rid)
        status = room.get("status", "available")
        if reservation and status not in ["maintenance", "blocked"]:
            status = "occupied"

        summary.append({
            "room_id": rid,
            "room_type": room.get("room_type") or room.get("name", ""),
            "status": status,
            "status_note": room.get("status_note", ""),
            "guest_name": reservation.get("guest_name") if reservation else None,
            "check_out": reservation.get("check_out") if reservation else None,
            "base_price": room.get("base_price") or room.get("price", 0),
        })

    status_counts = {}
    for s in summary:
        st = s["status"]
        status_counts[st] = status_counts.get(st, 0) + 1

    return {
        "date": today,
        "total_rooms": len(summary),
        "status_counts": status_counts,
        "rooms": summary,
    }


@router.post("/rooms/{room_id}/bulk-status")
async def bulk_room_status(room_ids: list, data: RoomStatusUpdate):
    """Birden fazla odanin durumunu toplu guncelle"""
    if not room_ids:
        raise HTTPException(400, "Oda ID listesi gerekli")

    result = await db.rooms.update_many(
        {"room_id": {"$in": room_ids}},
        {"$set": {
            "status": data.status,
            "status_note": data.note or "",
            "status_updated_at": utcnow(),
        }}
    )
    cache_invalidate("rooms:list")
    return {"updated": result.modified_count}
