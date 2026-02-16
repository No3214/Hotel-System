from fastapi import APIRouter
from services.cache_service import cache_stats, cache_invalidate

router = APIRouter(tags=["cache"])


@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache performance statistics."""
    return cache_stats()


@router.post("/cache/clear")
async def clear_cache():
    """Clear all caches."""
    cache_invalidate()
    return {"success": True, "message": "Tum onbellek temizlendi"}
