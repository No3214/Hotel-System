from fastapi import APIRouter
from database import db
from helpers import utcnow, new_id
from models import ChatRequest, WhatsAppMessage
from hotel_data import ROOMS, RESTAURANT_MENU, HOTEL_POLICIES, FOCA_LOCAL_GUIDE, GEMINI_SYSTEM_PROMPT

router = APIRouter(tags=["chatbot"])


@router.post("/chatbot")
async def chatbot(data: ChatRequest):
    from gemini_service import get_chat_response, detect_intent

    intent = detect_intent(data.message)
    context = ""

    if intent == "rooms":
        context = f"Oda bilgileri: {ROOMS}"
    elif intent == "menu":
        context = f"Menu: {RESTAURANT_MENU}"
    elif intent == "cancellation":
        context = f"Politikalar: {HOTEL_POLICIES}"
    elif intent == "local_guide":
        context = f"Cevre rehberi: {FOCA_LOCAL_GUIDE}"
    elif intent == "events":
        events = await db.events.find({"is_active": True}, {"_id": 0}).to_list(20)
        context = f"Aktif etkinlikler: {events}" if events else "Su anda aktif etkinlik bulunmuyor."

    response = await get_chat_response(
        message=data.message,
        session_id=data.session_id,
        system_prompt=GEMINI_SYSTEM_PROMPT,
        context=context,
    )

    msg_record = {
        "id": new_id(),
        "session_id": data.session_id,
        "user_message": data.message,
        "ai_response": response,
        "intent": intent,
        "created_at": utcnow(),
    }
    await db.chat_messages.insert_one(msg_record)

    return {
        "response": response,
        "session_id": data.session_id,
        "intent": intent,
    }


@router.get("/chatbot/history/{session_id}")
async def chat_history(session_id: str):
    messages = await db.chat_messages.find(
        {"session_id": session_id}, {"_id": 0}
    ).sort("created_at", 1).to_list(100)
    return {"messages": messages}


@router.delete("/chatbot/session/{session_id}")
async def clear_chat(session_id: str):
    from gemini_service import clear_session
    clear_session(session_id)
    await db.chat_messages.delete_many({"session_id": session_id})
    return {"success": True}
