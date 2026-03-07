from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
import json
from gemini_service import get_chat_response

router = APIRouter(tags=["marketing"])

# ==================== PHASE 12: AI LIFECYCLE RE-ENGAGEMENT ====================

@router.get("/marketing/ai-re-engagement")
async def ai_re_engagement_campaigns():
    """
    Eski misafirleri (ozellikle uzerinden aylarca / yillarca gecmis olanlari) tespit edip
    onlara ozel, isimlerine hitap eden (Retargeting) pazarlama mesajlari uretir.
    Orn: 'Gecen yaz Agustos'ta balayina geldiniz, bu yil donumunuz icin %20 indirim'
    """
    try:
        now_str = utcnow()[:10]
        
        # 1. Gecmis check-out yapmis rezervasyonlari al (Musterileri tespit)
        past_res = await db.reservations.find({
            "status": "checked_out"
        }, {"_id": 0, "guest_name": 1, "check_in": 1, "room_type": 1, "notes": 1, "guest_email": 1, "guest_phone": 1}).sort("check_in", 1).to_list(100)
        
        if not past_res:
            # Eger db bossa mock
            past_res = [
                {"guest_name": "Canan Yilmaz", "check_in": "2023-08-15", "room_type": "Suit", "guest_phone": "5551234567", "notes": "Balayi cifti, sarap ikrami yapildi."},
                {"guest_name": "Ahmet Demir", "check_in": "2024-01-20", "room_type": "Standart", "guest_email": "ahmet@gmail.com", "notes": "Sirket gezisi, kahvalti onemli."}
            ]

        # 2. Gemini'ye gonderecegimiz profile'leri hazirla
        profiles_to_analyze = []
        for r in past_res[:10]: # Token limit icin ilk 10'unu aliyoruz simdilik
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
        Her bir misafir icin spesifik gecmisini yansitan (Orn: 'Gecen Agutostaki balayiniz nasildi?') bir giris ve onlara uygun bir 'Teklif (Kanca)' iceren mesaj draftlari olustur.
        
        Sadece JSON dondur:
        {{
           "campaigns": [
              {{
                 "guest_name": "Canan Yilmaz", 
                 "target_segment": "Yildonumu Kutlamasi", 
                 "channel": "WhatsApp/SMS", 
                 "message": "Merhaba Canan Hanim, Kozbeyli Konagi'ndan sevgiler! Gecen agustostaki balayinizin uzerinden neredeyse 1 yil gecmis. Yildonumunuzu tekrar ayni romantik suitte (sarap ikramimizla) kutlamak isterseniz size ozel %20 indirim kodunuz: ASK20. Bekliyoruz!"
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
    Kullanicinin girdigi (veya sectigi) sektore (Orn: Sanayi, Liman, Serbest Bolge, Bilisim) gore,
    o bolgede olabilecek 'hayali (simule)' sirketleri (leads) ve bunlara atilacak kisisellestirilmis
    cok kanalli (Soguk Mail + LinkedIn DM) mesajlari uretir.
    """
    try:
        prompt = f"""
        Sen Kozbeyli Konagi adli luks butik otelin 'Kurumsal Satış (B2B) Yöneticisisin (AI)'.
        Kullanici '{industry}' sektorune yonelik kurumsal satis stratejisi istiyor. 
        Kozbeyli Konagi ozelikle cevresindeki Sanayi Bolgeleri (OSB), Liman Isletmeleri, Serbest Bolgeler
        veya teknoloji firmalari gibi buyuk endustriyel/kurumsal musterilere 'Uzun donem konaklama', 
        'Yabanci muhendis/eksper misafirligi', veya 'Yoneticiler icin izole toplantili konaklama' paketleri satmak istiyor.

        Lutfen '{industry}' sektorune uygun 4 adet yuksek potansiyelli hayali (gercekci isimli) kurumsal MUSTERI (Lead) uret.
        Her biri icin:
        - Sirket adi ve Yetkilisi (Orn: İK Müdürü, Satınalma Sorumlusu)
        - Sektor/Baglam: (Orn: Limanda calisan uluslararasi lojistik firmasi veya Organize Sanayi'deki fabrika)
        - Satış Açısı (Angle): Neden otelimizde kalmalilar? (Orn: Yurtdisindan gelen muhendisler icin havalimani transferli ozel suitler)
        - Cold Email Taslagi: Mukemmel donusum oranina sahip, profesyonel ama icten, direkt teklife giden bir e-posta.
        - LinkedIn DM Taslagi: Kisa, baglanti kurmaya yonelik, iliskiyibaslatan bir LinkedIn mesaji.

        SADECE JSON dondur:
        {{
            "leads": [
                {{
                    "company_name": "ABC Lojistik & Liman",
                    "contact_person": "Ahmet Yilmaz - Satinalma Muduru",
                    "angle": "Gemi murettebati ve kaptanlar icin huzurlu dinlenme ve transfer paketi.",
                    "status_label": "Yuksek Potansiyel (Sıcak)",
                    "linkedin_dm": "Ahmet Bey merhaba, limandaki yogun operasyonlarinizda kaptan ve VIP personellerinizin izole bir ortamda dinlenmesi gerektigini dusunerek size Kozbeyli Konagi'nin ozel paketlerinden bahsetmek isterim...",
                    "cold_email": "Konu: ABC Lojistik VIP Misafir Konaklamalari Hakkinda\\n\\nSayin Ahmet Bey,\\n\\nLimandaki operasyonlarinizda uluslararasi misafirlerinizi..."
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
