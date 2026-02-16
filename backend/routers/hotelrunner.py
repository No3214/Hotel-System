"""
HotelRunner API Integration (Mock Mode)
Two-way synchronization for reservations, availability, and pricing.
Includes cancellation policy engine, webhook processing, and OTA channel management.
"""
from fastapi import APIRouter, Query, Request
from typing import Optional
from datetime import datetime, timedelta, timezone
from database import db
from helpers import utcnow, new_id
import logging
import os

router = APIRouter(tags=["hotelrunner"])
logger = logging.getLogger(__name__)

HOTELRUNNER_API_KEY = os.environ.get("HOTELRUNNER_API_KEY", "")
HOTELRUNNER_HOTEL_ID = os.environ.get("HOTELRUNNER_HOTEL_ID", "")
MOCK_MODE = not (HOTELRUNNER_API_KEY and HOTELRUNNER_HOTEL_ID)

# Kozbeyli Konagi special days
SPECIAL_DATES = [
    (1, 1), (2, 14), (4, 23), (5, 1), (5, 19),
    (7, 15), (8, 30), (10, 29),
]

OTA_CHANNELS = [
    {"id": "booking", "name": "Booking.com", "commission": 15, "status": "pending"},
    {"id": "expedia", "name": "Expedia", "commission": 18, "status": "pending"},
    {"id": "airbnb", "name": "Airbnb", "commission": 3, "status": "pending"},
    {"id": "google", "name": "Google Hotel", "commission": 12, "status": "pending"},
    {"id": "trivago", "name": "Trivago", "commission": 10, "status": "pending"},
]


def is_special_day(d: datetime) -> bool:
    if d.weekday() in (5, 6):
        return True
    if (d.month, d.day) in SPECIAL_DATES:
        return True
    return False


