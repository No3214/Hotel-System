"""
Kozbeyli Konagi - Marketing & AI Copywriter Router
Sosyal medya + WhatsApp + Pinterest odakli pazarlama ajansi API'leri
+ AI Lifecycle Re-engagement + B2B Corporate Outreach
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from database import db
from helpers import utcnow, new_id, clean_doc
import json
from gemini_service import get_chat_response

router = APIRouter(tags=["marketing"])


# ==================== REQUEST MODELS ====================

class CopyRequest(BaseModel):
    topic: str
    platform: str = "instagram"
    psychology: Optional[str] = None  # social_proof, scarcity, fomo, urgency, authority, reciprocity
    tone: str = "warm"  # warm, professional, playful, elegant
    include_ab: bool = False


class CTAOptimizeRequest(BaseModel):
    current_cta: str
    context: str = ""


class RewriteRequest(BaseModel):
    original_text: str
    platform: str = "instagram"
    goal: str = "reservation"  # reservation, engagement, awareness, event, review


class WhatsAppSequenceRequest(BaseModel):
    sequence_type: str = "welcome"  # welcome, pre_arrival, during_stay, post_stay, win_back, seasonal, wedding, loyalty
    target_audience: str = "new_guest"
    message_count: int = 5


class PinterestPinRequest(BaseModel):
    category: str = "wedding"  # wedding, food, venue, local, decor
    count: int = 5
    image_descriptions: Optional[List[str]] = None


class ContentStrategyRequest(BaseModel):
    period: str = "weekly"  # weekly, monthly
    focus: Optional[str] = None
    platforms: Optional[List[str]] = None


class PsychologyRequest(BaseModel):
    post_type: str = "default"
    target: str = "couples"  # couples, families, business, solo, wedding


# ==================== ENDPOINTS ====================

@router.post("/marketing/ai-copy")
async def generate_copy(data: CopyRequest):
    """AI ile donusum odakli reklam metni uret"""
    from services.ai_copywriter_service import generate_conversion_copy
    result = await generate_conversion_copy(
        topic=data.topic,
        platform=data.platform,
        psychology=data.psychology,
        tone=data.tone,
        include_ab=data.include_ab,
    )
    return result


@router.post("/marketing/optimize-cta")
async def optimize_cta(data: CTAOptimizeRequest):
    """Mevcut CTA'yi optimize et"""
    from services.ai_copywriter_service import optimize_cta
    result = await optimize_cta(data.current_cta, data.context)
    return result


@router.post("/marketing/rewrite")
async def rewrite_copy(data: RewriteRequest):
    """Mevcut metni donusum odakli yeniden yaz"""
    from services.ai_copywriter_service import rewrite_for_conversion
    result = await rewrite_for_conversion(
        original_text=data.original_text,
        platform=data.platform,
        goal=data.goal,
    )
    return result


@router.post("/marketing/whatsapp-sequence")
async def generate_wa_sequence(data: WhatsAppSequenceRequest):
    """WhatsApp mesaj dizisi uret"""
    from services.ai_copywriter_service import generate_whatsapp_sequence
    result = await generate_whatsapp_sequence(
        sequence_type=data.sequence_type,
        target_audience=data.target_audience,
        message_count=data.message_count,
    )
    return result


@router.post("/marketing/pinterest-pins")
async def generate_pins(data: PinterestPinRequest):
    """Pinterest pin aciklamalari uret (dugun, yemek, mekan)"""
    from services.ai_copywriter_service import generate_pinterest_pins
    result = await generate_pinterest_pins(
        category=data.category,
        count=data.count,
        image_descriptions=data.image_descriptions,
    )
    return result


@router.post("/marketing/content-strategy")
async def generate_strategy(data: ContentStrategyRequest):
    """Haftalik/aylik icerik stratejisi olustur"""
    from services.ai_copywriter_service import generate_content_strategy
    result = await generate_content_strategy(
        period=data.period,
        focus=data.focus,
        platforms=data.platforms,
    )
    return result


@router.post("/marketing/psychology-tips")
async def psychology_tips(data: PsychologyRequest):
    """Hedef kitleye gore psikoloji onerileri"""
    from services.ai_copywriter_service import get_psychology_suggestions
    result = await get_psychology_suggestions(data.post_type, data.target)
    return result


@router.get("/marketing/platforms")
async def get_platforms():
    """Desteklenen platformlar ve kurallari"""
    from services.ai_copywriter_service import PLATFORM_COPY_RULES
    return {"platforms": PLATFORM_COPY_RULES}


@router.get("/marketing/psychology-triggers")
async def get_triggers():
    """Mevcut psikoloji tetikleyicileri"""
    from services.ai_copywriter_service import COPY_RULES
    return {
        "triggers": COPY_RULES["psychology_triggers"],
        "cta_principles": COPY_RULES["cta_principles"],
    }


@router.get("/marketing/sequence-types")
async def get_sequence_types():
    """WhatsApp dizi turleri"""
    return {
        "types": {
            "welcome": "Yeni misafir hosgeldin",
            "pre_arrival": "Check-in oncesi hatirlatma",
            "during_stay": "Konaklama sirasinda",
            "post_stay": "Konaklama sonrasi",
            "win_back": "Geri kazanma",
            "seasonal": "Mevsimsel kampanya",
            "wedding": "Dugun/nisan teklifi",
            "loyalty": "Sadik misafir odulu",
        }
    }


