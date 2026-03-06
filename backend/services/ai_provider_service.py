"""
Kozbeyli Konagi - Multi-AI Provider Service
Akilli is dagilimi: Gemini, DeepSeek, OpenRouter, Groq

Anthropic Prompt Engineering Best Practices:
- Role assignment ile uzman persona
- XML tag separation ile data/instruction ayirimi
- Chain-of-thought ile adim adim dusunme
- Structured JSON output
- Fallback chain: birisi basarisiz olursa digerine gec

Gorev Dagilimi:
- Gemini 2.5 Flash: Chatbot, misafir iletisimi (Turkce'de guclu, hizli)
- DeepSeek: Analiz, raporlama, veri isleme (ucuz, analitik odakli)
- OpenRouter: Yedek + ozel modeller (Claude, GPT fallback)
- Groq: Ultra-hizli kisa gorevler (intent detection, sentiment)
"""
import logging
import os
import json
import httpx
from typing import Optional, Dict, Any
from config import GOOGLE_API_KEY, DEEPSEEK_API_KEY, OPENROUTER_API_KEY, GROQ_API_KEY

logger = logging.getLogger(__name__)

# ==================== PROVIDER CONFIG ====================

PROVIDERS = {
    "gemini": {
        "name": "Gemini 2.5 Flash",
        "model": "gemini-2.5-flash",
        "strengths": ["turkce", "chatbot", "hizli", "genel"],
        "cost": "dusuk",
        "available": bool(GOOGLE_API_KEY),
    },
    "deepseek": {
        "name": "DeepSeek",
        "model": "deepseek-chat",
        "api_url": "https://api.deepseek.com/v1/chat/completions",
        "strengths": ["analiz", "rapor", "veri", "kod", "matematik"],
        "cost": "cok_dusuk",
        "available": bool(DEEPSEEK_API_KEY),
    },
    "openrouter": {
        "name": "OpenRouter",
        "model": "google/gemini-2.5-flash-preview",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "strengths": ["yedek", "cesitlilik", "fallback"],
        "cost": "degisken",
        "available": bool(OPENROUTER_API_KEY),
    },
    "groq": {
        "name": "Groq (Llama)",
        "model": "llama-3.3-70b-versatile",
        "api_url": "https://api.groq.com/openai/v1/chat/completions",
        "strengths": ["ultra_hizli", "siniflandirma", "kisa_gorev"],
        "cost": "dusuk",
        "available": bool(GROQ_API_KEY),
    },
}

# ==================== TASK ROUTING ====================
# Hangi gorev hangi provider'a gidecek

TASK_ROUTING = {
    # Chatbot & misafir iletisimi -> Gemini (Turkce guclu)
    "chatbot": ["gemini", "openrouter", "deepseek"],
    "review_response": ["gemini", "openrouter", "deepseek"],
    "guest_message": ["gemini", "openrouter", "deepseek"],

    # Analiz & raporlama -> DeepSeek (ucuz, analitik)
    "sentiment_analysis": ["groq", "deepseek", "gemini"],
    "review_analysis": ["deepseek", "gemini", "openrouter"],
    "data_analysis": ["deepseek", "gemini", "openrouter"],
    "report_generation": ["deepseek", "gemini", "openrouter"],

    # Hizli siniflandirma -> Groq (ultra hizli)
    "intent_detection": ["groq", "deepseek", "gemini"],
    "classification": ["groq", "deepseek", "gemini"],
    "quick_response": ["groq", "gemini", "deepseek"],

    # Pazarlama & icerik -> Gemini (yaratici, Turkce)
    "marketing_copy": ["gemini", "openrouter", "deepseek"],
    "ad_copy": ["gemini", "openrouter", "deepseek"],
    "social_media": ["gemini", "openrouter", "deepseek"],

    # Genel fallback
    "general": ["gemini", "deepseek", "openrouter", "groq"],
}


def get_provider_for_task(task_type: str) -> str:
    """Gorev turune gore en uygun provider'i sec"""
    chain = TASK_ROUTING.get(task_type, TASK_ROUTING["general"])
    for provider_id in chain:
        if PROVIDERS[provider_id]["available"]:
            return provider_id
    return "gemini"  # ultimate fallback


# ==================== PROVIDER IMPLEMENTATIONS ====================

