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

        post = {
            "id": new_id(),
            "title": title or "Kozbeyli Konagi",
            "content": content,
            "platforms": settings.get("platforms", ["instagram", "facebook"]),
            "post_type": topic_to_type.get(topic, "text"),
            "frame_style": "default",
            "hashtags": hashtags,
            "status": status,
            "source": "ai_auto_publish",
            "ai_topic": topic,
            "created_at": utcnow(),
            "updated_at": utcnow(),
        }

        if auto_approve:
            post["published_at"] = utcnow()

        db.social_posts.insert_one(post)

        # Log the action
        db.social_auto_publish_log.insert_one({
            "id": new_id(),
            "post_id": post["id"],
            "topic": topic,
            "status": status,
            "auto_approved": auto_approve,
            "title": post["title"],
            "content_preview": content[:100],
            "platforms": post["platforms"],
            "created_at": utcnow(),
        })

        logger.info(f"Auto-publish: {topic} -> {status} (post: {post['id']})")
        return {"status": "created", "post_id": post["id"], "topic": topic}

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
