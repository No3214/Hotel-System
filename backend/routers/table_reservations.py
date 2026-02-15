from fastapi import APIRouter, HTTPException
from typing import Optional, List
from database import db
from helpers import utcnow, new_id, clean_doc
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, timedelta

router = APIRouter(tags=["table_reservations"])


class TableStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SEATED = "seated"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class MealType(str, Enum):
    BREAKFAST = "breakfast"      # Kahvaltı - 2 saat
    LUNCH = "lunch"              # Öğlen - 2 saat
    DINNER = "dinner"            # Akşam - 4 saat


class TableReservationCreate(BaseModel):
    guest_name: str
    phone: str
    date: str
    time: str
    party_size: int = Field(ge=1, le=12)
    meal_type: MealType
    notes: Optional[str] = None
    occasion: Optional[str] = None  # birthday, anniversary, business, etc.
    is_hotel_guest: bool = False
    preferred_table_id: Optional[str] = None


# Masa tanımları
TABLES = [
    # 2 kişilik masalar (9 adet)
    {"id": "T01", "name": "Masa 1", "capacity": 2, "type": "small", "location": "indoor"},
    {"id": "T02", "name": "Masa 2", "capacity": 2, "type": "small", "location": "indoor"},
    {"id": "T03", "name": "Masa 3", "capacity": 2, "type": "small", "location": "indoor"},
    {"id": "T04", "name": "Masa 4", "capacity": 2, "type": "small", "location": "indoor"},
    {"id": "T05", "name": "Masa 5", "capacity": 2, "type": "small", "location": "indoor"},
    {"id": "T06", "name": "Masa 6", "capacity": 2, "type": "small", "location": "outdoor"},
    {"id": "T07", "name": "Masa 7", "capacity": 2, "type": "small", "location": "outdoor"},
    {"id": "T08", "name": "Masa 8", "capacity": 2, "type": "small", "location": "outdoor"},
    {"id": "T09", "name": "Masa 9", "capacity": 2, "type": "small", "location": "outdoor"},
    # 3 kişilik masalar (4 adet)
    {"id": "T10", "name": "Masa 10", "capacity": 3, "type": "small", "location": "indoor"},
    {"id": "T11", "name": "Masa 11", "capacity": 3, "type": "small", "location": "indoor"},
    {"id": "T12", "name": "Masa 12", "capacity": 3, "type": "small", "location": "outdoor"},
    {"id": "T13", "name": "Masa 13", "capacity": 3, "type": "small", "location": "outdoor"},
    # 4 kişilik masalar (6 adet)
    {"id": "T14", "name": "Masa 14", "capacity": 4, "type": "medium", "location": "indoor"},
    {"id": "T15", "name": "Masa 15", "capacity": 4, "type": "medium", "location": "indoor"},
    {"id": "T16", "name": "Masa 16", "capacity": 4, "type": "medium", "location": "indoor"},
    {"id": "T17", "name": "Masa 17", "capacity": 4, "type": "medium", "location": "outdoor"},
    {"id": "T18", "name": "Masa 18", "capacity": 4, "type": "medium", "location": "outdoor"},
    {"id": "T19", "name": "Masa 19", "capacity": 4, "type": "medium", "location": "outdoor"},
]

# Birleştirilebilir masa grupları (büyük gruplar için)
COMBINABLE_TABLES = [
    {"ids": ["T14", "T15"], "combined_capacity": 8, "name": "Masa 14-15 (Birlesik)", "location": "indoor"},
    {"ids": ["T17", "T18"], "combined_capacity": 8, "name": "Masa 17-18 (Birlesik)", "location": "outdoor"},
    {"ids": ["T14", "T15", "T16"], "combined_capacity": 12, "name": "Masa 14-15-16 (Birlesik)", "location": "indoor"},
]

# Öğün süreleri (dakika)
MEAL_DURATIONS = {
    MealType.BREAKFAST: 120,  # 2 saat
    MealType.LUNCH: 120,      # 2 saat
    MealType.DINNER: 240,     # 4 saat
}

# Öğün saatleri
MEAL_TIME_SLOTS = {
    MealType.BREAKFAST: ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30"],
    MealType.LUNCH: ["12:00", "12:30", "13:00", "13:30", "14:00"],
    MealType.DINNER: ["18:00", "18:30", "19:00", "19:30", "20:00", "20:30"],
}

