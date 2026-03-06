"""
Kozbeyli Konagi - Celery Tasks
All scheduled and on-demand background tasks.
Uses synchronous MongoDB (pymongo) since Celery workers are sync.
"""
import os
import logging
from datetime import datetime, timezone, timedelta
from celery_app import celery_app

from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
import uuid

load_dotenv(Path(__file__).parent / '.env')

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'vericevir_hotel')

# Singleton MongoDB client to prevent connection leaks
_mongo_client = None


def get_db():
    """Get synchronous MongoDB connection for Celery worker (singleton)."""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGO_URL, maxPoolSize=10)
        logger.info("Celery MongoDB client initialized")
    return _mongo_client[DB_NAME]


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def new_id():
    return str(uuid.uuid4())


def send_group_notification(db, notification_type: str, message: str):
    """Store group notification in DB."""
    notification = {
        "id": new_id(),
        "type": notification_type,
        "message": message,
        "status": "sent",
        "source": "celery",
        "created_at": utcnow(),
    }
    db.group_notifications.insert_one(notification)
    db.automation_logs.insert_one({
        "id": new_id(),
        "type": notification_type,
        "message": message,
        "status": "completed",
        "source": "celery",
        "created_at": utcnow(),
    })
    logger.info(f"Grup bildirimi: {notification_type}")
    return notification


# =====================================================
# TASK 1: KAHVALTI HAZIRLIGI (01:00)
# =====================================================

@celery_app.task(name='celery_tasks.breakfast_prep_task', bind=True, max_retries=2)
def breakfast_prep_task(self):
    """Sabah kahvalti hazirligi bildirimi"""
    try:
        db = get_db()
        today = datetime.now().strftime("%Y-%m-%d")
        reservations = list(db.reservations.find({
            "status": {"$in": ["confirmed", "checked_in"]},
            "check_in": {"$lte": today},
            "check_out": {"$gte": today},
        }, {"_id": 0}))

        if not reservations:
            send_group_notification(db, "breakfast_prep", "Sabah kahvalti yok - bugun misafir bulunmuyor.")
            return {"status": "no_guests"}

        total_guests = sum(r.get("guests_count", 1) for r in reservations)
        room_summary = {}
        for res in reservations:
            key = f"{res.get('guests_count', 1)} kisilik"
            room_summary[key] = room_summary.get(key, 0) + 1

        summary_text = ", ".join(f"{count} adet {key}" for key, count in sorted(room_summary.items()))
        msg = f"Sabah {summary_text} oda kahvalti var. Toplam {total_guests} kisi."
        send_group_notification(db, "breakfast_prep", msg)
        return {"status": "sent", "guests": total_guests}

    except Exception as e:
        logger.error(f"Kahvalti bildirimi hatasi: {e}")
        raise self.retry(exc=e, countdown=60)


# =====================================================
# TASK 2: SABAH HATIRLAMA (08:30)
# =====================================================

@celery_app.task(name='celery_tasks.morning_reminders_task', bind=True, max_retries=2)
def morning_reminders_task(self):
    """Sabah hatirlama mesajlari - tuvalet temizlik + check-in hazirligi"""
    try:
        db = get_db()
        today = datetime.now().strftime("%Y-%m-%d")

        toilet_msg = "Gunaydin! Ortak alan tuvaletleri temizlik ve stok kontrolu yapilmali. Sabun, kagit havlu ve tuvalet kagidi kontrol ediniz."
        send_group_notification(db, "morning_toilet_reminder", toilet_msg)

        checkins = list(db.reservations.find({
            "status": {"$in": ["pending", "confirmed"]},
            "check_in": today,
        }, {"_id": 0}))

        if checkins:
            room_numbers = [r.get("room_id", r.get("room_type", "")) for r in checkins]
            rooms_text = "-".join(room_numbers) if room_numbers else "Bilgi yok"
            checkin_msg = f"Bugun check-in yapacak odalar: {rooms_text}. Hosgeldin ikramlari (su, meyve, kurabiye) hazirlanmali."
        else:
            checkin_msg = "Bugun check-in yapacak misafir bulunmuyor."

        send_group_notification(db, "morning_checkin_reminder", checkin_msg)
        return {"status": "sent", "checkins": len(checkins)}

    except Exception as e:
        logger.error(f"Sabah hatirlama hatasi: {e}")
        raise self.retry(exc=e, countdown=60)


