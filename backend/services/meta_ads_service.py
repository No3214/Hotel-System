"""
Kozbeyli Konagi - Meta Ads Service
Facebook & Instagram Ads yonetimi + AI destekli reklam olusturma

Ozellikler:
- Kampanya olusturma/yonetme (mock + API-ready)
- Hedef kitle segmentasyonu (dugun, tatil, is, yemek)
- AI ile reklam metni olusturma
- Performans metrikleri
- Butce yonetimi
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime, timezone, timedelta
from helpers import utcnow, new_id

logger = logging.getLogger(__name__)

# ==================== AUDIENCE SEGMENTS ====================

AUDIENCE_SEGMENTS = {
    "wedding": {
        "name": "Dugun & Nisan",
        "tr": "Dugun Planlayanlari",
        "interests": ["Dugun mekanlari", "Kir dugunu", "Nisan organizasyonu", "Gelin buketi"],
        "age_range": "25-40",
        "demographics": "Nisanli ciftler, dugun planlayicilar",
        "geo": "Izmir, Istanbul, Ankara (yakin cografi bolge)",
        "budget_suggestion": "50-150 TL/gun",
    },
    "weekend_getaway": {
        "name": "Hafta Sonu Kacamagi",
        "tr": "Tatil Arayanlar",
        "interests": ["Butik otel", "Hafta sonu kacamagi", "Dogayla ic ice", "Ege tatili"],
        "age_range": "28-55",
        "demographics": "Ciftler, aileler, kucuk gruplar",
        "geo": "Izmir, Istanbul, Ankara, Bursa",
        "budget_suggestion": "30-100 TL/gun",
    },
    "foodie": {
        "name": "Gastronomi",
        "tr": "Yemek Tutkunlari",
        "interests": ["Ege mutfagi", "Restoran", "Organik yemek", "Gastronomi turu"],
        "age_range": "25-60",
        "demographics": "Yemek meraklilari, blog yazarlari",
        "geo": "Izmir ve cevresi (50km)",
        "budget_suggestion": "20-60 TL/gun",
    },
    "corporate": {
        "name": "Kurumsal",
        "tr": "Is Toplantilari",
        "interests": ["Toplanti mekani", "Team building", "Sirket etkinligi"],
        "age_range": "30-55",
        "demographics": "Yoneticiler, HR profesyonelleri",
        "geo": "Izmir, Istanbul",
        "budget_suggestion": "40-120 TL/gun",
    },
    "romantic": {
        "name": "Romantik Kacamak",
        "tr": "Romantik Ciftler",
        "interests": ["Romantik tatil", "Balay", "Yildonumu", "Ozel gece"],
        "age_range": "25-50",
        "demographics": "Ciftler, evli ciftler",
        "geo": "Izmir, Istanbul, Ankara",
        "budget_suggestion": "40-100 TL/gun",
    },
}

# ==================== AD TEMPLATES ====================

AD_TEMPLATES = {
    "wedding": {
        "headline": "Hayalinizdeki Kir Dugunu Kozbeyli Konagi'nda",
        "description": "Foca'nin essiz tasinda, zeytin agaclari arasinda unutulmaz bir dugun. 14 yillik deneyim, kisisellestirilmis organizasyon.",
        "cta": "Teklif Alin",
        "image_suggestion": "Bahce dugun setup, mumlarin esliginde masa duzeni",
    },
    "weekend": {
        "headline": "Sehirden Kacis: Kozbeyli Konagi'nda Huzur",
        "description": "Dogayla ic ice, organik kahvalti, Ege'nin en guzel koyunde butik konaklama. Hafta sonu icin son odalar!",
        "cta": "Hemen Rezervasyon Yap",
        "image_suggestion": "Konak dis cephe, bahce manzarasi, kahvalti sofrasi",
    },
    "restaurant": {
        "headline": "Ege'nin Lezzetleri Kozbeyli Konagi Restoraninda",
        "description": "Organik, yerel malzemelerle hazirlanan Ege mutfagi. Bahce manzarasinda mumlarin esliginde yemek keyfi.",
        "cta": "Masa Ayirtin",
        "image_suggestion": "Dallas steak, meze tabagi, bahce restoran",
    },
    "seasonal": {
        "headline": "Bu Sezon Kozbeyli Konagi'nda Sizi Bekliyoruz",
        "description": "Mevsime ozel firsatlar ve etkinliklerle unutulmaz bir deneyim. Sinirli kontenjan!",
        "cta": "Firsati Yakalayin",
        "image_suggestion": "Mevsime uygun dis mekan goruntusu",
    },
}

# ==================== AI PROMPTS ====================

META_AD_SYSTEM_PROMPT = """Sen Kozbeyli Konagi icin Meta (Facebook/Instagram) reklam metni yazan uzman bir dijital pazarlamacisin.

KONAK BILGISI:
- Kozbeyli Konagi: Foca/Izmir'de 14 yillik butik tas otel & restoran
- 6 oda (Loft Suite 6000TL, Deluxe 5000TL, Superior 3500-4500TL, Standard 2500TL)
- Organik koy kahvaltisi dahil
- Dugun/etkinlik mekani (kir dugunu, nisan, is toplantisi)
- Restoran: Ege mutfagi, Dallas Steak (3500TL), bahce ortami

REKLAM YAZIM KURALLARI:
1. Facebook: Baslik max 40 karakter, aciklama max 125 karakter
2. Instagram: Gorsel odakli, emoji kullan, hashtag ekle
3. Her reklamda TEK bir CTA olsun
4. Hedef kitleye gore psikoloji kullan (dugun=hayallere hitap, yemek=lezzet, tatil=huzur)
5. Fiyat avantaji veya sinirli kontenjan vurgula
6. Turkce yaz, samimi ama profesyonel ton

