"""
Kozbeyli Konagi - Organizasyon (Dugun/Nisan) Router
Organizasyon talepleri, bilgi formu ve yonetim endpoint'leri.
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, List
from database import db
from helpers import utcnow, new_id

from organization_data import (
    ORGANIZATION_TYPES, ACCOMMODATION_INFO, COCKTAIL_MENU,
    DINNER_MENU, DECORATION_PACKAGES, PHOTO_VIDEO_PACKAGES,
    MUSIC_OPTIONS, PAYMENT_TERMS, PRESENTATION_PDFS,
)

router = APIRouter(tags=["organization"])


# ===================== MODELS =====================

class OrganizationInquiry(BaseModel):
    guest_name: str
    phone: str
    email: str = ""
    second_contact: str = ""
    address: str = ""
    org_type: str = "dugun"
    date: str = ""
    alt_date: str = ""
    day_preference: str = ""
    start_time: str = ""
    end_time: str = ""
    guest_count_estimate: int = 0
    guest_count_final: int = 0
    child_0_6: int = 0
    child_7_12: int = 0
    extra_guests: int = 0
    needs_accommodation: str = ""
    checkin_date: str = ""
    checkout_date: str = ""
    nights: int = 0
    double_rooms: int = 0
    triple_rooms: int = 0
    family_rooms: int = 0
    bridal_suite: bool = False
    menu_type: str = ""
    drink_preference: str = ""
    drink_details: str = ""
    dietary_needs: List[str] = []
    menu_tasting: bool = False
    menu_notes: str = ""
    decoration_package: str = ""
    decoration_notes: str = ""
    wants_photo_video: bool = False
    photo_video_details: str = ""
    music_preference: str = ""
    music_details: str = ""
    wants_coordination: bool = False
    coordination_notes: str = ""
    budget_min: float = 0
    budget_max: float = 0
    payment_method: str = ""
    extra_notes: str = ""
    referral_source: str = ""
    platform: str = "web"


# ===================== PUBLIC ENDPOINTS =====================

@router.get("/organization/info")
async def get_organization_info():
    """Organizasyon hakkinda genel bilgi (public)"""
    return {
        "types": ORGANIZATION_TYPES,
        "accommodation": ACCOMMODATION_INFO,
        "cocktail_menu": COCKTAIL_MENU,
        "dinner_menu": DINNER_MENU,
        "decoration_packages": DECORATION_PACKAGES,
        "photo_video_packages": PHOTO_VIDEO_PACKAGES,
        "music_options": MUSIC_OPTIONS,
        "payment_terms": PAYMENT_TERMS,
        "presentations": PRESENTATION_PDFS,
    }


@router.post("/organization/inquiry")
async def submit_inquiry(data: OrganizationInquiry):
    """Organizasyon bilgi formu gonderimi"""
    inquiry = {
        "id": new_id(),
        **data.dict(),
        "status": "new",
        "assigned_to": "",
        "admin_notes": "",
        "price_quote": 0,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.organization_inquiries.insert_one(inquiry)

    # Bildirim olustur
    org_type_name = next((t["name"] for t in ORGANIZATION_TYPES if t["id"] == data.org_type), data.org_type)
    await db.group_notifications.insert_one({
        "id": new_id(),
        "type": "organization_inquiry",
        "message": f"Yeni {org_type_name} talebi: {data.guest_name} ({data.phone}), Tarih: {data.date}, ~{data.guest_count_estimate} kisi",
        "status": "pending",
        "created_at": utcnow(),
    })

    del inquiry["_id"]
    return inquiry


# ===================== ADMIN ENDPOINTS =====================

@router.get("/organization/inquiries")
async def list_inquiries(status: Optional[str] = None, limit: int = 50):
    """Organizasyon taleplerini listele (admin)"""
    query = {}
    if status:
        query["status"] = status
    inquiries = await db.organization_inquiries.find(
        query, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return {"inquiries": inquiries, "total": len(inquiries)}


@router.get("/organization/inquiries/{inquiry_id}")
async def get_inquiry(inquiry_id: str):
    """Tek bir organizasyon talebi detayi"""
    inquiry = await db.organization_inquiries.find_one({"id": inquiry_id}, {"_id": 0})
    if not inquiry:
        from fastapi import HTTPException
        raise HTTPException(404, "Talep bulunamadi")
    return inquiry


class InquiryUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    admin_notes: Optional[str] = None
    price_quote: Optional[float] = None


@router.patch("/organization/inquiries/{inquiry_id}")
async def update_inquiry(inquiry_id: str, data: InquiryUpdate):
    """Organizasyon talebi guncelle (admin)"""
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    update_data["updated_at"] = utcnow()
    await db.organization_inquiries.update_one(
        {"id": inquiry_id},
        {"$set": update_data}
    )
    updated = await db.organization_inquiries.find_one({"id": inquiry_id}, {"_id": 0})
    return updated


@router.delete("/organization/inquiries/{inquiry_id}")
async def delete_inquiry(inquiry_id: str):
    """Organizasyon talebi sil"""
    await db.organization_inquiries.delete_one({"id": inquiry_id})
    return {"deleted": True}


@router.get("/organization/stats")
async def get_org_stats():
    """Organizasyon istatistikleri"""
    total = await db.organization_inquiries.count_documents({})
    new_count = await db.organization_inquiries.count_documents({"status": "new"})
    contacted = await db.organization_inquiries.count_documents({"status": "contacted"})
    quoted = await db.organization_inquiries.count_documents({"status": "quoted"})
    confirmed = await db.organization_inquiries.count_documents({"status": "confirmed"})

    pipeline = [
        {"$group": {"_id": "$org_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    by_type = await db.organization_inquiries.aggregate(pipeline).to_list(20)

    return {
        "total": total,
        "new": new_count,
        "contacted": contacted,
        "quoted": quoted,
        "confirmed": confirmed,
        "by_type": by_type,
    }
