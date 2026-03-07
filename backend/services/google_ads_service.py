"""
Kozbeyli Konagi - Google Ads Service
Google Ads kampanya yonetimi

Ozellikler:
- Search Ads (Arama reklamlari)
- Display Ads (Goruntulu reklamlar)
- Kampanya olusturma/yonetme
- Anahtar kelime yonetimi
- Performans metrikleri
- Butce kontrolu
"""
import logging
from typing import Optional, List, Dict
from helpers import utcnow, new_id

logger = logging.getLogger(__name__)

# ==================== KEYWORD PLANS ====================

KEYWORD_PLANS = {
    "otel": {
        "name": "Otel & Konaklama",
        "keywords": [
            {"keyword": "foca butik otel", "match_type": "phrase", "suggested_bid": 3.5},
            {"keyword": "izmir boutique hotel", "match_type": "phrase", "suggested_bid": 4.0},
            {"keyword": "foca otel fiyatlari", "match_type": "broad", "suggested_bid": 2.5},
            {"keyword": "foca apart otel", "match_type": "exact", "suggested_bid": 3.0},
            {"keyword": "kozbeyli konagi", "match_type": "exact", "suggested_bid": 1.0},
            {"keyword": "foca konaklama", "match_type": "phrase", "suggested_bid": 2.8},
            {"keyword": "izmir yakin otel", "match_type": "broad", "suggested_bid": 3.2},
            {"keyword": "ege butik otel", "match_type": "phrase", "suggested_bid": 3.5},
        ],
    },
    "dugun": {
        "name": "Dugun & Organizasyon",
        "keywords": [
            {"keyword": "kir dugunu izmir", "match_type": "phrase", "suggested_bid": 5.0},
            {"keyword": "dugun mekani foca", "match_type": "phrase", "suggested_bid": 4.5},
            {"keyword": "kir dugunu mekanlari", "match_type": "broad", "suggested_bid": 6.0},
            {"keyword": "dugun organizasyonu izmir", "match_type": "phrase", "suggested_bid": 5.5},
            {"keyword": "nisan mekani izmir", "match_type": "phrase", "suggested_bid": 3.5},
            {"keyword": "dugun oteli", "match_type": "broad", "suggested_bid": 4.0},
            {"keyword": "bahce dugunu", "match_type": "phrase", "suggested_bid": 4.5},
            {"keyword": "rustic wedding venue izmir", "match_type": "phrase", "suggested_bid": 3.0},
        ],
    },
    "restoran": {
        "name": "Restoran & Yemek",
        "keywords": [
            {"keyword": "foca restoran", "match_type": "phrase", "suggested_bid": 2.0},
            {"keyword": "izmir ege mutfagi", "match_type": "phrase", "suggested_bid": 2.5},
            {"keyword": "foca yemek yerleri", "match_type": "broad", "suggested_bid": 1.8},
            {"keyword": "steak restoran izmir", "match_type": "phrase", "suggested_bid": 3.0},
            {"keyword": "romantik aksam yemegi izmir", "match_type": "phrase", "suggested_bid": 2.8},
            {"keyword": "organik kahvalti izmir", "match_type": "phrase", "suggested_bid": 2.2},
        ],
    },
    "kurumsal": {
        "name": "Kurumsal Etkinlik",
        "keywords": [
            {"keyword": "toplanti mekani izmir", "match_type": "phrase", "suggested_bid": 4.0},
            {"keyword": "sirket etkinligi mekani", "match_type": "phrase", "suggested_bid": 4.5},
            {"keyword": "team building izmir", "match_type": "phrase", "suggested_bid": 3.5},
            {"keyword": "kurumsal toplanti oteli", "match_type": "broad", "suggested_bid": 4.0},
            {"keyword": "is yemegi izmir", "match_type": "phrase", "suggested_bid": 2.5},
        ],
    },
}

# ==================== AD FORMATS ====================

AD_FORMATS = {
    "search": {
        "name": "Arama Reklamlari",
        "description": "Google arama sonuclarinda gosterilir",
        "fields": ["headline1", "headline2", "headline3", "description1", "description2", "final_url", "path1", "path2"],
        "limits": {
            "headline": 30,  # max karakter
            "description": 90,
            "path": 15,
        },
    },
    "display": {
        "name": "Goruntulu Reklamlar",
        "description": "Google Display Network'te gosterilir",
        "fields": ["headline", "long_headline", "description", "business_name", "final_url"],
        "limits": {
            "headline": 30,
            "long_headline": 90,
            "description": 90,
        },
    },
    "local": {
        "name": "Yerel Reklamlar",
        "description": "Google Maps ve yerel aramalarda gosterilir",
        "fields": ["headline1", "headline2", "description", "call_to_action", "phone"],
        "limits": {
            "headline": 30,
            "description": 90,
        },
    },
}

# ==================== SERVICE FUNCTIONS ====================

