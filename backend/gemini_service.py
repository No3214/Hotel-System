"""
Gemini AI Service for Kozbeyli Konagi chatbot
Uses google-generativeai SDK directly.
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
    try:
        if not GOOGLE_API_KEY:
            return "AI servisi su anda yapilandiriliyor. Lutfen daha sonra tekrar deneyin."

        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)

        full_system = system_prompt
        if context:
            full_system += f"\n\nEk Bilgi:\n{context}"

        if session_id not in _chat_sessions:
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                system_instruction=full_system,
            )
            _chat_sessions[session_id] = model.start_chat()

        chat = _chat_sessions[session_id]
        response = chat.send_message(message)
        return response.text

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


async def get_review_response(prompt: str, system_prompt: str) -> str:
    """Generate a professional response to a Google review"""
    try:
        if not GOOGLE_API_KEY:
            return "AI servisi su anda yapilandiriliyor. Lutfen daha sonra tekrar deneyin."

        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system_prompt,
        )
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        logger.error(f"Gemini review response error: {e}")
        return "Yanitlama sirasinda bir hata olustu. Lutfen tekrar deneyin."
