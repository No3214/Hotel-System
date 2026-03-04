from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from models import ReviewCreate
import logging
import aiohttp

logger = logging.getLogger(__name__)
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


async def _refresh_google_token():
    """Refresh Google OAuth2 access token using refresh token."""
    from config import (
        GOOGLE_BUSINESS_CLIENT_ID, GOOGLE_BUSINESS_CLIENT_SECRET,
        GOOGLE_BUSINESS_REFRESH_TOKEN,
    )
    if not all([GOOGLE_BUSINESS_CLIENT_ID, GOOGLE_BUSINESS_CLIENT_SECRET, GOOGLE_BUSINESS_REFRESH_TOKEN]):
        return None

    async with aiohttp.ClientSession() as session:
        async with session.post("https://oauth2.googleapis.com/token", data={
            "client_id": GOOGLE_BUSINESS_CLIENT_ID,
            "client_secret": GOOGLE_BUSINESS_CLIENT_SECRET,
            "refresh_token": GOOGLE_BUSINESS_REFRESH_TOKEN,
            "grant_type": "refresh_token",
        }) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("access_token")
            logger.error(f"Google token refresh failed: {resp.status}")
            return None


async def _post_reply_to_google(review_name: str, reply_text: str):
    """Post a reply to a Google Business review via the API.
    review_name: the Google review resource name e.g. accounts/{id}/locations/{id}/reviews/{id}
    """
    from config import GOOGLE_BUSINESS_ACCESS_TOKEN

    token = GOOGLE_BUSINESS_ACCESS_TOKEN
    if not token:
        token = await _refresh_google_token()
    if not token:
        return {"posted": False, "reason": "Google Business API kimlik bilgileri ayarlanmamis"}

    url = f"https://mybusiness.googleapis.com/v4/{review_name}/reply"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.put(url, json={"comment": reply_text}, headers=headers) as resp:
            if resp.status in (200, 201):
                logger.info(f"Google review reply posted: {review_name}")
                return {"posted": True}
            else:
                body = await resp.text()
                logger.error(f"Google reply failed {resp.status}: {body}")
                return {"posted": False, "reason": f"API hata: {resp.status}", "detail": body}


async def _fetch_google_reviews():
    """Fetch reviews from Google Business Profile API."""
    from config import (
        GOOGLE_BUSINESS_ACCOUNT_ID, GOOGLE_BUSINESS_LOCATION_ID,
        GOOGLE_BUSINESS_ACCESS_TOKEN,
    )

    token = GOOGLE_BUSINESS_ACCESS_TOKEN
    if not token:
        token = await _refresh_google_token()
    if not token:
        return None

    if not GOOGLE_BUSINESS_ACCOUNT_ID or not GOOGLE_BUSINESS_LOCATION_ID:
        return None

    url = f"https://mybusiness.googleapis.com/v4/accounts/{GOOGLE_BUSINESS_ACCOUNT_ID}/locations/{GOOGLE_BUSINESS_LOCATION_ID}/reviews"
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            logger.error(f"Google reviews fetch failed: {resp.status}")
            return None


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
        "google_review_name": None,
        "google_reply_posted": False,
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


@router.post("/reviews/{review_id}/post-to-google")
async def post_review_reply_to_google(review_id: str):
    """AI yanitini Google Business Profile'a gonder."""
    review = await db.reviews.find_one({"id": review_id}, {"_id": 0})
    if not review:
        raise HTTPException(404, "Yorum bulunamadi")
    if not review.get("ai_response"):
        raise HTTPException(400, "Once AI yanit olusturun")
    if not review.get("google_review_name"):
        raise HTTPException(400, "Bu yorum Google API ile eslesmemis — google_review_name gerekli")

    result = await _post_reply_to_google(review["google_review_name"], review["ai_response"])

    if result.get("posted"):
        await db.reviews.update_one(
            {"id": review_id},
            {"$set": {"google_reply_posted": True, "google_posted_at": utcnow(), "updated_at": utcnow()}}
        )

    return result


