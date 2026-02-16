from fastapi import APIRouter, Request
from typing import Optional
from datetime import datetime, timezone
from database import db
from helpers import utcnow, new_id

router = APIRouter(tags=["notifications"])


@router.post("/notifications/subscribe")
async def subscribe_push(request: Request):
    """Store push notification subscription."""
    body = await request.json()
    subscription = body.get("subscription")
    user_id = body.get("user_id")

    if not subscription:
        return {"success": False, "error": "Abonelik bilgisi gerekli"}

    await db.push_subscriptions.update_one(
        {"endpoint": subscription.get("endpoint")},
        {"$set": {
            "subscription": subscription,
            "user_id": user_id,
            "updated_at": utcnow(),
        }, "$setOnInsert": {
            "id": new_id(),
            "created_at": utcnow(),
        }},
        upsert=True,
    )
    return {"success": True, "message": "Bildirim aboneligi kaydedildi"}


@router.post("/notifications/unsubscribe")
async def unsubscribe_push(request: Request):
    """Remove push notification subscription."""
    body = await request.json()
    endpoint = body.get("endpoint")
    if endpoint:
        await db.push_subscriptions.delete_one({"endpoint": endpoint})
    return {"success": True, "message": "Bildirim aboneligi kaldirildi"}


@router.get("/notifications/today")
async def get_today_notifications():
    """Get today's check-in/check-out notifications for push."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    checkins = await db.reservations.find({
        "check_in": today,
        "status": {"$in": ["pending", "confirmed"]},
    }, {"_id": 0, "id": 1, "guest_name": 1, "room_id": 1, "room_type": 1, "check_in": 1}).to_list(50)

    checkouts = await db.reservations.find({
        "check_out": today,
        "status": {"$in": ["confirmed", "checked_in"]},
    }, {"_id": 0, "id": 1, "guest_name": 1, "room_id": 1, "room_type": 1, "check_out": 1}).to_list(50)

    notifications = []

    for ci in checkins:
        notifications.append({
            "id": f"checkin-{ci.get('id', '')}",
            "type": "check_in",
            "title": "Check-in Hatirlatma",
            "body": f"{ci.get('guest_name', 'Misafir')} - {ci.get('room_type', '')} ({ci.get('room_id', '')})",
            "time": ci.get("check_in"),
        })

    for co in checkouts:
        notifications.append({
            "id": f"checkout-{co.get('id', '')}",
            "type": "check_out",
            "title": "Check-out Hatirlatma",
            "body": f"{co.get('guest_name', 'Misafir')} - {co.get('room_type', '')} ({co.get('room_id', '')})",
            "time": co.get("check_out"),
        })

    return {
        "date": today,
        "total": len(notifications),
        "checkins": len(checkins),
        "checkouts": len(checkouts),
        "notifications": notifications,
    }


@router.post("/notifications/send-test")
async def send_test_notification():
    """Send a test notification entry."""
    await db.notification_logs.insert_one({
        "id": new_id(),
        "type": "test",
        "title": "Test Bildirimi",
        "body": "Kozbeyli Konagi bildirim sistemi calisiyor!",
        "status": "sent",
        "created_at": utcnow(),
    })
    return {
        "success": True,
        "notification": {
            "title": "Test Bildirimi",
            "body": "Kozbeyli Konagi bildirim sistemi calisiyor!",
        },
    }
