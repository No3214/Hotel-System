"""
Kozbeyli Konagi - WhatsApp Business API Service
Production-grade service for WhatsApp Cloud API messaging.
Supports: text, template, interactive, media messages.
Mock mode when credentials are not configured.
"""
import os
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any

import httpx

from database import db
from helpers import utcnow, new_id

logger = logging.getLogger(__name__)

# ==============================================
# CONFIGURATION
# ==============================================

API_VERSION = "v18.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"


def get_config():
    return {
        "access_token": os.environ.get("WHATSAPP_ACCESS_TOKEN", ""),
        "phone_number_id": os.environ.get("WHATSAPP_PHONE_NUMBER_ID", ""),
        "business_account_id": os.environ.get("WHATSAPP_BUSINESS_ACCOUNT_ID", ""),
        "app_secret": os.environ.get("WHATSAPP_APP_SECRET", ""),
        "verify_token": os.environ.get("WHATSAPP_VERIFY_TOKEN", "kozbeyli_verify_2026"),
    }


def is_configured() -> bool:
    cfg = get_config()
    return bool(cfg["access_token"] and cfg["phone_number_id"])


def format_phone(phone: str) -> str:
    """Normalize phone to international digits-only format (e.g. 905321234567)"""
    digits = "".join(c for c in phone if c.isdigit())
    if digits.startswith("0") and len(digits) == 11:
        digits = "90" + digits[1:]
    elif not digits.startswith("90") and len(digits) == 10:
        digits = "90" + digits
    return digits


# ==============================================
# CORE API METHODS
# ==============================================

async def _api_request(method: str, endpoint: str, payload: dict) -> Dict[str, Any]:
    """Make a request to the WhatsApp Cloud API."""
    cfg = get_config()
    url = f"{BASE_URL}/{cfg['phone_number_id']}{endpoint}"
    headers = {
        "Authorization": f"Bearer {cfg['access_token']}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.request(method, url, headers=headers, json=payload)
        if resp.status_code == 429:
            logger.warning("WhatsApp API rate limit hit")
        return resp.json()


async def _log_message(
    to_phone: str,
    direction: str,
    message_type: str = "text",
    content: str = "",
    template_name: str = "",
    wa_message_id: str = "",
    status: str = "sent",
    session_id: str = "",
):
    """Log WhatsApp message to DB."""
    await db.whatsapp_messages.insert_one({
        "id": new_id(),
        "session_id": session_id or f"wa_{to_phone}",
        "to" if direction == "outgoing" else "from": to_phone,
        "text": content[:1000] if content else "",
        "type": message_type,
        "template_name": template_name,
        "wa_message_id": wa_message_id,
        "direction": direction,
        "status": status,
        "created_at": utcnow(),
    })


# ==============================================
# SEND METHODS
# ==============================================

async def send_text_message(to: str, message: str, preview_url: bool = False) -> Dict[str, Any]:
    """Send a free-form text message (within 24h window or session)."""
    phone = format_phone(to)

    if not is_configured():
        await _log_message(phone, "outgoing", "text", message, status="mock_sent")
        return {"status": "mock", "to": phone, "message": message}

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "text",
        "text": {"preview_url": preview_url, "body": message},
    }
    result = await _api_request("POST", "/messages", payload)
    wa_id = (result.get("messages") or [{}])[0].get("id", "")
    await _log_message(phone, "outgoing", "text", message, wa_message_id=wa_id)
    return result


async def send_template_message(
    to: str,
    template_name: str,
    language_code: str = "tr",
    parameters: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Send an approved template message."""
    phone = format_phone(to)

    if not is_configured():
        await _log_message(phone, "outgoing", "template", f"[template:{template_name}]", template_name=template_name, status="mock_sent")
        return {"status": "mock", "template": template_name, "to": phone}

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
        },
    }
    if parameters:
        payload["template"]["components"] = parameters

    result = await _api_request("POST", "/messages", payload)
    wa_id = (result.get("messages") or [{}])[0].get("id", "")
    await _log_message(phone, "outgoing", "template", f"[template:{template_name}]", template_name=template_name, wa_message_id=wa_id)
    return result


async def send_interactive_buttons(
    to: str,
    header: str,
    body: str,
    buttons: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Send an interactive button message (max 3 buttons)."""
    phone = format_phone(to)

    if not is_configured():
        await _log_message(phone, "outgoing", "interactive", body, status="mock_sent")
        return {"status": "mock", "to": phone}

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {"type": "text", "text": header},
            "body": {"text": body},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": b["id"], "title": b["title"]}}
                    for b in buttons[:3]
                ]
            },
        },
    }
    result = await _api_request("POST", "/messages", payload)
    wa_id = (result.get("messages") or [{}])[0].get("id", "")
    await _log_message(phone, "outgoing", "interactive", body, wa_message_id=wa_id)
    return result