# =====================================================
# TASK 3: CHECKOUT TEMIZLIK (12:30)
# =====================================================

@celery_app.task(name='celery_tasks.checkout_cleaning_task', bind=True, max_retries=2)
def checkout_cleaning_task(self):
    """Check-out sonrasi temizlik listesi"""
    try:
        db = get_db()
        today = datetime.now().strftime("%Y-%m-%d")
        checkouts = list(db.reservations.find({
            "status": {"$in": ["confirmed", "checked_in"]},
            "check_out": today,
        }, {"_id": 0}))

        if not checkouts:
            return {"status": "no_checkouts"}

        room_numbers = [r.get("room_id", "") for r in checkouts if r.get("room_id")]
        if room_numbers:
            rooms_text = "-".join(sorted(room_numbers))
            msg = f"{rooms_text} temizlik cikis yaptilar."
        else:
            msg = f"{len(checkouts)} oda cikis yapti, temizlik gerekiyor."

        send_group_notification(db, "checkout_cleaning", msg)
        return {"status": "sent", "rooms": len(checkouts)}

    except Exception as e:
        logger.error(f"Temizlik bildirimi hatasi: {e}")
        raise self.retry(exc=e, countdown=60)


# =====================================================
# TASK 4: AKSAM ODA KONTROLU (18:00)
# =====================================================

@celery_app.task(name='celery_tasks.evening_room_check_task', bind=True, max_retries=2)
def evening_room_check_task(self):
    """Aksam oda kontrolu - klima/isik kapatma"""
    try:
        db = get_db()
        today = datetime.now().strftime("%Y-%m-%d")
        checkouts = list(db.reservations.find({
            "status": {"$in": ["confirmed", "checked_in"]},
            "check_out": today,
        }, {"_id": 0}))

        if not checkouts:
            send_group_notification(db, "evening_room_check", "Bugun check-out yapan misafir yok. Oda kontrolu gerekmiyor.")
            return {"status": "no_checkouts"}

        room_numbers = [r.get("room_id", "") for r in checkouts if r.get("room_id")]
        if room_numbers:
            rooms_text = ", ".join(sorted(room_numbers))
            msg = f"Aksam kontrol: Bugun cikis yapan odalar ({rooms_text}) kontrol edilmeli. Klima ve isiklarin kapatildiginden emin olunuz."
        else:
            msg = f"Aksam kontrol: Bugun {len(checkouts)} oda cikis yapti. Klima ve isiklarin kapatildigini kontrol ediniz."

        send_group_notification(db, "evening_room_check", msg)
        return {"status": "sent", "rooms": len(checkouts)}

    except Exception as e:
        logger.error(f"Aksam kontrol hatasi: {e}")
        raise self.retry(exc=e, countdown=60)


# =====================================================
# TASK 5: WHATSAPP REZERVASYON HATIRLATMA (10:00)
# =====================================================

@celery_app.task(name='celery_tasks.whatsapp_reservation_reminders_task', bind=True, max_retries=2)
def whatsapp_reservation_reminders_task(self):
    """Yarin check-in yapacak misafirlere WhatsApp hatirlatma"""
    try:
        db = get_db()
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
        reservations = list(db.reservations.find({
            "check_in": tomorrow,
            "reminder_sent": {"$ne": True},
            "status": {"$in": ["confirmed", "pending"]},
        }, {"_id": 0}))

        sent = 0
        for res in reservations:
            phone = res.get("phone") or res.get("guest_phone", "")
            guest_name = res.get("guest_name", "Misafir")
            if phone:
                db.whatsapp_messages.insert_one({
                    "id": new_id(),
                    "session_id": f"wa_reminder_{res['id']}",
                    "to": phone,
                    "text": f"Merhaba {guest_name}, yarin ({tomorrow}) check-in yapacaksiniz. Sizi bekliyoruz!",
                    "type": "template",
                    "template_name": "reservation_reminder_1day",
                    "direction": "outgoing",
                    "status": "mock_sent",
                    "created_at": utcnow(),
                })
                db.reservations.update_one({"id": res["id"]}, {"$set": {"reminder_sent": True}})
                sent += 1

        logger.info(f"WhatsApp hatirlatma: {sent}/{len(reservations)}")
        return {"status": "sent", "count": sent}

    except Exception as e:
        logger.error(f"WA hatirlatma hatasi: {e}")
        raise self.retry(exc=e, countdown=60)


