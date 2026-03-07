import os
import json
import logging
from functools import wraps

logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# TTL values in seconds
TTL_SHORT = 30       # 30 seconds - dashboard, real-time data
TTL_MEDIUM = 300     # 5 minutes - rooms, analytics
TTL_LONG = 1800      # 30 minutes - static config, pricing seasons

DURATION_MAP = {
    "short": TTL_SHORT,
    "medium": TTL_MEDIUM,
    "long": TTL_LONG,
}

_redis = None
_stats = {"hits": 0, "misses": 0}


def _get_redis():
    global _redis
    if _redis is None:
        try:
            import redis
            _redis = redis.from_url(REDIS_URL, decode_responses=True)
            _redis.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis unavailable, using in-memory fallback: {e}")
            _redis = None
    return _redis


# In-memory fallback
from cachetools import TTLCache
_fallback_caches = {
    "short": TTLCache(maxsize=100, ttl=TTL_SHORT),
    "medium": TTLCache(maxsize=200, ttl=TTL_MEDIUM),
    "long": TTLCache(maxsize=100, ttl=TTL_LONG),
}


def cache_get(key: str, duration: str = "medium"):
    r = _get_redis()
    if r:
        try:
            val = r.get(f"cache:{duration}:{key}")
            if val is not None:
                _stats["hits"] += 1
                return json.loads(val)
            _stats["misses"] += 1
            return None
        except Exception:
            pass

    # Fallback to in-memory
    c = _fallback_caches.get(duration, _fallback_caches["medium"])
    val = c.get(key)
    if val is not None:
        _stats["hits"] += 1
        return val
    _stats["misses"] += 1
    return None


def cache_set(key: str, value, duration: str = "medium"):
    ttl = DURATION_MAP.get(duration, TTL_MEDIUM)
    r = _get_redis()
    if r:
        try:
            r.setex(f"cache:{duration}:{key}", ttl, json.dumps(value, default=str))
            return
        except Exception:
            pass

    # Fallback to in-memory
    c = _fallback_caches.get(duration, _fallback_caches["medium"])
    c[key] = value


def cache_invalidate(key: str = None, duration: str = None):
    r = _get_redis()
    if r:
        try:
            if key and duration:
                r.delete(f"cache:{duration}:{key}")
            elif key:
                for d in DURATION_MAP:
                    r.delete(f"cache:{d}:{key}")
            else:
                # Clear all cache keys
                for pattern_key in r.scan_iter("cache:*"):
                    r.delete(pattern_key)
            return
        except Exception:
            pass

    # Fallback
    if key and duration:
        c = _fallback_caches.get(duration)
        if c:
            c.pop(key, None)
    elif key:
        for c in _fallback_caches.values():
            c.pop(key, None)
    else:
        for c in _fallback_caches.values():
            c.clear()


def cache_stats():
    total = _stats["hits"] + _stats["misses"]
    hit_rate = (_stats["hits"] / total * 100) if total > 0 else 0

    r = _get_redis()
    backend = "redis" if r else "in-memory"

    sizes = {}
    if r:
        try:
            for d in DURATION_MAP:
                count = 0
                for _ in r.scan_iter(f"cache:{d}:*"):
                    count += 1
                sizes[d] = count
        except Exception:
            sizes = {d: len(c) for d, c in _fallback_caches.items()}
    else:
        sizes = {d: len(c) for d, c in _fallback_caches.items()}

    result = {
        "backend": backend,
        "hits": _stats["hits"],
        "misses": _stats["misses"],
        "total_requests": total,
        "hit_rate_percent": round(hit_rate, 1),
        "cache_sizes": sizes,
    }
    if backend == "in-memory":
        result["warning"] = "Redis baglantisi kurulamadi, in-memory fallback aktif. Veriler yeniden baslatmada kaybolur."
    return result


def cached(key_prefix: str, duration: str = "medium"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            parts = [key_prefix]
            for k, v in sorted(kwargs.items()):
                if v is not None:
                    parts.append(f"{k}={v}")
            cache_key = ":".join(parts)

            result = cache_get(cache_key, duration)
            if result is not None:
                return result

            result = await func(*args, **kwargs)
            cache_set(cache_key, result, duration)
            return result
        return wrapper
    return decorator
