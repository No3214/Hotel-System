from fastapi import APIRouter, Request
from database import db
from helpers import utcnow, new_id
from models import ChatRequest, WhatsAppMessage
from pydantic import BaseModel
from typing import Optional
from hotel_data import ROOMS, RESTAURANT_MENU, HOTEL_POLICIES, FOCA_LOCAL_GUIDE, GEMINI_SYSTEM_PROMPT
from chatbot_engine import (
    process_chatbot_message, detect_intent, route_to_agent,
    ConversationFlow, ConversationState
)
from anti_hallucination import sanitize_response
from rate_limiter import rate_limit_or_raise

router = APIRouter(tags=["chatbot"])

class TranslateRequest(BaseModel):
    message: str
    target_language: str = "tr"  # Usually we want to translate foreign messages to Turkish for the staff
    hotel_context: Optional[str] = None # E.g. "Guest is asking for early checkin, we are full"


@router.post("/chatbot")
async def chatbot(data: ChatRequest, request: Request):
    from gemini_service import get_chat_response

    # Rate limit kontrolu
    rate_limit_or_raise(request, "chatbot", data.session_id)
    
    # 1. Akıllı chatbot engine ile işle
    engine_result = await process_chatbot_message(
        message=data.message,
        session_id=data.session_id,
        platform="web",
        language="tr"
    )
    
    # 2. Engine yanıt verdiyse kullan
    if engine_result and engine_result.get("response"):
        intent = engine_result.get("intent", "auto_reply")
        response = engine_result["response"]
        
        # Mesajı kaydet
        msg_record = {
            "id": new_id(),
            "session_id": data.session_id,
            "user_message": data.message,
            "ai_response": response,
            "intent": intent,
            "source": "engine",
            "created_at": utcnow(),
        }
        await db.chat_messages.insert_one(msg_record)
        
        return {
            "response": response,
            "session_id": data.session_id,
            "intent": intent,
            "reservation_created": engine_result.get("reservation_created", False),
        }
    
    # 3. Engine yanıt vermediyse AI'ya yönlendir
    intent = detect_intent(data.message)
    agent = route_to_agent(data.message)
    context = ""

    if intent == "rooms" or agent.value == "reservation":
        context = f"Oda bilgileri: {ROOMS}"
    elif intent == "menu" or agent.value == "restaurant":
        context = f"Menu: {RESTAURANT_MENU}"
    elif intent == "cancellation":
        context = f"Politikalar: {HOTEL_POLICIES}"
    elif intent == "local_guide" or agent.value == "concierge":
        context = f"Cevre rehberi: {FOCA_LOCAL_GUIDE}"
    elif intent == "events" or agent.value == "events":
        events = await db.events.find({"is_active": True}, {"_id": 0}).to_list(20)
        context = f"Aktif etkinlikler: {events}" if events else "Su anda aktif etkinlik bulunmuyor."

    raw_response = await get_chat_response(
        message=data.message,
        session_id=data.session_id,
        system_prompt=GEMINI_SYSTEM_PROMPT,
        context=context,
    )

    # Anti-halucinasyon kontrolu
    sanitized = sanitize_response(raw_response, intent)
    response = sanitized["text"]
    confidence = sanitized["confidence"]

    msg_record = {
        "id": new_id(),
        "session_id": data.session_id,
        "user_message": data.message,
        "ai_response": response,
        "intent": intent,
        "agent": agent.value,
        "source": "gemini",
        "confidence": confidence["confidence"],
        "hallucination_issues": confidence["issue_count"],
        "modified_by_filter": sanitized["modified"],
        "created_at": utcnow(),
    }
    await db.chat_messages.insert_one(msg_record)

    return {
        "response": response,
        "session_id": data.session_id,
        "intent": intent,
        "agent": agent.value,
        "confidence": confidence["confidence"],
    }


@router.get("/chatbot/history/{session_id}")
async def chat_history(session_id: str):
    messages = await db.chat_messages.find(
        {"session_id": session_id}, {"_id": 0}
    ).sort("created_at", 1).to_list(100)
    return {"messages": messages}


@router.post("/messages/ai-translate")
async def ai_translate_message(request: TranslateRequest):
    """
    Translates an incoming guest message to the staff's language (Turkish) 
    AND generates a proposed professional response in the guest's ORIGINAL language.
    """
    from gemini_service import get_chat_response
    import json
    import re
    
    prompt = f"""
    Sen Kozbeyli Konagi otelinin cok dilli iletisim asistanisin.
    
    Gelen Misafir Mesaji: "{request.message}"
    Otel Yoneticisinin (Senin) Notu / Baglami: "{request.hotel_context or 'Mantikli ve kibar bir sekilde yanitla.'}"
    
    Gorevlerin:
    1. Gelen mesajin dilini tespit et (Orn: 'en', 'ru', 'de').
    2. Gelen mesaji Turkceye cevir.
    3. Eger otel yoneticisinin bir notu varsa, bu notu baz alarak; yoksa genel otel kurallarina gore misafirin KENDI DİLİNDE profesyonel, kibar ve pazarimsil bir otel yaniti (smart reply) olustur.
    
    Lutfen SADECE asagidaki JSON formatinda sonuc don. Markdown icinde olabilir ama gecerli JSON olmali.
    {{
        "detected_language": "English",
        "translated_text": "Erken giris yapabilir miyim?",
        "suggested_reply": "Dear guest, subject to availability on your arrival day, we will do our best to accommodate your early check-in request. We look forward to welcoming you!"
    }}
    """
    
    try:
        ai_response = await get_chat_response("Translation Service", "translate_" + new_id(), prompt)
        
        json_match = re.search(r'```(?:json)?(.*?)```', ai_response, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_response
        parsed_result = json.loads(res_str)
        
        return {"success": True, "data": parsed_result}
    except Exception as e:
        return {"success": False, "error": f"AI Ceviri hatasi: {str(e)}"}


@router.delete("/chatbot/session/{session_id}")
async def clear_chat(session_id: str):
    from gemini_service import clear_session
    clear_session(session_id)
    await db.chat_messages.delete_many({"session_id": session_id})
    return {"success": True}
