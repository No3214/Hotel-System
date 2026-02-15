"""
Kozbeyli Konagi - Zamanli Gorev Yoneticisi (Scheduler)
- 01:00: Kahvalti hazirligi bildirimi
- 08:30: Sabah hatirlama mesajlari (tuvalet temizlik + check-in hazirligi)
- Check-out sonrasi: Temizlik listesi bildirimi
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def get_todays_reservations():
    """Bugunku aktif rezervasyonlari getir"""
    from database import db
    today = datetime.now().strftime("%Y-%m-%d")
    reservations = await db.reservations.find({
        "status": {"$in": ["confirmed", "checked_in"]},
        "check_in": {"$lte": today},
        "check_out": {"$gte": today},
    }, {"_id": 0}).to_list(200)
    return reservations


async def get_todays_checkouts():
    """Bugun check-out yapacak rezervasyonlari getir"""
    from database import db
    today = datetime.now().strftime("%Y-%m-%d")
    checkouts = await db.reservations.find({
        "status": {"$in": ["confirmed", "checked_in"]},
        "check_out": today,
    }, {"_id": 0}).to_list(200)
    return checkouts


async def get_todays_checkins():
    """Bugun check-in yapacak rezervasyonlari getir"""
    from database import db
    today = datetime.now().strftime("%Y-%m-%d")
    checkins = await db.reservations.find({
        "status": {"$in": ["pending", "confirmed"]},
        "check_in": today,
    }, {"_id": 0}).to_list(200)
    return checkins


async def send_group_notification(notification_type: str, message: str):
    """WhatsApp grubuna bildirim gonder (mock modda DB'ye kaydeder)"""
    from database import db
    from helpers import utcnow, new_id

    notification = {
        "id": new_id(),
        "type": notification_type,
        "message": message,
        "status": "sent",
        "source": "scheduler",
        "created_at": utcnow(),
    }
    await db.group_notifications.insert_one(notification)

    await db.automation_logs.insert_one({
        "id": new_id(),
        "type": notification_type,
        "message": message,
        "status": "completed",
        "source": "scheduler",
        "created_at": utcnow(),
    })
    logger.info(f"Grup bildirimi gonderildi: {notification_type}")
    return notification


# =====================================================
# JOB 1: KAHVALTI HAZIRLIGI (Her gece 01:00)
# =====================================================

async def breakfast_prep_job():
    """Sabah kahvalti hazirligi bildirimi"""
    try:
        reservations = await get_todays_reservations()

        if not reservations:
            msg = "Sabah kahvalti yok - bugun misafir bulunmuyor."
            await send_group_notification("breakfast_prep", msg)
            return

        room_summary = {}
        total_guests = 0

        for res in reservations:
            guests = res.get("guests_count", 1)
            room_type = res.get("room_type", "Standart")
            total_guests += guests

            key = f"{guests} kisilik"
            if key not in room_summary:
                room_summary[key] = 0
            room_summary[key] += 1

        lines = []
        for key, count in sorted(room_summary.items()):
            lines.append(f"{count} adet {key}")

        summary_text = ", ".join(lines)
        msg = f"Sabah {summary_text} oda kahvalti var. Toplam {total_guests} kisi."

        await send_group_notification("breakfast_prep", msg)
        logger.info(f"Kahvalti bildirimi gonderildi: {total_guests} kisi")

    except Exception as e:
        logger.error(f"Kahvalti bildirimi hatasi: {e}")


# =====================================================
# JOB 2: SABAH HATIRLAMA (Her gun 08:30)
# =====================================================

async def morning_reminders_job():
    """Sabah hatirlama mesajlari"""
    try:
        # Mesaj 1: Tuvalet temizlik ve stok kontrolu
        toilet_msg = "Gunaydin! Ortak alan tuvaletleri temizlik ve stok kontrolu yapilmali. Sabun, kagit havlu ve tuvalet kagidi kontrol ediniz."
        await send_group_notification("morning_toilet_reminder", toilet_msg)

        # Mesaj 2: Check-in odalari hazirligi
        checkins = await get_todays_checkins()

        if checkins:
            room_numbers = []
            for res in checkins:
                room_id = res.get("room_id", "")
                room_type = res.get("room_type", "")
                room_numbers.append(room_id or room_type)

            rooms_text = "-".join(room_numbers) if room_numbers else "Bilgi yok"
            checkin_msg = f"Bugun check-in yapacak odalar: {rooms_text}. Hosgeldin ikramlari (su, meyve, kurabiye) hazirlanmali."
        else:
            checkin_msg = "Bugun check-in yapacak misafir bulunmuyor."

        await send_group_notification("morning_checkin_reminder", checkin_msg)
        logger.info("Sabah hatirlama mesajlari gonderildi")

    except Exception as e:
        logger.error(f"Sabah hatirlama hatasi: {e}")


# =====================================================
# JOB 3: TEMIZLIK LISTESI (Check-out sonrasi)
# =====================================================

async def checkout_cleaning_job():
    """Check-out sonrasi temizlik listesi bildirimi"""
    try:
        checkouts = await get_todays_checkouts()

        if not checkouts:
            return

        room_numbers = []
        for res in checkouts:
            room_id = res.get("room_id", "")
            if room_id:
                room_numbers.append(room_id)

        if room_numbers:
            rooms_text = "-".join(sorted(room_numbers))
            msg = f"{rooms_text} temizlik cikis yaptilar."
        else:
            msg = f"{len(checkouts)} oda cikis yapti, temizlik gerekiyor."

        await send_group_notification("checkout_cleaning", msg)
        logger.info(f"Temizlik bildirimi gonderildi: {len(checkouts)} oda")

    except Exception as e:
        logger.error(f"Temizlik bildirimi hatasi: {e}")


# =====================================================
# JOB 4: AKSAM ODA KONTROLU (Her gun 18:00)
# =====================================================

async def evening_room_check_job():
    """Check-out yapan misafirlerin odalarinda klima ve isiklarin kapatilmasini kontrol et"""
    try:
        checkouts = await get_todays_checkouts()

        if not checkouts:
            msg = "Bugun check-out yapan misafir yok. Oda kontrolu gerekmiyor."
            await send_group_notification("evening_room_check", msg)
            return

        room_numbers = []
        for res in checkouts:
            room_id = res.get("room_id", "")
            if room_id:
                room_numbers.append(room_id)

        if room_numbers:
            rooms_text = ", ".join(sorted(room_numbers))
            msg = f"Aksam kontrol: Bugun cikis yapan odalar ({rooms_text}) kontrol edilmeli. Klima ve isiklarin kapatildiginden emin olunuz."
        else:
            msg = f"Aksam kontrol: Bugun {len(checkouts)} oda cikis yapti. Klima ve isiklarin kapatildigini kontrol ediniz."

        await send_group_notification("evening_room_check", msg)
        logger.info(f"Aksam oda kontrol bildirimi gonderildi: {len(checkouts)} oda")

    except Exception as e:
        logger.error(f"Aksam oda kontrol hatasi: {e}")


# =====================================================
# SCHEDULER BASLATMA
# =====================================================

def start_scheduler():
    """Zamanli gorevleri baslat"""
    if scheduler.running:
        return

    # 01:00 - Kahvalti hazirligi
    scheduler.add_job(
        breakfast_prep_job,
        CronTrigger(hour=1, minute=0),
        id="breakfast_prep",
        name="Kahvalti Hazirligi",
        replace_existing=True,
    )

    # 08:30 - Sabah hatirlama
    scheduler.add_job(
        morning_reminders_job,
        CronTrigger(hour=8, minute=30),
        id="morning_reminders",
        name="Sabah Hatirlama",
        replace_existing=True,
    )

    # 12:30 - Check-out temizlik (ogle civari, check-out 12:00)
    scheduler.add_job(
        checkout_cleaning_job,
        CronTrigger(hour=12, minute=30),
        id="checkout_cleaning",
        name="Check-out Temizlik",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler baslatildi - 3 zamanli gorev aktif")


def get_scheduled_jobs():
    """Zamanli gorevlerin durumunu getir"""
    jobs = []
    for job in scheduler.get_jobs():
        next_run = job.next_run_time
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": next_run.isoformat() if next_run else None,
            "status": "active" if next_run else "paused",
        })
    return jobs
