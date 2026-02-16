"""
HotelRunner API Integration (Mock Mode)
Two-way synchronization for reservations, availability, and pricing.
When API keys are provided, switch MOCK_MODE to False.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime, timedelta, timezone
from database import db
from helpers import utcnow, new_id
import logging
import os

router = APIRouter(tags=["hotelrunner"])
logger = logging.getLogger(__name__)

# Configuration - set in .env when keys arrive
HOTELRUNNER_API_KEY = os.environ.get("HOTELRUNNER_API_KEY", "")
HOTELRUNNER_HOTEL_ID = os.environ.get("HOTELRUNNER_HOTEL_ID", "")
MOCK_MODE = not (HOTELRUNNER_API_KEY and HOTELRUNNER_HOTEL_ID)


async def mock_sync_reservations():
    """Simulates fetching reservations from HotelRunner"""
    return {
        "synced": 0,
        "new_reservations": 0,
        "updated_reservations": 0,
        "mock": True,
        "message": "Mock mod: API anahtarlari ayarlandiginda gercek senkronizasyon yapilacak",
    }


async def mock_sync_availability():
    """Simulates pushing availability to HotelRunner"""
    return {
        "synced": 0,
        "rooms_updated": 0,
        "mock": True,
        "message": "Mock mod: Musaitlik bilgisi HotelRunner'a gonderilecek",
    }


async def mock_sync_rates():
    """Simulates pushing rates to HotelRunner"""
    return {
        "synced": 0,
        "rates_updated": 0,
        "mock": True,
        "message": "Mock mod: Fiyat bilgisi HotelRunner'a gonderilecek",
    }


# ==================== SYNC ENDPOINTS ====================

@router.post("/hotelrunner/sync/reservations")
async def sync_reservations():
    if MOCK_MODE:
        result = await mock_sync_reservations()
    else:
        # Real API call would go here
        result = await mock_sync_reservations()

    # Log sync
    await db.sync_logs.insert_one({
        "id": new_id(),
        "timestamp": utcnow(),
        "sync_type": "reservations",
        "status": "success",
        "items_processed": result.get("synced", 0),
        "items_failed": 0,
        "mock": MOCK_MODE,
        "duration_ms": 0,
    })

    return {"success": True, "type": "reservations", **result}


@router.post("/hotelrunner/sync/availability")
async def sync_availability():
    if MOCK_MODE:
        result = await mock_sync_availability()
    else:
        result = await mock_sync_availability()

    await db.sync_logs.insert_one({
        "id": new_id(),
        "timestamp": utcnow(),
        "sync_type": "availability",
        "status": "success",
        "items_processed": result.get("synced", 0),
        "items_failed": 0,
        "mock": MOCK_MODE,
        "duration_ms": 0,
    })

    return {"success": True, "type": "availability", **result}


@router.post("/hotelrunner/sync/rates")
async def sync_rates():
    if MOCK_MODE:
        result = await mock_sync_rates()
    else:
        result = await mock_sync_rates()

    await db.sync_logs.insert_one({
        "id": new_id(),
        "timestamp": utcnow(),
        "sync_type": "rates",
        "status": "success",
        "items_processed": result.get("synced", 0),
        "items_failed": 0,
        "mock": MOCK_MODE,
        "duration_ms": 0,
    })

    return {"success": True, "type": "rates", **result}


@router.post("/hotelrunner/sync/full")
async def full_sync():
    """Run full two-way sync"""
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


# ==================== WEBHOOK ====================

@router.post("/hotelrunner/webhook")
async def hotelrunner_webhook(payload: dict = {}):
    """Handle incoming webhooks from HotelRunner"""
    event_type = payload.get("event_type", "unknown")

    await db.hotelrunner_webhooks.insert_one({
        "id": new_id(),
        "timestamp": utcnow(),
        "event_type": event_type,
        "payload": payload,
        "processed": False,
    })

    logger.info(f"HotelRunner webhook received: {event_type}")
    return {"success": True, "event_type": event_type}


# ==================== CONFIGURATION ====================

@router.get("/hotelrunner/config")
async def get_config():
    return {
        "mock_mode": MOCK_MODE,
        "api_key_set": bool(HOTELRUNNER_API_KEY),
        "hotel_id_set": bool(HOTELRUNNER_HOTEL_ID),
        "sync_interval_minutes": 5,
        "features": {
            "reservation_sync": True,
            "availability_sync": True,
            "rate_sync": True,
            "webhook_handler": True,
        },
    }
