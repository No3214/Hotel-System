from fastapi import APIRouter
from typing import Optional
from database import db
from helpers import utcnow, new_id
from models import WhatsAppMessage
from hotel_data import GEMINI_SYSTEM_PROMPT

router = APIRouter(tags=["messages"])


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(data: WhatsAppMessage):
    from gemini_service import get_chat_response, detect_intent

    session_id = f"wa-{data.from_number}"
    intent = detect_intent(data.message)

    response = await get_chat_response(
        message=data.message,
        session_id=session_id,
        system_prompt=GEMINI_SYSTEM_PROMPT,
    )

    msg = {
        "id": new_id(),
        "platform": "whatsapp",
        "from_number": data.from_number,
        "sender_name": data.sender_name,
        "message": data.message,
        "response": response,
        "intent": intent,
        "created_at": utcnow(),
    }
    await db.messages.insert_one(msg)

    return {"reply": response, "intent": intent}


@router.get("/whatsapp/messages")
async def list_whatsapp_messages(limit: int = 50):
    msgs = await db.messages.find(
        {"platform": "whatsapp"}, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return {"messages": msgs}


@router.post("/instagram/webhook")
async def instagram_webhook(data: dict):
    from gemini_service import get_chat_response

    msg_text = data.get("message", "")
    sender = data.get("sender", "unknown")
    session_id = f"ig-{sender}"

    response = await get_chat_response(
        message=msg_text,
        session_id=session_id,
        system_prompt=GEMINI_SYSTEM_PROMPT,
    )

    msg = {
        "id": new_id(),
        "platform": "instagram",
        "sender": sender,
        "message": msg_text,
        "response": response,
        "created_at": utcnow(),
    }
    await db.messages.insert_one(msg)

    return {"reply": response}


@router.get("/messages")
async def list_all_messages(platform: Optional[str] = None, limit: int = 50):
    query = {"platform": platform} if platform else {}
    msgs = await db.messages.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return {"messages": msgs}
