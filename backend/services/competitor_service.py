"""
Kozbeyli Konagi - Rakip Analizi Servisi
Yakin butik otellerin karsilastirmali analizi
"""
import logging
from typing import Optional, List, Dict
from helpers import utcnow, new_id

logger = logging.getLogger(__name__)

# ==================== DEFAULT COMPETITORS ====================

COMPETITORS = {
    "hanedan_butik": {
        "id": "hanedan_butik",
        "name": "Hanedan Butik Otel",
        "type": "butik_otel",
        "location": "Foca, Izmir",
        "platforms": {
            "google": {"rating": 4.3, "review_count": 95, "url": "g.page/hanedanbutik"},
            "booking": {"rating": 8.7, "review_count": 62, "url": "booking.com/hanedanbutik"},
            "tripadvisor": {"rating": 4.0, "review_count": 48, "url": "tripadvisor.com/hanedanbutik"},
        },
        "price_range": "$$",
        "strengths": ["Denize yakinlik", "Kahvalti"],
        "weaknesses": ["Otopark", "Gece gurultusu"],
    },
    "tas_konak": {
        "id": "tas_konak",
        "name": "Tas Konak Otel",
        "type": "butik_otel",
        "location": "Eski Foca, Izmir",
        "platforms": {
            "google": {"rating": 4.5, "review_count": 112, "url": "g.page/taskonak"},
            "booking": {"rating": 9.0, "review_count": 78, "url": "booking.com/taskonak"},
            "tripadvisor": {"rating": 4.5, "review_count": 65, "url": "tripadvisor.com/taskonak"},
        },
        "price_range": "$$$",
        "strengths": ["Tarihi doku", "Konum", "Dekorasyon"],
        "weaknesses": ["Fiyat", "Kucuk odalar"],
    },
    "foca_sahil": {
        "id": "foca_sahil",
        "name": "Foca Sahil Pansiyon",
        "type": "pansiyon",
        "location": "Foca, Izmir",
        "platforms": {
            "google": {"rating": 4.1, "review_count": 67, "url": "g.page/focasahil"},
            "booking": {"rating": 8.2, "review_count": 41, "url": "booking.com/focasahil"},
        },
        "price_range": "$",
        "strengths": ["Fiyat/performans", "Sahil erisimine yakinlik"],
        "weaknesses": ["Eski tesis", "Sinirli hizmetler"],
    },
    "zeytindalı_konaklari": {
        "id": "zeytindalı_konaklari",
        "name": "Zeytindali Konaklari",
        "type": "butik_otel",
        "location": "Yeni Foca, Izmir",
        "platforms": {
            "google": {"rating": 4.4, "review_count": 83, "url": "g.page/zeytindali"},
            "booking": {"rating": 8.9, "review_count": 55, "url": "booking.com/zeytindali"},
            "tripadvisor": {"rating": 4.3, "review_count": 39, "url": "tripadvisor.com/zeytindali"},
        },
        "price_range": "$$",
        "strengths": ["Bahce", "Huzurlu ortam", "Organik kahvalti"],
        "weaknesses": ["Merkeze uzaklik", "Ulasim"],
    },
}

# ==================== KOZBEYLI KONAGI PROFILI ====================

KOZBEYLI_PROFILE = {
    "name": "Kozbeyli Konagi",
    "type": "butik_otel",
    "location": "Kozbeyli, Foca, Izmir",
    "platforms": {
        "google": {"rating": 4.6, "review_count": 127},
        "booking": {"rating": 9.1, "review_count": 85},
        "tripadvisor": {"rating": 4.5, "review_count": 72},
    },
    "price_range": "$$",
    "strengths": ["Yemek", "Atmosfer", "Personel", "Tarihi doku", "Huzur"],
    "weaknesses": ["Ulasim", "Merkeze uzaklik"],
}


# ==================== SERVICE FUNCTIONS ====================

async def get_competitors() -> List[dict]:
    """Tum rakipleri listele (DB + varsayilan)"""
    from database import db

    # DB'den kayitli rakipleri al
    db_competitors = await db.competitors.find({}, {"_id": 0}).to_list(100)
    db_ids = {c["id"] for c in db_competitors}

    # Varsayilan rakipleri ekle (DB'de yoksa)
    all_competitors = list(db_competitors)
    for comp_id, comp_data in COMPETITORS.items():
        if comp_id not in db_ids:
            all_competitors.append(comp_data)

    return all_competitors


