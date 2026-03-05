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
