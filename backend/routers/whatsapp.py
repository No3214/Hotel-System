"""
Kozbeyli Konagi - WhatsApp Webhook Router
WhatsApp Business Cloud API Integration
"""
from fastapi import APIRouter, Request, HTTPException, Query
from typing import Optional
from database import db
from helpers import utcnow, new_id
from chatbot_engine import process_chatbot_message
from pydantic import BaseModel
import os
import httpx

router = APIRouter(tags=["whatsapp"])

# ==============================================
# CONFIGURATION
# ==============================================

def get_whatsapp_config():
    return {
        "token": os.environ.get("WHATSAPP_TOKEN", ""),
        "phone_number_id": os.environ.get("WHATSAPP_PHONE_NUMBER_ID", ""),
        "verify_token": os.environ.get("WHATSAPP_VERIFY_TOKEN", "kozbeyli_verify_2026"),
        "business_account_id": os.environ.get("WHATSAPP_BUSINESS_ID", ""),
    }


def is_configured():
    config = get_whatsapp_config()
    return bool(config["token"] and config["phone_number_id"])


# ==============================================
# WHATSAPP API FUNCTIONS
# ==============================================

async def send_whatsapp_message(to: str, message: str):
    """WhatsApp mesajı gönder"""
    config = get_whatsapp_config()
    
    if not is_configured():
        # Mock mode - sadece kaydet
        await db.whatsapp_outgoing.insert_one({
            "id": new_id(),
            "to": to,
            "message": message,
            "status": "mock_sent",
            "created_at": utcnow(),
        })
        return {"status": "mock", "message": "WhatsApp credentials not configured"}
    
    url = f"https://graph.facebook.com/v18.0/{config['phone_number_id']}/messages"
    headers = {
        "Authorization": f"Bearer {config['token']}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        
        # Log
        await db.whatsapp_outgoing.insert_one({
            "id": new_id(),
            "to": to,
            "message": message,
            "status": "sent" if response.status_code == 200 else "failed",
            "response_code": response.status_code,
            "created_at": utcnow(),
        })
        
        return response.json()


async def send_interactive_buttons(to: str, body_text: str, buttons: list):
    """WhatsApp butonlu mesaj gönder"""
    config = get_whatsapp_config()
    
    if not is_configured():
        return {"status": "mock"}
    
    url = f"https://graph.facebook.com/v18.0/{config['phone_number_id']}/messages"
    headers = {
        "Authorization": f"Bearer {config['token']}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": btn["id"], "title": btn["title"]}}
                    for btn in buttons[:3]  # Max 3 buttons
                ]
            }
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        return response.json()


async def send_to_group(group_id: str, message: str):
    """WhatsApp grubuna mesaj gönder"""
    # Not: WhatsApp Business API doğrudan grup mesajı desteklemiyor
    # Bunun yerine webhook ile çalışan bir sistem kullanıyoruz
    
    notification = {
        "id": new_id(),
        "group_id": group_id,
        "message": message,
        "status": "pending",
        "created_at": utcnow(),
    }
    await db.group_notifications.insert_one(notification)
    return notification


# ==============================================
# WEBHOOK ENDPOINTS
# ==============================================

