"""
Kozbeyli Konagi - Unified Webhook Router
Handles incoming webhooks from WhatsApp and Instagram platforms.
Processes messages through the chatbot engine and sends responses.
"""
import hmac
import hashlib
import logging
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Query, Header
from database import db
from helpers import utcnow, new_id
from chatbot_engine import process_chatbot_message

from services.whatsapp_service import (
    get_config as get_wa_config,
    send_text_message as wa_send_text,
    send_interactive_buttons as wa_send_buttons,
    format_phone,
)
from services.instagram_service import (
    get_config as get_ig_config,
    send_text_message as ig_send_text,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["webhooks"])


# ==============================================
# WHATSAPP WEBHOOK
# ==============================================

@router.get("/webhooks/whatsapp")
async def verify_whatsapp_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """WhatsApp webhook verification (Meta subscription handshake)."""
    cfg = get_wa_config()
    if hub_mode == "subscribe" and hub_token == cfg["verify_token"]:
        logger.info("WhatsApp webhook verified successfully")
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(hub_challenge or "")
    raise HTTPException(403, "Verification failed")


@router.post("/webhooks/whatsapp")
async def receive_whatsapp_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
):
    """Process incoming WhatsApp messages and status updates."""
    body_bytes = await request.body()
    import json as _json
    body = _json.loads(body_bytes)

    # Signature verification (optional - when APP_SECRET is set)
    cfg = get_wa_config()
    if cfg["app_secret"] and x_hub_signature_256:
        expected = hmac.new(
            cfg["app_secret"].encode(), body_bytes, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(f"sha256={expected}", x_hub_signature_256):
            raise HTTPException(401, "Invalid signature")

    # Log raw payload
    await db.whatsapp_incoming_raw.insert_one({
        "id": new_id(),
        "body": body,
        "created_at": utcnow(),
    })

    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            # Process incoming messages
            for message in value.get("messages", []):
                await _process_whatsapp_message(message, value)

            # Process status updates
            for status_update in value.get("statuses", []):
                await _process_whatsapp_status(status_update)

    return {"status": "processed"}


async def _process_whatsapp_message(message: dict, value: dict):
    """Handle a single incoming WhatsApp message."""
    from_number = message.get("from", "")
    message_type = message.get("type", "")
    message_id = message.get("id", "")

    # Extract text content
    text = ""
    if message_type == "text":
        text = message.get("text", {}).get("body", "")
    elif message_type == "interactive":
        interactive = message.get("interactive", {})
        if "button_reply" in interactive:
            text = interactive["button_reply"].get("title", "")
        elif "list_reply" in interactive:
            text = interactive["list_reply"].get("title", "")
    elif message_type == "image":
        text = message.get("image", {}).get("caption", "[Gorsel mesaj]")
    elif message_type == "location":
        loc = message.get("location", {})
        text = f"[Konum: {loc.get('latitude')}, {loc.get('longitude')}]"

    if not text:
        return

    # Contact info
    contacts = value.get("contacts", [{}])
    contact_name = contacts[0].get("profile", {}).get("name", "Misafir") if contacts else "Misafir"
    session_id = f"wa_{from_number}"

    # Store incoming message
    await db.whatsapp_messages.insert_one({
        "id": new_id(),
        "message_id": message_id,
        "session_id": session_id,
        "from": from_number,
        "contact_name": contact_name,
        "text": text,
        "type": message_type,
        "direction": "incoming",
        "created_at": utcnow(),
    })

    # Process through chatbot engine
    result = await process_chatbot_message(
        message=text,
        session_id=session_id,
        platform="whatsapp",
        language="tr",
    )

    # Get response text
    response_text = ""
    if result and result.get("response"):
        response_text = result["response"]
    else:
        # Fall back to AI
        from gemini_service import get_chat_response
        from hotel_data import GEMINI_SYSTEM_PROMPT

        response_text = await get_chat_response(
            message=text,
            session_id=session_id,
            system_prompt=GEMINI_SYSTEM_PROMPT,
            context=f"WhatsApp uzerinden gelen misafir mesaji. Misafir: {contact_name}",
        )

    # Send response
    await wa_send_text(from_number, response_text)

    # Store outgoing message
    await db.whatsapp_messages.insert_one({
        "id": new_id(),
        "session_id": session_id,
        "to": from_number,
        "text": response_text,
        "direction": "outgoing",
        "created_at": utcnow(),
    })

    # Notify group if reservation was created
    if result and result.get("reservation_created"):
        await _notify_reservation_group(result.get("reservation", {}))


async def _process_whatsapp_status(status_update: dict):
    """Handle message delivery/read status updates."""
    wa_msg_id = status_update.get("id", "")
    new_status = status_update.get("status", "")  # sent, delivered, read, failed

    if wa_msg_id:
        await db.whatsapp_messages.update_one(
            {"wa_message_id": wa_msg_id},
            {"$set": {"status": new_status, "status_updated_at": utcnow()}},
        )
        logger.info(f"WhatsApp message {wa_msg_id} status: {new_status}")


async def _notify_reservation_group(reservation: dict):
    """Send group notification for new reservations."""
    import os
    from chatbot_engine import format_date_turkish

    message = f"""*Yeni Masa Rezervasyonu*

Tarih: {format_date_turkish(reservation.get('date', ''))}
Saat: {reservation.get('time', '')}
Kisi: {reservation.get('party_size', '')}
Isim: {reservation.get('guest_name', '')}
Telefon: {reservation.get('phone', '')}
Masa: {reservation.get('table_name', 'Atanacak')}

WhatsApp Bot ile alindi
Rez No: #{reservation.get('id', '')[:8].upper()}"""

    await db.group_notifications.insert_one({
        "id": new_id(),
        "type": "table_reservation",
        "reservation_id": reservation.get("id"),
        "message": message,
        "status": "pending",
        "created_at": utcnow(),
    })

    group_number = os.environ.get("WHATSAPP_GROUP_NUMBER", "")
    if group_number:
        await wa_send_text(group_number, message)


# ==============================================
# INSTAGRAM WEBHOOK
# ==============================================

@router.get("/webhooks/instagram")
async def verify_instagram_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """Instagram webhook verification."""
    cfg = get_ig_config()
    if hub_mode == "subscribe" and hub_token == cfg["verify_token"]:
        logger.info("Instagram webhook verified successfully")
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(hub_challenge or "")
    raise HTTPException(403, "Verification failed")


@router.post("/webhooks/instagram")
async def receive_instagram_webhook(request: Request):
    """Process incoming Instagram Direct Messages."""
    body = await request.json()

    await db.instagram_incoming_raw.insert_one({
        "id": new_id(),
        "body": body,
        "created_at": utcnow(),
    })

    for entry in body.get("entry", []):
        messaging_list = entry.get("messaging", [])
        for event in messaging_list:
            sender_id = event.get("sender", {}).get("id", "")
            message_data = event.get("message", {})

            if not sender_id or not message_data:
                continue

            text = message_data.get("text", "")
            if not text:
                # Could be an attachment
                attachments = message_data.get("attachments", [])
                if attachments:
                    text = f"[{attachments[0].get('type', 'attachment')}]"
                else:
                    continue

            ig_message_id = message_data.get("mid", "")
            session_id = f"ig_{sender_id}"

            # Store incoming
            await db.instagram_messages.insert_one({
                "id": new_id(),
                "session_id": session_id,
                "user_id": sender_id,
                "ig_message_id": ig_message_id,
                "text": text,
                "direction": "incoming",
                "created_at": utcnow(),
            })

            # Process through chatbot
            result = await process_chatbot_message(
                message=text,
                session_id=session_id,
                platform="instagram",
                language="tr",
            )

            response_text = ""
            if result and result.get("response"):
                response_text = result["response"]
            else:
                from gemini_service import get_chat_response
                from hotel_data import GEMINI_SYSTEM_PROMPT

                response_text = await get_chat_response(
                    message=text,
                    session_id=session_id,
                    system_prompt=GEMINI_SYSTEM_PROMPT,
                    context="Instagram DM uzerinden gelen mesaj.",
                )

            # Send response
            await ig_send_text(sender_id, response_text)

            # Store outgoing
            await db.instagram_messages.insert_one({
                "id": new_id(),
                "session_id": session_id,
                "user_id": sender_id,
                "text": response_text,
                "direction": "outgoing",
                "created_at": utcnow(),
            })

    return {"status": "processed"}


# ==============================================
# ADMIN/STATUS ENDPOINTS
# ==============================================

@router.get("/webhooks/status")
async def webhook_status():
    """Get configuration status for both platforms."""
    from services.whatsapp_service import is_configured as wa_configured
    from services.instagram_service import is_configured as ig_configured

    wa_msg_count = await db.whatsapp_messages.count_documents({})
    ig_msg_count = await db.instagram_messages.count_documents({})

    return {
        "whatsapp": {
            "configured": wa_configured(),
            "verify_token": get_wa_config()["verify_token"],
            "total_messages": wa_msg_count,
        },
        "instagram": {
            "configured": ig_configured(),
            "verify_token": get_ig_config()["verify_token"],
            "total_messages": ig_msg_count,
        },
    }


@router.get("/webhooks/instagram/messages")
async def list_instagram_messages(session_id: Optional[str] = None, limit: int = 50):
    """List Instagram messages."""
    query = {}
    if session_id:
        query["session_id"] = session_id
    messages = await db.instagram_messages.find(
        query, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return {"messages": messages}


@router.get("/webhooks/instagram/sessions")
async def list_instagram_sessions(limit: int = 50):
    """List Instagram conversation sessions."""
    pipeline = [
        {"$group": {
            "_id": "$session_id",
            "last_message": {"$last": "$text"},
            "last_time": {"$last": "$created_at"},
            "message_count": {"$sum": 1},
            "user_id": {"$first": "$user_id"},
        }},
        {"$sort": {"last_time": -1}},
        {"$limit": limit},
    ]
    sessions = await db.instagram_messages.aggregate(pipeline).to_list(limit)
    return {"sessions": sessions}
