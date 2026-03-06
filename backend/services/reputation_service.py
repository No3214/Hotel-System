"""
Kozbeyli Konagi - Reputation Management Service
Coklu platform itibar yonetimi + AI analiz

Ozellikler:
- Google, TripAdvisor, Booking.com, Instagram degerlendirme takibi
- Duygu analizi (sentiment)
- Trend analizi
- Rakip karsilastirma
- AI ile otomatik yanit onerisi
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime, timezone, timedelta
from helpers import utcnow, new_id

logger = logging.getLogger(__name__)

# ==================== PLATFORM CONFIGS ====================

REVIEW_PLATFORMS = {
    "google": {
        "name": "Google",
        "icon": "star",
        "color": "#4285F4",
        "url": "g.page/kozbeylikonagi",
    },
    "tripadvisor": {
        "name": "TripAdvisor",
        "icon": "award",
        "color": "#00AF87",
        "url": "tripadvisor.com/kozbeylikonagi",
    },
    "booking": {
        "name": "Booking.com",
        "icon": "bed",
        "color": "#003580",
        "url": "booking.com/kozbeylikonagi",
    },
    "instagram": {
        "name": "Instagram",
        "icon": "instagram",
        "color": "#E4405F",
        "url": "instagram.com/kozbeylikonagi",
    },
}

# ==================== SENTIMENT KEYWORDS ====================

SENTIMENT_KEYWORDS = {
    "positive": [
        "harika", "muhtesem", "mukemmel", "guzel", "huzurlu", "temiz",
        "lezzetli", "sicak", "misafirperver", "romantik", "amazing",
        "wonderful", "perfect", "beautiful", "excellent", "clean", "delicious",
    ],
    "negative": [
        "kotu", "berbat", "kirli", "soguk", "pahali", "gurultulu",
        "ilgisiz", "yetersiz", "hayal kirikligi", "bad", "dirty",
        "expensive", "noisy", "disappointing", "poor",
    ],
    "categories": {
        "temizlik": ["temiz", "kirli", "hijyen", "clean", "dirty"],
        "yemek": ["kahvalti", "yemek", "lezzet", "restoran", "breakfast", "food", "delicious"],
        "konum": ["konum", "yer", "ulasim", "manzara", "location", "view"],
        "personel": ["personel", "ilgi", "misafirperver", "staff", "friendly", "helpful"],
        "fiyat": ["fiyat", "pahali", "uygun", "deger", "price", "value", "expensive"],
        "oda": ["oda", "yatak", "banyo", "room", "bed", "bathroom"],
    },
}

REPUTATION_AI_PROMPT = """Sen Kozbeyli Konagi icin itibar yonetimi uzmanisin.

GOREV: Verilen degerlendirmeleri analiz et ve asagidakileri cikart:
1. Genel duygu (pozitif/negatif/notr) ve puan (1-10)
2. Kategori bazli analiz (temizlik, yemek, konum, personel, fiyat, oda)
3. Onemli anahtar kelimeler
4. Iyilestirme onerileri
5. Profesyonel yanit onerisi

JSON formatinda cevapla:
{
  "sentiment": "positive/negative/neutral",
  "score": 8,
  "categories": {"temizlik": 9, "yemek": 8, ...},
  "keywords": ["harika", "temiz", ...],
  "improvements": ["Oneri 1", ...],
  "suggested_response": "Yanit metni"
}"""


def analyze_sentiment_simple(text: str) -> dict:
    """Basit keyword-tabanli duygu analizi"""
    text_lower = text.lower()
    pos_count = sum(1 for w in SENTIMENT_KEYWORDS["positive"] if w in text_lower)
    neg_count = sum(1 for w in SENTIMENT_KEYWORDS["negative"] if w in text_lower)

    if pos_count > neg_count:
        sentiment = "positive"
        score = min(10, 6 + pos_count)
    elif neg_count > pos_count:
        sentiment = "negative"
        score = max(1, 5 - neg_count)
    else:
        sentiment = "neutral"
        score = 5

    # Category detection
    categories = {}
    for cat, keywords in SENTIMENT_KEYWORDS["categories"].items():
        if any(kw in text_lower for kw in keywords):
            categories[cat] = "mentioned"

    return {
        "sentiment": sentiment,
        "score": score,
        "positive_signals": pos_count,
        "negative_signals": neg_count,
        "categories_mentioned": categories,
    }


async def analyze_review_ai(review_text: str, platform: str = "google", rating: int = 0) -> dict:
    """AI ile derinlemesine degerlendirme analizi"""
    from gemini_service import get_chat_response

    prompt = f"""Platform: {platform}