# =====================================================
# TASK 6: WHATSAPP CHECKOUT TESEKKUR (14:00)
# =====================================================

@celery_app.task(name='celery_tasks.whatsapp_checkout_thanks_task', bind=True, max_retries=2)
def whatsapp_checkout_thanks_task(self):
    """Check-out yapan misafirlere tesekkur mesaji"""
    try:
        db = get_db()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        checkouts = list(db.reservations.find({
            "check_out": today,
            "thanks_sent": {"$ne": True},
            "status": "checked_out",
        }, {"_id": 0}))

        sent = 0
        for res in checkouts:
            phone = res.get("phone") or res.get("guest_phone", "")
            guest_name = res.get("guest_name", "Misafir")
            if phone:
                db.whatsapp_messages.insert_one({
                    "id": new_id(),
                    "session_id": f"wa_thanks_{res['id']}",
                    "to": phone,
                    "text": f"Merhaba {guest_name}, Kozbeyli Konagi'nda kaldiginiz icin tesekkur ederiz. Yorumlariniz bizim icin degerli!",
                    "type": "template",
                    "template_name": "checkout_thanks_review",
                    "direction": "outgoing",
                    "status": "mock_sent",
                    "created_at": utcnow(),
                })
                db.reservations.update_one({"id": res["id"]}, {"$set": {"thanks_sent": True}})
                sent += 1

        logger.info(f"WA tesekkur: {sent}/{len(checkouts)}")
        return {"status": "sent", "count": sent}

    except Exception as e:
        logger.error(f"WA tesekkur hatasi: {e}")
        raise self.retry(exc=e, countdown=60)


# =====================================================
# ON-DEMAND TASKS (Manuel tetikleme)
# =====================================================

@celery_app.task(name='celery_tasks.send_whatsapp_notification')
def send_whatsapp_notification(phone: str, message: str):
    """WhatsApp mesaji gonder (on-demand)"""
    db = get_db()
    db.whatsapp_messages.insert_one({
        "id": new_id(),
        "to": phone,
        "text": message,
        "direction": "outgoing",
        "status": "mock_sent",
        "created_at": utcnow(),
    })
    return {"status": "sent", "to": phone}


@celery_app.task(name='celery_tasks.process_audit_alert')
def process_audit_alert(alert_type: str, details: dict):
    """Guvenlik uyarisi isle (on-demand)"""
    db = get_db()
    db.audit_logs.insert_one({
        "id": new_id(),
        "action": "security_alert",
        "entity": alert_type,
        "details": details,
        "created_at": utcnow(),
    })
    return {"status": "logged", "type": alert_type}


# =====================================================
# TASK 7: OTOMATIK SOSYAL MEDYA ICERIK URETIMI (10:00)
# =====================================================

CONTENT_TOPICS_LIST = [
    "morning", "menu_highlight", "seasonal", "local",
    "weekend", "guest_story", "behind_scenes", "event",
]

CONTENT_TOPICS_PROMPTS = {
    "menu_highlight": "Restoranin gunun lezzeti veya ozel menusunu tanitici bir gonderi yaz",
    "promo": "Otelin ozel teklif veya indirim kampanyasini duyuran bir gonderi yaz",
    "event": "Otelde yaklasan etkinlik veya organizasyonu duyuran bir gonderi yaz",
    "announcement": "Otel hakkinda genel bir duyuru gonderisi yaz",
    "morning": "Otelin sabah atmosferi, kahvalti veya gunaydin temali bir gonderi yaz",
    "seasonal": "Mevsime uygun otel deneyimini anlatan bir gonderi yaz",
    "local": "Foca ve cevresindeki dogal/kulturel guzelliklerle oteli birlikte tanitan bir gonderi yaz",
    "guest_story": "Misafir deneyimi veya misafirperverlik temali bir gonderi yaz",
    "behind_scenes": "Otelin mutfak, bahce veya hazirliklariyla ilgili sahne arkasi gonderi yaz",
    "weekend": "Hafta sonu kacamagi temali bir gonderi yaz",
}

