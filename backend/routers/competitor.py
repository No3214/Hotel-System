"""
Kozbeyli Konagi - Rakip Analizi Router
Rakip otellerin takibi, karsilastirma, SWOT analizi
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(tags=["competitor"])


class AddCompetitorRequest(BaseModel):
    name: str
    type: str = "butik_otel"
    location: str = "Foca, Izmir"
    price_range: str = "$$"
    booking_url: Optional[str] = None
    tripadvisor_url: Optional[str] = None
    google_url: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None


@router.get("/competitor/list")
async def get_competitors():
    """Tum rakipleri listele"""
    from services.competitor_service import get_competitors as get_comps
    competitors = await get_comps()
    return {"competitors": competitors, "total": len(competitors)}


@router.post("/competitor/add")
async def add_competitor(request: AddCompetitorRequest):
    """Yeni rakip ekle"""
    from services.competitor_service import add_competitor
    return await add_competitor(request.model_dump())


@router.post("/competitor/analyze")
async def analyze_competitor(competitor_id: str):
    """AI ile rakip analizi"""
    from database import db
    from services.competitor_service import COMPETITORS, analyze_competitor as do_analyze
    # Direct DB lookup instead of fetching all competitors
    comp = await db.competitors.find_one({"id": competitor_id}, {"_id": 0})
    if not comp:
        comp = COMPETITORS.get(competitor_id)
    if not comp:
        raise HTTPException(404, "Rakip bulunamadi")
    return await do_analyze(comp)


@router.get("/competitor/compare")
async def compare_ratings():
    """Platform bazinda puan karsilastirmasi"""
    from services.competitor_service import compare_ratings
    return await compare_ratings()


@router.get("/competitor/swot")
async def get_swot():
    """AI ile SWOT analizi"""
    from services.competitor_service import generate_swot
    return await generate_swot()


@router.get("/competitor/market-position")
async def get_market_position():
    """Pazar konumu raporu"""
    from services.competitor_service import get_market_position
    return await get_market_position()
