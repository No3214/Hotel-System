"""
Kozbeyli Konagi - WhatsApp Automatic Triggers
Triggered by scheduler or events to send WhatsApp notifications.
"""
import logging
from datetime import datetime, timezone, timedelta

from database import db
from helpers import utcnow
from services.whatsapp_service import (
    send_checkout_thanks,
    send_reservation_reminder,
    send_welcome_checkin,
    notify_cleaning_team,
    send_text_message as wa_send_text,
)

logger = logging.getLogger(__name__)


async def trigger_reservation_reminders():
    """Send reminders for tomorrow's check-ins."""
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
    reservations = await db.reservations.find(
        {"check_in": tomorrow, "reminder_sent": {"$ne": True}, "status": {"$in": ["confirmed", "pending"]}},
        {"_id": 0},
    ).to_list(100)

    sent_count = 0
    for res in reservations:
        phone = res.get("phone") or res.get("guest_phone", "")
        guest_name = res.get("guest_name", "Misafir")
        if phone:
            try:
                await send_reservation_reminder(phone, guest_name, tomorrow)
                await db.reservations.update_one(
                    {"id": res["id"]},
                    {"$set": {"reminder_sent": True}},
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Reminder failed for {res.get('id')}: {e}")

    logger.info(f"Reservation reminders sent: {sent_count}/{len(reservations)}")
    return sent_count


async def trigger_checkout_thanks():
    """Send thank-you messages for today's check-outs."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    checkouts = await db.reservations.find(
        {"check_out": today, "thanks_sent": {"$ne": True}, "status": "checked_out"},
        {"_id": 0},
    ).to_list(100)

    sent_count = 0
    for res in checkouts:
        phone = res.get("phone") or res.get("guest_phone", "")
        guest_name = res.get("guest_name", "Misafir")
        if phone:
            try:
                await send_checkout_thanks(phone, guest_name)
                await db.reservations.update_one(
                    {"id": res["id"]},
                    {"$set": {"thanks_sent": True}},
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Checkout thanks failed for {res.get('id')}: {e}")

    logger.info(f"Checkout thanks sent: {sent_count}/{len(checkouts)}")
    return sent_count


async def trigger_cleaning_notification(room_number: str, guest_name: str, priority: str = "Normal"):
    """Notify cleaning staff about a room that needs cleaning."""
    import os

    cleaning_phone = os.environ.get("WHATSAPP_GROUP_NUMBER", "")
    if not cleaning_phone:
        logger.warning("No cleaning team phone configured")
        await db.group_notifications.insert_one({
            "id": (await __import__('helpers')).new_id() if False else "",
            "type": "cleaning",
            "message": f"Oda {room_number} temizlik bekliyor ({guest_name})",
            "status": "pending",
            "created_at": utcnow(),
        })
        return {"status": "mock", "message": "No phone configured"}

    return await notify_cleaning_team(cleaning_phone, room_number, guest_name, priority)
