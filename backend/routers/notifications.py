from fastapi import APIRouter, Request
from datetime import datetime, timezone
from database import db
from helpers import utcnow, new_id
import os

router = APIRouter(tags=["notifications"])

VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY", "")


@router.get("/notifications/vapid-key")
async def get_vapid_key():
    """Return VAPID public key for frontend subscription."""
    return {"publicKey": VAPID_PUBLIC_KEY}


@router.post("/notifications/subscribe")
async def subscribe_push(request: Request):
    """Store push notification subscription in MongoDB."""
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
    """Get today's check-in/check-out notifications."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    checkins = await db.reservations.find({
        "check_in": today,
        "status": {"$in": ["pending", "confirmed"]},
    }, {"_id": 0, "id": 1, "guest_name": 1, "room_id": 1, "room_type": 1}).to_list(50)

    checkouts = await db.reservations.find({
        "check_out": today,
        "status": {"$in": ["confirmed", "checked_in"]},
    }, {"_id": 0, "id": 1, "guest_name": 1, "room_id": 1, "room_type": 1}).to_list(50)

    notifications = []
    for ci in checkins:
        notifications.append({
            "id": f"checkin-{ci.get('id', '')}",
            "type": "check_in",
            "title": "Check-in Hatirlatma",
            "body": f"{ci.get('guest_name', 'Misafir')} - {ci.get('room_type', '')} ({ci.get('room_id', '')})",
        })
    for co in checkouts:
        notifications.append({
            "id": f"checkout-{co.get('id', '')}",
            "type": "check_out",
            "title": "Check-out Hatirlatma",
            "body": f"{co.get('guest_name', 'Misafir')} - {co.get('room_type', '')} ({co.get('room_id', '')})",
        })

    return {
        "date": today,
        "total": len(notifications),
        "checkins": len(checkins),
        "checkouts": len(checkouts),
        "notifications": notifications,
    }


@router.post("/notifications/send-push")
async def send_push_notification(request: Request):
    """Send push notification to all subscribers."""
    body = await request.json()
    title = body.get("title", "Kozbeyli Konagi")
    message = body.get("body", "")
    tag = body.get("tag", "kozbeyli")

    from services.push_service import send_push_to_all
    result = await send_push_to_all(db, title, message, tag)

    await db.notification_logs.insert_one({
        "id": new_id(),
        "type": "push",
        "title": title,
        "body": message,
        "result": result,
        "created_at": utcnow(),
    })
    return {"success": True, **result}


@router.post("/notifications/send-test")
async def send_test_notification():
    """Send a test push notification."""
    from services.push_service import send_push_to_all
    result = await send_push_to_all(
        db,
        title="Test Bildirimi",
        body="Kozbeyli Konagi bildirim sistemi calisiyor!",
        tag="test",
    )

    await db.notification_logs.insert_one({
        "id": new_id(),
        "type": "test",
        "title": "Test Bildirimi",
        "body": "Kozbeyli Konagi bildirim sistemi calisiyor!",
        "result": result,
        "created_at": utcnow(),
    })
    return {
        "success": True,
        "notification": {
            "title": "Test Bildirimi",
            "body": "Kozbeyli Konagi bildirim sistemi calisiyor!",
        },
        **result,
    }


@router.get("/notifications/subscribers")
async def get_subscriber_count():
    """Get push notification subscriber count."""
    count = await db.push_subscriptions.count_documents({})
    return {"count": count}
