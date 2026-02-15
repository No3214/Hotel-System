"""
Kozbeyli Konagi - Musteri Sadakat Sistemi
Tekrar gelen misafir takibi, sadakat seviyeleri, otomatik indirim
"""
from fastapi import APIRouter
from typing import Optional
from database import db
from helpers import utcnow, new_id

router = APIRouter(tags=["loyalty"])

# Sadakat Seviyeleri
LOYALTY_LEVELS = {
    "bronze": {"min_stays": 1, "max_stays": 2, "discount": 0, "label_tr": "Bronz", "label_en": "Bronze", "color": "#CD7F32"},
    "silver": {"min_stays": 3, "max_stays": 4, "discount": 5, "label_tr": "Gumus", "label_en": "Silver", "color": "#C0C0C0"},
    "gold": {"min_stays": 5, "max_stays": 9, "discount": 10, "label_tr": "Altin", "label_en": "Gold", "color": "#FFD700"},
    "platinum": {"min_stays": 10, "max_stays": 999, "discount": 15, "label_tr": "Platin", "label_en": "Platinum", "color": "#E5E4E2"},
}


def calculate_loyalty_level(total_stays: int) -> dict:
    """Konaklama sayisina gore sadakat seviyesi hesapla"""
    for level_id, level in LOYALTY_LEVELS.items():
        if level["min_stays"] <= total_stays <= level["max_stays"]:
            return {"level": level_id, **level}
    return {"level": "bronze", **LOYALTY_LEVELS["bronze"]}


@router.get("/loyalty/levels")
async def get_loyalty_levels():
    """Sadakat seviyelerini getir"""
    return {"levels": LOYALTY_LEVELS}


@router.get("/loyalty/guests")
async def get_loyalty_guests(level: Optional[str] = None, min_stays: int = 0, limit: int = 50):
    """Sadakat programindaki misafirleri listele"""
    query = {"total_stays": {"$gt": min_stays}}
    if level:
        level_info = LOYALTY_LEVELS.get(level)
        if level_info:
            query["total_stays"] = {"$gte": level_info["min_stays"], "$lte": level_info["max_stays"]}

    guests = await db.guests.find(query, {"_id": 0}).sort("total_stays", -1).limit(limit).to_list(limit)

    enriched = []
    for guest in guests:
        stays = guest.get("total_stays", 0)
        loyalty = calculate_loyalty_level(stays)
        enriched.append({
            **guest,
            "loyalty_level": loyalty["level"],
            "loyalty_label": loyalty["label_tr"],
            "loyalty_color": loyalty["color"],
            "discount_percent": loyalty["discount"],
            "next_level": _get_next_level_info(stays),
        })

    return {"guests": enriched, "total": len(enriched)}


@router.get("/loyalty/guest/{guest_id}")
async def get_guest_loyalty(guest_id: str):
    """Misafir sadakat detaylari"""
    guest = await db.guests.find_one({"id": guest_id}, {"_id": 0})
    if not guest:
        return {"error": "Misafir bulunamadi"}

    stays = guest.get("total_stays", 0)
    loyalty = calculate_loyalty_level(stays)

    # Konaklama gecmisi
    reservations = await db.reservations.find(
        {"guest_id": guest_id, "status": {"$in": ["checked_out", "confirmed", "checked_in"]}},
        {"_id": 0}
    ).sort("check_in", -1).to_list(50)

    total_spent = sum(r.get("total_price", 0) for r in reservations if r.get("total_price"))
    total_nights = sum(_calc_nights(r) for r in reservations)

    return {
        "guest": guest,
        "loyalty": {
            "level": loyalty["level"],
            "label": loyalty["label_tr"],
            "color": loyalty["color"],
            "discount_percent": loyalty["discount"],
            "total_stays": stays,
            "total_spent": total_spent,
            "total_nights": total_nights,
            "next_level": _get_next_level_info(stays),
            "avg_spend_per_stay": round(total_spent / stays, 2) if stays > 0 else 0,
        },
        "reservation_history": reservations[:10],
    }


