from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from models import ReviewCreate

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
