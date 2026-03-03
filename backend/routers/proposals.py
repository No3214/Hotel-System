"""
Kozbeyli Konagi - Teklif Yonetimi (Proposal/Quote Management) Router
Organizasyon teklifleri olusturma, takip ve arsiv sistemi.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from database import db
from helpers import utcnow, new_id
from datetime import datetime, timezone, timedelta

router = APIRouter(tags=["proposals"])


# ===================== MODELS =====================

class AccommodationItem(BaseModel):
    room_type: str = ""
    room_count: int = 0
    nights: int = 1
    per_room_price: float = 0
    total: float = 0
    note: str = ""

class MealOption(BaseModel):
    description: str = ""
    per_person_price: float = 0
    guest_count: int = 0
    payment_method: str = ""
    total: float = 0

class ExtraService(BaseModel):
    name: str = ""
    description: str = ""
    price: float = 0

class ProposalCreate(BaseModel):
    # Musteri bilgileri
    customer_name: str
    customer_phone: str = ""
    customer_email: str = ""
    inquiry_id: str = ""
    # Etkinlik bilgileri
    event_type: str = "dugun"
    event_date: str = ""
    event_date_note: str = ""
    guest_count: int = 0
    # Konaklama
    accommodation_items: List[AccommodationItem] = []
    accommodation_total: float = 0
    accommodation_note: str = "Tum oda fiyatlarina kisi basi gurme serpme kahvalti dahildir."
    # Yemek
    meal_options: List[MealOption] = []
    meal_total: float = 0
    meal_note: str = ""
    # Ek hizmetler
    extra_services: List[ExtraService] = []
    extras_total: float = 0
    # Ozet
    grand_total: float = 0
    discount_amount: float = 0
    discount_note: str = ""
    # Odeme
    deposit_percentage: int = 50
    payment_note: str = "Kalan tutar etkinlik tarihinden 1 hafta once tahsil edilecektir."
    # Gecerlilik
    validity_days: int = 15
    # Notlar
    notes: str = ""
    internal_notes: str = ""


class ProposalUpdate(BaseModel):
    status: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    event_date: Optional[str] = None
    guest_count: Optional[int] = None
    accommodation_items: Optional[List[AccommodationItem]] = None
    accommodation_total: Optional[float] = None
    meal_options: Optional[List[MealOption]] = None
    meal_total: Optional[float] = None
    extra_services: Optional[List[ExtraService]] = None
    extras_total: Optional[float] = None
    grand_total: Optional[float] = None
    discount_amount: Optional[float] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None


# ===================== HELPER =====================

async def generate_proposal_number():
    """TKL-2026-001 formatinda teklif numarasi uret"""
    year = datetime.now(timezone.utc).year
    count = await db.proposals.count_documents({"proposal_number": {"$regex": f"TKL-{year}"}})
    return f"TKL-{year}-{str(count + 1).zfill(3)}"


# ===================== ENDPOINTS =====================

@router.post("/proposals")
async def create_proposal(data: ProposalCreate):
    """Yeni teklif olustur"""
    proposal_number = await generate_proposal_number()

    # Toplam hesapla
    acc_total = data.accommodation_total or sum(i.total for i in data.accommodation_items)
    meal_total = data.meal_total or (max((m.total for m in data.meal_options), default=0) if data.meal_options else 0)
    ext_total = data.extras_total or sum(s.price for s in data.extra_services)
    grand = data.grand_total or (acc_total + meal_total + ext_total - data.discount_amount)

    now = utcnow()
    expires = (datetime.now(timezone.utc) + timedelta(days=data.validity_days)).isoformat()

    proposal = {
        "id": new_id(),
        "proposal_number": proposal_number,
        "status": "draft",
        **data.dict(),
        "accommodation_total": acc_total,
        "meal_total": meal_total,
        "extras_total": ext_total,
        "grand_total": grand,
        "expires_at": expires,
        "sent_at": "",
        "responded_at": "",
        "created_at": now,
        "updated_at": now,
    }

    # Pydantic nesnelerini dict'e cevir
    proposal["accommodation_items"] = [i.dict() for i in data.accommodation_items]
    proposal["meal_options"] = [m.dict() for m in data.meal_options]
    proposal["extra_services"] = [s.dict() for s in data.extra_services]

    await db.proposals.insert_one(proposal)
    del proposal["_id"]

    # Inquiry varsa bagla
    if data.inquiry_id:
        await db.organization_inquiries.update_one(
            {"id": data.inquiry_id},
            {"$set": {"status": "quoted", "price_quote": grand, "proposal_id": proposal["id"], "updated_at": now}},
        )

    return proposal


@router.get("/proposals")
async def list_proposals(status: Optional[str] = None, limit: int = 100):
    """Teklifleri listele"""
    query = {}
    if status:
        query["status"] = status
    proposals = await db.proposals.find(
        query, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return {"proposals": proposals, "total": len(proposals)}


@router.get("/proposals/{proposal_id}")
async def get_proposal(proposal_id: str):
    """Teklif detayi"""
    p = await db.proposals.find_one({"id": proposal_id}, {"_id": 0})
    if not p:
        raise HTTPException(404, "Teklif bulunamadi")
    return p


@router.patch("/proposals/{proposal_id}")
async def update_proposal(proposal_id: str, data: ProposalUpdate):
    """Teklif guncelle"""
    update_data = {}
    for k, v in data.dict().items():
        if v is not None:
            if isinstance(v, list):
                update_data[k] = [i.dict() if hasattr(i, 'dict') else i for i in v]
            else:
                update_data[k] = v

    update_data["updated_at"] = utcnow()

    # Durum guncelleme
    if data.status == "sent":
        update_data["sent_at"] = utcnow()
    elif data.status in ("accepted", "rejected"):
        update_data["responded_at"] = utcnow()

    await db.proposals.update_one({"id": proposal_id}, {"$set": update_data})
    updated = await db.proposals.find_one({"id": proposal_id}, {"_id": 0})
    return updated


@router.delete("/proposals/{proposal_id}")
async def delete_proposal(proposal_id: str):
    """Teklif sil"""
    await db.proposals.delete_one({"id": proposal_id})
    return {"deleted": True}


@router.post("/proposals/{proposal_id}/duplicate")
async def duplicate_proposal(proposal_id: str):
    """Teklifi kopyala (yeni musteri icin sablondan olustur)"""
    original = await db.proposals.find_one({"id": proposal_id}, {"_id": 0})
    if not original:
        raise HTTPException(404, "Teklif bulunamadi")

    new_number = await generate_proposal_number()
    now = utcnow()
    expires = (datetime.now(timezone.utc) + timedelta(days=original.get("validity_days", 15))).isoformat()

    new_proposal = {
        **original,
        "id": new_id(),
        "proposal_number": new_number,
        "status": "draft",
        "customer_name": original["customer_name"] + " (Kopya)",
        "inquiry_id": "",
        "sent_at": "",
        "responded_at": "",
        "expires_at": expires,
        "created_at": now,
        "updated_at": now,
    }
    await db.proposals.insert_one(new_proposal)
    del new_proposal["_id"]
    return new_proposal


@router.get("/proposals/stats/summary")
async def proposal_stats():
    """Teklif istatistikleri"""
    total = await db.proposals.count_documents({})
    draft = await db.proposals.count_documents({"status": "draft"})
    sent = await db.proposals.count_documents({"status": "sent"})
    accepted = await db.proposals.count_documents({"status": "accepted"})
    rejected = await db.proposals.count_documents({"status": "rejected"})
    expired = await db.proposals.count_documents({"status": "expired"})

    # Toplam teklif tutari
    pipeline = [
        {"$match": {"status": {"$in": ["sent", "accepted"]}}},
        {"$group": {"_id": None, "total_value": {"$sum": "$grand_total"}, "count": {"$sum": 1}}},
    ]
    agg = await db.proposals.aggregate(pipeline).to_list(1)
    total_value = agg[0]["total_value"] if agg else 0

    # Kabul edilen toplam
    pipeline2 = [
        {"$match": {"status": "accepted"}},
        {"$group": {"_id": None, "total_value": {"$sum": "$grand_total"}}},
    ]
    agg2 = await db.proposals.aggregate(pipeline2).to_list(1)
    accepted_value = agg2[0]["total_value"] if agg2 else 0

    return {
        "total": total,
        "draft": draft,
        "sent": sent,
        "accepted": accepted,
        "rejected": rejected,
        "expired": expired,
        "total_value": total_value,
        "accepted_value": accepted_value,
        "conversion_rate": round(accepted / sent * 100, 1) if sent > 0 else 0,
    }