async def add_competitor(data: dict) -> dict:
    """Yeni rakip ekle"""
    from database import db

    competitor = {
        "id": new_id(),
        "name": data["name"],
        "type": data.get("type", "butik_otel"),
        "location": data.get("location", "Foca, Izmir"),
        "platforms": {},
        "price_range": data.get("price_range", "$$"),
        "strengths": [],
        "weaknesses": [],
        "created_at": utcnow(),
    }

    # Platform bilgilerini ekle
    if data.get("booking_url"):
        competitor["platforms"]["booking"] = {
            "url": data["booking_url"],
            "rating": data.get("rating"),
            "review_count": data.get("review_count"),
        }
    if data.get("tripadvisor_url"):
        competitor["platforms"]["tripadvisor"] = {
            "url": data["tripadvisor_url"],
            "rating": data.get("rating"),
            "review_count": data.get("review_count"),
        }
    if data.get("google_url"):
        competitor["platforms"]["google"] = {
            "url": data["google_url"],
            "rating": data.get("rating"),
            "review_count": data.get("review_count"),
        }

    await db.competitors.insert_one(competitor)
    competitor.pop("_id", None)
    return competitor


async def analyze_competitor(competitor_data: dict) -> dict:
    """AI ile rakip analizi"""
    from services.ai_provider_service import ai_request, build_system_prompt

    system_prompt = build_system_prompt(
        role="Sen otelcilik sektorunde deneyimli bir pazar analisti ve rekabet stratejistisin.",
        task="Verilen rakip otel bilgilerini analiz et ve Kozbeyli Konagi icin stratejik onerilerde bulun.",
        context=f"""<rakip_bilgileri>
{_format_competitor_for_prompt(competitor_data)}
</rakip_bilgileri>

<bizim_otel>
Ad: Kozbeyli Konagi
Konum: Kozbeyli, Foca, Izmir
Tur: Butik Otel
Google Puani: 4.6 | Booking: 9.1
Guclu Yanlar: Yemek, Atmosfer, Personel
</bizim_otel>""",
        output_format="""{
  "rakip_degerlendirme": "Genel degerlendirme metni",
  "tehdit_seviyesi": "dusuk/orta/yuksek",
  "farklilasma_alanlari": ["Alan 1", "Alan 2"],
  "stratejik_oneriler": ["Oneri 1", "Oneri 2", "Oneri 3"],
  "fiyat_karsilastirma": "Karsilastirma metni",
  "guclu_yanlari": ["Guclu yan 1", ...],
  "zayif_yanlari": ["Zayif yan 1", ...]
}""",
    )

    result = await ai_request(
        message=f"Bu rakip oteli analiz et: {competitor_data.get('name', 'Bilinmeyen')}",
        system_prompt=system_prompt,
        task_type="data_analysis",
    )

    return {
        "competitor": competitor_data.get("name"),
        "analysis": result["response"],
        "provider": result.get("provider_name", "AI"),
        "analyzed_at": utcnow(),
    }


async def compare_ratings(competitor_ids: Optional[List[str]] = None, competitors: Optional[List[dict]] = None) -> dict:
    """Platform bazinda puan karsilastirmasi"""
    if competitors is None:
        competitors = await get_competitors()

    # Belirli rakipler istendiyse filtrele
    if competitor_ids:
        competitors = [c for c in competitors if c.get("id") in competitor_ids]

    comparison = {
        "kozbeyli_konagi": KOZBEYLI_PROFILE["platforms"],
        "competitors": [],
        "platform_averages": {},
    }

    platform_totals = {"google": [], "booking": [], "tripadvisor": []}

    for comp in competitors:
        comp_entry = {
            "name": comp["name"],
            "platforms": comp.get("platforms", {}),
        }
        comparison["competitors"].append(comp_entry)

        # Ortalama hesabi icin topla
        for platform in ["google", "booking", "tripadvisor"]:
            if platform in comp.get("platforms", {}):
                rating = comp["platforms"][platform].get("rating")
                if rating:
                    platform_totals[platform].append(rating)

    # Platform ortalamalari
    for platform, ratings in platform_totals.items():
        if ratings:
            avg = round(sum(ratings) / len(ratings), 1)
            our_rating = KOZBEYLI_PROFILE["platforms"].get(platform, {}).get("rating", 0)
            comparison["platform_averages"][platform] = {
                "competitor_average": avg,
                "our_rating": our_rating,
                "difference": round(our_rating - avg, 1) if our_rating else None,
                "position": "above_average" if our_rating and our_rating > avg else "below_average",
            }

    comparison["generated_at"] = utcnow()
    return comparison


