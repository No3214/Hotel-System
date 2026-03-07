from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from models import ReviewCreate
import json

router = APIRouter(tags=["reviews"])

REVIEW_RESPONSE_PROMPT = """Sen Kozbeyli Konagi'nin profesyonel misafir iliskileri uzmanisin. Google Business yorumlarini yanitliyorsun.

KESIN KURALLAR:
1. SADECE otelle ilgili BILINEN gercekleri kullan. ASLA bilgi uydurmayacaksin (halusnasyon yasak).
2. Kibar, samimi ve profesyonel ol. Asla kaba veya savunmaci olma.
3. Olumlu yorumlara: Icerikten bahset, tesekur et, tekrar bekle.
4. Olumsuz yorumlara: Ozur dile, cozum one sur, iyilestirme sozu ver. Asla suclama yapma.
5. Yorumda gecen SPESIFIK detaylara deginerek kisisellestirilmis yanit yaz.
6. Yanit 2-4 cumle uzunlugunda olsun, cok uzun veya cok kisa olmasin.
7. Yanit sonunda misafiri tekrar davet et.

OTEL BILGILERI (Sadece bunlari kullanabilirsin):
- Otel Adi: Kozbeyli Konagi
- Yer: Kozbeyli Koyu, Foca/Izmir
- Tip: Butik Tas Otel & Restoran
- 600 yillik tarihi koy, 2013'ten beri hizmet
- Kurucular: Inci & Varol Oruk
- Restoran: Antakya Sofrasi - Yogurtlu Balik, Kalamar Dolmasi, Sac Kavurma
- Ucretsiz organik koy kahvaltisi
- Oduller: TripAdvisor Travelers' Choice, Booking.com 8.8/10
- 16 oda: Tek, Cift, Superior, Aile odalari
- Evcil hayvan dostu, ucretsiz otopark, WiFi
- Foca bolgesi: Plajlar, antik Phokaia, tekne turlari

BILMEDIGIN veya otel hakkinda emin olmadigin seyleri ASLA yanitina ekleme.
Sadece yukaridaki bilgileri ve misafirin yorumunda bahsettiklerini kullan."""


@router.get("/reviews")
async def list_reviews(platform: Optional[str] = None, limit: int = 50, skip: int = 0):
    query = {"platform": platform} if platform else {}
    reviews = await db.reviews.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.reviews.count_documents(query)
    return {"reviews": reviews, "total": total}


