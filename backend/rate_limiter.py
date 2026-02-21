"""
Kozbeyli Konagi - Rate Limiter
IP/session bazli istek sinirlamasi
"""
import time
import logging
from collections import defaultdict
from fastapi import Request, HTTPException

logger = logging.getLogger(__name__)

# Yapilandirma
RATE_LIMITS = {
    "login": {"max_requests": 5, "window_seconds": 300},     # 5 attempts per 5 min
    "chatbot": {"max_requests": 15, "window_seconds": 60},   # 15 per minute
    "reviews": {"max_requests": 10, "window_seconds": 60},   # 10 per minute
    "default": {"max_requests": 60, "window_seconds": 60},   # 60 per minute
}

# In-memory istek sayaci
_request_counts: dict = defaultdict(list)


def _clean_old_requests(key: str, window: int):
    """Eski istekleri temizle"""
    now = time.time()
    _request_counts[key] = [t for t in _request_counts[key] if now - t < window]
    # Remove empty keys to prevent memory leak
    if not _request_counts[key]:
        del _request_counts[key]


def check_rate_limit(identifier: str, endpoint_type: str = "default") -> dict:
    """Rate limit kontrolu yap"""
    config = RATE_LIMITS.get(endpoint_type, RATE_LIMITS["default"])
    max_requests = config["max_requests"]
    window = config["window_seconds"]

    key = f"{endpoint_type}:{identifier}"
    _clean_old_requests(key, window)

    current_count = len(_request_counts[key])

    if current_count >= max_requests:
        remaining_time = int(window - (time.time() - _request_counts[key][0]))
        return {
            "allowed": False,
            "current": current_count,
            "limit": max_requests,
            "remaining": 0,
            "retry_after": max(1, remaining_time),
        }

    _request_counts[key].append(time.time())

    return {
        "allowed": True,
        "current": current_count + 1,
        "limit": max_requests,
        "remaining": max_requests - current_count - 1,
        "retry_after": 0,
    }


def get_client_identifier(request: Request, session_id: str = None) -> str:
    """Istemci tanimlayicisi olustur"""
    if session_id:
        return session_id

    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()

    return request.client.host if request.client else "unknown"


def rate_limit_or_raise(request: Request, endpoint_type: str = "default", session_id: str = None):
    """Rate limit kontrol et, asimda HTTPException firlat"""
    identifier = get_client_identifier(request, session_id)
    result = check_rate_limit(identifier, endpoint_type)

    if not result["allowed"]:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Cok fazla istek gonderdiniz. Lutfen biraz bekleyin.",
                "retry_after": result["retry_after"],
                "limit": result["limit"],
            }
        )

    return result


def get_rate_limit_stats() -> dict:
    """Rate limit istatistikleri"""
    stats = {}
    now = time.time()
    for key, timestamps in _request_counts.items():
        active = [t for t in timestamps if now - t < 60]
        if active:
            stats[key] = {
                "active_requests": len(active),
                "oldest": int(now - active[0]) if active else 0,
            }
    return {"active_keys": len(stats), "details": stats}