@router.post("/reviews/sync-google")
async def sync_google_reviews():
    """Google Business Profile'dan yorumlari cek ve veritabanina kaydet."""
    data = await _fetch_google_reviews()
    if data is None:
        return {
            "success": False,
            "message": "Google Business API baglantisi yapilamadi. Ayarlar sayfasindan API bilgilerini girin.",
            "setup_guide": {
                "steps": [
                    "1. Google Cloud Console'a gidin (console.cloud.google.com)",
                    "2. 'Google My Business API' etkinlestirin",
                    "3. OAuth 2.0 Client ID olusturun (Web Application)",
                    "4. Authorized redirect URI: https://hotel-system-production.up.railway.app/api/reviews/google-callback",
                    "5. Client ID, Client Secret bilgilerini Railway env vars'a ekleyin",
                    "6. /api/reviews/google-auth adresine giderek yetkilendirme yapin",
                ],
                "env_vars": [
                    "GOOGLE_BUSINESS_CLIENT_ID=xxx",
                    "GOOGLE_BUSINESS_CLIENT_SECRET=xxx",
                    "GOOGLE_BUSINESS_ACCOUNT_ID=xxx (accounts/ sonraki ID)",
                    "GOOGLE_BUSINESS_LOCATION_ID=xxx (locations/ sonraki ID)",
                ],
            }
        }

    reviews_list = data.get("reviews", [])
    synced = 0
    for gr in reviews_list:
        review_name = gr.get("name", "")
        existing = await db.reviews.find_one({"google_review_name": review_name})
        if existing:
            continue

        star_map = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}
        rating = star_map.get(gr.get("starRating", "FIVE"), 5)

        review = {
            "id": new_id(),
            "reviewer_name": gr.get("reviewer", {}).get("displayName", "Misafir"),
            "rating": rating,
            "review_text": gr.get("comment", ""),
            "platform": "google",
            "google_review_name": review_name,
            "google_reply_posted": bool(gr.get("reviewReply")),
            "ai_response": gr.get("reviewReply", {}).get("comment") if gr.get("reviewReply") else None,
            "response_tone": None,
            "responded_at": gr.get("reviewReply", {}).get("updateTime") if gr.get("reviewReply") else None,
            "review_date": gr.get("createTime", "")[:10],
            "created_at": utcnow(),
            "updated_at": utcnow(),
        }
        await db.reviews.insert_one(review)
        synced += 1

    return {"success": True, "synced": synced, "total_from_google": len(reviews_list)}


@router.get("/reviews/google-config")
async def get_google_review_config():
    """Google Business API yapilandirma durumunu goster."""
    from config import (
        GOOGLE_BUSINESS_ACCOUNT_ID, GOOGLE_BUSINESS_LOCATION_ID,
        GOOGLE_BUSINESS_ACCESS_TOKEN, GOOGLE_BUSINESS_REFRESH_TOKEN,
        GOOGLE_BUSINESS_CLIENT_ID, GOOGLE_BUSINESS_CLIENT_SECRET,
    )
    return {
        "configured": bool(GOOGLE_BUSINESS_CLIENT_ID and GOOGLE_BUSINESS_CLIENT_SECRET),
        "has_account_id": bool(GOOGLE_BUSINESS_ACCOUNT_ID),
        "has_location_id": bool(GOOGLE_BUSINESS_LOCATION_ID),
        "has_access_token": bool(GOOGLE_BUSINESS_ACCESS_TOKEN),
        "has_refresh_token": bool(GOOGLE_BUSINESS_REFRESH_TOKEN),
        "setup_url": "https://console.cloud.google.com/apis/library/mybusinessbusinessinformation.googleapis.com",
        "setup_steps_tr": [
            "1. Google Cloud Console'a gidin",
            "2. Yeni proje olusturun veya mevcut projeyi secin",
            "3. 'Google My Business API' veya 'Business Profile APIs' etkinlestirin",
            "4. Kimlik bilgileri > OAuth 2.0 istemci kimligi olusturun",
            "5. Redirect URI: https://hotel-system-production.up.railway.app/api/reviews/google-callback",
            "6. Elde ettiginiz CLIENT_ID ve CLIENT_SECRET degerleri Railway environment variables'a ekleyin",
            "7. Google Business Profile'da isletmenizin account ID ve location ID bilgilerini bulun",
            "8. Tum degerleri env vars olarak Railway'e ekleyin",
        ],
    }


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
    google_posted = await db.reviews.count_documents({"google_reply_posted": True})
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
        "google_posted": google_posted,
        "avg_rating": avg_rating,
        "by_rating": by_rating,
    }