@router.post("/loyalty/update-guest/{guest_id}")
async def update_guest_loyalty(guest_id: str):
    """Misafir sadakat bilgisini guncelle (check-out sonrasi)"""
    guest = await db.guests.find_one({"id": guest_id}, {"_id": 0})
    if not guest:
        return {"error": "Misafir bulunamadi"}

    # Tamamlanan rezervasyonlari say
    completed_stays = await db.reservations.count_documents({
        "guest_id": guest_id,
        "status": {"$in": ["checked_out"]}
    })

    total_spent_pipeline = await db.reservations.aggregate([
        {"$match": {"guest_id": guest_id, "status": {"$in": ["checked_out"]}}},
        {"$group": {"_id": None, "total": {"$sum": "$total_price"}}},
    ]).to_list(1)
    total_spent = total_spent_pipeline[0]["total"] if total_spent_pipeline else 0

    # Son ziyaret
    last_reservation = await db.reservations.find_one(
        {"guest_id": guest_id, "status": "checked_out"},
        {"_id": 0}, sort=[("check_out", -1)]
    )

    loyalty = calculate_loyalty_level(completed_stays)

    update_data = {
        "total_stays": completed_stays,
        "total_spent": total_spent,
        "loyalty_level": loyalty["level"],
        "discount_percent": loyalty["discount"],
        "vip": completed_stays >= 5,
        "last_visit": last_reservation.get("check_out") if last_reservation else None,
        "updated_at": utcnow(),
    }

    await db.guests.update_one({"id": guest_id}, {"$set": update_data})

    return {"success": True, "guest_id": guest_id, "loyalty": loyalty, "total_stays": completed_stays}


@router.post("/loyalty/match-guest")
async def match_returning_guest(phone: Optional[str] = None, email: Optional[str] = None):
    """Telefon veya email ile tekrar gelen misafiri bul"""
    if not phone and not email:
        return {"matched": False, "error": "Telefon veya email gerekli"}

    query_parts = []
    if phone:
        cleaned = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        query_parts.append({"phone": {"$regex": cleaned[-10:]}})
    if email:
        query_parts.append({"email": {"$regex": email, "$options": "i"}})

    guest = await db.guests.find_one({"$or": query_parts}, {"_id": 0}) if query_parts else None

    if guest:
        stays = guest.get("total_stays", 0)
        loyalty = calculate_loyalty_level(stays)
        return {
            "matched": True,
            "guest": guest,
            "loyalty": {
                "level": loyalty["level"],
                "label": loyalty["label_tr"],
                "discount": loyalty["discount"],
                "total_stays": stays,
            },
            "is_returning": stays > 0,
        }

    return {"matched": False}


@router.get("/loyalty/stats")
async def get_loyalty_stats():
    """Sadakat programi istatistikleri"""
    total_guests = await db.guests.count_documents({})
    returning_guests = await db.guests.count_documents({"total_stays": {"$gte": 2}})

    level_counts = {}
    for level_id, level_info in LOYALTY_LEVELS.items():
        count = await db.guests.count_documents({
            "total_stays": {"$gte": level_info["min_stays"], "$lte": level_info["max_stays"]}
        })
        level_counts[level_id] = count

    # Top 5 VIP misafir
    top_vips = await db.guests.find(
        {"total_stays": {"$gte": 1}}, {"_id": 0}
    ).sort("total_stays", -1).limit(5).to_list(5)

    top_vips_enriched = []
    for g in top_vips:
        stays = g.get("total_stays", 0)
        loyalty = calculate_loyalty_level(stays)
        top_vips_enriched.append({
            "id": g.get("id"),
            "name": g.get("name"),
            "total_stays": stays,
            "total_spent": g.get("total_spent", 0),
            "loyalty_level": loyalty["level"],
            "loyalty_label": loyalty["label_tr"],
            "loyalty_color": loyalty["color"],
        })

    return {
        "total_guests": total_guests,
        "returning_guests": returning_guests,
        "return_rate": round(returning_guests / total_guests * 100, 1) if total_guests > 0 else 0,
        "level_counts": level_counts,
        "top_vips": top_vips_enriched,
    }


def _get_next_level_info(current_stays: int) -> dict:
    """Bir sonraki seviye bilgisi"""
    levels_list = list(LOYALTY_LEVELS.items())
    for i, (level_id, level) in enumerate(levels_list):
        if level["min_stays"] <= current_stays <= level["max_stays"]:
            if i < len(levels_list) - 1:
                next_id, next_level = levels_list[i + 1]
                return {
                    "level": next_id,
                    "label": next_level["label_tr"],
                    "stays_needed": next_level["min_stays"] - current_stays,
                    "discount": next_level["discount"],
                }
            return None
    return None


def _calc_nights(reservation: dict) -> int:
    """Gece sayisi hesapla"""
    try:
        from datetime import datetime
        ci = reservation.get("check_in", "")
        co = reservation.get("check_out", "")
        if ci and co:
            d1 = datetime.fromisoformat(ci[:10])
            d2 = datetime.fromisoformat(co[:10])
            return max(1, (d2 - d1).days)
    except Exception:
        pass
    return 1
