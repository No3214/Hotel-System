from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from database import db
from helpers import utcnow, new_id, clean_doc
import re
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter(tags=["social-media"])


def convert_drive_link(url: str) -> str:
    """Convert Google Drive share link to direct image URL"""
    # Pattern 1: https://drive.google.com/file/d/FILE_ID/view
    match = re.search(r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)', url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    
    # Pattern 2: https://drive.google.com/open?id=FILE_ID
    match = re.search(r'drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)', url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    
    # Pattern 3: Already direct link or other URL
    if 'drive.google.com/uc' in url:
        return url
    
    # Return as-is if not a Drive link (could be any image URL)
    return url


class PostCreate(BaseModel):
    title: str
    content: str
    platforms: list = []  # instagram, facebook, twitter, tiktok, linkedin, whatsapp
    post_type: str = "text"  # text, promo, event, menu_highlight, announcement
    scheduled_at: Optional[str] = None
    frame_style: str = "default"  # default, elegant, bold, minimal, festive
    hashtags: list = []
    status: str = "draft"  # draft, scheduled, published
    image_url: Optional[str] = None


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    platforms: Optional[list] = None
    post_type: Optional[str] = None
    scheduled_at: Optional[str] = None
    frame_style: Optional[str] = None
    hashtags: Optional[list] = None
    status: Optional[str] = None
    image_url: Optional[str] = None


# Templates for different post types
POST_TEMPLATES = {
    "menu_highlight": {
        "title": "Gunun Lezzeti",
        "content": "Kozbeyli Konagi'nin essiz lezzetlerini kesfet...",
        "hashtags": ["KozbeyliKonagi", "TasOtel", "FocaLezzet", "EgeMutfagi"],
    },
    "promo": {
        "title": "Ozel Teklif",
        "content": "Misafirlerimize ozel firsatlar...",
        "hashtags": ["KozbeyliKonagi", "OzelTeklif", "FocaTatil"],
    },
    "event": {
        "title": "Etkinlik Duyurusu",
        "content": "Kozbeyli Konagi'nda unutulmaz anlar...",
        "hashtags": ["KozbeyliKonagi", "Etkinlik", "FocaGece"],
    },
    "announcement": {
        "title": "Duyuru",
        "content": "",
        "hashtags": ["KozbeyliKonagi", "Duyuru"],
    },
    "text": {
        "title": "",
        "content": "",
        "hashtags": ["KozbeyliKonagi"],
    },
}

FRAME_STYLES = [
    {"id": "default", "name": "Varsayilan", "bg": "#515249", "text": "#F8F5EF", "accent": "#B07A2A"},
    {"id": "elegant", "name": "Elegans", "bg": "#1E1B16", "text": "#F8F5EF", "accent": "#C5A059"},
    {"id": "bold", "name": "Cesur", "bg": "#8FAA86", "text": "#1E1B16", "accent": "#515249"},
    {"id": "minimal", "name": "Minimal", "bg": "#F3EEE4", "text": "#1E1B16", "accent": "#515249"},
    {"id": "festive", "name": "Senlik", "bg": "#3F403A", "text": "#F8F5EF", "accent": "#D4A847"},
]


@router.get("/social/posts")
async def list_posts(status: Optional[str] = None, post_type: Optional[str] = None):
    query = {}
    if status:
        query["status"] = status
    if post_type:
        query["post_type"] = post_type
    posts = await db.social_posts.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"posts": posts}


@router.post("/social/check-duplicate-media")
async def check_duplicate_media(data: ImageLinkRequest):
    """Check if a media URL has already been used in a post"""
    if not data.url:
        return {"duplicate": False}

    # Normalize the URL for comparison
    normalized = convert_drive_link(data.url)

    existing = await db.social_posts.find_one(
        {"image_url": normalized},
        {"_id": 0, "id": 1, "title": 1, "status": 1, "created_at": 1, "platforms": 1}
    )
    if existing:
        return {
            "duplicate": True,
            "existing_post": existing,
            "message": f"Bu gorsel daha once '{existing.get('title', 'Basliksiz')}' gonderisinde kullanildi."
        }
    return {"duplicate": False}


