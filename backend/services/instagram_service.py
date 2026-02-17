"""
Kozbeyli Konagi - Instagram Messaging API Service
Handles Instagram Direct Messages through the Meta Graph API.
Mock mode when credentials are not configured.
"""
import os
import logging
from typing import Optional, Dict, Any

import httpx

from database import db
from helpers import utcnow, new_id

logger = logging.getLogger(__name__)

API_VERSION = "v18.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"


def get_config():
    return {
        "access_token": os.environ.get("INSTAGRAM_ACCESS_TOKEN", ""),
        "page_id": os.environ.get("INSTAGRAM_PAGE_ID", ""),
        "verify_token": os.environ.get("INSTAGRAM_VERIFY_TOKEN", "kozbeyli_ig_verify_2026"),
    }


def is_configured() -> bool:
    cfg = get_config()
    return bool(cfg["access_token"] and cfg["page_id"])


async def _api_request(method: str, url: str, payload: dict) -> Dict[str, Any]:
    cfg = get_config()
    headers = {
        "Authorization": f"Bearer {cfg['access_token']}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.request(method, url, headers=headers, json=payload)
        return resp.json()


async def _log_message(
    user_id: str,
    direction: str,
    content: str = "",
    ig_message_id: str = "",
    status: str = "sent",
):
    await db.instagram_messages.insert_one({
        "id": new_id(),
        "session_id": f"ig_{user_id}",
        "user_id": user_id,
        "text": content[:1000] if content else "",
        "ig_message_id": ig_message_id,
        "direction": direction,
        "status": status,
        "created_at": utcnow(),
    })


async def send_text_message(recipient_id: str, message: str) -> Dict[str, Any]:
    """Send a text message to an Instagram user via page messaging."""
    if not is_configured():
        await _log_message(recipient_id, "outgoing", message, status="mock_sent")
        return {"status": "mock", "to": recipient_id, "message": message}

    cfg = get_config()
    url = f"{BASE_URL}/{cfg['page_id']}/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message},
    }
    result = await _api_request("POST", url, payload)
    ig_id = result.get("message_id", "")
    await _log_message(recipient_id, "outgoing", message, ig_message_id=ig_id)
    return result


async def send_quick_replies(
    recipient_id: str,
    text: str,
    quick_replies: list,
) -> Dict[str, Any]:
    """Send a message with quick reply options."""
    if not is_configured():
        await _log_message(recipient_id, "outgoing", text, status="mock_sent")
        return {"status": "mock", "to": recipient_id}

    cfg = get_config()
    url = f"{BASE_URL}/{cfg['page_id']}/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {
            "text": text,
            "quick_replies": [
                {"content_type": "text", "title": qr["title"], "payload": qr.get("payload", qr["title"])}
                for qr in quick_replies[:13]
            ],
        },
    }
    result = await _api_request("POST", url, payload)
    await _log_message(recipient_id, "outgoing", text)
    return result
