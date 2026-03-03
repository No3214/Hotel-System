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
    party_size: int = Field(ge=1, le=24)
    meal_type: MealType
    notes: Optional[str] = None
    occasion: Optional[str] = None  # birthday, anniversary, business, etc.
    is_hotel_guest: bool = False
    preferred_table_id: Optional[str] = None


# Masa tanımları - Kozbeyli Konağı Gerçek Yerleşim Planı
# 13 dikdörtgen + 3 yuvarlak + 4 küçük = 20 masa
TABLES = [
    # SOMINE BOLGESI (Sol taraf)
    {"id": "M1", "name": "Masa 1", "capacity": 6, "type": "rectangular", "zone": "somine", "zone_label": "Somine"},
    {"id": "M2", "name": "Masa 2", "capacity": 6, "type": "rectangular", "zone": "somine", "zone_label": "Somine"},
    {"id": "M3", "name": "Masa 3", "capacity": 6, "type": "rectangular", "zone": "somine", "zone_label": "Somine"},
    {"id": "A", "name": "Yuvarlak A", "capacity": 8, "type": "round", "zone": "somine", "zone_label": "Somine"},
    {"id": "B", "name": "Yuvarlak B", "capacity": 8, "type": "round", "zone": "somine", "zone_label": "Somine"},
    {"id": "C", "name": "Yuvarlak C", "capacity": 8, "type": "round", "zone": "somine", "zone_label": "Somine"},
    # SAHNE BOLGESI (Orta)
    {"id": "M5", "name": "Masa 5", "capacity": 6, "type": "rectangular", "zone": "sahne", "zone_label": "Sahne"},
    {"id": "M6", "name": "Masa 6", "capacity": 6, "type": "rectangular", "zone": "sahne", "zone_label": "Sahne"},
    {"id": "M7", "name": "Masa 7", "capacity": 6, "type": "rectangular", "zone": "sahne", "zone_label": "Sahne"},
    {"id": "M8", "name": "Masa 8", "capacity": 6, "type": "rectangular", "zone": "sahne", "zone_label": "Sahne"},
    # MANZARA BOLGESI (Sag taraf)
    {"id": "M10", "name": "Masa 10", "capacity": 6, "type": "rectangular", "zone": "manzara", "zone_label": "Manzara"},
    {"id": "M11", "name": "Masa 11", "capacity": 6, "type": "rectangular", "zone": "manzara", "zone_label": "Manzara"},
    {"id": "M12", "name": "Masa 12", "capacity": 6, "type": "rectangular", "zone": "manzara", "zone_label": "Manzara"},
    {"id": "M13", "name": "Masa 13", "capacity": 6, "type": "rectangular", "zone": "manzara", "zone_label": "Manzara"},
    # KUCUK MASALAR (Sahne-Manzara arasi)
    {"id": "S1", "name": "Kucuk S1", "capacity": 2, "type": "small", "zone": "ara", "zone_label": "Ara Bolge"},
    {"id": "S2", "name": "Kucuk S2", "capacity": 2, "type": "small", "zone": "ara", "zone_label": "Ara Bolge"},
    {"id": "S3", "name": "Kucuk S3", "capacity": 2, "type": "small", "zone": "ara", "zone_label": "Ara Bolge"},
    {"id": "S4", "name": "Kucuk S4", "capacity": 2, "type": "small", "zone": "ara", "zone_label": "Ara Bolge"},
    # BAR BOLGESI (2 bar taburesi masasi)
    {"id": "BAR1", "name": "Bar 1", "capacity": 4, "type": "bar", "zone": "bar", "zone_label": "Bar"},
    {"id": "BAR2", "name": "Bar 2", "capacity": 4, "type": "bar", "zone": "bar", "zone_label": "Bar"},
]

# Birleştirilebilir masa grupları (büyük gruplar için)
COMBINABLE_TABLES = [
    {"ids": ["M1", "M2"], "combined_capacity": 12, "name": "Masa 1-2 (Birlesik)", "zone": "somine"},
    {"ids": ["M1", "M2", "M3"], "combined_capacity": 18, "name": "Masa 1-2-3 (Birlesik)", "zone": "somine"},
    {"ids": ["M5", "M6"], "combined_capacity": 12, "name": "Masa 5-6 (Birlesik)", "zone": "sahne"},
    {"ids": ["M7", "M8"], "combined_capacity": 12, "name": "Masa 7-8 (Birlesik)", "zone": "sahne"},
    {"ids": ["M5", "M6", "M7", "M8"], "combined_capacity": 24, "name": "Masa 5-8 (Birlesik)", "zone": "sahne"},
    {"ids": ["M10", "M11"], "combined_capacity": 12, "name": "Masa 10-11 (Birlesik)", "zone": "manzara"},
    {"ids": ["M12", "M13"], "combined_capacity": 12, "name": "Masa 12-13 (Birlesik)", "zone": "manzara"},
    {"ids": ["M10", "M11", "M12", "M13"], "combined_capacity": 24, "name": "Masa 10-13 (Birlesik)", "zone": "manzara"},
    {"ids": ["A", "B", "C"], "combined_capacity": 24, "name": "Yuvarlak A-B-C (Birlesik)", "zone": "somine"},
]