@router.post("/social/posts")
async def create_post(data: PostCreate):
    # Check for duplicate media before creating
    if data.image_url:
        existing = await db.social_posts.find_one(
            {"image_url": data.image_url},
            {"_id": 0, "id": 1, "title": 1}
        )
        if existing:
            raise HTTPException(
                409,
                f"Bu gorsel daha once '{existing.get('title', 'Basliksiz')}' gonderisinde kullanildi. Ayni gorseli tekrar kullanamazsiniz."
            )

    post = {
        "id": new_id(),
        **data.model_dump(),
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.social_posts.insert_one(post)
    return clean_doc(post)


@router.get("/social/posts/{post_id}")
async def get_post(post_id: str):
    post = await db.social_posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(404, "Gonderi bulunamadi")
    return post


@router.patch("/social/posts/{post_id}")
async def update_post(post_id: str, data: PostUpdate):
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(400, "Guncellenecek alan yok")

    # Check for duplicate media when image is being changed
    if "image_url" in updates and updates["image_url"]:
        existing = await db.social_posts.find_one(
            {"image_url": updates["image_url"], "id": {"$ne": post_id}},
            {"_id": 0, "id": 1, "title": 1}
        )
        if existing:
            raise HTTPException(
                409,
                f"Bu gorsel daha once '{existing.get('title', 'Basliksiz')}' gonderisinde kullanildi. Ayni gorseli tekrar kullanamazsiniz."
            )

    updates["updated_at"] = utcnow()
    result = await db.social_posts.update_one({"id": post_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(404, "Gonderi bulunamadi")
    return await db.social_posts.find_one({"id": post_id}, {"_id": 0})


@router.delete("/social/posts/{post_id}")
async def delete_post(post_id: str):
    result = await db.social_posts.delete_one({"id": post_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Gonderi bulunamadi")
    return {"success": True}


@router.post("/social/posts/{post_id}/publish")
async def publish_post(post_id: str):
    """Mark post as published and log the action"""
    post = await db.social_posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(404, "Gonderi bulunamadi")

    await db.social_posts.update_one(
        {"id": post_id},
        {"$set": {"status": "published", "published_at": utcnow(), "updated_at": utcnow()}}
    )

    # Log publish history
    await db.social_publish_log.insert_one({
        "id": new_id(),
        "post_id": post_id,
        "platforms": post.get("platforms", []),
        "published_at": utcnow(),
    })

    return {"success": True, "message": "Gonderi yayinlandi olarak isaretlendi"}


@router.get("/social/templates")
async def get_templates():
    return {"templates": POST_TEMPLATES, "frame_styles": FRAME_STYLES}


@router.get("/social/stats")
async def get_stats():
    total = await db.social_posts.count_documents({})
    published = await db.social_posts.count_documents({"status": "published"})
    drafts = await db.social_posts.count_documents({"status": "draft"})
    scheduled = await db.social_posts.count_documents({"status": "scheduled"})

    # Platform breakdown
    pipeline = [
        {"$unwind": "$platforms"},
        {"$group": {"_id": "$platforms", "count": {"$sum": 1}}},
    ]
    platform_counts = {}
    async for doc in db.social_posts.aggregate(pipeline):
        platform_counts[doc["_id"]] = doc["count"]

    return {
        "total": total,
        "published": published,
        "drafts": drafts,
        "scheduled": scheduled,
        "platforms": platform_counts,
    }


class ImageLinkRequest(BaseModel):
    url: str


@router.post("/social/convert-image-link")
async def convert_image_link(data: ImageLinkRequest):
    """Convert Google Drive share link to direct viewable URL"""
    if not data.url:
        raise HTTPException(400, "URL gerekli")

    direct_url = convert_drive_link(data.url)
    return {"success": True, "image_url": direct_url}


# ==================== AI ICERIK URETIMI ====================

AI_CONTENT_SYSTEM_PROMPT = """Sen Kozbeyli Konagi'nin sosyal medya yoneticisisin.
Kozbeyli Konagi, Foca/Izmir'de 14 yillik aile isletmesi olan butik bir tas otel ve restorandir.
Dogayla ic ice, organik kahvalti, yerel lezzetler ve sicak misafirperverlik ile taninan bir mekandir.

Gonderiler icin kurallarin:
- Turkce yaz, samimi ama profesyonel bir dil kullan
- Emoji kullan ama abartma (2-4 arasi)
- Otel/restoran/bolge temasiyla uyumlu icerik uret
- Instagram, Facebook, Twitter, LinkedIn gibi platformlara uygun icerikler olustur
- Hashtag onerilerini ayri bir listede ver
- Icerik 150-300 karakter arasi olsun (kisa ve etkili)

Otel ozellikleri:
- Foca tasindan insa edilmis tarihi konak
- 5 benzersiz oda (Nar, Zeytin, Tas, Badem, Asma)
- Organik bahce kahvaltisi
- Yerel Ege mutfagi
- Dugun/nisan/ozel etkinlik alani
- Dogayla ic ice huzurlu ortam
"""

CONTENT_TOPICS = {
    "menu_highlight": "Restoranin gunun lezzeti veya ozel menusunu tanitici bir gonderi yaz",
    "promo": "Otelin ozel teklif veya indirim kampanyasini duyuran bir gonderi yaz",
    "event": "Otelde yaklasan etkinlik veya organizasyonu duyuran bir gonderi yaz",
    "announcement": "Otel hakkinda genel bir duyuru gonderisi yaz",
    "morning": "Otelin sabah atmosferi, kahvalti veya gunaydin temali bir gonderi yaz",
    "seasonal": "Mevsime uygun (ilkbahar/yaz/sonbahar/kis) otel deneyimini anlatan bir gonderi yaz",
    "local": "Foca ve cevresindeki dogal/kulturel guzelliklerle oteli birlikte tanitan bir gonderi yaz",
    "guest_story": "Misafir deneyimi veya misafirperverlik temali bir gonderi yaz",
    "behind_scenes": "Otelin mutfak, bahce veya hazirliklariyla ilgili sahne arkasi gonderi yaz",
    "weekend": "Hafta sonu kacamagi temali bir gonderi yaz",
}


class AIContentRequest(BaseModel):
    post_type: str = "text"
    topic: Optional[str] = None  # CONTENT_TOPICS key or free-form topic
    platform: Optional[str] = None  # instagram, facebook, twitter, linkedin
    custom_prompt: Optional[str] = None
    tone: str = "warm"  # warm, professional, playful, elegant


class AutoPublishSettingsModel(BaseModel):
    enabled: bool = False
    frequency: str = "daily"  # daily, weekly, twice_weekly
    preferred_time: str = "10:00"  # HH:MM
    platforms: List[str] = []
    topics: List[str] = []  # rotation topics
    auto_approve: bool = False  # if True, publishes directly; if False, creates as draft


@router.post("/social/ai-generate")
async def ai_generate_content(data: AIContentRequest):
    """Gemini AI ile sosyal medya icerigi uret"""
    from gemini_service import get_chat_response

    topic_prompt = ""
    if data.custom_prompt:
        topic_prompt = data.custom_prompt
    elif data.topic and data.topic in CONTENT_TOPICS:
        topic_prompt = CONTENT_TOPICS[data.topic]
    elif data.topic:
        topic_prompt = data.topic
    else:
        topic_prompt = CONTENT_TOPICS.get(data.post_type, "Oteli tanitan genel bir gonderi yaz")

    platform_hint = ""
    if data.platform:
        platform_hints = {
            "instagram": "Instagram icin yaziyorsun - gorsel odakli, hashtag agirlikli, kisa ve cezbedici",
            "facebook": "Facebook icin yaziyorsun - biraz daha detayli, topluluk odakli",
            "twitter": "X (Twitter) icin yaziyorsun - 280 karakter siniri, cok kisa ve vurucu",
            "linkedin": "LinkedIn icin yaziyorsun - profesyonel ton, B2B ve turizm sektoru odakli",
        }
        platform_hint = platform_hints.get(data.platform, "")

    tone_hints = {
        "warm": "Sicak, samimi ve davetkar bir ton kullan",
        "professional": "Profesyonel ve guvenlir bir ton kullan",
        "playful": "Eglenceli ve enerjik bir ton kullan",
        "elegant": "Zarif ve sofistike bir ton kullan",
    }

    full_prompt = f"""{topic_prompt}

{platform_hint}
{tone_hints.get(data.tone, '')}

Yanit formatini asagidaki gibi ver:
BASLIK: [gonderi basligi]
ICERIK: [gonderi icerigi]
HASHTAGLER: [virgullerle ayrilmis hashtag listesi, # isareti olmadan]"""

    try:
        session_id = f"social_ai_{new_id()[:8]}"
        response = await get_chat_response(full_prompt, session_id, AI_CONTENT_SYSTEM_PROMPT)

        # Parse response
        title = ""
        content = ""
        hashtags = []

        lines = response.strip().split("\n")
        current_field = None
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.upper().startswith("BASLIK:"):
                title = line_stripped[7:].strip()
                current_field = "title"
            elif line_stripped.upper().startswith("ICERIK:"):
                content = line_stripped[7:].strip()
                current_field = "content"
            elif line_stripped.upper().startswith("HASHTAGLER:") or line_stripped.upper().startswith("HASHTAG:"):
                tag_text = line_stripped.split(":", 1)[1].strip()
                hashtags = [h.strip().lstrip("#") for h in tag_text.split(",") if h.strip()]
                current_field = "hashtags"
            elif current_field == "content" and line_stripped:
                content += " " + line_stripped

        # Fallback if parsing failed
        if not content:
            content = response.strip()
        if not hashtags:
            hashtags = ["KozbeyliKonagi", "FocaOtel", "ButikOtel"]

        return {
            "success": True,
            "generated": {
                "title": title or "Kozbeyli Konagi",
                "content": content,
                "hashtags": hashtags,
                "post_type": data.post_type,
                "platform": data.platform,
                "tone": data.tone,
            },
            "raw_response": response,
        }

    except Exception as e:
        logger.error(f"AI content generation error: {e}")
        raise HTTPException(500, f"AI icerik uretimi basarisiz: {str(e)}")


@router.get("/social/ai-topics")
async def get_ai_topics():
    """Kullanilabilir AI icerik konularini getir"""
    topics = [
        {"id": k, "label": v.split(" yaz")[0] if " yaz" in v else v}
        for k, v in CONTENT_TOPICS.items()
    ]
    tones = [
        {"id": "warm", "label": "Sicak & Samimi"},
        {"id": "professional", "label": "Profesyonel"},
        {"id": "playful", "label": "Eglenceli"},
        {"id": "elegant", "label": "Zarif"},
    ]
    return {"topics": topics, "tones": tones}


# ==================== OTOMATIK YAYINLAMA ====================

@router.get("/social/auto-publish/settings")
async def get_auto_publish_settings():
    """Otomatik yayinlama ayarlarini getir"""
    settings = await db.social_auto_publish_settings.find_one(
        {"_id": "auto_publish"}, {"_id": 0}
    )
    if not settings:
        settings = {
            "enabled": False,
            "frequency": "daily",
            "preferred_time": "10:00",
            "platforms": ["instagram", "facebook"],
            "topics": ["morning", "menu_highlight", "seasonal", "local", "weekend"],
            "auto_approve": False,
        }
    return settings


@router.put("/social/auto-publish/settings")
async def update_auto_publish_settings(data: AutoPublishSettingsModel):
    """Otomatik yayinlama ayarlarini guncelle"""
    settings = {
        **data.model_dump(),
        "updated_at": utcnow(),
    }
    await db.social_auto_publish_settings.update_one(
        {"_id": "auto_publish"},
        {"$set": settings},
        upsert=True,
    )
    return {"success": True, "settings": settings}


@router.post("/social/auto-publish/trigger")
async def trigger_auto_publish():
    """Manuel olarak otomatik icerik uretimini tetikle"""
    from celery_tasks import auto_publish_content_task
    auto_publish_content_task.delay()
    return {"success": True, "message": "Otomatik icerik uretimi kuyruga eklendi"}


@router.get("/social/auto-publish/history")
async def get_auto_publish_history(limit: int = 20):
    """Otomatik yayinlama gecmisini getir"""
    history = await db.social_auto_publish_log.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return {"history": history, "total": len(history)}


# ==================== TOPLU DRIVE ICERIK ISLEME ====================

class BatchDriveRequest(BaseModel):
    drive_links: List[str]  # List of Google Drive share links
    platforms: List[str] = ["instagram", "facebook"]
    tone: str = "warm"
    auto_caption: bool = True  # Generate AI caption for each image
    post_type: str = "text"


@router.post("/social/batch-drive")
async def batch_drive_import(data: BatchDriveRequest):
    """Birden fazla Drive linkinden toplu gonderi olustur + AI caption uret"""
    from gemini_service import get_chat_response

    if not data.drive_links:
        raise HTTPException(400, "En az bir Drive linki gerekli")
    if len(data.drive_links) > 20:
        raise HTTPException(400, "Tek seferde en fazla 20 gorsel yuklenebilir")

    results = []
    errors = []

    for idx, link in enumerate(data.drive_links):
        try:
            # Convert Drive link
            direct_url = convert_drive_link(link.strip())

            # Check duplicate
            existing = await db.social_posts.find_one(
                {"image_url": direct_url},
                {"_id": 0, "id": 1, "title": 1}
            )
            if existing:
                errors.append({
                    "index": idx,
                    "link": link,
                    "error": f"Bu gorsel daha once '{existing.get('title', 'Basliksiz')}' gonderisinde kullanildi.",
                })
                continue

            # Generate AI caption if enabled
            title = ""
            content = ""
            hashtags = ["KozbeyliKonagi", "FocaOtel", "ButikOtel"]

            if data.auto_caption:
                try:
                    tone_hints = {
                        "warm": "Sicak, samimi ve davetkar bir ton kullan",
                        "professional": "Profesyonel ve guvenlir bir ton kullan",
                        "playful": "Eglenceli ve enerjik bir ton kullan",
                        "elegant": "Zarif ve sofistike bir ton kullan",
                    }

                    prompt = f"""Bu bir otel/restoran gorseli icin sosyal medya gonderisi yaz.
Instagram ve Facebook icin uygun olsun.
{tone_hints.get(data.tone, '')}
Gorsel sira numarasi: {idx + 1}

Yanit formatini asagidaki gibi ver:
BASLIK: [gonderi basligi]
ICERIK: [gonderi icerigi - 150-300 karakter]
HASHTAGLER: [virgullerle ayrilmis hashtag listesi, # isareti olmadan]"""

                    session_id = f"batch_ai_{new_id()[:8]}"
                    response = await get_chat_response(prompt, session_id, AI_CONTENT_SYSTEM_PROMPT)

                    # Parse AI response
                    lines = response.strip().split("\n")
                    current_field = None
                    for line in lines:
                        line_stripped = line.strip()
                        if line_stripped.upper().startswith("BASLIK:"):
                            title = line_stripped[7:].strip()
                            current_field = "title"
                        elif line_stripped.upper().startswith("ICERIK:"):
                            content = line_stripped[7:].strip()
                            current_field = "content"
                        elif line_stripped.upper().startswith("HASHTAGLER:") or line_stripped.upper().startswith("HASHTAG:"):
                            tag_text = line_stripped.split(":", 1)[1].strip()
                            hashtags = [h.strip().lstrip("#") for h in tag_text.split(",") if h.strip()]
                            current_field = "hashtags"
                        elif current_field == "content" and line_stripped:
                            content += " " + line_stripped

                    if not content:
                        content = response.strip()[:300]
                except Exception as e:
                    logger.warning(f"AI caption generation failed for link {idx}: {e}")
                    title = f"Kozbeyli Konagi #{idx + 1}"
                    content = "Kozbeyli Konagi'ndan bir kare..."

            if not title:
                title = f"Kozbeyli Konagi #{idx + 1}"

            # Create post
            post = {
                "id": new_id(),
                "title": title,
                "content": content,
                "platforms": data.platforms,
                "post_type": data.post_type,
                "frame_style": "default",
                "hashtags": hashtags,
                "status": "draft",
                "image_url": direct_url,
                "source": "batch_drive_import",
                "created_at": utcnow(),
                "updated_at": utcnow(),
            }
            await db.social_posts.insert_one(post)
            results.append(clean_doc(post))

        except Exception as e:
            errors.append({
                "index": idx,
                "link": link,
                "error": str(e),
            })

    return {
        "success": True,
        "created": len(results),
        "errors": len(errors),
        "posts": results,
        "error_details": errors,
    }


# ==================== GERCEK PLATFORM YAYINLAMA ====================

class PlatformPublishRequest(BaseModel):
    post_id: str
    platforms: Optional[List[str]] = None  # Override post platforms


@router.post("/social/posts/{post_id}/publish-to-platforms")
async def publish_to_platforms(post_id: str, data: Optional[PlatformPublishRequest] = None):
    """Gonderiyi gercek platformlara yayin - Instagram/Facebook Graph API"""
    post = await db.social_posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(404, "Gonderi bulunamadi")

    platforms_to_publish = (data.platforms if data and data.platforms else post.get("platforms", []))
    publish_results = {}

    for platform in platforms_to_publish:
        try:
            if platform == "instagram":
                result = await _publish_to_instagram(post)
                publish_results["instagram"] = result
            elif platform == "facebook":
                result = await _publish_to_facebook(post)
                publish_results["facebook"] = result
            else:
                publish_results[platform] = {
                    "status": "not_supported",
                    "message": f"{platform} API entegrasyonu henuz aktif degil. Icerik kopyalanarak manuel paylasim yapilabilir."
                }
        except Exception as e:
            logger.error(f"Platform publish error ({platform}): {e}")
            publish_results[platform] = {"status": "error", "message": str(e)}

    # Update post status
    update_data = {
        "status": "published",
        "published_at": utcnow(),
        "updated_at": utcnow(),
        "publish_results": publish_results,
    }
    await db.social_posts.update_one({"id": post_id}, {"$set": update_data})

    # Log publish
    await db.social_publish_log.insert_one({
        "id": new_id(),
        "post_id": post_id,
        "platforms": platforms_to_publish,
        "results": publish_results,
        "published_at": utcnow(),
    })

    return {
        "success": True,
        "post_id": post_id,
        "results": publish_results,
    }


async def _publish_to_instagram(post: dict) -> dict:
    """Instagram Graph API ile gorsel/carousel paylasimi"""
    access_token = os.environ.get("META_ACCESS_TOKEN", "")
    ig_account_id = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")

    if not access_token or not ig_account_id:
        # Mock mode - return simulated success
        return {
            "status": "mock_published",
            "message": "Instagram API kimlik bilgileri yapilandirilmamis. Mock modda calisiliyor.",
            "mock": True,
        }

    import httpx

    caption = f"{post.get('title', '')}\n\n{post.get('content', '')}"
    if post.get("hashtags"):
        caption += "\n\n" + " ".join(f"#{h}" for h in post["hashtags"])

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: Create media container
        if post.get("image_url"):
            container_resp = await client.post(
                f"https://graph.facebook.com/v18.0/{ig_account_id}/media",
                params={
                    "image_url": post["image_url"],
                    "caption": caption,
                    "access_token": access_token,
                }
            )
            container_data = container_resp.json()

            if "id" not in container_data:
                return {"status": "error", "message": container_data.get("error", {}).get("message", "Container olusturulamadi")}

            container_id = container_data["id"]

            # Step 2: Publish the container
            publish_resp = await client.post(
                f"https://graph.facebook.com/v18.0/{ig_account_id}/media_publish",
                params={
                    "creation_id": container_id,
                    "access_token": access_token,
                }
            )
            publish_data = publish_resp.json()

            if "id" in publish_data:
                return {"status": "published", "media_id": publish_data["id"], "platform": "instagram"}
            else:
                return {"status": "error", "message": publish_data.get("error", {}).get("message", "Yayinlama basarisiz")}
        else:
            return {"status": "skipped", "message": "Instagram icin gorsel gerekli"}


async def _publish_to_facebook(post: dict) -> dict:
    """Facebook Graph API ile sayfa paylasimi"""
    access_token = os.environ.get("META_ACCESS_TOKEN", "")
    page_id = os.environ.get("FACEBOOK_PAGE_ID", "")

    if not access_token or not page_id:
        return {
            "status": "mock_published",
            "message": "Facebook API kimlik bilgileri yapilandirilmamis. Mock modda calisiliyor.",
            "mock": True,
        }

    import httpx

    message = f"{post.get('title', '')}\n\n{post.get('content', '')}"
    if post.get("hashtags"):
        message += "\n\n" + " ".join(f"#{h}" for h in post["hashtags"])

    async with httpx.AsyncClient(timeout=60.0) as client:
        params = {
            "message": message,
            "access_token": access_token,
        }

        if post.get("image_url"):
            # Photo post
            params["url"] = post["image_url"]
            resp = await client.post(
                f"https://graph.facebook.com/v18.0/{page_id}/photos",
                params=params,
            )
        else:
            # Text-only post
            resp = await client.post(
                f"https://graph.facebook.com/v18.0/{page_id}/feed",
                params=params,
            )

        data = resp.json()
        if "id" in data or "post_id" in data:
            return {"status": "published", "post_id": data.get("id") or data.get("post_id"), "platform": "facebook"}
        else:
            return {"status": "error", "message": data.get("error", {}).get("message", "Yayinlama basarisiz")}


@router.get("/social/platform-status")
async def get_platform_status():
    """Hangi platformlarin API'si aktif, hangisi mock modda"""
    meta_token = os.environ.get("META_ACCESS_TOKEN", "")
    ig_account = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
    fb_page = os.environ.get("FACEBOOK_PAGE_ID", "")

    return {
        "platforms": {
            "instagram": {
                "configured": bool(meta_token and ig_account),
                "mode": "live" if (meta_token and ig_account) else "mock",
                "env_vars": ["META_ACCESS_TOKEN", "INSTAGRAM_BUSINESS_ACCOUNT_ID"],
            },
            "facebook": {
                "configured": bool(meta_token and fb_page),
                "mode": "live" if (meta_token and fb_page) else "mock",
                "env_vars": ["META_ACCESS_TOKEN", "FACEBOOK_PAGE_ID"],
            },
            "twitter": {"configured": False, "mode": "manual", "message": "Manuel paylasim - icerik kopyalanabilir"},
            "tiktok": {"configured": False, "mode": "manual", "message": "Manuel paylasim - icerik kopyalanabilir"},
            "linkedin": {"configured": False, "mode": "manual", "message": "Manuel paylasim - icerik kopyalanabilir"},
            "whatsapp": {"configured": False, "mode": "manual", "message": "WhatsApp Business API ayri moduldedir"},
        }
    }


@router.get("/social/content-calendar")
async def get_content_calendar(days: int = 7):
    """Yaklasan zamanlanan gonderileri takvim formatinda getir"""
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    calendar = []

    for i in range(days):
        date = (now + timedelta(days=i)).strftime("%Y-%m-%d")
        day_name = ["Pzt", "Sal", "Car", "Per", "Cum", "Cmt", "Paz"][(now + timedelta(days=i)).weekday()]

        # Find scheduled/published posts for this date
        day_posts = await db.social_posts.find(
            {
                "$or": [
                    {"scheduled_at": {"$regex": f"^{date}"}},
                    {"published_at": {"$regex": f"^{date}"}},
                    {"created_at": {"$regex": f"^{date}"}},
                ]
            },
            {"_id": 0, "id": 1, "title": 1, "status": 1, "platforms": 1, "post_type": 1}
        ).to_list(20)

        calendar.append({
            "date": date,
            "day_name": day_name,
            "posts": day_posts,
            "post_count": len(day_posts),
        })

    return {"calendar": calendar, "days": days}