async def send_media_message(
    to: str,
    media_type: str,
    media_url: str,
    caption: Optional[str] = None,
) -> Dict[str, Any]:
    """Send image/document/video message."""
    phone = format_phone(to)

    if not is_configured():
        await _log_message(phone, "outgoing", media_type, caption or media_url, status="mock_sent")
        return {"status": "mock", "to": phone}

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": media_type,
        media_type: {"link": media_url},
    }
    if caption:
        payload[media_type]["caption"] = caption

    result = await _api_request("POST", "/messages", payload)
    await _log_message(phone, "outgoing", media_type, caption or media_url)
    return result


# ==============================================
# HOTEL-SPECIFIC CONVENIENCE METHODS
# ==============================================

async def send_checkout_thanks(phone: str, guest_name: str):
    """Check-out sonrasi tesekkur + yorum istegi."""
    params = [
        {"type": "header", "parameters": [{"type": "text", "text": guest_name}]},
        {"type": "body", "parameters": [{"type": "text", "text": guest_name}]},
    ]
    return await send_template_message(phone, "checkout_thanks_review", parameters=params)


async def send_reservation_reminder(phone: str, guest_name: str, check_in_date: str):
    """Rezervasyon hatirlatma (1 gun once)."""
    params = [
        {"type": "body", "parameters": [
            {"type": "text", "text": guest_name},
            {"type": "text", "text": check_in_date},
        ]},
    ]
    return await send_template_message(phone, "reservation_reminder_1day", parameters=params)


async def send_welcome_checkin(phone: str, guest_name: str, room_number: str):
    """Check-in hos geldiniz mesaji."""
    params = [
        {"type": "body", "parameters": [
            {"type": "text", "text": guest_name},
            {"type": "text", "text": room_number},
        ]},
    ]
    return await send_template_message(phone, "welcome_checkin", parameters=params)


async def notify_cleaning_team(phone: str, room_number: str, guest_name: str, priority: str = "Normal"):
    """Temizlik ekibine bildirim."""
    now_str = datetime.now(timezone.utc).strftime("%H:%M")
    params = [
        {"type": "body", "parameters": [
            {"type": "text", "text": room_number},
            {"type": "text", "text": guest_name},
            {"type": "text", "text": now_str},
            {"type": "text", "text": priority},
        ]},
    ]
    return await send_template_message(phone, "cleaning_notification", parameters=params)


async def send_room_ready(phone: str, guest_name: str, room_number: str):
    """Oda hazir bildirimi."""
    params = [
        {"type": "body", "parameters": [
            {"type": "text", "text": guest_name},
            {"type": "text", "text": room_number},
        ]},
    ]
    return await send_template_message(phone, "room_ready_notification", parameters=params)


async def send_reservation_confirmation(reservation_data: dict):
    """Yeni rezervasyon onay mesaji."""
    guest_name = reservation_data.get("guest_name", "Misafir")
    phone = reservation_data.get("phone", "")
    check_in = reservation_data.get("check_in", "")
    check_out = reservation_data.get("check_out", "")

    if not phone:
        return None

    msg = (
        f"*Rezervasyon Onay*\n\n"
        f"Merhaba {guest_name},\n\n"
        f"Rezervasyonunuz basariyla olusturuldu.\n\n"
        f"Giris: {check_in}\n"
        f"Cikis: {check_out}\n\n"
        f"Sorulariniz icin: +90 532 234 26 86"
    )
    return await send_text_message(phone, msg)
