"""
Kozbeyli Konagi - Online Presence Monitor Router
Otel sayfalarinin musteri gozunden denetimi
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, List

router = APIRouter(tags=["presence-monitor"])


class PlatformAuditData(BaseModel):
    """Tek platform icin manuel kontrol verileri"""
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    photo_count: int = 0
    photos_checked: bool = False
    cover_photo_ok: Optional[bool] = None
    outdated_photos: bool = False
    description: Optional[str] = None
    description_checked: bool = False
    amenities_listed: List[str] = []
    room_count: Optional[int] = None
    cancellation_policy_checked: Optional[bool] = None
    rating: Optional[float] = None
    review_count: int = 0
    response_rate: int = 0
    unanswered_negative: int = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class FullAuditRequest(BaseModel):
    """Tum platformlar icin toplu denetim verileri"""
    platforms: Dict[str, PlatformAuditData] = {}


class SingleAuditRequest(BaseModel):
    """Tek platform denetim istegi"""
    platform_id: str
    data: PlatformAuditData


@router.get("/presence/platforms")
async def get_platforms():
    """Desteklenen platformlari ve kontrol listesini getir"""
    from services.presence_monitor_service import get_platforms_info
    return get_platforms_info()


@router.post("/presence/audit")
async def run_full_audit(request: FullAuditRequest):
    """Tum platformlar icin toplu denetim calistir"""
    from services.presence_monitor_service import run_full_audit as do_audit, save_audit

    audit_data = {pid: data.model_dump() for pid, data in request.platforms.items()}
    audit = await do_audit(audit_data)
    await save_audit(audit)
    return audit


@router.post("/presence/audit/platform")
async def audit_single_platform(request: SingleAuditRequest):
    """Tek platform denetimi calistir"""
    from services.presence_monitor_service import run_platform_audit
    audit = await run_platform_audit(request.platform_id, request.data.model_dump())
    return audit


@router.get("/presence/audit/history")
async def get_audit_history(limit: int = 10):
    """Gecmis denetim sonuclarini getir"""
    from services.presence_monitor_service import get_audit_history as get_history
    audits = await get_history(limit)
    return {"audits": audits, "total": len(audits)}


@router.get("/presence/audit/{audit_id}")
async def get_audit_detail(audit_id: str):
    """Belirli bir denetim sonucunun detayini getir"""
    from database import db
    audit = await db.presence_audits.find_one({"id": audit_id}, {"_id": 0})
    if not audit:
        from fastapi import HTTPException
        raise HTTPException(404, "Denetim bulunamadi")
    return audit


@router.get("/presence/truth-source")
async def get_truth_source():
    """Dogru bilgi kaynagini getir (hotel_config'den)"""
    from services.presence_monitor_service import TRUTH_SOURCE, PLATFORMS
    return {
        "truth_source": TRUTH_SOURCE,
        "platform_urls": {pid: p["url"] for pid, p in PLATFORMS.items() if p["url"]},
    }
