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
    from google import genai

    try:
        if not GOOGLE_API_KEY:
            return "AI servisi su anda yapilandiriliyor. Lutfen daha sonra tekrar deneyin."

        full_system = system_prompt
        if context:
            full_system += f"\n\nEk Bilgi:\n{context}"

        client = genai.Client(api_key=GOOGLE_API_KEY)

        # Maintain chat history per session
        if session_id not in _chat_sessions:
            _chat_sessions[session_id] = []

        _chat_sessions[session_id].append({"role": "user", "parts": [{"text": message}]})

        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=_chat_sessions[session_id],
            config=genai.types.GenerateContentConfig(
                system_instruction=full_system,
                temperature=0.7,
                max_output_tokens=2000,
            ),
        )

        result = response.text
        _chat_sessions[session_id].append({"role": "model", "parts": [{"text": result}]})
        return result

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
    from google import genai

    try:
        if not GOOGLE_API_KEY:
            return "AI servisi su anda yapilandiriliyor. Lutfen daha sonra tekrar deneyin."

        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=2000,
            ),
        )
        return response.text

    except Exception as e:
        logger.error(f"Gemini review response error: {e}")
        return "Yanitlama sirasinda bir hata olustu. Lutfen tekrar deneyin."
