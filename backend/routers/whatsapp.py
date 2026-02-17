"""
Kozbeyli Konagi - WhatsApp Admin Router
Provides admin endpoints for viewing WhatsApp messages, sessions, and managing configuration.
Webhook processing is handled by routers/webhooks.py.
"""
from fastapi import APIRouter
from typing import Optional
from database import db
from helpers import utcnow, new_id
from pydantic import BaseModel

from services.whatsapp_service import (
    send_text_message as wa_send_text,
    send_template_message as wa_send_template,
    send_interactive_buttons as wa_send_buttons,
    send_checkout_thanks,
    send_reservation_reminder,
    send_welcome_checkin,
    notify_cleaning_team,
    send_room_ready,
    is_configured,
    get_config,
)

router = APIRouter(tags=["whatsapp"])


# ==============================================
# ADMIN ENDPOINTS
# ==============================================

@router.get("/whatsapp/messages")
async def list_whatsapp_messages(session_id: Optional[str] = None, limit: int = 50):
    """WhatsApp mesajlarını listele"""
    query = {}
    if session_id:
        query["session_id"] = session_id
    
    messages = await db.whatsapp_messages.find(
        query, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {"messages": messages}


@router.get("/whatsapp/sessions")
async def list_whatsapp_sessions(limit: int = 50):
    """WhatsApp konuşma oturumlarını listele"""
    pipeline = [
        {"$group": {
            "_id": "$session_id",
            "last_message": {"$last": "$text"},
            "last_time": {"$last": "$created_at"},
            "message_count": {"$sum": 1},
            "contact_name": {"$first": "$contact_name"},
        }},
        {"$sort": {"last_time": -1}},
        {"$limit": limit}
    ]
    
    sessions = await db.whatsapp_messages.aggregate(pipeline).to_list(limit)
    return {"sessions": sessions}


@router.get("/whatsapp/notifications")
async def list_group_notifications(status: Optional[str] = None, limit: int = 50):
    """Grup bildirimlerini listele"""
    query = {}
    if status:
        query["status"] = status
    
    notifications = await db.group_notifications.find(
        query, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {"notifications": notifications}


class SendMessageRequest(BaseModel):
    to: str
    message: str


class SendTemplateRequest(BaseModel):
    to: str
    template_name: str
    language_code: str = "tr"


@router.post("/whatsapp/send")
async def send_message_manual(data: SendMessageRequest):
    """Manuel WhatsApp mesaji gonder"""
    result = await wa_send_text(data.to, data.message)
    return {"success": True, "result": result}


@router.post("/whatsapp/send-template")
async def send_template_manual(data: SendTemplateRequest):
    """Manuel sablon mesaji gonder"""
    result = await wa_send_template(data.to, data.template_name, data.language_code)
    return {"success": True, "result": result}


@router.post("/whatsapp/send-checkout-thanks")
async def api_send_checkout_thanks(phone: str, guest_name: str):
    """Check-out tesekkur mesaji gonder"""
    result = await send_checkout_thanks(phone, guest_name)
    return {"success": True, "result": result}


@router.post("/whatsapp/send-reservation-reminder")
async def api_send_reservation_reminder(phone: str, guest_name: str, check_in_date: str):
    """Rezervasyon hatirlatma mesaji gonder"""
    result = await send_reservation_reminder(phone, guest_name, check_in_date)
    return {"success": True, "result": result}


@router.post("/whatsapp/send-welcome")
async def api_send_welcome(phone: str, guest_name: str, room_number: str):
    """Check-in hos geldiniz mesaji gonder"""
    result = await send_welcome_checkin(phone, guest_name, room_number)
    return {"success": True, "result": result}


@router.post("/whatsapp/notify-cleaning")
async def api_notify_cleaning(phone: str, room_number: str, guest_name: str, priority: str = "Normal"):
    """Temizlik ekibine bildirim gonder"""
    result = await notify_cleaning_team(phone, room_number, guest_name, priority)
    return {"success": True, "result": result}


@router.post("/whatsapp/send-room-ready")
async def api_send_room_ready(phone: str, guest_name: str, room_number: str):
    """Oda hazir bildirimi gonder"""
    result = await send_room_ready(phone, guest_name, room_number)
    return {"success": True, "result": result}


@router.get("/whatsapp/config")
async def get_config_status():
    """WhatsApp yapilandirma durumu"""
    cfg = get_config()
    return {
        "configured": is_configured(),
        "has_token": bool(cfg["access_token"]),
        "has_phone_id": bool(cfg["phone_number_id"]),
        "verify_token": cfg["verify_token"],
    }


@router.get("/whatsapp/templates")
async def list_available_templates():
    """Kullanilabilir WhatsApp sablon listesi"""
    templates = [
        {
            "name": "checkout_thanks_review",
            "description": "Check-out tesekkur + yorum istegi",
            "params": ["guest_name"],
        },
        {
            "name": "reservation_reminder_1day",
            "description": "Rezervasyon hatirlatma (1 gun once)",
            "params": ["guest_name", "check_in_date"],
        },
        {
            "name": "welcome_checkin",
            "description": "Check-in hos geldiniz",
            "params": ["guest_name", "room_number"],
        },
        {
            "name": "cleaning_notification",
            "description": "Temizlik ekibi bildirimi",
            "params": ["room_number", "guest_name", "time", "priority"],
        },
        {
            "name": "room_ready_notification",
            "description": "Oda hazir bildirimi",
            "params": ["guest_name", "room_number"],
        },
    ]
    return {"templates": templates}
