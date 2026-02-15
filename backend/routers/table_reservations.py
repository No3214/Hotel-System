from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from pydantic import BaseModel, Field
from enum import Enum

router = APIRouter(tags=["table_reservations"])


class TableStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SEATED = "seated"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class TableReservationCreate(BaseModel):
    guest_name: str
    phone: str
    date: str
    time: str
    party_size: int = Field(ge=1, le=20)
    notes: Optional[str] = None
    occasion: Optional[str] = None  # birthday, anniversary, business, etc.
    is_hotel_guest: bool = False


# Restoran kapasitesi
RESTAURANT_CONFIG = {
    "name": "Antakya Sofrasi",
    "total_tables": 15,
    "total_capacity": 60,
    "indoor_tables": 8,
    "outdoor_tables": 7,
    "time_slots": ["12:00", "12:30", "13:00", "13:30", "19:00", "19:30", "20:00", "20:30", "21:00"],
    "avg_duration_minutes": 90,
}


@router.get("/table-reservations")
async def list_table_reservations(date: Optional[str] = None, status: Optional[str] = None, limit: int = 50):
    query = {}
    if date:
        query["date"] = date
    if status:
        query["status"] = status
    items = await db.table_reservations.find(query, {"_id": 0}).sort("date", -1).limit(limit).to_list(limit)
    total = await db.table_reservations.count_documents(query)
    return {"reservations": items, "total": total, "config": RESTAURANT_CONFIG}


@router.post("/table-reservations")
async def create_table_reservation(data: TableReservationCreate):
    # Check availability for that slot
    existing = await db.table_reservations.count_documents({
        "date": data.date,
        "time": data.time,
        "status": {"$in": [TableStatus.PENDING, TableStatus.CONFIRMED, TableStatus.SEATED]},
    })
    if existing >= RESTAURANT_CONFIG["total_tables"]:
        raise HTTPException(409, f"{data.date} {data.time} icin musait masa bulunmuyor.")

    reservation = {
        "id": new_id(),
        **data.model_dump(),
        "status": TableStatus.PENDING,
        "table_number": None,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.table_reservations.insert_one(reservation)
    return clean_doc(reservation)


@router.patch("/table-reservations/{res_id}/status")
async def update_table_reservation_status(res_id: str, status: str, table_number: Optional[int] = None):
    update = {"status": status, "updated_at": utcnow()}
    if table_number:
        update["table_number"] = table_number
    if status == TableStatus.SEATED:
        update["seated_at"] = utcnow()
    elif status == TableStatus.COMPLETED:
        update["completed_at"] = utcnow()

    result = await db.table_reservations.update_one({"id": res_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(404, "Masa rezervasyonu bulunamadi")
    return {"success": True}


@router.delete("/table-reservations/{res_id}")
async def delete_table_reservation(res_id: str):
    result = await db.table_reservations.delete_one({"id": res_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Masa rezervasyonu bulunamadi")
    return {"success": True}


@router.get("/table-reservations/availability")
async def check_table_availability(date: str):
    slots = []
    for time_slot in RESTAURANT_CONFIG["time_slots"]:
        booked = await db.table_reservations.count_documents({
            "date": date,
            "time": time_slot,
            "status": {"$in": [TableStatus.PENDING, TableStatus.CONFIRMED, TableStatus.SEATED]},
        })
        available = RESTAURANT_CONFIG["total_tables"] - booked
        slots.append({
            "time": time_slot,
            "booked": booked,
            "available": available,
            "total": RESTAURANT_CONFIG["total_tables"],
            "is_available": available > 0,
        })
    return {"date": date, "slots": slots, "config": RESTAURANT_CONFIG}


@router.get("/table-reservations/stats")
async def table_reservation_stats():
    total = await db.table_reservations.count_documents({})
    today_str = utcnow()[:10]
    today = await db.table_reservations.count_documents({"date": today_str})
    pending = await db.table_reservations.count_documents({"status": TableStatus.PENDING})
    confirmed = await db.table_reservations.count_documents({"status": TableStatus.CONFIRMED})
    return {
        "total": total,
        "today": today,
        "pending": pending,
        "confirmed": confirmed,
    }