CIKTI FORMATI (JSON):
{
  "headline": "Baslik",
  "primary_text": "Ana metin (Facebook icin)",
  "description": "Kisa aciklama",
  "cta_button": "CTA butonu metni",
  "hashtags": ["#hashtag1", "#hashtag2"],
  "targeting_suggestion": "Hedefleme onerisi",
  "ab_variant": { ... } // ikinci varyant
}"""


async def generate_ad_copy(segment: str, ad_type: str = "awareness", platform: str = "both") -> dict:
    """AI ile Meta reklam metni olustur"""
    from gemini_service import get_chat_response

    template = AD_TEMPLATES.get(ad_type, AD_TEMPLATES["weekend"])
    audience = AUDIENCE_SEGMENTS.get(segment, AUDIENCE_SEGMENTS["weekend_getaway"])

    prompt = f"""Asagidaki hedef kitle icin Facebook ve Instagram reklami olustur:

Hedef Kitle: {audience['name']} - {audience['tr']}
Ilgi Alanlari: {', '.join(audience['interests'])}
Yas Araligi: {audience['age_range']}
Demografik: {audience['demographics']}
Platform: {platform}

Sablon Referans:
Baslik: {template['headline']}
Aciklama: {template['description']}
CTA: {template['cta']}

Lutfen bu sablonu baz alarak yaratici, donusum odakli bir reklam metni olustur.
A/B test icin 2 varyant ver. JSON formatinda cevapla."""

    result = await get_chat_response(
        message=prompt,
        session_id=f"meta-ad-{segment}-{new_id()[:8]}",
        system_prompt=META_AD_SYSTEM_PROMPT,
    )

    return {
        "ad_copy": result,
        "segment": segment,
        "audience": audience,
        "template_used": ad_type,
        "platform": platform,
        "generated_at": utcnow(),
    }


async def get_campaign_performance(campaign_id: Optional[str] = None) -> dict:
    """Kampanya performans metrikleri (mock data - API entegrasyonu icin hazir)"""
    from database import db
    import random

    if campaign_id:
        campaign = await db.meta_campaigns.find_one({"id": campaign_id}, {"_id": 0})
        if campaign:
            return campaign

    # Mock performance data for demo
    return {
        "summary": {
            "total_spend": round(random.uniform(500, 5000), 2),
            "total_impressions": random.randint(5000, 50000),
            "total_clicks": random.randint(200, 2000),
            "total_conversions": random.randint(5, 50),
            "ctr": round(random.uniform(1.5, 5.0), 2),
            "cpc": round(random.uniform(0.5, 3.0), 2),
            "roas": round(random.uniform(2.0, 8.0), 2),
            "period": "son_30_gun",
        },
        "campaigns": [
            {
                "id": "camp_demo_1",
                "name": "Dugun Mekani - Instagram",
                "status": "active",
                "objective": "conversions",
                "budget_daily": 100,
                "spend": round(random.uniform(200, 2000), 2),
                "impressions": random.randint(3000, 20000),
                "clicks": random.randint(100, 1000),
                "conversions": random.randint(2, 20),
                "ctr": round(random.uniform(2.0, 5.0), 2),
                "platform": "instagram",
            },
            {
                "id": "camp_demo_2",
                "name": "Hafta Sonu Kacamagi - Facebook",
                "status": "active",
                "objective": "traffic",
                "budget_daily": 75,
                "spend": round(random.uniform(150, 1500), 2),
                "impressions": random.randint(2000, 15000),
                "clicks": random.randint(80, 800),
                "conversions": random.randint(1, 10),
                "ctr": round(random.uniform(1.5, 4.0), 2),
                "platform": "facebook",
            },
            {
                "id": "camp_demo_3",
                "name": "Restoran Tanitimi - Both",
                "status": "paused",
                "objective": "awareness",
                "budget_daily": 50,
                "spend": round(random.uniform(100, 800), 2),
                "impressions": random.randint(5000, 30000),
                "clicks": random.randint(50, 500),
                "conversions": random.randint(0, 5),
                "ctr": round(random.uniform(1.0, 3.0), 2),
                "platform": "both",
            },
        ],
    }


async def create_campaign(data: dict) -> dict:
    """Yeni kampanya olustur"""
    from database import db

    campaign = {
        "id": new_id(),
        "name": data.get("name", "Yeni Kampanya"),
        "objective": data.get("objective", "awareness"),
        "segment": data.get("segment", "weekend_getaway"),
        "platform": data.get("platform", "both"),
        "budget_daily": data.get("budget_daily", 50),
        "budget_total": data.get("budget_total", 0),
        "status": "draft",
        "ad_copy": data.get("ad_copy", {}),
        "targeting": AUDIENCE_SEGMENTS.get(data.get("segment", "weekend_getaway"), {}),
        "impressions": 0,
        "clicks": 0,
        "conversions": 0,
        "spend": 0,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }

    await db.meta_campaigns.insert_one(campaign)
    del campaign["_id"]
    return campaign


async def update_campaign_status(campaign_id: str, status: str) -> dict:
    """Kampanya durumunu guncelle"""
    from database import db

    result = await db.meta_campaigns.update_one(
        {"id": campaign_id},
        {"$set": {"status": status, "updated_at": utcnow()}}
    )
    if result.modified_count == 0:
        return {"error": "Kampanya bulunamadi"}

    campaign = await db.meta_campaigns.find_one({"id": campaign_id}, {"_id": 0})
    return campaign or {"error": "Kampanya bulunamadi"}