# Bölge bilgileri
ZONES = [
    {"id": "somine", "name": "Somine Bolgesi", "description": "Sol taraf, somine yakininda, 3 dikdortgen + 3 yuvarlak masa"},
    {"id": "sahne", "name": "Sahne Bolgesi", "description": "Orta kisim, sahne onunde, 4 dikdortgen masa"},
    {"id": "manzara", "name": "Manzara Bolgesi", "description": "Sag taraf, manzara yonunde, 4 dikdortgen masa"},
    {"id": "ara", "name": "Ara Bolge", "description": "Sahne-manzara arasi, 4 kucuk masa"},
    {"id": "bar", "name": "Bar Bolgesi", "description": "Ana giris yaninda, 2 bar masasi"},
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
    "name": "Kozbeyli Konagi - Antakya Sofrasi",
    "total_tables": len(TABLES),
    "rectangular_tables": len([t for t in TABLES if t["type"] == "rectangular"]),
    "round_tables": len([t for t in TABLES if t["type"] == "round"]),
    "small_tables": len([t for t in TABLES if t["type"] == "small"]),
    "bar_tables": len([t for t in TABLES if t["type"] == "bar"]),
    "total_capacity": sum(t["capacity"] for t in TABLES),
    "max_party_size": 24,
    "tables": TABLES,
    "combinable_tables": COMBINABLE_TABLES,
    "zones": ZONES,
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
    
    # Also check combined table reservations
    for res in overlapping:
        if res.get("combined_table_ids"):
            for tid in res["combined_table_ids"]:
                occupied_tables.add(tid)
    
    available = []
    
    # First check single tables
    for table in TABLES:
        if table["id"] in occupied_tables:
            continue
        if table["capacity"] >= party_size:
            available.append({**table, "is_combined": False})
    
    # For larger groups (5+), check combinable tables
    if party_size > 4:
        for combo in COMBINABLE_TABLES:
            if combo["combined_capacity"] >= party_size:
                # Check if all tables in combo are available
                all_available = all(tid not in occupied_tables for tid in combo["ids"])
                if all_available:
                    available.append({
                        "id": "_".join(combo["ids"]),
                        "name": combo["name"],
                        "capacity": combo["combined_capacity"],
                        "type": "combined",
                        "zone": combo["zone"],
                        "is_combined": True,
                        "combined_table_ids": combo["ids"],
                    })
    
    # Sort by capacity (prefer smaller suitable tables/combos)
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
        "is_combined": selected_table.get("is_combined", False),
        "combined_table_ids": selected_table.get("combined_table_ids"),
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



@router.get("/table-reservations/floor-plan")
async def get_floor_plan(date: Optional[str] = None):
    """Get full floor plan with current table statuses for a given date"""
    check_date = date or utcnow()[:10]
    now_time = datetime.now().strftime("%H:%M")

    reservations = await db.table_reservations.find({
        "date": check_date,
        "status": {"$in": [TableStatus.PENDING, TableStatus.CONFIRMED, TableStatus.SEATED]},
    }, {"_id": 0}).to_list(200)

    # Build table status map
    table_status_map = {}
    for res in reservations:
        tid = res.get("table_id")
        if tid:
            start = time_to_minutes(res["time"])
            end = start + res.get("duration_minutes", 120)
            now_mins = time_to_minutes(now_time)
            is_current = start <= now_mins < end
            table_status_map[tid] = {
                "reservation_id": res["id"],
                "guest_name": res["guest_name"],
                "party_size": res["party_size"],
                "time": res["time"],
                "end_time": res.get("end_time", ""),
                "status": res["status"],
                "meal_type": res.get("meal_type", ""),
                "is_current": is_current,
            }

    floor_plan = []
    for zone in ZONES:
        zone_tables = []
        for table in TABLES:
            if table["zone"] == zone["id"]:
                reservation_info = table_status_map.get(table["id"])
                zone_tables.append({
                    **table,
                    "is_occupied": table["id"] in table_status_map,
                    "reservation": reservation_info,
                })
        floor_plan.append({
            **zone,
            "tables": zone_tables,
            "occupied_count": sum(1 for t in zone_tables if t["is_occupied"]),
            "total_count": len(zone_tables),
        })

    return {
        "date": check_date,
        "zones": floor_plan,
        "total_tables": len(TABLES),
        "occupied_tables": len(table_status_map),
        "available_tables": len(TABLES) - len(table_status_map),
        "total_capacity": sum(t["capacity"] for t in TABLES),
    }


@router.get("/table-reservations/zones")
async def get_zones():
    """Get zone definitions"""
    return {"zones": ZONES}