AI_SYSTEM_PROMPT_CELERY = """Sen Kozbeyli Konagi'nin sosyal medya yoneticisisin.
Kozbeyli Konagi, Foca/Izmir'de 14 yillik aile isletmesi olan butik bir tas otel ve restorandir.
Dogayla ic ice, organik kahvalti, yerel lezzetler ve sicak misafirperverlik ile taninan bir mekandir.

Gonderiler icin kurallarin:
- Turkce yaz, samimi ama profesyonel bir dil kullan
- Emoji kullan ama abartma (2-4 arasi)
- Icerik 150-300 karakter arasi olsun
- Hashtag onerilerini ayri ver

Otel: Foca tasindan insa edilmis tarihi konak, 5 oda (Nar, Zeytin, Tas, Badem, Asma),
organik bahce kahvaltisi, yerel Ege mutfagi, dugun/nisan alani, dogayla ic ice.

Yanit formati:
BASLIK: [baslik]
ICERIK: [icerik]
HASHTAGLER: [virgullerle ayrilmis, # olmadan]"""


def _should_run_today(settings, db):
    """Frequency ayarina gore bugun calisip calismayacagini kontrol et."""
    frequency = settings.get("frequency", "daily")
    if frequency == "daily":
        return True

    today = datetime.now(timezone.utc)
    day_of_week = today.weekday()  # 0=Monday, 6=Sunday

    if frequency == "weekly":
        # Haftada 1 - Pazartesi
        return day_of_week == 0
    elif frequency == "twice_weekly":
        # Haftada 2 - Pazartesi ve Persembe
        return day_of_week in (0, 3)

    return True


def _publish_to_platform_sync(post: dict, platform: str) -> dict:
    """Sync wrapper for publishing to Instagram/Facebook Graph API."""
    import httpx

    if platform == "instagram":
        access_token = os.environ.get("META_ACCESS_TOKEN", "")
        ig_account_id = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")

        if not access_token or not ig_account_id:
            return {"status": "mock_published", "platform": "instagram", "mock": True,
                    "message": "Instagram API kimlik bilgileri yapilandirilmamis. Mock modda."}

        caption = f"{post.get('title', '')}\n\n{post.get('content', '')}"
        if post.get("hashtags"):
            caption += "\n\n" + " ".join(f"#{h}" for h in post["hashtags"])

        with httpx.Client(timeout=60.0) as client:
            if post.get("image_url"):
                # Step 1: Create media container
                container_resp = client.post(
                    f"https://graph.facebook.com/v18.0/{ig_account_id}/media",
                    params={"image_url": post["image_url"], "caption": caption, "access_token": access_token}
                )
                container_data = container_resp.json()
                if "id" not in container_data:
                    return {"status": "error", "platform": "instagram",
                            "message": container_data.get("error", {}).get("message", "Container olusturulamadi")}

                # Step 2: Publish
                publish_resp = client.post(
                    f"https://graph.facebook.com/v18.0/{ig_account_id}/media_publish",
                    params={"creation_id": container_data["id"], "access_token": access_token}
                )
                publish_data = publish_resp.json()
                if "id" in publish_data:
                    return {"status": "published", "platform": "instagram", "media_id": publish_data["id"]}
                return {"status": "error", "platform": "instagram",
                        "message": publish_data.get("error", {}).get("message", "Yayinlama basarisiz")}
            else:
                return {"status": "skipped", "platform": "instagram", "message": "Gorsel gerekli"}

    elif platform == "facebook":
        access_token = os.environ.get("META_ACCESS_TOKEN", "")
        page_id = os.environ.get("FACEBOOK_PAGE_ID", "")

        if not access_token or not page_id:
            return {"status": "mock_published", "platform": "facebook", "mock": True,
                    "message": "Facebook API kimlik bilgileri yapilandirilmamis. Mock modda."}

        message = f"{post.get('title', '')}\n\n{post.get('content', '')}"
        if post.get("hashtags"):
            message += "\n\n" + " ".join(f"#{h}" for h in post["hashtags"])

        with httpx.Client(timeout=60.0) as client:
            params = {"message": message, "access_token": access_token}
            if post.get("image_url"):
                params["url"] = post["image_url"]
                resp = client.post(f"https://graph.facebook.com/v18.0/{page_id}/photos", params=params)
            else:
                resp = client.post(f"https://graph.facebook.com/v18.0/{page_id}/feed", params=params)

            data = resp.json()
            if "id" in data or "post_id" in data:
                return {"status": "published", "platform": "facebook",
                        "post_id": data.get("id") or data.get("post_id")}
            return {"status": "error", "platform": "facebook",
                    "message": data.get("error", {}).get("message", "Yayinlama basarisiz")}

    return {"status": "not_supported", "platform": platform, "message": f"{platform} henuz desteklenmiyor"}


