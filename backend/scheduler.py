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
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    reservations = await db.reservations.find({
        "status": {"$in": ["confirmed", "checked_in"]},
        "check_in": {"$lte": today},
        "check_out": {"$gte": today},
    }, {"_id": 0}).to_list(200)
    return reservations


async def get_todays_checkouts():
    """Bugun check-out yapacak rezervasyonlari getir"""
    from database import db
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    checkouts = await db.reservations.find({
        "status": {"$in": ["confirmed", "checked_in"]},
        "check_out": today,
    }, {"_id": 0}).to_list(200)
    return checkouts


async def get_todays_checkins():
    """Bugun check-in yapacak rezervasyonlari getir"""
    from database import db
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
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
# JOB 5: SOSYAL MEDYA OTOMATIK YAYIN (Her 5 dk)
# =====================================================

async def publish_scheduled_posts_job():
    """Zamanlanmis sosyal medya gonderilerini otomatik yayinla"""
    try:
        from database import db
        now = datetime.now(timezone.utc).isoformat()

        # scheduled_at zamani gecmis ve hala "scheduled" durumunda olan gonderileri bul
        posts = await db.social_posts.find({
            "status": "scheduled",
            "scheduled_at": {"$lte": now},
        }, {"_id": 0}).to_list(20)

        if not posts:
            return

        for post in posts:
            try:
                from routers.social_media import _publish_to_platform
                publish_results = {}
                for platform in post.get("platforms", []):
                    try:
                        result = await _publish_to_platform(platform, post)
                        publish_results[platform] = result
                    except Exception as e:
                        publish_results[platform] = {"success": False, "error": str(e)}

                await db.social_posts.update_one(
                    {"id": post["id"]},
                    {"$set": {
                        "status": "published",
                        "published_at": now,
                        "updated_at": now,
                        "publish_results": publish_results,
                    }}
                )
                logger.info(f"Zamanlanmis gonderi yayinlandi: {post['id']}")
            except Exception as e:
                logger.error(f"Gonderi yayinlama hatasi {post.get('id')}: {e}")

    except Exception as e:
        logger.error(f"Sosyal medya auto-publish hatasi: {e}")


# =====================================================
# JOB 6: SELF-HEALING HEALTH CHECK (Her 10 dk)
# =====================================================

async def health_check_job():
    """Sistem saglik kontrolu ve otomatik iyilestirme"""
    try:
        from database import db

        # 1. DB baglanti kontrolu
        try:
            await db.command("ping")
        except Exception as e:
            logger.error(f"DB baglanti hatasi, yeniden baglaniliyor: {e}")
            # Motor driver otomatik reconnect yapar, sadece logluyoruz

        # 2. Stuck reservation'lari kontrol et (7+ gun checked_in ama check_out gecmis)
        cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
        stuck = await db.reservations.count_documents({
            "status": "checked_in",
            "check_out": {"$lt": cutoff},
        })
        if stuck > 0:
            logger.warning(f"Self-healing: {stuck} adet stuck rezervasyon bulundu (7+ gun gecmis check-out)")
            # Auto-fix: mark as checked_out
            await db.reservations.update_many(
                {"status": "checked_in", "check_out": {"$lt": cutoff}},
                {"$set": {"status": "checked_out", "auto_fixed": True, "auto_fixed_at": datetime.now(timezone.utc).isoformat()}}
            )
            logger.info(f"Self-healing: {stuck} stuck rezervasyon otomatik checked_out yapildi")

        # 3. Stuck tasks (30+ gun completed olmamis urgent task)
        task_cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        stuck_tasks = await db.tasks.count_documents({
            "status": {"$in": ["pending", "in_progress"]},
            "created_at": {"$lt": task_cutoff},
        })
        if stuck_tasks > 0:
            logger.warning(f"Self-healing: {stuck_tasks} adet 30+ gunluk tamamlanmamis gorev var")

        # 4. Room status consistency check
        occupied_rooms = await db.reservations.distinct("room_id", {
            "status": {"$in": ["checked_in"]},
        })
        if occupied_rooms:
            await db.rooms.update_many(
                {"room_id": {"$in": occupied_rooms}, "status": {"$ne": "occupied"}},
                {"$set": {"status": "occupied"}}
            )

        logger.debug("Health check tamamlandi")

    except Exception as e:
        logger.error(f"Health check hatasi: {e}")


# =====================================================
# JOB 7: STALE DATA TEMIZLIGI (Her gece 03:00)
# =====================================================

async def cleanup_stale_data_job():
    """Eski log'lari ve gecici verileri temizle"""
    try:
        from database import db

        cutoff_90d = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
        cutoff_30d = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

        # 90 gunden eski audit log'larini sil
        result = await db.audit_logs.delete_many({"timestamp": {"$lt": cutoff_90d}})
        if result.deleted_count:
            logger.info(f"Cleanup: {result.deleted_count} eski audit log silindi")

        # 30 gunden eski automation log'larini sil
        result = await db.automation_logs.delete_many({"created_at": {"$lt": cutoff_30d}})
        if result.deleted_count:
            logger.info(f"Cleanup: {result.deleted_count} eski automation log silindi")

        # 30 gunden eski cozulmus security alert'leri sil
        result = await db.security_alerts.delete_many({
            "resolved": True,
            "timestamp": {"$lt": cutoff_30d},
        })
        if result.deleted_count:
            logger.info(f"Cleanup: {result.deleted_count} eski security alert silindi")

        # 90 gunden eski group notification'lari sil
        result = await db.group_notifications.delete_many({"created_at": {"$lt": cutoff_90d}})
        if result.deleted_count:
            logger.info(f"Cleanup: {result.deleted_count} eski bildirim silindi")

        logger.info("Gece temizligi tamamlandi")

    except Exception as e:
        logger.error(f"Stale data cleanup hatasi: {e}")


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

    # 18:00 - Aksam oda kontrolu (klima/isik kapatma)
    scheduler.add_job(
        evening_room_check_job,
        CronTrigger(hour=18, minute=0),
        id="evening_room_check",
        name="Aksam Oda Kontrolu",
        replace_existing=True,
    )

    # Her 5 dk - Sosyal medya zamanlanmis gonderi yayinla
    scheduler.add_job(
        publish_scheduled_posts_job,
        'interval',
        minutes=5,
        id="social_auto_publish",
        name="Sosyal Medya Otomatik Yayin",
        replace_existing=True,
    )

    # Her 10 dk - Self-healing: DB baglanti kontrolu
    scheduler.add_job(
        health_check_job,
        'interval',
        minutes=10,
        id="health_check",
        name="Sistem Saglik Kontrolu",
        replace_existing=True,
    )

    # Her gece 03:00 - Stale data temizligi
    scheduler.add_job(
        cleanup_stale_data_job,
        CronTrigger(hour=3, minute=0),
        id="stale_cleanup",
        name="Eski Veri Temizligi",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler baslatildi - 7 zamanli gorev aktif")


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