@router.post("/reviews")
async def create_review(data: ReviewCreate):
    review = {
        "id": new_id(),
        **data.model_dump(),
        "ai_response": None,
        "response_tone": None,
        "responded_at": None,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.reviews.insert_one(review)
    return clean_doc(review)


@router.post("/reviews/{review_id}/generate-response")
async def generate_review_response(review_id: str, tone: str = "professional"):
    from gemini_service import get_review_response

    review = await db.reviews.find_one({"id": review_id}, {"_id": 0})
    if not review:
        raise HTTPException(404, "Yorum bulunamadi")

    tone_map = {
        "professional": "Profesyonel ve resmi bir ton kullan.",
        "friendly": "Samimi ve sicak bir ton kullan, sanki eski bir dost gibi.",
        "formal": "Cok resmi ve kurumsal bir ton kullan.",
    }
    tone_instruction = tone_map.get(tone, tone_map["professional"])

    prompt = f"""Asagidaki Google yorumuna yanit yaz.

Misafir Adi: {review['reviewer_name']}
Puan: {review['rating']}/5
Yorum: {review['review_text']}

Ton: {tone_instruction}

Yanit:"""

    # Multi-provider AI: review gorevi -> Gemini oncelikli
    try:
        from services.ai_provider_service import ai_request
        ai_result = await ai_request(
            message=prompt,
            system_prompt=REVIEW_RESPONSE_PROMPT,
            task_type="review_response",
        )
        response = ai_result["response"]
    except Exception:
        response = await get_review_response(
            prompt=prompt,
            system_prompt=REVIEW_RESPONSE_PROMPT,
        )

    update = {
        "ai_response": response,
        "response_tone": tone,
        "responded_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.reviews.update_one({"id": review_id}, {"$set": update})

    return {"success": True, "response": response, "tone": tone}


@router.patch("/reviews/{review_id}")
async def update_review(review_id: str, data: dict):
    data["updated_at"] = utcnow()
    result = await db.reviews.update_one({"id": review_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(404, "Yorum bulunamadi")
    return {"success": True}


@router.delete("/reviews/{review_id}")
async def delete_review(review_id: str):
    result = await db.reviews.delete_one({"id": review_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Yorum bulunamadi")
    return {"success": True}


@router.get("/reviews/stats")
async def review_stats():
    total = await db.reviews.count_documents({})
    responded = await db.reviews.count_documents({"ai_response": {"$ne": None}})
    pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$rating"}}}]
    avg_result = await db.reviews.aggregate(pipeline).to_list(1)
    avg_rating = round(avg_result[0]["avg"], 1) if avg_result and avg_result[0].get("avg") else 0
    by_rating = {}
    for r in range(1, 6):
        by_rating[str(r)] = await db.reviews.count_documents({"rating": r})
    return {
        "total": total,
        "responded": responded,
        "pending": total - responded,
        "avg_rating": avg_rating,
        "by_rating": by_rating,
    }

@router.get("/reviews/ai-analytics")
async def get_review_ai_analytics():
    """Misafir yorumlarini NLP ile analiz edip genel musteri memnuniyeti raporu sunar"""
    from gemini_service import get_chat_response
    
    # Get last 50 reviews to analyze
    reviews = await db.reviews.find({}, {"_id": 0, "rating": 1, "review_text": 1}).sort("created_at", -1).limit(50).to_list(50)
    
    if not reviews:
        return {"success": True, "analytics": {"summary": "Yeterli veri yok.", "positives": [], "negatives": []}}
        
    context = "Son Yorumlar:\n"
    for r in reviews:
        context += f"- Puan: {r['rating']}/5, Yorum: {r['review_text']}\n"
        
    system_prompt = """
    Sen Kozbeyli Konagi'nin Duygu Analizi (Sentiment Analysis) ve Musteri Deneyimi (CX) yapay zekasisin.
    Gorevin, son misafir yorumlarina bakarak genel bir izlenim, duygu analizi ve ozet cikartmak.
    
    Senden sadece asagidaki JSON formatinda sonuc uretmeni istiyorum:
    {
      "sentiment_score": "1 ile 100 arasi genel duygu skoru (orn: 85)",
      "summary": "Musterilerin genel hissiyatini ve onemli egilimleri ozetleyen 2-3 cumle",
      "positives": ["En cok begenilen 1. detay", "En cok begenilen 2. detay", "En cok begenilen 3. detay"],
      "negatives": ["En cok sikayet edilen veya gelistirilmesi gereken 1. detay", "2. detay", "3. detay"]
    }
    """
    
    try:
        response_text = await get_chat_response(
            message="Son misafir yorumlarini analiz edip raporla.",
            session_id=new_id(),
            system_prompt=system_prompt,
            context=context
        )
        clean_json = response_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        return {"success": True, "analytics": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Analytics hatasi: {str(e)}")

# ==================== PHASE 15: AI DEEP SENTIMENT ENGINE ====================

@router.get("/reviews/{review_id}/ai-sentiment")
async def get_deep_sentiment(review_id: str):
    """
    Spesifik bir misafir yorumunun derinine inerek satir aralarindaki gizli hissiyati,
    departman bazli (Temizlik, Lezzet, Hizmet) minyatür skorlamalari ve yonetime uyari cikarir.
    """
    from gemini_service import get_chat_response

    review = await db.reviews.find_one({"id": review_id}, {"_id": 0})
    if not review:
        raise HTTPException(404, "Yorum bulunamadi")

    # Eger onceden analiz edildiyse direkt dondur (maliyet tasarrufu)
    if "deep_sentiment" in review and review["deep_sentiment"]:
         return {"success": True, "sentiment": review["deep_sentiment"]}

    prompt = f"""
    Sen Kozbeyli Konagi'nin Duygu Analizi Uzmanisin (Deep Sentiment Engine).
    Gorevin, asagidaki misafir yorumunun EN DERININE inerek (NLP tabanli) acik/gizli elestiri ve ovguleri ortaya cikarmak.

    Yorum Degerlendirmesi ({review['rating']}/5):
    "{review['review_text']}"

    SADECE JSON DONDUR:
    {{
       "scores": {{
          "service": 8,
          "cleanliness": 10,
          "food_quality": 5
       }},
       "hidden_complaints": ["Garsonlarin yavaskalmasi sebebiyle siparis gecikti.", "Kahve soguk geldi."],
       "hidden_praises": ["Odanin manzarasi ve yatagin rahatligi cok iyiydi."],
       "action_required": true,
       "department_warning": "F&B Ekibi: Servis hizini artirmak ve sicak icecek sicakligini kontrol etmek gerekiyor."
    }}
    (Skorlar 1-10 arasinda, bahsedilmeyen konuya 0 veya null verme, yorumun genel hissiyatina gore ortalama (orn: 7) ver, acikca elestiri varsa dusur)
    """

    try:
        ai_resp = await get_chat_response("reviews_sentiment", f"snt_{review_id}", prompt)
        
        import re
        json_match = re.search(r'```(?:json)?(.*?)```', ai_resp, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_resp
        sentiment_data = json.loads(res_str)

        # DB'ye kaydet ki tekrar tekrar sormasin
        await db.reviews.update_one(
             {"id": review_id},
             {"$set": {"deep_sentiment": sentiment_data}}
        )

        return {
            "success": True,
            "sentiment": sentiment_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deep Sentiment hatasi: {str(e)}")