# Restoran konfigi
RESTAURANT_CONFIG = {
    "name": "Antakya Sofrasi",
    "total_tables": len(TABLES),
    "small_tables_2": len([t for t in TABLES if t["capacity"] == 2]),
    "small_tables_3": len([t for t in TABLES if t["capacity"] == 3]),
    "medium_tables_4": len([t for t in TABLES if t["capacity"] == 4]),
    "indoor_tables": len([t for t in TABLES if t["location"] == "indoor"]),
    "outdoor_tables": len([t for t in TABLES if t["location"] == "outdoor"]),
    "max_party_size": 12,  # Masa birleştirme ile
    "tables": TABLES,
    "combinable_tables": COMBINABLE_TABLES,
    "meal_durations": {k.value: v for k, v in MEAL_DURATIONS.items()},
    "meal_time_slots": {k.value: v for k, v in MEAL_TIME_SLOTS.items()},
}


def time_to_minutes(time_str: str) -> int:
    """Convert HH:MM to minutes since midnight"""
    h, m = map(int, time_str.split(":"))
    return h * 60 + m


def minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight to HH:MM"""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


async def get_table_reservations_in_range(date: str, start_time: str, end_time: str) -> List[dict]:
    """Get all active reservations that overlap with given time range"""
    reservations = await db.table_reservations.find({
        "date": date,
        "status": {"$in": [TableStatus.PENDING, TableStatus.CONFIRMED, TableStatus.SEATED]},
    }, {"_id": 0}).to_list(200)
    
    start_mins = time_to_minutes(start_time)
    end_mins = time_to_minutes(end_time)
    
    overlapping = []
    for res in reservations:
        res_start = time_to_minutes(res["time"])
        res_duration = MEAL_DURATIONS.get(MealType(res.get("meal_type", "lunch")), 120)
        res_end = res_start + res_duration
        
        # Check if time ranges overlap
        if res_start < end_mins and res_end > start_mins:
            overlapping.append(res)
    
    return overlapping


async def find_available_tables(date: str, time: str, meal_type: MealType, party_size: int) -> List[dict]:
    """Find tables that are available for the given reservation"""
    duration = MEAL_DURATIONS[meal_type]
    start_mins = time_to_minutes(time)
    end_mins = start_mins + duration
    end_time = minutes_to_time(end_mins)
    
    # Get overlapping reservations
    overlapping = await get_table_reservations_in_range(date, time, end_time)
    occupied_tables = {res.get("table_id") for res in overlapping if res.get("table_id")}
    
    # Find suitable tables
    available = []
    for table in TABLES:
        if table["id"] in occupied_tables:
            continue
        if table["capacity"] >= party_size:
            available.append(table)
    
    # Sort by capacity (prefer smaller suitable tables)
    available.sort(key=lambda t: t["capacity"])
    return available


@router.get("/table-reservations")
async def list_table_reservations(date: Optional[str] = None, status: Optional[str] = None, limit: int = 50):
    query = {}
    if date:
        query["date"] = date
    if status:
        query["status"] = status
    items = await db.table_reservations.find(query, {"_id": 0}).sort([("date", -1), ("time", 1)]).limit(limit).to_list(limit)
    total = await db.table_reservations.count_documents(query)
    return {"reservations": items, "total": total, "config": RESTAURANT_CONFIG}


@router.get("/table-reservations/tables")
async def get_tables():
    """Get all table definitions"""
    return {"tables": TABLES, "config": RESTAURANT_CONFIG}


@router.post("/table-reservations")
async def create_table_reservation(data: TableReservationCreate):
    # Find available tables
    available_tables = await find_available_tables(
        data.date, data.time, data.meal_type, data.party_size
    )
    
    if not available_tables:
        raise HTTPException(
            409, 
            f"{data.date} {data.time} icin {data.party_size} kisilik musait masa bulunmuyor."
        )
    
    # Select table (preferred or first available)
    selected_table = None
    if data.preferred_table_id:
        for t in available_tables:
            if t["id"] == data.preferred_table_id:
                selected_table = t
                break
    if not selected_table:
        selected_table = available_tables[0]
    
    # Calculate end time
    duration = MEAL_DURATIONS[data.meal_type]
    start_mins = time_to_minutes(data.time)
    end_time = minutes_to_time(start_mins + duration)
    
    reservation = {
        "id": new_id(),
        **data.model_dump(),
        "table_id": selected_table["id"],
        "table_name": selected_table["name"],
        "table_capacity": selected_table["capacity"],
        "end_time": end_time,
        "duration_minutes": duration,
        "status": TableStatus.PENDING,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.table_reservations.insert_one(reservation)
    return {**clean_doc(reservation), "available_tables": available_tables}


@router.patch("/table-reservations/{res_id}/status")
async def update_table_reservation_status(res_id: str, status: str, table_id: Optional[str] = None):
    update = {"status": status, "updated_at": utcnow()}
    
    if table_id:
        # Find table info
        table = next((t for t in TABLES if t["id"] == table_id), None)
        if table:
            update["table_id"] = table_id
            update["table_name"] = table["name"]
            update["table_capacity"] = table["capacity"]
    
    if status == TableStatus.SEATED:
        update["seated_at"] = utcnow()
    elif status == TableStatus.COMPLETED:
        update["completed_at"] = utcnow()

    result = await db.table_reservations.update_one({"id": res_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(404, "Masa rezervasyonu bulunamadi")
    
    updated = await db.table_reservations.find_one({"id": res_id}, {"_id": 0})
    return {"success": True, "reservation": updated}


@router.patch("/table-reservations/{res_id}/table")
async def change_table(res_id: str, table_id: str):
    """Change the assigned table for a reservation"""
    reservation = await db.table_reservations.find_one({"id": res_id}, {"_id": 0})
    if not reservation:
        raise HTTPException(404, "Masa rezervasyonu bulunamadi")
    
    # Check if new table is available
    duration = reservation.get("duration_minutes", 120)
    start_mins = time_to_minutes(reservation["time"])
    end_time = minutes_to_time(start_mins + duration)
    
    overlapping = await get_table_reservations_in_range(reservation["date"], reservation["time"], end_time)
    occupied = {r.get("table_id") for r in overlapping if r["id"] != res_id}
    
    if table_id in occupied:
        raise HTTPException(409, "Secilen masa bu saat araliginda dolu")
    
    table = next((t for t in TABLES if t["id"] == table_id), None)
    if not table:
        raise HTTPException(404, "Masa bulunamadi")
    
    await db.table_reservations.update_one(
        {"id": res_id},
        {"$set": {
            "table_id": table_id,
            "table_name": table["name"],
            "table_capacity": table["capacity"],
            "updated_at": utcnow()
        }}
    )
    return {"success": True}


@router.delete("/table-reservations/{res_id}")
async def delete_table_reservation(res_id: str):
    result = await db.table_reservations.delete_one({"id": res_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Masa rezervasyonu bulunamadi")
    return {"success": True}


@router.get("/table-reservations/availability")
async def check_table_availability(date: str, meal_type: Optional[str] = None, party_size: int = 2):
    """Check availability for a specific date, optionally filtered by meal type"""
    result = {}
    
    meal_types = [MealType(meal_type)] if meal_type else list(MealType)
    
    for mt in meal_types:
        slots = []
        for time_slot in MEAL_TIME_SLOTS[mt]:
            available_tables = await find_available_tables(date, time_slot, mt, party_size)
            slots.append({
                "time": time_slot,
                "meal_type": mt.value,
                "duration_minutes": MEAL_DURATIONS[mt],
                "available_tables": len(available_tables),
                "available_table_ids": [t["id"] for t in available_tables],
                "is_available": len(available_tables) > 0,
            })
        result[mt.value] = slots
    
    return {"date": date, "party_size": party_size, "availability": result, "config": RESTAURANT_CONFIG}


@router.get("/table-reservations/daily-view")
async def get_daily_view(date: str):
    """Get a visual timeline of all reservations for a date"""
    reservations = await db.table_reservations.find({
        "date": date,
        "status": {"$in": [TableStatus.PENDING, TableStatus.CONFIRMED, TableStatus.SEATED]},
    }, {"_id": 0}).to_list(200)
    
    # Build timeline for each table
    table_timelines = {}
    for table in TABLES:
        table_timelines[table["id"]] = {
            "table": table,
            "reservations": []
        }
    
    for res in reservations:
        table_id = res.get("table_id")
        if table_id and table_id in table_timelines:
            table_timelines[table_id]["reservations"].append({
                "id": res["id"],
                "guest_name": res["guest_name"],
                "time": res["time"],
                "end_time": res.get("end_time"),
                "party_size": res["party_size"],
                "meal_type": res.get("meal_type"),
                "status": res["status"],
            })
    
    return {
        "date": date,
        "tables": list(table_timelines.values()),
        "total_reservations": len(reservations),
    }


@router.get("/table-reservations/stats")
async def table_reservation_stats():
    total = await db.table_reservations.count_documents({})
    today_str = utcnow()[:10]
    today = await db.table_reservations.count_documents({"date": today_str})
    pending = await db.table_reservations.count_documents({"status": TableStatus.PENDING})
    confirmed = await db.table_reservations.count_documents({"status": TableStatus.CONFIRMED})
    
    # Meal type breakdown
    breakfast = await db.table_reservations.count_documents({"meal_type": "breakfast"})
    lunch = await db.table_reservations.count_documents({"meal_type": "lunch"})
    dinner = await db.table_reservations.count_documents({"meal_type": "dinner"})
    
    return {
        "total": total,
        "today": today,
        "pending": pending,
        "confirmed": confirmed,
        "by_meal": {
            "breakfast": breakfast,
            "lunch": lunch,
            "dinner": dinner,
        },
        "config": RESTAURANT_CONFIG,
    }
