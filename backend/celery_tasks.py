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


def get_db():
    """Get synchronous MongoDB connection for Celery worker."""
    client = MongoClient(MONGO_URL)
    return client[DB_NAME]


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
