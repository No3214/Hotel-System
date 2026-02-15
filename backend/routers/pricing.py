from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from hotel_data import ROOMS, HOTEL_INFO
import math

router = APIRouter(tags=["pricing"])

# ==================== TATIL TAKVIMI ====================

HOLIDAYS_2026 = [
    {"date": "2026-01-01", "name": "Yilbasi", "multiplier": 1.5},
    {"date": "2026-02-14", "name": "Sevgililer Gunu", "multiplier": 1.3},
    {"date": "2026-03-18", "name": "Canakkale Zaferi", "multiplier": 1.1},
    {"date": "2026-04-23", "name": "Ulusal Egemenlik ve Cocuk Bayrami", "multiplier": 1.2},
    {"date": "2026-05-01", "name": "Isci Bayrami", "multiplier": 1.1},
    {"date": "2026-05-19", "name": "Ataturk'u Anma", "multiplier": 1.1},
    {"date": "2026-06-15", "name": "Arefe (Kurban Bayrami)", "multiplier": 1.5},
    {"date": "2026-06-16", "name": "Kurban Bayrami 1. gun", "multiplier": 1.6},
    {"date": "2026-06-17", "name": "Kurban Bayrami 2. gun", "multiplier": 1.6},
    {"date": "2026-06-18", "name": "Kurban Bayrami 3. gun", "multiplier": 1.5},
    {"date": "2026-06-19", "name": "Kurban Bayrami 4. gun", "multiplier": 1.4},
    {"date": "2026-07-15", "name": "Demokrasi ve Milli Birlik Gunu", "multiplier": 1.2},
    {"date": "2026-08-30", "name": "Zafer Bayrami", "multiplier": 1.2},
    {"date": "2026-10-29", "name": "Cumhuriyet Bayrami", "multiplier": 1.3},
]

# Sezon çarpanları
SEASON_CONFIG = {
    "off_season": {"months": [1, 2, 3, 11, 12], "multiplier": 0.8, "label": "Dusuk Sezon"},
    "mid_season": {"months": [4, 5, 10], "multiplier": 1.0, "label": "Orta Sezon"},
    "high_season": {"months": [6, 7, 8, 9], "multiplier": 1.4, "label": "Yuksek Sezon"},
}

# Hafta sonu çarpanı
WEEKEND_MULTIPLIER = 1.2  # Cuma-Cumartesi


def get_season(month: int) -> dict:
    for season_key, cfg in SEASON_CONFIG.items():
        if month in cfg["months"]:
            return {"key": season_key, **cfg}
    return {"key": "mid_season", "multiplier": 1.0, "label": "Orta Sezon"}


def get_holiday(date_str: str) -> dict | None:
    for h in HOLIDAYS_2026:
        if h["date"] == date_str:
            return h
    return None


def is_weekend(date_str: str) -> bool:
    from datetime import datetime
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.weekday() in [4, 5]  # Cuma=4, Cumartesi=5
    except ValueError:
        return False


def calculate_price(room_id: str, date_str: str, occupancy_rate: float = 0.0) -> dict:
    room = None
    for r in ROOMS:
        if r["room_id"] == room_id:
            room = r
            break
    if not room:
        return {"error": "Oda bulunamadi"}

    base_price = room["base_price_try"]

    # Parse month
    try:
        month = int(date_str.split("-")[1])
    except (IndexError, ValueError):
        month = 6

    # Season multiplier
    season = get_season(month)
    price = base_price * season["multiplier"]

    # Holiday multiplier
    holiday = get_holiday(date_str)
    if holiday:
        price *= holiday["multiplier"]

    # Weekend multiplier
    weekend = is_weekend(date_str)
    if weekend and not holiday:
        price *= WEEKEND_MULTIPLIER

    # Occupancy-based dynamic adjustment
    if occupancy_rate >= 0.9:
        price *= 1.25  # %90+ doluluk → %25 artis
    elif occupancy_rate >= 0.75:
        price *= 1.15  # %75+ doluluk → %15 artis
    elif occupancy_rate >= 0.5:
        price *= 1.05  # %50+ doluluk → %5 artis
    elif occupancy_rate < 0.25 and occupancy_rate > 0:
        price *= 0.9   # %25 alti doluluk → %10 indirim

    final_price = math.ceil(price / 50) * 50  # 50 TL'ye yuvarla

    return {
        "room_id": room_id,
        "room_name": room["name_tr"],
        "date": date_str,
        "base_price": base_price,
        "final_price": final_price,
        "currency": "TRY",
        "season": season["label"],
        "season_multiplier": season["multiplier"],
        "is_holiday": holiday is not None,
        "holiday_name": holiday["name"] if holiday else None,
        "holiday_multiplier": holiday["multiplier"] if holiday else 1.0,
        "is_weekend": weekend,
        "weekend_multiplier": WEEKEND_MULTIPLIER if weekend and not holiday else 1.0,
        "occupancy_rate": occupancy_rate,
        "savings": base_price - final_price if final_price < base_price else 0,
        "surcharge": final_price - base_price if final_price > base_price else 0,
    }


@router.get("/pricing/calculate")
async def get_dynamic_price(room_id: str, date: str):
    from models import ReservationStatus
    total_rooms = HOTEL_INFO["total_rooms"]
    occupied = await db.reservations.count_documents({"status": ReservationStatus.CHECKED_IN})
    occupancy = occupied / total_rooms if total_rooms else 0

    result = calculate_price(room_id, date, occupancy)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.get("/pricing/range")
async def get_price_range(room_id: str, start_date: str, end_date: str):
    from datetime import datetime, timedelta
    from models import ReservationStatus

    total_rooms = HOTEL_INFO["total_rooms"]
    occupied = await db.reservations.count_documents({"status": ReservationStatus.CHECKED_IN})
    occupancy = occupied / total_rooms if total_rooms else 0

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "Tarih formati: YYYY-MM-DD")

    days = []
    total = 0
    current = start
    while current < end:
        date_str = current.strftime("%Y-%m-%d")
        result = calculate_price(room_id, date_str, occupancy)
        if "error" not in result:
            days.append(result)
            total += result["final_price"]
        current += timedelta(days=1)

    nights = len(days)
    avg_price = round(total / nights) if nights else 0

    return {
        "room_id": room_id,
        "start_date": start_date,
        "end_date": end_date,
        "nights": nights,
        "total_price": total,
        "average_nightly": avg_price,
        "daily_breakdown": days,
    }


@router.get("/pricing/seasons")
async def get_seasons():
    return {
        "seasons": [
            {"key": k, "label": v["label"], "months": v["months"], "multiplier": v["multiplier"]}
            for k, v in SEASON_CONFIG.items()
        ],
        "weekend_multiplier": WEEKEND_MULTIPLIER,
        "weekend_days": ["Cuma", "Cumartesi"],
    }


@router.get("/pricing/holidays")
async def get_holidays():
    return {"holidays": HOLIDAYS_2026}


@router.patch("/pricing/seasons/{season_key}")
async def update_season_multiplier(season_key: str, multiplier: float):
    if season_key not in SEASON_CONFIG:
        raise HTTPException(404, "Sezon bulunamadi")
    # Save custom multiplier to DB
    await db.pricing_config.update_one(
        {"type": "season", "key": season_key},
        {"$set": {"multiplier": multiplier, "updated_at": utcnow()}},
        upsert=True,
    )
    return {"success": True, "season": season_key, "multiplier": multiplier}