@celery_app.task(name='celery_tasks.auto_publish_content_task', bind=True, max_retries=2)
def auto_publish_content_task(self):
    """Otomatik AI icerik uretimi ve yayinlama"""
    import random

    try:
        db = get_db()

        # Check settings
        settings = db.social_auto_publish_settings.find_one({"_id": "auto_publish"})
        if not settings or not settings.get("enabled", False):
            logger.info("Otomatik yayinlama devre disi, atlaniyor")
            return {"status": "disabled"}

        # Frequency check - bugun calisacak mi?
        if not _should_run_today(settings, db):
            logger.info(f"Otomatik yayinlama: Bugun calisma gunu degil (frequency: {settings.get('frequency')})")
            return {"status": "skipped_frequency"}

        # Pick a topic from rotation
        topics = settings.get("topics", CONTENT_TOPICS_LIST)
        if not topics:
            topics = CONTENT_TOPICS_LIST

        # Get last used topic to avoid repetition
        last_log = db.social_auto_publish_log.find_one(
            {}, sort=[("created_at", -1)]
        )
        last_topic = last_log.get("topic", "") if last_log else ""

        available_topics = [t for t in topics if t != last_topic]
        if not available_topics:
            available_topics = topics
        topic = random.choice(available_topics)

        topic_prompt = CONTENT_TOPICS_PROMPTS.get(topic, "Oteli tanitan genel bir gonderi yaz")

        # Generate content using Gemini (sync wrapper)
        GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
        if not GOOGLE_API_KEY:
            logger.warning("GOOGLE_API_KEY not set, skipping auto-publish")
            db.social_auto_publish_log.insert_one({
                "id": new_id(),
                "status": "error",
                "error": "API key not configured",
                "topic": topic,
                "created_at": utcnow(),
            })
            return {"status": "error", "message": "API key not configured"}

        # Use emergentintegrations sync call
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        import asyncio

        full_prompt = f"{topic_prompt}\n\nSicak ve samimi bir ton kullan."

        chat = LlmChat(
            api_key=GOOGLE_API_KEY,
            session_id=f"auto_publish_{new_id()[:8]}",
            system_message=AI_SYSTEM_PROMPT_CELERY,
        ).with_model("gemini", "gemini-2.5-flash")

        user_msg = UserMessage(text=full_prompt)

        # Run async in sync context
        loop = asyncio.new_event_loop()
        try:
            response = loop.run_until_complete(chat.send_message(user_msg))
        finally:
            loop.close()

        # Validate response
        if not response or not isinstance(response, str) or len(response.strip()) < 10:
            logger.warning(f"Auto-publish: AI returned empty or invalid response: {repr(response)[:100]}")
            db.social_auto_publish_log.insert_one({
                "id": new_id(),
                "status": "error",
                "error": "AI returned empty or invalid response",
                "topic": topic,
                "created_at": utcnow(),
            })
            return {"status": "error", "message": "AI returned invalid response"}

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

        if not content:
            content = response.strip()
        if not hashtags:
            hashtags = ["KozbeyliKonagi", "FocaOtel", "ButikOtel"]

        # Determine post status based on auto_approve
        auto_approve = settings.get("auto_approve", False)
        status = "published" if auto_approve else "draft"

        # Map topic to post_type
        topic_to_type = {
            "morning": "text", "menu_highlight": "menu_highlight", "seasonal": "text",
            "local": "text", "weekend": "promo", "guest_story": "text",
            "behind_scenes": "text", "event": "event", "promo": "promo",
            "announcement": "announcement",
        }

        platforms = settings.get("platforms", ["instagram", "facebook"])

        post = {
            "id": new_id(),
            "title": title or "Kozbeyli Konagi",
            "content": content,
            "platforms": platforms,
            "post_type": topic_to_type.get(topic, "text"),
            "frame_style": "default",
            "hashtags": hashtags,
            "status": status,
            "source": "ai_auto_publish",
            "ai_topic": topic,
            "created_at": utcnow(),
            "updated_at": utcnow(),
        }

        # If auto_approve, actually publish to platforms via Graph API
        publish_results = {}
        if auto_approve:
            post["published_at"] = utcnow()
            for platform in platforms:
                try:
                    result = _publish_to_platform_sync(post, platform)
                    publish_results[platform] = result
                    logger.info(f"Auto-publish platform result ({platform}): {result.get('status')}")
                except Exception as e:
                    publish_results[platform] = {"status": "error", "message": str(e)}
                    logger.error(f"Auto-publish platform error ({platform}): {e}")
            post["publish_results"] = publish_results

        db.social_posts.insert_one(post)

        # Log to publish_log if published
        if auto_approve:
            db.social_publish_log.insert_one({
                "id": new_id(),
                "post_id": post["id"],
                "platforms": platforms,
                "results": publish_results,
                "source": "ai_auto_publish",
                "published_at": utcnow(),
            })

        # Log the action
        db.social_auto_publish_log.insert_one({
            "id": new_id(),
            "post_id": post["id"],
            "topic": topic,
            "status": status,
            "auto_approved": auto_approve,
            "title": post["title"],
            "content_preview": content[:100],
            "platforms": platforms,
            "publish_results": publish_results if auto_approve else None,
            "created_at": utcnow(),
        })

        logger.info(f"Auto-publish: {topic} -> {status} (post: {post['id']})")
        return {"status": "created", "post_id": post["id"], "topic": topic, "publish_results": publish_results}

    except Exception as e:
        logger.error(f"Auto-publish hatasi: {e}")
        try:
            db = get_db()
            db.social_auto_publish_log.insert_one({
                "id": new_id(),
                "status": "error",
                "error": str(e),
                "created_at": utcnow(),
            })
        except Exception:
            pass
        raise self.retry(exc=e, countdown=120)


