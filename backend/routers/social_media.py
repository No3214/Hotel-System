from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
import re

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
    platforms: list = []  # instagram, facebook, x, tiktok, linkedin, pinterest, google_business, whatsapp
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
    """Publish post to selected platforms via API or mark as published"""
    post = await db.social_posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(404, "Gonderi bulunamadi")

    platforms = post.get("platforms", [])
    publish_results = {}

    # Try auto-publishing to each platform
    for platform in platforms:
        try:
            result = await _publish_to_platform(platform, post)
            publish_results[platform] = result
        except Exception as e:
            publish_results[platform] = {"success": False, "error": str(e)}

    await db.social_posts.update_one(
        {"id": post_id},
        {"$set": {
            "status": "published",
            "published_at": utcnow(),
            "updated_at": utcnow(),
            "publish_results": publish_results,
        }}
    )

    # Log publish history
    await db.social_publish_log.insert_one({
        "id": new_id(),
        "post_id": post_id,
        "platforms": platforms,
        "publish_results": publish_results,
        "published_at": utcnow(),
    })

    return {"success": True, "message": "Gonderi yayinlandi", "results": publish_results}


async def _download_drive_media(url: str) -> tuple:
    """Download media from Google Drive link to temp file, return (path, content_type)"""
    import tempfile
    import aiohttp

    direct_url = convert_drive_link(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(direct_url, allow_redirects=True) as resp:
            if resp.status != 200:
                return None, None
            content_type = resp.content_type or "image/jpeg"
            ext = ".mp4" if "video" in content_type else ".jpg"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
            tmp.write(await resp.read())
            tmp.close()
            return tmp.name, content_type


async def _publish_to_platform(platform: str, post: dict) -> dict:
    """Publish content to a specific platform via its API"""
    import os
    import logging
    logger = logging.getLogger(__name__)

    content = f"{post.get('title', '')}\n\n{post.get('content', '')}"
    hashtags = ' '.join(f"#{h}" for h in post.get('hashtags', []))
    full_text = f"{content}\n\n{hashtags}".strip()
    image_url = post.get("image_url")

    # ==================== FACEBOOK ====================
    if platform == "facebook":
        token = os.getenv("META_PAGE_ACCESS_TOKEN")
        page_id = os.getenv("META_PAGE_ID")
        if not token or not page_id:
            return {"success": False, "error": "META_PAGE_ACCESS_TOKEN veya META_PAGE_ID ayarlanmamis", "mode": "manual"}

        import aiohttp
        async with aiohttp.ClientSession() as session:
            if image_url:
                # Photo post
                url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
                data = {"url": convert_drive_link(image_url), "caption": full_text, "access_token": token}
            else:
                url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
                data = {"message": full_text, "access_token": token}
            async with session.post(url, data=data) as resp:
                result = await resp.json()
                if "id" in result:
                    return {"success": True, "post_id": result["id"], "platform": "facebook"}
                return {"success": False, "error": result.get("error", {}).get("message", "Facebook hata")}

    # ==================== INSTAGRAM ====================
    elif platform == "instagram":
        token = os.getenv("META_PAGE_ACCESS_TOKEN")
        ig_account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        if not token or not ig_account_id:
            return {"success": False, "error": "META_PAGE_ACCESS_TOKEN veya INSTAGRAM_BUSINESS_ACCOUNT_ID ayarlanmamis", "mode": "manual"}
        if not image_url:
            return {"success": False, "error": "Instagram icin gorsel/video gerekli"}

        direct_media_url = convert_drive_link(image_url)
        is_video = any(ext in image_url.lower() for ext in ['.mp4', '.mov', '.avi', 'video'])

        import aiohttp
        async with aiohttp.ClientSession() as session:
            # Step 1: Create media container
            url = f"https://graph.facebook.com/v19.0/{ig_account_id}/media"
            if is_video:
                data = {"video_url": direct_media_url, "caption": full_text, "media_type": "REELS", "access_token": token}
            else:
                data = {"image_url": direct_media_url, "caption": full_text, "access_token": token}
            async with session.post(url, data=data) as resp:
                result = await resp.json()
                container_id = result.get("id")
                if not container_id:
                    return {"success": False, "error": result.get("error", {}).get("message", "Container olusturulamadi")}

            # For video, wait for processing
            if is_video:
                import asyncio
                for _ in range(30):  # max 5 min wait
                    await asyncio.sleep(10)
                    status_url = f"https://graph.facebook.com/v19.0/{container_id}?fields=status_code&access_token={token}"
                    async with session.get(status_url) as resp:
                        status = await resp.json()
                        if status.get("status_code") == "FINISHED":
                            break
                        if status.get("status_code") == "ERROR":
                            return {"success": False, "error": "Instagram video isleme hatasi"}

            # Step 2: Publish
            url = f"https://graph.facebook.com/v19.0/{ig_account_id}/media_publish"
            data = {"creation_id": container_id, "access_token": token}
            async with session.post(url, data=data) as resp:
                result = await resp.json()
                if "id" in result:
                    return {"success": True, "post_id": result["id"], "platform": "instagram"}
                return {"success": False, "error": result.get("error", {}).get("message", "Yayin basarisiz")}

    # ==================== X (TWITTER) ====================
    elif platform in ("x", "twitter"):
        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        if not all([api_key, api_secret, access_token, access_secret]):
            return {"success": False, "error": "X/Twitter API anahtarlari ayarlanmamis", "mode": "manual"}

        from requests_oauthlib import OAuth1Session
        # Twitter API v2 - Create Tweet
        twitter = OAuth1Session(api_key, client_secret=api_secret,
                                resource_owner_key=access_token, resource_owner_secret=access_secret)

        tweet_text = full_text[:280]  # Twitter char limit
        payload = {"text": tweet_text}

        # Upload media if present
        if image_url:
            try:
                tmp_path, content_type = await _download_drive_media(image_url)
                if tmp_path:
                    # Upload to Twitter media endpoint (v1.1)
                    upload_url = "https://upload.twitter.com/1.1/media/upload.json"
                    with open(tmp_path, "rb") as f:
                        files = {"media": f}
                        upload_resp = twitter.post(upload_url, files=files)
                    import os as _os
                    _os.unlink(tmp_path)  # cleanup temp file
                    if upload_resp.status_code == 200:
                        media_id = upload_resp.json().get("media_id_string")
                        if media_id:
                            payload["media"] = {"media_ids": [media_id]}
            except Exception as e:
                logger.warning(f"X media upload failed: {e}")

        resp = twitter.post("https://api.twitter.com/2/tweets", json=payload)
        if resp.status_code in (200, 201):
            tweet_data = resp.json().get("data", {})
            return {"success": True, "post_id": tweet_data.get("id"), "platform": "x"}
        return {"success": False, "error": f"X API hata: {resp.status_code} - {resp.text[:200]}"}

    # ==================== LINKEDIN ====================
    elif platform == "linkedin":
        access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        org_id = os.getenv("LINKEDIN_ORG_ID")  # Organization URN
        if not access_token:
            return {"success": False, "error": "LINKEDIN_ACCESS_TOKEN ayarlanmamis", "mode": "manual"}

        import aiohttp
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        author = f"urn:li:organization:{org_id}" if org_id else None
        if not author:
            # Try personal profile
            person_id = os.getenv("LINKEDIN_PERSON_ID")
            if person_id:
                author = f"urn:li:person:{person_id}"
            else:
                return {"success": False, "error": "LINKEDIN_ORG_ID veya LINKEDIN_PERSON_ID ayarlanmamis", "mode": "manual"}

        payload = {
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": full_text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        # If image, upload first
        if image_url:
            async with aiohttp.ClientSession() as session:
                # Register upload
                register_payload = {
                    "registerUploadRequest": {
                        "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                        "owner": author,
                        "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]
                    }
                }
                async with session.post(
                    "https://api.linkedin.com/v2/assets?action=registerUpload",
                    headers=headers, json=register_payload
                ) as resp:
                    reg_result = await resp.json()

                upload_url = reg_result.get("value", {}).get("uploadMechanism", {}).get(
                    "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}
                ).get("uploadUrl")
                asset = reg_result.get("value", {}).get("asset")

                if upload_url and asset:
                    tmp_path, _ = await _download_drive_media(image_url)
                    if tmp_path:
                        with open(tmp_path, "rb") as f:
                            async with session.put(upload_url, headers={"Authorization": f"Bearer {access_token}"}, data=f.read()) as resp:
                                pass
                        import os as _os
                        _os.unlink(tmp_path)

                    payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                    payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                        "status": "READY",
                        "media": asset,
                        "title": {"text": post.get("title", "")},
                    }]

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.linkedin.com/v2/ugcPosts", headers=headers, json=payload) as resp:
                if resp.status in (200, 201):
                    result = await resp.json()
                    return {"success": True, "post_id": result.get("id"), "platform": "linkedin"}
                error_text = await resp.text()
                return {"success": False, "error": f"LinkedIn hata: {resp.status} - {error_text[:200]}"}

    # ==================== TIKTOK ====================
    elif platform == "tiktok":
        access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        if not access_token:
            return {"success": False, "error": "TIKTOK_ACCESS_TOKEN ayarlanmamis", "mode": "manual"}
        if not image_url:
            return {"success": False, "error": "TikTok icin video gerekli"}

        import aiohttp
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        # TikTok Content Posting API - Direct Post
        async with aiohttp.ClientSession() as session:
            # Step 1: Init upload
            init_payload = {
                "post_info": {
                    "title": full_text[:150],
                    "privacy_level": "PUBLIC_TO_EVERYONE",
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "video_url": convert_drive_link(image_url),
                }
            }
            async with session.post(
                "https://open.tiktokapis.com/v2/post/publish/video/init/",
                headers=headers, json=init_payload
            ) as resp:
                result = await resp.json()
                if result.get("data", {}).get("publish_id"):
                    return {"success": True, "publish_id": result["data"]["publish_id"], "platform": "tiktok"}
                return {"success": False, "error": result.get("error", {}).get("message", "TikTok yayin hatasi")}

    # ==================== PINTEREST ====================
    elif platform == "pinterest":
        access_token = os.getenv("PINTEREST_ACCESS_TOKEN")
        board_id = os.getenv("PINTEREST_BOARD_ID")
        if not access_token or not board_id:
            return {"success": False, "error": "PINTEREST_ACCESS_TOKEN veya PINTEREST_BOARD_ID ayarlanmamis", "mode": "manual"}
        if not image_url:
            return {"success": False, "error": "Pinterest icin gorsel gerekli"}

        import aiohttp
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        payload = {
            "board_id": board_id,
            "title": post.get("title", "Kozbeyli Konagi")[:100],
            "description": full_text[:500],
            "media_source": {"source_type": "image_url", "url": convert_drive_link(image_url)},
            "link": "https://www.kozbeylikonagi.com",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.pinterest.com/v5/pins", headers=headers, json=payload) as resp:
                result = await resp.json()
                if resp.status in (200, 201):
                    return {"success": True, "pin_id": result.get("id"), "platform": "pinterest"}
                return {"success": False, "error": f"Pinterest hata: {result.get('message', resp.status)}"}

    # ==================== GOOGLE BUSINESS ====================
    elif platform == "google_business":
        access_token = os.getenv("GOOGLE_BUSINESS_ACCESS_TOKEN")
        location_id = os.getenv("GOOGLE_BUSINESS_LOCATION_ID")
        if not access_token or not location_id:
            return {"success": False, "error": "GOOGLE_BUSINESS_ACCESS_TOKEN veya GOOGLE_BUSINESS_LOCATION_ID ayarlanmamis", "mode": "manual"}

        import aiohttp
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        payload = {
            "languageCode": "tr",
            "summary": full_text[:1500],
            "topicType": "STANDARD",
        }
        if image_url:
            payload["media"] = [{"mediaFormat": "PHOTO", "sourceUrl": convert_drive_link(image_url)}]

        async with aiohttp.ClientSession() as session:
            url = f"https://mybusiness.googleapis.com/v4/{location_id}/localPosts"
            async with session.post(url, headers=headers, json=payload) as resp:
                result = await resp.json()
                if resp.status in (200, 201):
                    return {"success": True, "post_name": result.get("name"), "platform": "google_business"}
                return {"success": False, "error": f"Google Business hata: {result.get('error', {}).get('message', resp.status)}"}

    # ==================== WHATSAPP BROADCAST ====================
    elif platform == "whatsapp":
        wa_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        wa_phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        if not wa_token or not wa_phone_id:
            return {"success": False, "error": "WhatsApp API ayarlanmamis", "mode": "manual"}
        return {"success": True, "mode": "broadcast_ready", "message": "WhatsApp broadcast hazir", "platform": "whatsapp"}

    return {"success": False, "error": f"{platform} icin API entegrasyonu henuz yapilanmamis", "mode": "manual"}


@router.get("/social/platforms")
async def get_platform_status():
    """Get configuration status for all supported platforms"""
    import os
    return {
        "platforms": [
            {"id": "facebook", "name": "Facebook", "icon": "facebook", "configured": bool(os.getenv("META_PAGE_ACCESS_TOKEN") and os.getenv("META_PAGE_ID")), "needs": ["META_PAGE_ACCESS_TOKEN", "META_PAGE_ID"]},
            {"id": "instagram", "name": "Instagram", "icon": "instagram", "configured": bool(os.getenv("META_PAGE_ACCESS_TOKEN") and os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")), "needs": ["META_PAGE_ACCESS_TOKEN", "INSTAGRAM_BUSINESS_ACCOUNT_ID"], "note": "Gorsel/video zorunlu"},
            {"id": "x", "name": "X (Twitter)", "icon": "twitter", "configured": bool(os.getenv("TWITTER_API_KEY") and os.getenv("TWITTER_ACCESS_TOKEN")), "needs": ["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET"]},
            {"id": "linkedin", "name": "LinkedIn", "icon": "linkedin", "configured": bool(os.getenv("LINKEDIN_ACCESS_TOKEN")), "needs": ["LINKEDIN_ACCESS_TOKEN", "LINKEDIN_ORG_ID"]},
            {"id": "tiktok", "name": "TikTok", "icon": "video", "configured": bool(os.getenv("TIKTOK_ACCESS_TOKEN")), "needs": ["TIKTOK_ACCESS_TOKEN"], "note": "Video zorunlu"},
            {"id": "pinterest", "name": "Pinterest", "icon": "pin", "configured": bool(os.getenv("PINTEREST_ACCESS_TOKEN") and os.getenv("PINTEREST_BOARD_ID")), "needs": ["PINTEREST_ACCESS_TOKEN", "PINTEREST_BOARD_ID"], "note": "Gorsel zorunlu"},
            {"id": "google_business", "name": "Google Business", "icon": "map-pin", "configured": bool(os.getenv("GOOGLE_BUSINESS_ACCESS_TOKEN") and os.getenv("GOOGLE_BUSINESS_LOCATION_ID")), "needs": ["GOOGLE_BUSINESS_ACCESS_TOKEN", "GOOGLE_BUSINESS_LOCATION_ID"]},
            {"id": "whatsapp", "name": "WhatsApp", "icon": "message-circle", "configured": bool(os.getenv("WHATSAPP_ACCESS_TOKEN") and os.getenv("WHATSAPP_PHONE_NUMBER_ID")), "needs": ["WHATSAPP_ACCESS_TOKEN", "WHATSAPP_PHONE_NUMBER_ID"]},
        ]
    }


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


@router.get("/social/branding")
async def get_branding():
    """Get brand guidelines, hashtag sets, content calendar, and auto-post templates"""
    from branding import (
        BRAND, BRAND_COLORS, SOCIAL_MEDIA_GUIDE, HASHTAG_SETS,
        CONTENT_CALENDAR_THEMES, PLATFORM_BIOS, AUTO_POST_TEMPLATES
    )
    return {
        "brand": BRAND,
        "colors": BRAND_COLORS,
        "social_guide": SOCIAL_MEDIA_GUIDE,
        "hashtags": HASHTAG_SETS,
        "content_calendar": CONTENT_CALENDAR_THEMES,
        "platform_bios": PLATFORM_BIOS,
        "auto_templates": AUTO_POST_TEMPLATES,
    }


@router.post("/social/convert-image-link")
async def convert_image_link(data: ImageLinkRequest):
    """Convert Google Drive share link to direct viewable URL"""
    if not data.url:
        raise HTTPException(400, "URL gerekli")
    
    direct_url = convert_drive_link(data.url)
    return {"success": True, "image_url": direct_url}
