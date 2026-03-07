"""
Kozbeyli Konagi - Meta Ads Manager Router
Facebook & Instagram reklam yonetimi API'leri
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(tags=["meta-ads"])


# ==================== REQUEST MODELS ====================

class AdCopyRequest(BaseModel):
    segment: str = "weekend_getaway"  # wedding, weekend_getaway, foodie, corporate, romantic
    ad_type: str = "weekend"  # wedding, weekend, restaurant, seasonal
    platform: str = "both"  # facebook, instagram, both


class CampaignCreateRequest(BaseModel):
    name: str
    objective: str = "awareness"  # awareness, traffic, conversions, engagement
    segment: str = "weekend_getaway"
    platform: str = "both"
    budget_daily: float = 50
    budget_total: float = 0
    ad_copy: Optional[dict] = None


class CampaignStatusRequest(BaseModel):
    campaign_id: str
    status: str  # draft, active, paused, completed


# ==================== ENDPOINTS ====================

@router.post("/meta-ads/generate-copy")
async def generate_ad_copy(data: AdCopyRequest):
    """AI ile Meta reklam metni olustur"""
    from services.meta_ads_service import generate_ad_copy
    result = await generate_ad_copy(
        segment=data.segment,
        ad_type=data.ad_type,
        platform=data.platform,
    )
    return result


@router.get("/meta-ads/audiences")
async def get_audiences():
    """Hedef kitle segmentleri"""
    from services.meta_ads_service import AUDIENCE_SEGMENTS
    return {"audiences": AUDIENCE_SEGMENTS}


@router.get("/meta-ads/templates")
async def get_ad_templates():
    """Reklam sablonlari"""
    from services.meta_ads_service import AD_TEMPLATES
    return {"templates": AD_TEMPLATES}


@router.get("/meta-ads/performance")
async def get_performance(campaign_id: Optional[str] = None):
    """Kampanya performans metrikleri"""
    from services.meta_ads_service import get_campaign_performance
    result = await get_campaign_performance(campaign_id)
    return result


@router.post("/meta-ads/campaigns")
async def create_campaign(data: CampaignCreateRequest):
    """Yeni kampanya olustur"""
    from services.meta_ads_service import create_campaign
    result = await create_campaign(data.model_dump())
    return result


@router.get("/meta-ads/campaigns")
async def list_campaigns(status: Optional[str] = None, limit: int = 20):
    """Kampanyalari listele"""
    from database import db
    query = {"status": status} if status else {}
    items = await db.meta_campaigns.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return {"campaigns": items}


@router.put("/meta-ads/campaigns/status")
async def update_status(data: CampaignStatusRequest):
    """Kampanya durumunu guncelle"""
    from services.meta_ads_service import update_campaign_status
    result = await update_campaign_status(data.campaign_id, data.status)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.get("/meta-ads/budget-suggestions")
async def get_budget_suggestions():
    """Segment bazli butce onerileri"""
    from services.meta_ads_service import AUDIENCE_SEGMENTS
    suggestions = {}
    for key, seg in AUDIENCE_SEGMENTS.items():
        suggestions[key] = {
            "name": seg["name"],
            "budget_range": seg["budget_suggestion"],
            "recommended_objective": "conversions" if key in ["wedding", "romantic"] else "traffic",
            "best_platform": "instagram" if key in ["wedding", "foodie", "romantic"] else "both",
        }
    return {"suggestions": suggestions}