# =====================================================
# TASK 8: ZAMANLANMIS POSTLARI YAYINLA (Her saat basi)
# =====================================================

@celery_app.task(name='celery_tasks.publish_scheduled_posts_task', bind=True, max_retries=2)
def publish_scheduled_posts_task(self):
    """Zamani gelmis 'scheduled' postlari otomatik yayinla"""
    try:
        db = get_db()
        now = datetime.now(timezone.utc).isoformat()

        # scheduled_at zamani gecmis ve hala scheduled olan postlari bul
        scheduled_posts = list(db.social_posts.find({
            "status": "scheduled",
            "scheduled_at": {"$lte": now},
        }, {"_id": 0}))

        if not scheduled_posts:
            return {"status": "no_scheduled_posts"}

        published_count = 0
        for post in scheduled_posts:
            post_id = post["id"]
            platforms = post.get("platforms", [])
            publish_results = {}

            for platform in platforms:
                try:
                    result = _publish_to_platform_sync(post, platform)
                    publish_results[platform] = result
                except Exception as e:
                    publish_results[platform] = {"status": "error", "message": str(e)}
                    logger.error(f"Scheduled publish error ({platform}, post {post_id}): {e}")

            # Update post status
            db.social_posts.update_one(
                {"id": post_id},
                {"$set": {
                    "status": "published",
                    "published_at": utcnow(),
                    "updated_at": utcnow(),
                    "publish_results": publish_results,
                }}
            )

            # Log publish
            db.social_publish_log.insert_one({
                "id": new_id(),
                "post_id": post_id,
                "platforms": platforms,
                "results": publish_results,
                "source": "scheduled_auto",
                "published_at": utcnow(),
            })

            published_count += 1
            logger.info(f"Scheduled post published: {post_id}")

        return {"status": "done", "published": published_count}

    except Exception as e:
        logger.error(f"Scheduled publish hatasi: {e}")
        raise self.retry(exc=e, countdown=120)


