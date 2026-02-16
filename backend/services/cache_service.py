import time
import logging
from cachetools import TTLCache
from functools import wraps

logger = logging.getLogger(__name__)

# Cache stores with TTL (seconds)
_caches = {
    "short": TTLCache(maxsize=100, ttl=30),      # 30 seconds - dashboard, real-time data
    "medium": TTLCache(maxsize=200, ttl=300),     # 5 minutes - rooms, analytics
    "long": TTLCache(maxsize=100, ttl=1800),      # 30 minutes - static config, pricing seasons
}

_stats = {"hits": 0, "misses": 0}


def get_cache(duration: str = "medium"):
    return _caches.get(duration, _caches["medium"])


def cache_get(key: str, duration: str = "medium"):
    c = get_cache(duration)
    val = c.get(key)
    if val is not None:
        _stats["hits"] += 1
        return val
    _stats["misses"] += 1
    return None


def cache_set(key: str, value, duration: str = "medium"):
    c = get_cache(duration)
    c[key] = value


def cache_invalidate(key: str = None, duration: str = None):
    """Invalidate a specific key or all caches."""
    if key and duration:
        c = get_cache(duration)
        c.pop(key, None)
    elif key:
        for c in _caches.values():
            c.pop(key, None)
    else:
        for c in _caches.values():
            c.clear()


def cache_stats():
    total = _stats["hits"] + _stats["misses"]
    hit_rate = (_stats["hits"] / total * 100) if total > 0 else 0
    sizes = {k: len(v) for k, v in _caches.items()}
    return {
        "hits": _stats["hits"],
        "misses": _stats["misses"],
        "total_requests": total,
        "hit_rate_percent": round(hit_rate, 1),
        "cache_sizes": sizes,
    }


def cached(key_prefix: str, duration: str = "medium"):
    """Decorator for caching async endpoint responses."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key from prefix + sorted kwargs
            parts = [key_prefix]
            for k, v in sorted(kwargs.items()):
                if v is not None:
                    parts.append(f"{k}={v}")
            cache_key = ":".join(parts)

            result = cache_get(cache_key, duration)
            if result is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return result

            result = await func(*args, **kwargs)
            cache_set(cache_key, result, duration)
            logger.debug(f"Cache SET: {cache_key}")
            return result
        return wrapper
    return decorator