def calculate_cancellation_penalty(check_in_str: str, total_price: float) -> dict:
    try:
        check_in = datetime.strptime(check_in_str[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return {"percentage": 0, "amount": 0, "reason": "Gecersiz tarih"}

    days_until = (check_in - datetime.now()).days

    if is_special_day(check_in):
        return {
            "percentage": 100,
            "amount": total_price,
            "reason": "Ozel gun - on odeme zorunlu, iade yapilmaz",
            "is_special_day": True,
            "days_until": days_until,
        }

    if days_until > 3:
        return {
            "percentage": 0,
            "amount": 0,
            "reason": f"Ucretsiz iptal ({days_until} gun var)",
            "is_special_day": False,
            "days_until": days_until,
        }

    return {
        "percentage": 100,
        "amount": total_price,
        "reason": f"3 gun icinde iptal ({days_until} gun kaldi) - %100 ceza",
        "is_special_day": False,
        "days_until": days_until,
    }


def map_hr_reservation(hr_res: dict) -> dict:
    status_map = {
        "new": "confirmed", "confirmed": "confirmed", "modified": "modified",
        "cancelled": "cancelled", "no_show": "no_show",
        "checked_in": "checked_in", "checked_out": "checked_out",
    }
    ci = hr_res.get("checkin_date") or hr_res.get("check_in", "")
    co = hr_res.get("checkout_date") or hr_res.get("check_out", "")

    nights = 1
    if ci and co:
        try:
            nights = max(1, (datetime.strptime(co[:10], "%Y-%m-%d") - datetime.strptime(ci[:10], "%Y-%m-%d")).days)
        except (ValueError, TypeError):
            pass

    total = hr_res.get("total_price", 0)
    return {
        "guest_name": hr_res.get("guest_name", ""),
        "guest_surname": hr_res.get("guest_surname", ""),
        "guest_email": hr_res.get("guest_email", ""),
        "guest_phone": hr_res.get("guest_phone", ""),
        "check_in": ci, "check_out": co, "nights": nights,
        "room_type_name": hr_res.get("room_type_name", ""),
        "adults": hr_res.get("adults", 1),
        "children": hr_res.get("children", 0),
        "total_price": total,
        "nightly_rate": round(total / nights, 2) if nights > 0 else total,
        "currency": hr_res.get("currency", "TRY"),
        "status": status_map.get(hr_res.get("status", ""), "confirmed"),
        "source": hr_res.get("channel_name", "direct"),
        "confirmation_code": hr_res.get("confirmation_code", ""),
        "hotelrunner_id": hr_res.get("id", ""),
    }


# ==================== MOCK SYNC ====================

async def mock_sync_reservations():
    return {"synced": 0, "new_reservations": 0, "updated_reservations": 0, "mock": True,
            "message": "Mock mod: API anahtarlari ayarlandiginda gercek senkronizasyon yapilacak"}

async def mock_sync_availability():
    return {"synced": 0, "rooms_updated": 0, "mock": True,
            "message": "Mock mod: Musaitlik bilgisi HotelRunner'a gonderilecek"}

async def mock_sync_rates():
    return {"synced": 0, "rates_updated": 0, "mock": True,
            "message": "Mock mod: Fiyat bilgisi HotelRunner'a gonderilecek"}


# ==================== SYNC ENDPOINTS ====================

@router.post("/hotelrunner/sync/reservations")
async def sync_reservations():
    result = await mock_sync_reservations()
    await db.sync_logs.insert_one({
        "id": new_id(), "timestamp": utcnow(), "sync_type": "reservations",
        "status": "success", "items_processed": result.get("synced", 0),
        "items_failed": 0, "mock": MOCK_MODE, "duration_ms": 0,
    })
    return {"success": True, "type": "reservations", **result}


@router.post("/hotelrunner/sync/availability")
async def sync_availability():
    result = await mock_sync_availability()
    await db.sync_logs.insert_one({
        "id": new_id(), "timestamp": utcnow(), "sync_type": "availability",
        "status": "success", "items_processed": result.get("synced", 0),
        "items_failed": 0, "mock": MOCK_MODE, "duration_ms": 0,
    })
    return {"success": True, "type": "availability", **result}


@router.post("/hotelrunner/sync/rates")
async def sync_rates():
    result = await mock_sync_rates()
    await db.sync_logs.insert_one({
        "id": new_id(), "timestamp": utcnow(), "sync_type": "rates",
        "status": "success", "items_processed": result.get("synced", 0),
        "items_failed": 0, "mock": MOCK_MODE, "duration_ms": 0,
    })
    return {"success": True, "type": "rates", **result}


@router.post("/hotelrunner/sync/full")
async def full_sync():
    results = {
        "reservations": await sync_reservations(),
        "availability": await sync_availability(),
        "rates": await sync_rates(),
    }
    return {"success": True, "type": "full_sync", "results": results, "mock": MOCK_MODE}


# ==================== STATUS & LOGS ====================

@router.get("/hotelrunner/status")
async def get_status():
    last_sync = await db.sync_logs.find_one({}, {"_id": 0}, sort=[("timestamp", -1)])
    total_syncs = await db.sync_logs.count_documents({})
    failed_syncs = await db.sync_logs.count_documents({"status": "error"})

    return {
        "connected": not MOCK_MODE,
        "mock_mode": MOCK_MODE,
        "api_key_set": bool(HOTELRUNNER_API_KEY),
        "hotel_id_set": bool(HOTELRUNNER_HOTEL_ID),
        "last_sync": last_sync,
        "total_syncs": total_syncs,
        "failed_syncs": failed_syncs,
        "channels": OTA_CHANNELS,
    }


@router.get("/hotelrunner/sync-logs")
async def get_sync_logs(
    sync_type: Optional[str] = Query(default=None),
    limit: int = Query(default=50),
):
    query = {}
    if sync_type:
        query["sync_type"] = sync_type
    logs = await db.sync_logs.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return {"logs": logs, "total": len(logs)}


# ==================== CANCELLATION POLICY ====================

@router.post("/hotelrunner/cancellation-penalty")
async def check_cancellation_penalty(request: Request):
    body = await request.json()
    check_in = body.get("check_in", "")
    total_price = float(body.get("total_price", 0))
    penalty = calculate_cancellation_penalty(check_in, total_price)
    return penalty


# ==================== WEBHOOK ====================

@router.post("/hotelrunner/webhook")
async def hotelrunner_webhook(request: Request):
    payload = await request.json()
    event_type = payload.get("event_type", "unknown")

    webhook_log = {
        "id": new_id(), "timestamp": utcnow(), "event_type": event_type,
        "payload": payload, "processed": False,
    }

    # Process known events
    event_data = payload.get("data", {})
    if event_type == "reservation.created":
        mapped = map_hr_reservation(event_data.get("reservation", {}))
        mapped["id"] = new_id()
        mapped["source"] = event_data.get("channel", "hotelrunner")
        mapped["hotelrunner_id"] = event_data.get("reservation", {}).get("id", "")
        mapped["created_at"] = utcnow()
        await db.reservations.insert_one(mapped)
        webhook_log["processed"] = True
        logger.info(f"New HR reservation: {mapped.get('guest_name')}")

    elif event_type == "reservation.cancelled":
        hr_id = event_data.get("reservation", {}).get("id", "")
        if hr_id:
            await db.reservations.update_one(
                {"hotelrunner_id": hr_id},
                {"$set": {"status": "cancelled", "cancelled_at": utcnow()}},
            )
            webhook_log["processed"] = True

    elif event_type == "reservation.modified":
        hr_id = event_data.get("reservation", {}).get("id", "")
        if hr_id:
            mapped = map_hr_reservation(event_data.get("reservation", {}))
            await db.reservations.update_one(
                {"hotelrunner_id": hr_id},
                {"$set": {**mapped, "modified_at": utcnow()}},
            )
            webhook_log["processed"] = True

    await db.hotelrunner_webhooks.insert_one(webhook_log)
    logger.info(f"HotelRunner webhook: {event_type} (processed: {webhook_log['processed']})")
    return {"success": True, "event_type": event_type, "processed": webhook_log["processed"]}


# ==================== CHANNELS ====================

@router.get("/hotelrunner/channels")
async def get_channels():
    return {"channels": OTA_CHANNELS, "mock_mode": MOCK_MODE}


# ==================== CONFIGURATION ====================

@router.get("/hotelrunner/config")
async def get_config():
    return {
        "mock_mode": MOCK_MODE,
        "api_key_set": bool(HOTELRUNNER_API_KEY),
        "hotel_id_set": bool(HOTELRUNNER_HOTEL_ID),
        "sync_interval_minutes": 15,
        "features": {
            "reservation_sync": True,
            "availability_sync": True,
            "rate_sync": True,
            "webhook_handler": True,
            "cancellation_policy": True,
            "channel_management": True,
        },
    }
