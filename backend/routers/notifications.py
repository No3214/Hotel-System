from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from database import db
from helpers import utcnow, new_id
import os

router = APIRouter(tags=["notifications"])


class PushSubscribeRequest(BaseModel):
    subscription: dict
    user_id: Optional[str] = None


class PushUnsubscribeRequest(BaseModel):
    endpoint: str


class SendPushRequest(BaseModel):
    title: str = "Kozbeyli Konagi"
    body: str = ""
    tag: str = "kozbeyli"


class InAppNotificationRequest(BaseModel):
    type: str = "info"
    title: str
    body: str = ""
    link: Optional[str] = None

VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY", "")


@router.get("/notifications/vapid-key")
async def get_vapid_key():
    """Return VAPID public key for frontend subscription."""
    return {"publicKey": VAPID_PUBLIC_KEY}


@router.post("/notifications/subscribe")
async def subscribe_push(data: PushSubscribeRequest):
    """Store push notification subscription in MongoDB."""
    await db.push_subscriptions.update_one(
        {"endpoint": data.subscription.get("endpoint")},
        {"$set": {
            "subscription": data.subscription,
            "user_id": data.user_id,
            "updated_at": utcnow(),
        }, "$setOnInsert": {
            "id": new_id(),
            "created_at": utcnow(),
        }},
        upsert=True,
    )
    return {"success": True, "message": "Bildirim aboneligi kaydedildi"}


@router.post("/notifications/unsubscribe")
async def unsubscribe_push(data: PushUnsubscribeRequest):
    """Remove push notification subscription."""
    await db.push_subscriptions.delete_one({"endpoint": data.endpoint})
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
async def send_push_notification(data: SendPushRequest):
    """Send push notification to all subscribers."""
    from services.push_service import send_push_to_all
    result = await send_push_to_all(db, data.title, data.body, data.tag)

    await db.notification_logs.insert_one({
        "id": new_id(),
        "type": "push",
        "title": data.title,
        "body": data.body,
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


# ==================== IN-APP NOTIFICATION HISTORY ====================

@router.get("/notifications/history")
async def get_notification_history(limit: int = 50, offset: int = 0, unread_only: bool = False):
    """In-app bildirim gecmisi - tum bildirimler (push, sistem, olay)."""
    query = {}
    if unread_only:
        query["read"] = False

    total = await db.in_app_notifications.count_documents(query)
    notifications = await db.in_app_notifications.find(
        query, {"_id": 0}
    ).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)

    unread_count = await db.in_app_notifications.count_documents({"read": False})

    return {
        "total": total,
        "unread_count": unread_count,
        "notifications": notifications,
    }


@router.post("/notifications/in-app")
async def create_in_app_notification(data: InAppNotificationRequest):
    """Yeni in-app bildirim olustur."""
    notification = {
        "id": new_id(),
        "type": data.type,
        "title": data.title,
        "body": data.body,
        "link": data.link,
        "read": False,
        "created_at": utcnow(),
    }
    await db.in_app_notifications.insert_one(notification)
    return {"success": True, "notification": {k: v for k, v in notification.items() if k != "_id"}}


@router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Bildirimi okundu olarak isaretle."""
    result = await db.in_app_notifications.update_one(
        {"id": notification_id},
        {"$set": {"read": True, "read_at": utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Bildirim bulunamadi")
    return {"success": True}


@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read():
    """Tum bildirimleri okundu olarak isaretle."""
    result = await db.in_app_notifications.update_many(
        {"read": False},
        {"$set": {"read": True, "read_at": utcnow()}}
    )
    return {"success": True, "updated": result.modified_count}


@router.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: str):
    """Bildirimi sil."""
    result = await db.in_app_notifications.delete_one({"id": notification_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Bildirim bulunamadi")
    return {"success": True}


@router.delete("/notifications/history/clear")
async def clear_notification_history():
    """Tum bildirim gecmisini temizle (okunmus olanlari sil)."""
    result = await db.in_app_notifications.delete_many({"read": True})
    return {"success": True, "deleted": result.deleted_count}