async def create_google_campaign(data: dict) -> dict:
    """Yeni Google Ads kampanyasi olustur"""
    from database import db

    campaign = {
        "id": new_id(),
        "name": data.get("name", "Yeni Kampanya"),
        "campaign_type": data.get("campaign_type", "search"),  # search, display, local
        "keyword_plan": data.get("keyword_plan", "otel"),
        "status": "draft",
        "budget_daily": data.get("budget_daily", 50),
        "bid_strategy": data.get("bid_strategy", "maximize_clicks"),  # maximize_clicks, target_cpa, manual_cpc
        "target_cpa": data.get("target_cpa", 0),
        "geo_targeting": data.get("geo_targeting", ["Izmir", "Istanbul", "Ankara"]),
        "language": data.get("language", "tr"),
        "ad_groups": data.get("ad_groups", []),
        "keywords": [],
        "ads": data.get("ads", []),
        "impressions": 0,
        "clicks": 0,
        "conversions": 0,
        "spend": 0,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }

    # Keyword plan'dan anahtar kelimeleri yukle
    plan = KEYWORD_PLANS.get(data.get("keyword_plan", "otel"))
    if plan:
        campaign["keywords"] = plan["keywords"]

    await db.google_campaigns.insert_one(campaign)
    del campaign["_id"]
    return campaign


async def update_google_campaign(campaign_id: str, updates: dict) -> dict:
    """Kampanya guncelle"""
    from database import db

    updates["updated_at"] = utcnow()
    result = await db.google_campaigns.update_one(
        {"id": campaign_id},
        {"$set": updates}
    )
    if result.modified_count == 0:
        return {"error": "Kampanya bulunamadi"}

    campaign = await db.google_campaigns.find_one({"id": campaign_id}, {"_id": 0})
    return campaign or {"error": "Kampanya bulunamadi"}


async def add_ad_to_campaign(campaign_id: str, ad_data: dict) -> dict:
    """Kampanyaya reklam ekle (kullanicinin yazdigi metin)"""
    from database import db

    ad = {
        "id": new_id(),
        "ad_format": ad_data.get("ad_format", "search"),
        "headline1": ad_data.get("headline1", ""),
        "headline2": ad_data.get("headline2", ""),
        "headline3": ad_data.get("headline3", ""),
        "description1": ad_data.get("description1", ""),
        "description2": ad_data.get("description2", ""),
        "final_url": ad_data.get("final_url", "https://kozbeylikonagi.com"),
        "path1": ad_data.get("path1", ""),
        "path2": ad_data.get("path2", ""),
        "status": "draft",
        "created_at": utcnow(),
    }

    await db.google_campaigns.update_one(
        {"id": campaign_id},
        {"$push": {"ads": ad}}
    )

    return ad


async def update_campaign_keywords(campaign_id: str, keywords: list) -> dict:
    """Kampanya anahtar kelimelerini guncelle"""
    from database import db

    await db.google_campaigns.update_one(
        {"id": campaign_id},
        {"$set": {"keywords": keywords, "updated_at": utcnow()}}
    )

    campaign = await db.google_campaigns.find_one({"id": campaign_id}, {"_id": 0})
    return campaign or {"error": "Kampanya bulunamadi"}


async def get_google_performance(campaign_id: Optional[str] = None) -> dict:
    """Performans metrikleri (mock - API entegrasyonu icin hazir)"""
    from database import db
    import random

    if campaign_id:
        campaign = await db.google_campaigns.find_one({"id": campaign_id}, {"_id": 0})
        if campaign:
            return campaign

    return {
        "summary": {
            "total_spend": round(random.uniform(500, 5000), 2),
            "total_impressions": random.randint(10000, 100000),
            "total_clicks": random.randint(500, 5000),
            "total_conversions": random.randint(5, 50),
            "avg_cpc": round(random.uniform(1.0, 5.0), 2),
            "ctr": round(random.uniform(2.0, 8.0), 2),
            "conversion_rate": round(random.uniform(2.0, 8.0), 2),
            "cost_per_conversion": round(random.uniform(50, 300), 2),
            "quality_score_avg": round(random.uniform(6, 9), 1),
            "period": "son_30_gun",
        },
        "by_campaign_type": {
            "search": {
                "impressions": random.randint(5000, 50000),
                "clicks": random.randint(300, 3000),
                "conversions": random.randint(3, 30),
                "spend": round(random.uniform(200, 2000), 2),
                "ctr": round(random.uniform(3.0, 8.0), 2),
            },
            "display": {
                "impressions": random.randint(10000, 80000),
                "clicks": random.randint(100, 1000),
                "conversions": random.randint(1, 10),
                "spend": round(random.uniform(100, 1000), 2),
                "ctr": round(random.uniform(0.5, 2.0), 2),
            },
            "local": {
                "impressions": random.randint(3000, 20000),
                "clicks": random.randint(200, 1500),
                "calls": random.randint(10, 60),
                "directions": random.randint(20, 100),
                "spend": round(random.uniform(100, 800), 2),
                "ctr": round(random.uniform(4.0, 10.0), 2),
            },
        },
        "top_keywords": [
            {"keyword": "foca butik otel", "impressions": random.randint(500, 5000), "clicks": random.randint(30, 300), "ctr": round(random.uniform(3, 8), 1), "avg_cpc": round(random.uniform(2, 5), 2), "quality_score": random.randint(7, 10)},
            {"keyword": "kir dugunu izmir", "impressions": random.randint(300, 3000), "clicks": random.randint(20, 200), "ctr": round(random.uniform(3, 8), 1), "avg_cpc": round(random.uniform(3, 7), 2), "quality_score": random.randint(6, 9)},
            {"keyword": "foca restoran", "impressions": random.randint(400, 4000), "clicks": random.randint(25, 250), "ctr": round(random.uniform(3, 8), 1), "avg_cpc": round(random.uniform(1, 3), 2), "quality_score": random.randint(7, 10)},
        ],
    }