@router.get("/marketing/pinterest-boards")
async def get_pinterest_boards():
    """Pinterest board kategorileri"""
    return {
        "boards": {
            "wedding": {"tr": "Dugun Mekanlari Izmir", "en": "Wedding Venues Izmir"},
            "food": {"tr": "Ege Mutfagi", "en": "Aegean Cuisine"},
            "venue": {"tr": "Butik Otel Foca", "en": "Boutique Hotel Foca"},
            "local": {"tr": "Foca Gezi Rehberi", "en": "Foca Travel Guide"},
            "decor": {"tr": "Kir Dugunu Dekorasyon", "en": "Rustic Wedding Decor"},
        }
    }


# ==================== PHASE 12: AI LIFECYCLE RE-ENGAGEMENT ====================

@router.get("/marketing/ai-re-engagement")
async def ai_re_engagement_campaigns():
    """
    Eski misafirleri tespit edip onlara ozel, isimlerine hitap eden
    (Retargeting) pazarlama mesajlari uretir.
    """
    try:
        now_str = utcnow()[:10]

        past_res = await db.reservations.find({
            "status": "checked_out"
        }, {"_id": 0, "guest_name": 1, "check_in": 1, "room_type": 1, "notes": 1, "guest_email": 1, "guest_phone": 1}).sort("check_in", 1).to_list(100)

        if not past_res:
            past_res = [
                {"guest_name": "Canan Yilmaz", "check_in": "2023-08-15", "room_type": "Suit", "guest_phone": "5551234567", "notes": "Balayi cifti, sarap ikrami yapildi."},
                {"guest_name": "Ahmet Demir", "check_in": "2024-01-20", "room_type": "Standart", "guest_email": "ahmet@gmail.com", "notes": "Sirket gezisi, kahvalti onemli."}
            ]

        profiles_to_analyze = []
        for r in past_res[:10]:
            profiles_to_analyze.append({
                "name": r.get("guest_name", "Misafir"),
                "last_visit_date": r.get("check_in", ""),
                "stayed_in": r.get("room_type", ""),
                "known_preferences": r.get("notes", "Bilinmiyor")
            })

        prompt = f"""
        Sen Kozbeyli Konagi'nin AI Pazarlama (CRM & Retargeting) Uzmanisin.
        Asagidaki eski misafir listesine bakarak onlari 'tekrar otele gelmeye tesvik edecek'
        KIŞİSELLEŞTİRİLMİŞ, sicak, ikna edici ve cazip teklifler iceren kampanya SMS/Email mesajlari uret.

        Eski Misafirler:
        {json.dumps(profiles_to_analyze, ensure_ascii=False, indent=2)}

        Gorevin:
        Her bir misafir icin spesifik gecmisini yansitan bir giris ve onlara uygun bir 'Teklif (Kanca)' iceren mesaj draftlari olustur.

        Sadece JSON dondur:
        {{
           "campaigns": [
              {{
                 "guest_name": "Canan Yilmaz",
                 "target_segment": "Yildonumu Kutlamasi",
                 "channel": "WhatsApp/SMS",
                 "message": "Merhaba Canan Hanim, Kozbeyli Konagi'ndan sevgiler!"
              }}
           ]
        }}
        """

        ai_resp = await get_chat_response("re_engagement", new_id(), prompt)

        import re
        json_match = re.search(r'```(?:json)?(.*?)```', ai_resp, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_resp
        marketing_data = json.loads(res_str)

        return {
            "success": True,
            "campaigns": marketing_data.get("campaigns", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Retargeting hatasi: {str(e)}")


# ==================== PHASE 13: AI B2B CORPORATE OUTREACH & LEAD GEN ====================

@router.get("/marketing/b2b-leads")
async def ai_b2b_corporate_leads(industry: str = "Genel"):
    """
    Kullanicinin girdigi sektore gore kurumsal satis stratejisi ve lead uretir.
    """
    try:
        prompt = f"""
        Sen Kozbeyli Konagi adli luks butik otelin 'Kurumsal Satış (B2B) Yöneticisisin (AI)'.
        Kullanici '{industry}' sektorune yonelik kurumsal satis stratejisi istiyor.

        Lutfen '{industry}' sektorune uygun 4 adet yuksek potansiyelli hayali kurumsal MUSTERI (Lead) uret.
        Her biri icin:
        - Sirket adi ve Yetkilisi
        - Sektor/Baglam
        - Satış Açısı (Angle)
        - Cold Email Taslagi
        - LinkedIn DM Taslagi

        SADECE JSON dondur:
        {{
            "leads": [
                {{
                    "company_name": "ABC Lojistik & Liman",
                    "contact_person": "Ahmet Yilmaz - Satinalma Muduru",
                    "angle": "Gemi murettebati icin huzurlu dinlenme paketi.",
                    "status_label": "Yuksek Potansiyel (Sıcak)",
                    "linkedin_dm": "Ahmet Bey merhaba...",
                    "cold_email": "Konu: ABC Lojistik VIP Misafir Konaklamalari\\n\\nSayin Ahmet Bey,\\n\\n..."
                }}
            ]
        }}
        """

        ai_resp = await get_chat_response("b2b_leads", new_id(), prompt)

        import re
        json_match = re.search(r'```(?:json)?(.*?)```', ai_resp, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_resp
        b2b_data = json.loads(res_str)

        return {
            "success": True,
            "leads": b2b_data.get("leads", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI B2B Leads hatasi: {str(e)}")
