"""
Kozbeyli Konagi - Reputation Management Router
Coklu platform itibar yonetimi API'leri
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["reputation"])


# ==================== REQUEST MODELS ====================

class ReviewAnalyzeRequest(BaseModel):
    text: str
    platform: str = "google"
    rating: int = 5


class ReviewAddRequest(BaseModel):
    platform: str = "google"
    author: str = "Anonim"
    rating: int = 5
    text: str
    date: Optional[str] = None


# ==================== ENDPOINTS ====================

@router.get("/reputation/overview")
async def reputation_overview():
    """Tum platformlardan itibar ozeti"""
    from services.reputation_service import get_reputation_overview
    result = await get_reputation_overview()
    return result


@router.get("/reputation/platforms")
async def get_platforms():
    """Desteklenen degerlendirme platformlari"""
    from services.reputation_service import REVIEW_PLATFORMS
    return {"platforms": REVIEW_PLATFORMS}


@router.post("/reputation/analyze")
async def analyze_review(data: ReviewAnalyzeRequest):
    """AI ile degerlendirme analizi"""
    from services.reputation_service import analyze_review_ai
    result = await analyze_review_ai(
        review_text=data.text,
        platform=data.platform,
        rating=data.rating,
    )
    return result


@router.post("/reputation/reviews")
async def add_review(data: ReviewAddRequest):
    """Yeni degerlendirme ekle"""
    from services.reputation_service import add_review_to_db
    result = await add_review_to_db(data.dict())
    return result


@router.get("/reputation/reviews")
async def list_reviews(platform: Optional[str] = None, sentiment: Optional[str] = None, limit: int = 50):
    """Degerlendirmeleri listele"""
    from database import db
    query = {}
    if platform:
        query["platform"] = platform
    if sentiment:
        query["sentiment"] = sentiment
    items = await db.reputation_reviews.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return {"reviews": items}


@router.get("/reputation/competitors")
async def competitor_comparison():
    """Rakip karsilastirma"""
    from services.reputation_service import get_competitor_comparison
    result = await get_competitor_comparison()
    return result


@router.get("/reputation/sentiment-keywords")
async def get_sentiment_keywords():
    """Duygu analizi anahtar kelimeleri"""
    from services.reputation_service import SENTIMENT_KEYWORDS
    return {"keywords": SENTIMENT_KEYWORDS}


@router.post("/reputation/quick-sentiment")
async def quick_sentiment(data: ReviewAnalyzeRequest):
    """Hizli (AI'siz) duygu analizi"""
    from services.reputation_service import analyze_sentiment_simple
    result = analyze_sentiment_simple(data.text)
    return result
