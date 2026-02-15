from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
import os
import base64

router = APIRouter(tags=["social-media"])

# Upload directory for social media images
UPLOAD_DIR = "/app/frontend/public/uploads/social"
os.makedirs(UPLOAD_DIR, exist_ok=True)


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


@router.post("/social/posts")
async def create_post(data: PostCreate):
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