Puan: {rating}/5
Degerlendirme: {review_text}

Bu degerlendirmeyi analiz et ve JSON formatinda sonuc ver."""

    result = await get_chat_response(
        message=prompt,
        session_id=f"reputation-{new_id()[:8]}",
        system_prompt=REPUTATION_AI_PROMPT,
    )

    basic = analyze_sentiment_simple(review_text)

    return {
        "ai_analysis": result,
        "basic_analysis": basic,
        "platform": platform,
        "rating": rating,
        "analyzed_at": utcnow(),
    }


async def get_reputation_overview() -> dict:
    """Tum platformlardan itibar ozeti (mock + DB)"""
    from database import db
    import random

    # Try to get real data from DB
    review_count = await db.reviews.count_documents({})

    # Generate realistic mock overview
    return {
        "overall_score": round(random.uniform(4.2, 4.8), 1),
        "total_reviews": max(review_count, 127),
        "platforms": {
            "google": {
                "rating": round(random.uniform(4.3, 4.9), 1),
                "review_count": random.randint(40, 60),
                "trend": "up",
                "response_rate": random.randint(85, 100),
            },
            "tripadvisor": {
                "rating": round(random.uniform(4.0, 4.7), 1),
                "review_count": random.randint(25, 40),
                "trend": "stable",
                "response_rate": random.randint(70, 95),
            },
            "booking": {
                "rating": round(random.uniform(8.5, 9.5), 1),
                "review_count": random.randint(30, 50),
                "trend": "up",
                "response_rate": random.randint(80, 100),
            },
            "instagram": {
                "mentions": random.randint(15, 40),
                "sentiment": "positive",
                "engagement_rate": round(random.uniform(3.0, 8.0), 1),
            },
        },
        "sentiment_distribution": {
            "positive": random.randint(70, 85),
            "neutral": random.randint(10, 20),
            "negative": random.randint(2, 10),
        },
        "top_categories": {
            "yemek": round(random.uniform(4.5, 5.0), 1),
            "temizlik": round(random.uniform(4.3, 4.9), 1),
            "konum": round(random.uniform(4.0, 4.8), 1),
            "personel": round(random.uniform(4.5, 5.0), 1),
            "fiyat_deger": round(random.uniform(3.8, 4.5), 1),
        },
        "recent_trend": "improving",
        "updated_at": utcnow(),
    }


async def get_competitor_comparison() -> dict:
    """Rakip otel karsilastirmasi (mock data)"""
    return {
        "our_hotel": {
            "name": "Kozbeyli Konagi",
            "google_rating": 4.6,
            "review_count": 127,
            "strengths": ["Yemek", "Atmosfer", "Personel"],
            "weaknesses": ["Ulasim"],
        },
        "competitors": [
            {
                "name": "Foca Butik Otelleri (Ortalama)",
                "google_rating": 4.2,
                "review_count": 85,
                "comparison": "Kozbeyli Konagi ortalamanin uzerinde",
            },
            {
                "name": "Izmir Bolge Butik Otelleri",
                "google_rating": 4.3,
                "review_count": 150,
                "comparison": "Rekabetci konumda",
            },
        ],
        "market_position": "Foca bolgesi butik otelleri arasinda lider konumda",
        "improvement_areas": [
            "Online gorunurlugu artir (SEO + reklam)",
            "Uluslararasi platformlarda (Booking, TripAdvisor) yorum sayisini artir",
            "Ingilizce degerlendirme yanit oranini yukselt",
        ],
    }


async def add_review_to_db(review_data: dict) -> dict:
    """Degerlendirme kaydet"""
    from database import db

    review = {
        "id": new_id(),
        "platform": review_data.get("platform", "google"),
        "author": review_data.get("author", "Anonim"),
        "rating": review_data.get("rating", 5),
        "text": review_data.get("text", ""),
        "response": review_data.get("response", ""),
        "response_status": "pending",
        "sentiment": analyze_sentiment_simple(review_data.get("text", ""))["sentiment"],
        "created_at": review_data.get("date", utcnow()),
        "added_at": utcnow(),
    }

    await db.reputation_reviews.insert_one(review)
    del review["_id"]
    return review