async def _call_gemini(message: str, system_prompt: str, session_id: str = "") -> str:
    """Gemini API cagrisi (emergentintegrations uzerinden)"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    if not GOOGLE_API_KEY:
        raise Exception("GOOGLE_API_KEY not configured")

    chat = LlmChat(
        api_key=GOOGLE_API_KEY,
        session_id=session_id or f"ai-{id(message)}",
        system_message=system_prompt
    ).with_model("gemini", "gemini-2.5-flash")

    user_msg = UserMessage(text=message)
    response = await chat.send_message(user_msg)
    return response


async def _call_openai_compatible(
    message: str, system_prompt: str, api_url: str, api_key: str, model: str
) -> str:
    """OpenAI-compatible API cagrisi (DeepSeek, OpenRouter, Groq)"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # OpenRouter icin ek header
    if "openrouter" in api_url:
        headers["HTTP-Referer"] = "https://kozbeylikonagi.com"
        headers["X-Title"] = "Kozbeyli Konagi"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
        "temperature": 0.7,
        "max_tokens": 2000,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def call_provider(provider_id: str, message: str, system_prompt: str, session_id: str = "") -> str:
    """Belirli bir provider'i cagir"""
    provider = PROVIDERS.get(provider_id)
    if not provider or not provider["available"]:
        raise Exception(f"Provider {provider_id} not available")

    if provider_id == "gemini":
        return await _call_gemini(message, system_prompt, session_id)

    api_keys = {
        "deepseek": DEEPSEEK_API_KEY,
        "openrouter": OPENROUTER_API_KEY,
        "groq": GROQ_API_KEY,
    }

    return await _call_openai_compatible(
        message=message,
        system_prompt=system_prompt,
        api_url=provider["api_url"],
        api_key=api_keys[provider_id],
        model=provider["model"],
    )


# ==================== MAIN API ====================

async def ai_request(
    message: str,
    system_prompt: str,
    task_type: str = "general",
    session_id: str = "",
    preferred_provider: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Ana AI istek fonksiyonu - akilli routing + fallback

    Args:
        message: Kullanici mesaji
        system_prompt: Sistem promptu (Anthropic best practices ile)
        task_type: Gorev turu (chatbot, sentiment_analysis, marketing_copy, vb.)
        session_id: Oturum ID (chatbot icin)
        preferred_provider: Tercih edilen provider (opsiyonel, override)

    Returns:
        {"response": str, "provider": str, "task_type": str}
    """
    # Provider chain belirle
    if preferred_provider and PROVIDERS.get(preferred_provider, {}).get("available"):
        chain = [preferred_provider] + [p for p in TASK_ROUTING.get(task_type, TASK_ROUTING["general"]) if p != preferred_provider]
    else:
        chain = TASK_ROUTING.get(task_type, TASK_ROUTING["general"])

    last_error = None
    for provider_id in chain:
        if not PROVIDERS[provider_id]["available"]:
            continue
        try:
            logger.info(f"AI request: task={task_type}, provider={provider_id}")
            response = await call_provider(provider_id, message, system_prompt, session_id)
            return {
                "response": response,
                "provider": provider_id,
                "provider_name": PROVIDERS[provider_id]["name"],
                "task_type": task_type,
            }
        except Exception as e:
            last_error = e
            logger.warning(f"Provider {provider_id} failed for task {task_type}: {e}")
            continue

    # Hepsi basarisiz
    logger.error(f"All providers failed for task {task_type}: {last_error}")
    return {
        "response": f"AI servisi su anda kullanilamiyor. Lutfen bizi +90 232 826 11 12 numarasindan arayin.",
        "provider": "none",
        "provider_name": "Yok",
        "task_type": task_type,
        "error": str(last_error) if last_error else "No providers available",
    }


def get_available_providers() -> dict:
    """Kullanilabilir provider'lari listele"""
    return {
        pid: {
            "name": p["name"],
            "available": p["available"],
            "strengths": p["strengths"],
            "cost": p["cost"],
        }
        for pid, p in PROVIDERS.items()
    }


def get_task_routing() -> dict:
    """Gorev routing tablosunu goster"""
    result = {}
    for task, chain in TASK_ROUTING.items():
        active_chain = [p for p in chain if PROVIDERS[p]["available"]]
        result[task] = {
            "chain": chain,
            "active_provider": active_chain[0] if active_chain else "none",
            "fallbacks": active_chain[1:] if len(active_chain) > 1 else [],
        }
    return result


# ==================== PROMPT TEMPLATES (Anthropic Best Practices) ====================
# Role assignment + XML tags + Chain-of-thought + Structured output

def build_system_prompt(role: str, task: str, context: str = "", output_format: str = "") -> str:
    """
    Anthropic prompt engineering best practices ile sistem promptu olustur

    Kullanim:
        prompt = build_system_prompt(
            role="Sen Kozbeyli Konagi'nin deneyimli misafir iliskileri uzmanisin.",
            task="Misafir degerlendirmelerini analiz et.",
            context="<hotel_info>Kozbeyli Konagi: Foca/Izmir butik otel</hotel_info>",
            output_format='{"sentiment": "positive/negative/neutral", "score": 1-10}'
        )
    """
    prompt_parts = []

    # Role assignment (Chapter 3)
    prompt_parts.append(role)

    # Task description
    prompt_parts.append(f"\n<gorev>\n{task}\n</gorev>")

    # Context with XML tags (Chapter 4 - data separation)
    if context:
        prompt_parts.append(f"\n{context}")

    # Output format (Chapter 5)
    if output_format:
        prompt_parts.append(f"\n<cikti_formati>\nCevabini asagidaki JSON formatinda ver:\n{output_format}\n</cikti_formati>")

    # Chain-of-thought instruction (Chapter 6)
    prompt_parts.append("\n<talimat>\nAdim adim dusun. Once durumu analiz et, sonra cevabini olustur.\nTurkce cevapla.\n</talimat>")

    return "\n".join(prompt_parts)
