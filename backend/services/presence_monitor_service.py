"""
Kozbeyli Konagi - Online Presence Monitor Service
Musteri gozunden otel sayfalarini kontrol et:
- Bilgi tutarliligi (ad, adres, telefon, check-in/out)
- Platform puanlari ve yorum sayilari
- Fotograf durumu
- Aciklama kalitesi
- Eksik/hatali bilgi tespiti

Desteklenen platformlar:
- Google Business Profile
- Booking.com
- TripAdvisor
- Instagram
- Facebook
- Airbnb
- HotelRunner kanallari
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

# ==================== DOGRU BILGILER (Truth Source) ====================
# hotel_config.py'den alinan kesin bilgiler - diger platformlar buna karsi kontrol edilir

from hotel_config import HOTEL_INFO, ROOM_TYPES, CANCELLATION_POLICY

TRUTH_SOURCE = {
    "name": HOTEL_INFO["name"],
    "name_en": HOTEL_INFO["name_en"],
    "phone": HOTEL_INFO["phone"],
    "email": HOTEL_INFO["email"],
    "website": HOTEL_INFO["website"],
    "address": HOTEL_INFO["address"]["full"],
    "city": HOTEL_INFO["address"]["city"],
    "district": HOTEL_INFO["address"]["district"],
    "check_in": HOTEL_INFO["check_in"],
    "check_out": HOTEL_INFO["check_out"],
    "total_rooms": sum(r["count"] for r in ROOM_TYPES),
    "room_types": len(ROOM_TYPES),
    "latitude": HOTEL_INFO["location"]["latitude"],
    "longitude": HOTEL_INFO["location"]["longitude"],
    "amenities": HOTEL_INFO["amenities"],
    "pet_friendly": True,
    "parking": True,
    "wifi": True,
    "pool": True,
    "restaurant": True,
}

# ==================== PLATFORM TANIMLARI ====================

PLATFORMS = {
    "google_business": {
        "name": "Google Business Profile",
        "url": HOTEL_INFO["social_media"].get("google_reviews", ""),
        "type": "review_platform",
        "priority": "critical",  # En onemli - SEO etkisi
        "checks": ["name", "address", "phone", "website", "hours", "photos", "reviews", "amenities", "description"],
    },
    "booking": {
        "name": "Booking.com",
        "url": HOTEL_INFO["social_media"].get("booking", ""),
        "type": "ota",
        "priority": "critical",
        "checks": ["name", "address", "photos", "room_types", "amenities", "description", "policies", "reviews"],
    },
    "tripadvisor": {
        "name": "TripAdvisor",
        "url": HOTEL_INFO["social_media"].get("tripadvisor", ""),
        "type": "review_platform",
        "priority": "high",
        "checks": ["name", "address", "phone", "photos", "reviews", "amenities", "description"],
    },
    "instagram": {
        "name": "Instagram",
        "url": HOTEL_INFO["social_media"].get("instagram", ""),
        "type": "social",
        "priority": "high",
        "checks": ["bio", "contact", "link", "photos", "highlights", "consistency"],
    },
    "facebook": {
        "name": "Facebook",
        "url": HOTEL_INFO["social_media"].get("facebook", ""),
        "type": "social",
        "priority": "medium",
        "checks": ["name", "address", "phone", "website", "hours", "photos", "about", "reviews"],
    },
    "airbnb": {
        "name": "Airbnb",
        "url": "",
        "type": "ota",
        "priority": "medium",
        "checks": ["name", "photos", "amenities", "description", "house_rules", "reviews"],
    },
    "expedia": {
        "name": "Expedia",
        "url": "",
        "type": "ota",
        "priority": "medium",
        "checks": ["name", "address", "photos", "amenities", "description", "reviews"],
    },
    "trivago": {
        "name": "Trivago",
        "url": "",
        "type": "ota",
        "priority": "low",
        "checks": ["name", "photos", "reviews", "price_accuracy"],
    },
}

# ==================== KONTROL KATEGORILERI ====================

CHECK_CATEGORIES = {
    "identity": {
        "label": "Kimlik Bilgileri",
        "description": "Otel adi, adresi, telefonu her yerde ayni mi?",
        "weight": 30,  # Toplam puandaki agirlik
        "fields": ["name", "address", "phone", "email", "website"],
    },
    "visual": {
        "label": "Gorsel Kalitesi",
        "description": "Fotograflar guncel, kaliteli ve dogru siralanmis mi?",
        "weight": 25,
        "fields": ["photos", "cover_photo", "photo_count", "photo_quality"],
    },
    "content": {
        "label": "Icerik Kalitesi",
        "description": "Aciklamalar eksiksiz, cezbedici ve dogru mu?",
        "weight": 20,
        "fields": ["description", "amenities", "room_types", "policies"],
    },
    "reviews": {
        "label": "Degerlendirme Yonetimi",
        "description": "Yorumlara zamaninda ve profesyonelce yanit veriliyor mu?",
        "weight": 15,
        "fields": ["rating", "review_count", "response_rate", "response_time"],
    },
    "technical": {
        "label": "Teknik Dogruluk",
        "description": "Konum, saatler, oda bilgileri teknik olarak dogru mu?",
        "weight": 10,
        "fields": ["hours", "location", "room_count", "pricing_accuracy"],
    },
}

# ==================== PLATFORM AUDIT ENGINE ====================


async def run_platform_audit(platform_id: str, manual_data: Dict = None) -> Dict:
    """
    Tek bir platformun denetimini calistir.
    manual_data: Kullanici tarafindan girilen platform bilgileri
    (API olmayan platformlar icin manuel kontrol)
    """
    from helpers import utcnow, new_id

    platform = PLATFORMS.get(platform_id)
    if not platform:
        return {"error": f"Platform bulunamadi: {platform_id}"}

    issues = []
    scores = {}
    total_checks = 0
    passed_checks = 0

    data = manual_data or {}

    # 1. Kimlik Kontrolleri
    identity_issues = _check_identity(platform_id, data)
    issues.extend(identity_issues)
    identity_passed = len([c for c in platform["checks"] if c in CHECK_CATEGORIES["identity"]["fields"]]) - len(identity_issues)
    identity_total = len([c for c in platform["checks"] if c in CHECK_CATEGORIES["identity"]["fields"]])
    scores["identity"] = max(0, round(identity_passed / max(identity_total, 1) * 100))

    # 2. Gorsel Kontrolleri
    visual_issues = _check_visuals(platform_id, data)
    issues.extend(visual_issues)
    visual_total = max(1, len(visual_issues) + (3 if data.get("photo_count", 0) >= 10 else 0))
    scores["visual"] = max(0, round((visual_total - len(visual_issues)) / visual_total * 100))

    # 3. Icerik Kontrolleri
    content_issues = _check_content(platform_id, data)
    issues.extend(content_issues)
    content_total = max(1, len([c for c in platform["checks"] if c in CHECK_CATEGORIES["content"]["fields"]]))
    scores["content"] = max(0, round((content_total - len(content_issues)) / content_total * 100))

    # 4. Degerlendirme Kontrolleri
    review_issues = _check_reviews(platform_id, data)
    issues.extend(review_issues)
    scores["reviews"] = max(0, 100 - len(review_issues) * 25)

    # 5. Teknik Kontroller
    technical_issues = _check_technical(platform_id, data)
    issues.extend(technical_issues)
    scores["technical"] = max(0, 100 - len(technical_issues) * 20)

    # Toplam puan hesapla (agirlikli)
    overall_score = 0
    for cat_id, cat in CHECK_CATEGORIES.items():
        overall_score += scores.get(cat_id, 0) * cat["weight"] / 100

    overall_score = round(overall_score)

    # Sonuc
    audit = {
        "id": new_id(),
        "platform_id": platform_id,
        "platform_name": platform["name"],
        "platform_url": platform["url"],
        "platform_type": platform["type"],
        "priority": platform["priority"],
        "overall_score": overall_score,
        "grade": _score_to_grade(overall_score),
        "category_scores": scores,
        "issues": issues,
        "issue_count": len(issues),
        "critical_issues": len([i for i in issues if i["severity"] == "critical"]),
        "data_provided": bool(manual_data),
        "created_at": utcnow(),
    }

    return audit


def _check_identity(platform_id: str, data: Dict) -> List[Dict]:
    """Kimlik bilgisi tutarlilik kontrolu"""
    issues = []

    # Otel adi kontrolu
    if data.get("name"):
        if data["name"].lower().strip() != TRUTH_SOURCE["name"].lower().strip():
            issues.append({
                "category": "identity",
                "field": "name",
                "severity": "critical",
                "message": f"Otel adi uyumsuz: '{data['name']}' (olmasi gereken: '{TRUTH_SOURCE['name']}')",
                "expected": TRUTH_SOURCE["name"],
                "found": data["name"],
                "fix": f"Otel adini '{TRUTH_SOURCE['name']}' olarak guncelleyin",
            })

    # Adres kontrolu
    if data.get("address"):
        truth_parts = [TRUTH_SOURCE["district"].lower(), TRUTH_SOURCE["city"].lower(), "kozbeyli"]
        found_lower = data["address"].lower()
        missing = [p for p in truth_parts if p not in found_lower]
        if missing:
            issues.append({
                "category": "identity",
                "field": "address",
                "severity": "high",
                "message": f"Adres eksik/hatali. Eksik: {', '.join(missing)}",
                "expected": TRUTH_SOURCE["address"],
                "found": data["address"],
                "fix": f"Adresi guncelleyin: {TRUTH_SOURCE['address']}",
            })

    # Telefon kontrolu
    if data.get("phone"):
        clean_truth = TRUTH_SOURCE["phone"].replace(" ", "").replace("+", "")
        clean_found = data["phone"].replace(" ", "").replace("+", "").replace("-", "").replace("(", "").replace(")", "")
        if clean_truth not in clean_found and clean_found not in clean_truth:
            issues.append({
                "category": "identity",
                "field": "phone",
                "severity": "critical",
                "message": f"Telefon numarasi uyumsuz: '{data['phone']}'",
                "expected": TRUTH_SOURCE["phone"],
                "found": data["phone"],
                "fix": f"Telefonu '{TRUTH_SOURCE['phone']}' olarak guncelleyin",
            })

    # Website kontrolu
    if data.get("website"):
        if "kozbeylikonagi" not in data["website"].lower():
            issues.append({
                "category": "identity",
                "field": "website",
                "severity": "high",
                "message": f"Website linki yanlis: '{data['website']}'",
                "expected": TRUTH_SOURCE["website"],
                "found": data["website"],
                "fix": f"Website'i '{TRUTH_SOURCE['website']}' olarak guncelleyin",
            })

    # Hicbir bilgi girilmediyse uyari
    if not any(data.get(f) for f in ["name", "address", "phone", "website"]):
        issues.append({
            "category": "identity",
            "field": "general",
            "severity": "info",
            "message": "Bu platform icin kimlik bilgileri henuz kontrol edilmedi",
            "fix": "Platformu ziyaret edip bilgileri girin",
        })

    return issues


def _check_visuals(platform_id: str, data: Dict) -> List[Dict]:
    """Gorsel kalitesi kontrolu"""
    issues = []

    photo_count = data.get("photo_count", 0)

    if photo_count == 0 and not data.get("photos_checked"):
        issues.append({
            "category": "visual",
            "field": "photos",
            "severity": "info",
            "message": "Fotograf kontrolu yapilmadi",
            "fix": "Platformdaki fotograflari kontrol edin ve sayisini girin",
        })
    elif photo_count < 5:
        issues.append({
            "category": "visual",
            "field": "photo_count",
            "severity": "critical",
            "message": f"Yetersiz fotograf sayisi: {photo_count} (minimum 10 onerilir)",
            "fix": "En az 10 kaliteli fotograf yukleyin (odalar, restoran, bahce, havuz, manzara)",
        })
    elif photo_count < 10:
        issues.append({
            "category": "visual",
            "field": "photo_count",
            "severity": "medium",
            "message": f"Fotograf sayisi arttirilabilir: {photo_count}/10+",
            "fix": "Daha fazla fotograf ekleyin: oda iclerinden, restorandan, manzaralardan",
        })

    if data.get("cover_photo_ok") is False:
        issues.append({
            "category": "visual",
            "field": "cover_photo",
            "severity": "high",
            "message": "Kapak fotografi uygun degil veya dusuk kaliteli",
            "fix": "Yuksek cozunurluklu, otelin dis cephesini veya en cezbedici alanini gosteren bir kapak fotografi secin",
        })

    if data.get("outdated_photos"):
        issues.append({
            "category": "visual",
            "field": "photo_quality",
            "severity": "medium",
            "message": "Eski/guncelliginini yitirmis fotograflar var",
            "fix": "Eski fotograflari kaldirin, mevsime uygun guncel fotograflar ekleyin",
        })

    return issues


def _check_content(platform_id: str, data: Dict) -> List[Dict]:
    """Icerik kalitesi kontrolu"""
    issues = []

    # Aciklama kontrolu
    desc_length = len(data.get("description", ""))
    if data.get("description_checked") and desc_length < 100:
        issues.append({
            "category": "content",
            "field": "description",
            "severity": "high",
            "message": f"Aciklama cok kisa ({desc_length} karakter). En az 200 karakter onerilir.",
            "fix": "Otelin hikayesini, konumunu, ozelliklerini ve farklilaricini anlatan detayli bir aciklama yazin",
        })

    # Amenity (olanak) kontrolu
    if data.get("amenities_listed"):
        listed = set(a.lower() for a in data.get("amenities_listed", []))
        truth = set(a.lower() for a in TRUTH_SOURCE["amenities"])
        missing = truth - listed
        if missing:
            issues.append({
                "category": "content",
                "field": "amenities",
                "severity": "medium",
                "message": f"Eksik olanaklar: {', '.join(list(missing)[:5])}",
                "fix": f"Platformda bu olanakları ekleyin: {', '.join(list(missing)[:5])}",
            })

    # Oda bilgisi kontrolu
    if data.get("room_count") and data["room_count"] != TRUTH_SOURCE["total_rooms"]:
        issues.append({
            "category": "content",
            "field": "room_types",
            "severity": "medium",
            "message": f"Oda sayisi uyumsuz: {data['room_count']} (gercek: {TRUTH_SOURCE['total_rooms']})",
            "expected": TRUTH_SOURCE["total_rooms"],
            "found": data["room_count"],
            "fix": f"Oda sayisini {TRUTH_SOURCE['total_rooms']} olarak guncelleyin",
        })

    # Iptal politikasi
    if data.get("cancellation_policy_checked") is False:
        issues.append({
            "category": "content",
            "field": "policies",
            "severity": "medium",
            "message": "Iptal politikasi kontrolu yapilmadi veya uyumsuz",
            "fix": "Iptal politikasini kontrol edin: " + CANCELLATION_POLICY["standard"]["description"],
        })

    return issues


def _check_reviews(platform_id: str, data: Dict) -> List[Dict]:
    """Degerlendirme yonetimi kontrolu"""
    issues = []

    rating = data.get("rating", 0)
    if rating and rating < 4.0:
        issues.append({
            "category": "reviews",
            "field": "rating",
            "severity": "high",
            "message": f"Puan dusuk: {rating}/5. Hedef: 4.5+",
            "fix": "Olumsuz degerlendirmelere profesyonel yanit verin, hizmet kalitesini artirin",
        })

    response_rate = data.get("response_rate", 0)
    if data.get("review_count", 0) > 0 and response_rate < 80:
        issues.append({
            "category": "reviews",
            "field": "response_rate",
            "severity": "medium",
            "message": f"Yorum yanit orani dusuk: %{response_rate} (hedef: %90+)",
            "fix": "Tum yorumlara 24 saat icinde profesyonel yanit verin",
        })

    if data.get("unanswered_negative", 0) > 0:
        issues.append({
            "category": "reviews",
            "field": "response_rate",
            "severity": "critical",
            "message": f"{data['unanswered_negative']} yanitsiz olumsuz yorum var!",
            "fix": "Oncelikle olumsuz yorumlara ozur + cozum odakli yanit verin",
        })

    return issues


def _check_technical(platform_id: str, data: Dict) -> List[Dict]:
    """Teknik dogruluk kontrolu"""
    issues = []

    # Check-in/out saatleri
    if data.get("check_in") and data["check_in"] != TRUTH_SOURCE["check_in"]:
        issues.append({
            "category": "technical",
            "field": "hours",
            "severity": "high",
            "message": f"Check-in saati uyumsuz: {data['check_in']} (olmasi gereken: {TRUTH_SOURCE['check_in']})",
            "fix": f"Check-in saatini {TRUTH_SOURCE['check_in']} olarak guncelleyin",
        })

    if data.get("check_out") and data["check_out"] != TRUTH_SOURCE["check_out"]:
        issues.append({
            "category": "technical",
            "field": "hours",
            "severity": "high",
            "message": f"Check-out saati uyumsuz: {data['check_out']} (olmasi gereken: {TRUTH_SOURCE['check_out']})",
            "fix": f"Check-out saatini {TRUTH_SOURCE['check_out']} olarak guncelleyin",
        })

    # Konum kontrolu
    if data.get("latitude") and data.get("longitude"):
        lat_diff = abs(float(data["latitude"]) - TRUTH_SOURCE["latitude"])
        lon_diff = abs(float(data["longitude"]) - TRUTH_SOURCE["longitude"])
        if lat_diff > 0.01 or lon_diff > 0.01:
            issues.append({
                "category": "technical",
                "field": "location",
                "severity": "critical",
                "message": "Harita konumu yanlis! Musteri oteli bulamayabilir.",
                "fix": f"Konumu duzeltin: {TRUTH_SOURCE['latitude']}, {TRUTH_SOURCE['longitude']}",
            })

    return issues


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 40:
        return "D"
    return "F"


# ==================== TOPLU DENETIM ====================

async def run_full_audit(audit_data: Dict = None) -> Dict:
    """Tum platformlar icin toplu denetim calistir"""
    from helpers import utcnow, new_id

    results = []
    all_issues = []

    for platform_id in PLATFORMS:
        platform_data = (audit_data or {}).get(platform_id, {})
        audit = await run_platform_audit(platform_id, platform_data)
        results.append(audit)
        all_issues.extend(audit.get("issues", []))

    # Genel skor
    total_score = 0
    scored_count = 0
    for r in results:
        if r.get("data_provided"):
            total_score += r["overall_score"]
            scored_count += 1

    overall = round(total_score / max(scored_count, 1))

    # Kategori bazli ozet
    category_summary = {}
    for cat_id, cat in CHECK_CATEGORIES.items():
        cat_scores = [r["category_scores"].get(cat_id, 0) for r in results if r.get("data_provided")]
        category_summary[cat_id] = {
            "label": cat["label"],
            "avg_score": round(sum(cat_scores) / max(len(cat_scores), 1)),
            "weight": cat["weight"],
        }

    full_audit = {
        "id": new_id(),
        "type": "full_audit",
        "overall_score": overall,
        "grade": _score_to_grade(overall),
        "platforms_audited": scored_count,
        "platforms_total": len(PLATFORMS),
        "total_issues": len(all_issues),
        "critical_issues": len([i for i in all_issues if i["severity"] == "critical"]),
        "high_issues": len([i for i in all_issues if i["severity"] == "high"]),
        "category_summary": category_summary,
        "platform_results": results,
        "created_at": utcnow(),
    }

    return full_audit


async def save_audit(audit: Dict) -> Dict:
    """Denetim sonucunu DB'ye kaydet"""
    from database import db
    await db.presence_audits.insert_one(audit)
    return {"success": True, "id": audit["id"]}


async def get_audit_history(limit: int = 10) -> List[Dict]:
    """Gecmis denetim sonuclarini getir"""
    from database import db
    audits = await db.presence_audits.find(
        {}, {"_id": 0, "platform_results": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return audits


def get_platforms_info() -> Dict:
    """Platform bilgilerini ve kontrol listesini getir"""
    return {
        "platforms": {
            pid: {
                "name": p["name"],
                "url": p["url"],
                "type": p["type"],
                "priority": p["priority"],
                "checks": p["checks"],
            }
            for pid, p in PLATFORMS.items()
        },
        "categories": {
            cid: {
                "label": c["label"],
                "description": c["description"],
                "weight": c["weight"],
            }
            for cid, c in CHECK_CATEGORIES.items()
        },
        "truth_source": TRUTH_SOURCE,
    }