# ==================== MARKETING AUTOMATION ORCHESTRATOR ====================
# Anthropic patterns: Orchestrator-Subagents, Prompt Chaining

@celery_app.task(bind=True, max_retries=2)
def marketing_daily_report_task(self):
    """Gunluk pazarlama raporu olustur (her gun 09:00)"""
    try:
        db = get_db()

        # Verileri topla
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)

        social_posts = db.social_posts.count_documents({"created_at": {"$gte": yesterday.isoformat()}})
        new_reviews = db.reviews.count_documents({"created_at": {"$gte": yesterday.isoformat()}})
        pending_reviews = db.reviews.count_documents({"ai_response": None})
        lifecycle_sent = db.lifecycle_messages.count_documents({"created_at": {"$gte": yesterday.isoformat()}})
        meta_campaigns = db.meta_campaigns.count_documents({"status": "active"})
        google_campaigns = db.google_campaigns.count_documents({"status": "active"})

        report = {
            "id": str(uuid.uuid4()),
            "type": "daily_marketing_report",
            "date": today.strftime("%Y-%m-%d"),
            "metrics": {
                "social_posts_created": social_posts,
                "new_reviews": new_reviews,
                "pending_review_responses": pending_reviews,
                "lifecycle_messages_sent": lifecycle_sent,
                "active_meta_campaigns": meta_campaigns,
                "active_google_campaigns": google_campaigns,
            },
            "alerts": [],
            "created_at": utcnow(),
        }

        # Uyarilar
        if pending_reviews > 5:
            report["alerts"].append(f"{pending_reviews} yanitlanmamis degerlendirme var!")
        if social_posts == 0:
            report["alerts"].append("Dun hic sosyal medya gonderi olusturulmadi")
        if meta_campaigns == 0 and google_campaigns == 0:
            report["alerts"].append("Aktif reklam kampanyasi yok")

        db.marketing_reports.insert_one(report)
        logger.info(f"Daily marketing report generated: {report['id']}")
        return {"status": "done", "report_id": report["id"], "alerts": len(report["alerts"])}

    except Exception as e:
        logger.error(f"Marketing report hatasi: {e}")
        raise self.retry(exc=e, countdown=120)


@celery_app.task(bind=True, max_retries=2)
def reputation_monitor_task(self):
    """Itibar izleme - olumsuz yorumlari tespit et (her 6 saatte)"""
    try:
        db = get_db()

        # Son 24 saatteki yanitlanmamis olumsuz yorumlari bul
        from services.reputation_service import SENTIMENT_KEYWORDS

        pending = list(db.reviews.find(
            {"ai_response": None},
            {"_id": 0}
        ).sort("created_at", -1).limit(20))

        urgent = []
        for review in pending:
            text = (review.get("review_text", "") or "").lower()
            rating = review.get("rating", 5)
            neg_count = sum(1 for w in SENTIMENT_KEYWORDS["negative"] if w in text)

            if rating <= 2 or neg_count >= 2:
                urgent.append({
                    "review_id": review.get("id"),
                    "rating": rating,
                    "reviewer": review.get("reviewer_name", "Anonim"),
                    "negative_signals": neg_count,
                })

        if urgent:
            alert = {
                "id": str(uuid.uuid4()),
                "type": "reputation_alert",
                "urgent_reviews": urgent,
                "count": len(urgent),
                "message": f"{len(urgent)} acil yanitlanmasi gereken olumsuz degerlendirme var!",
                "created_at": utcnow(),
            }
            db.marketing_reports.insert_one(alert)
            logger.warning(f"Reputation alert: {len(urgent)} urgent reviews")

        return {"status": "done", "urgent_count": len(urgent)}

    except Exception as e:
        logger.error(f"Reputation monitor hatasi: {e}")
        raise self.retry(exc=e, countdown=120)