async def generate_swot() -> dict:
    """AI ile SWOT analizi olustur"""
    from services.ai_provider_service import ai_request, build_system_prompt

    competitors = await get_competitors()
    competitors_text = "\n".join([
        f"- {c['name']}: {c.get('location', '')}, "
        f"Google: {c.get('platforms', {}).get('google', {}).get('rating', 'N/A')}, "
        f"Guclu: {', '.join(c.get('strengths', []))}, "
        f"Zayif: {', '.join(c.get('weaknesses', []))}"
        for c in competitors
    ])

    system_prompt = build_system_prompt(
        role="Sen otelcilik sektorunde SWOT analizi uzmanisin. Kozbeyli Konagi'nin stratejik konumunu degerlendiriyorsun.",
        task="Kozbeyli Konagi icin kapsamli bir SWOT analizi olustur. Rakip bilgilerini de dikkate al.",
        context=f"""<bizim_otel>
Ad: Kozbeyli Konagi
Konum: Kozbeyli Koyu, Foca, Izmir
Tur: Tarihi tas konak - butik otel
Google: 4.6 (127 yorum) | Booking: 9.1 (85 yorum) | TripAdvisor: 4.5 (72 yorum)
Guclu Yanlar: Yemek kalitesi, Tarihi atmosfer, Sicak personel, Huzurlu ortam
Zayif Yanlar: Sehir merkezine uzaklik, Ulasim
Fiyat: Orta-ust segment ($$)
</bizim_otel>

<rakipler>
{competitors_text}
</rakipler>""",
        output_format="""{
  "strengths": ["Guclu yan 1", "Guclu yan 2", ...],
  "weaknesses": ["Zayif yan 1", "Zayif yan 2", ...],
  "opportunities": ["Firsat 1", "Firsat 2", ...],
  "threats": ["Tehdit 1", "Tehdit 2", ...],
  "summary": "Genel degerlendirme metni",
  "priority_actions": ["Oncelikli aksiyon 1", "Oncelikli aksiyon 2", ...]
}""",
    )

    result = await ai_request(
        message="Kozbeyli Konagi icin detayli SWOT analizi olustur. Rakip otelleri de dikkate al.",
        system_prompt=system_prompt,
        task_type="data_analysis",
    )

    return {
        "swot": result["response"],
        "provider": result.get("provider_name", "AI"),
        "competitor_count": len(competitors),
        "generated_at": utcnow(),
    }


async def get_market_position() -> dict:
    """Pazar konumu raporu"""
    competitors = await get_competitors()
    comparison = await compare_ratings(competitors=competitors)

    # Genel puan hesapla
    our_avg = 0
    our_count = 0
    for platform, data in KOZBEYLI_PROFILE["platforms"].items():
        if data.get("rating"):
            our_avg += data["rating"]
            our_count += 1
    our_avg = round(our_avg / our_count, 2) if our_count else 0

    comp_ratings = []
    for comp in competitors:
        ratings = [
            p.get("rating", 0)
            for p in comp.get("platforms", {}).values()
            if p.get("rating")
        ]
        if ratings:
            comp_ratings.append(sum(ratings) / len(ratings))

    market_avg = round(sum(comp_ratings) / len(comp_ratings), 2) if comp_ratings else 0

    # Siralama
    all_ratings = comp_ratings + [our_avg]
    all_ratings.sort(reverse=True)
    position = all_ratings.index(our_avg) + 1 if our_avg in all_ratings else len(all_ratings)

    total_review_count = sum(
        p.get("review_count", 0)
        for p in KOZBEYLI_PROFILE["platforms"].values()
    )

    return {
        "hotel": "Kozbeyli Konagi",
        "our_average_rating": our_avg,
        "market_average_rating": market_avg,
        "rating_difference": round(our_avg - market_avg, 2),
        "market_position": position,
        "total_competitors": len(competitors),
        "total_review_count": total_review_count,
        "strengths": KOZBEYLI_PROFILE["strengths"],
        "weaknesses": KOZBEYLI_PROFILE["weaknesses"],
        "platform_comparison": comparison.get("platform_averages", {}),
        "status": "lider" if position == 1 else ("rekabetci" if position <= 2 else "gelistirilmeli"),
        "generated_at": utcnow(),
    }


# ==================== HELPERS ====================

def _format_competitor_for_prompt(comp: dict) -> str:
    """Rakip bilgilerini prompt icin formatla"""
    lines = [
        f"Ad: {comp.get('name', 'Bilinmeyen')}",
        f"Tur: {comp.get('type', 'N/A')}",
        f"Konum: {comp.get('location', 'N/A')}",
        f"Fiyat Araligi: {comp.get('price_range', 'N/A')}",
    ]
    for platform, data in comp.get("platforms", {}).items():
        rating = data.get("rating", "N/A")
        reviews = data.get("review_count", "N/A")
        lines.append(f"{platform.capitalize()}: Puan {rating}, {reviews} yorum")
    if comp.get("strengths"):
        lines.append(f"Guclu Yanlar: {', '.join(comp['strengths'])}")
    if comp.get("weaknesses"):
        lines.append(f"Zayif Yanlar: {', '.join(comp['weaknesses'])}")
    return "\n".join(lines)
