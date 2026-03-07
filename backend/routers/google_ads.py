"""
Kozbeyli Konagi - Google Ads Manager Router
Google arama, goruntulu ve yerel reklam yonetimi
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(tags=["google-ads"])


# ==================== REQUEST MODELS ====================

class GoogleCampaignCreate(BaseModel):
    name: str
    campaign_type: str = "search"  # search, display, local
    keyword_plan: str = "otel"  # otel, dugun, restoran, kurumsal
    budget_daily: float = 50
    bid_strategy: str = "maximize_clicks"
    target_cpa: float = 0
    geo_targeting: Optional[List[str]] = None
    ads: Optional[List[dict]] = None


class GoogleCampaignUpdate(BaseModel):
    campaign_id: str
    name: Optional[str] = None
    status: Optional[str] = None
    budget_daily: Optional[float] = None
    bid_strategy: Optional[str] = None
    target_cpa: Optional[float] = None
    geo_targeting: Optional[List[str]] = None


class GoogleAdCreate(BaseModel):
    campaign_id: str
    ad_format: str = "search"
    headline1: str = ""
    headline2: str = ""
    headline3: str = ""
    description1: str = ""
    description2: str = ""
    final_url: str = "https://kozbeylikonagi.com"
    path1: str = ""
    path2: str = ""


class KeywordUpdate(BaseModel):
    campaign_id: str
    keywords: List[dict]


# ==================== ENDPOINTS ====================

@router.get("/google-ads/keyword-plans")
async def get_keyword_plans():
    """Hazir anahtar kelime planlari"""
    from services.google_ads_service import KEYWORD_PLANS
    return {"plans": KEYWORD_PLANS}


@router.get("/google-ads/ad-formats")
async def get_ad_formats():
    """Reklam formatlari ve limitleri"""
    from services.google_ads_service import AD_FORMATS
    return {"formats": AD_FORMATS}


@router.post("/google-ads/campaigns")
async def create_campaign(data: GoogleCampaignCreate):
    """Yeni kampanya olustur"""
    from services.google_ads_service import create_google_campaign
    result = await create_google_campaign(data.model_dump())
    return result


@router.get("/google-ads/campaigns")
async def list_campaigns(status: Optional[str] = None, campaign_type: Optional[str] = None, limit: int = 20):
    """Kampanyalari listele"""
    from database import db
    query = {}
    if status:
        query["status"] = status
    if campaign_type:
        query["campaign_type"] = campaign_type
    items = await db.google_campaigns.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return {"campaigns": items}


@router.put("/google-ads/campaigns")
async def update_campaign(data: GoogleCampaignUpdate):
    """Kampanya guncelle"""
    from services.google_ads_service import update_google_campaign
    updates = {k: v for k, v in data.model_dump().items() if v is not None and k != "campaign_id"}
    result = await update_google_campaign(data.campaign_id, updates)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/google-ads/campaigns/ads")
async def add_ad(data: GoogleAdCreate):
    """Kampanyaya reklam ekle"""
    from services.google_ads_service import add_ad_to_campaign
    result = await add_ad_to_campaign(data.campaign_id, data.model_dump())
    return result


@router.put("/google-ads/campaigns/keywords")
async def update_keywords(data: KeywordUpdate):
    """Anahtar kelimeleri guncelle"""
    from services.google_ads_service import update_campaign_keywords
    result = await update_campaign_keywords(data.campaign_id, data.keywords)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.get("/google-ads/performance")
async def get_performance(campaign_id: Optional[str] = None):
    """Performans metrikleri"""
    from services.google_ads_service import get_google_performance
    result = await get_google_performance(campaign_id)
    return result


@router.delete("/google-ads/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Kampanya sil"""
    from database import db
    result = await db.google_campaigns.delete_one({"id": campaign_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Kampanya bulunamadi")
    return {"success": True}
