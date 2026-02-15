"""
Gemini AI Service for Kozbeyli Konagi chatbot
"""
import logging
import os
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / '.env')

logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')

_chat_sessions = {}


async def get_chat_response(message: str, session_id: str, system_prompt: str, context: str = "") -> str:
    """Get AI response from Gemini"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    try:
        if not GOOGLE_API_KEY:
            return "AI servisi su anda yapilandiriliyor. Lutfen daha sonra tekrar deneyin."

        full_system = system_prompt
        if context:
            full_system += f"\n\nEk Bilgi:\n{context}"

        if session_id not in _chat_sessions:
            chat = LlmChat(
                api_key=GOOGLE_API_KEY,
                session_id=session_id,
                system_message=full_system
            ).with_model("gemini", "gemini-2.5-flash")
            _chat_sessions[session_id] = chat

        chat = _chat_sessions[session_id]
        user_msg = UserMessage(text=message)
        response = await chat.send_message(user_msg)
        return response

    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return f"Bir hata olustu. Lutfen daha sonra tekrar deneyin veya bizi {os.environ.get('HOTEL_PHONE', '+90 232 826 11 12')} numarasindan arayin."


def clear_session(session_id: str):
    """Clear a chat session"""
    if session_id in _chat_sessions:
        del _chat_sessions[session_id]


def detect_intent(message: str) -> str:
    """Detect user intent from message"""
    from hotel_data import INTENT_KEYWORDS

    message_lower = message.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                return intent
    return "general"