@router.get("/webhook/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """WhatsApp webhook doğrulama"""
    config = get_whatsapp_config()
    
    if hub_mode == "subscribe" and hub_token == config["verify_token"]:
        return int(hub_challenge) if hub_challenge else ""
    
    raise HTTPException(403, "Verification failed")


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """WhatsApp gelen mesaj webhook'u"""
    body = await request.json()
    
    # Log all incoming
    await db.whatsapp_incoming_raw.insert_one({
        "id": new_id(),
        "body": body,
        "created_at": utcnow(),
    })
    
    try:
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        
        # Mesaj var mı?
        messages = value.get("messages", [])
        if not messages:
            return {"status": "no_message"}
        
        message = messages[0]
        from_number = message.get("from", "")
        message_type = message.get("type", "")
        message_id = message.get("id", "")
        
        # Metin mesajı
        text = ""
        if message_type == "text":
            text = message.get("text", {}).get("body", "")
        elif message_type == "interactive":
            interactive = message.get("interactive", {})
            if "button_reply" in interactive:
                text = interactive["button_reply"].get("title", "")
            elif "list_reply" in interactive:
                text = interactive["list_reply"].get("title", "")
        
        if not text:
            return {"status": "unsupported_message_type"}
        
        # Kişi bilgisi
        contacts = value.get("contacts", [{}])
        contact_name = contacts[0].get("profile", {}).get("name", "Misafir") if contacts else "Misafir"
        
        # Session ID oluştur (telefon numarasından)
        session_id = f"wa_{from_number}"
        
        # Gelen mesajı kaydet
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
        
        # Chatbot engine ile işle
        result = await process_chatbot_message(
            message=text,
            session_id=session_id,
            platform="whatsapp",
            language="tr"
        )
        
        response_text = ""
        
        if result and result.get("response"):
            response_text = result["response"]
        else:
            # AI yanıtı al
            from gemini_service import get_chat_response
            from hotel_data import GEMINI_SYSTEM_PROMPT
            
            response_text = await get_chat_response(
                message=text,
                session_id=session_id,
                system_prompt=GEMINI_SYSTEM_PROMPT,
                context="WhatsApp uzerinden gelen misafir mesaji.",
            )
        
        # Yanıtı gönder
        await send_whatsapp_message(from_number, response_text)
        
        # Yanıtı kaydet
        await db.whatsapp_messages.insert_one({
            "id": new_id(),
            "session_id": session_id,
            "to": from_number,
            "text": response_text,
            "direction": "outgoing",
            "created_at": utcnow(),
        })
        
        # Rezervasyon oluşturulduysa grup bildirimi gönder
        if result and result.get("reservation_created"):
            reservation = result.get("reservation", {})
            await notify_reservation_group(reservation)
        
        return {"status": "processed"}
        
    except Exception as e:
        print(f"WhatsApp webhook error: {e}")
        return {"status": "error", "message": str(e)}


async def notify_reservation_group(reservation: dict):
    """Rezervasyon grubuna bildirim gönder"""
    from chatbot_engine import format_date_turkish
    
    message = f"""🍽️ *Yeni Masa Rezervasyonu*

📅 {format_date_turkish(reservation.get('date', ''))}
⏰ {reservation.get('time', '')}
👥 {reservation.get('party_size', '')} kişi
📝 {reservation.get('guest_name', '')}
📱 {reservation.get('phone', '')}
🪑 {reservation.get('table_name', 'Atanacak')}

_WhatsApp Bot ile alındı_
Rezervasyon No: #{reservation.get('id', '')[:8].upper()}"""
    
    # Grup bildirimi kaydet (admin panelden görülecek)
    await db.group_notifications.insert_one({
        "id": new_id(),
        "type": "table_reservation",
        "reservation_id": reservation.get("id"),
        "message": message,
        "status": "pending",
        "created_at": utcnow(),
    })
    
    # Eğer grup WhatsApp numarası ayarlıysa gönder
    group_number = os.environ.get("WHATSAPP_GROUP_NUMBER", "")
    if group_number:
        await send_whatsapp_message(group_number, message)


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


@router.post("/whatsapp/send")
async def send_message_manual(data: SendMessageRequest):
    """Manuel WhatsApp mesajı gönder"""
    result = await send_whatsapp_message(data.to, data.message)
    return {"success": True, "result": result}


@router.get("/whatsapp/config")
async def get_config_status():
    """WhatsApp yapılandırma durumu"""
    config = get_whatsapp_config()
    return {
        "configured": is_configured(),
        "has_token": bool(config["token"]),
        "has_phone_id": bool(config["phone_number_id"]),
        "verify_token": config["verify_token"],
    }
