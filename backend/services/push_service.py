import os
import json
import logging

logger = logging.getLogger(__name__)

try:
    from pywebpush import webpush, WebPushException
except ImportError:
    logger.warning("pywebpush not installed — push notifications disabled. Install with: pip install pywebpush")
    webpush = None
    WebPushException = Exception

VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "")
VAPID_CLAIMS_EMAIL = os.environ.get("VAPID_CLAIMS_EMAIL", "mailto:info@kozbeylikonagi.com")


async def send_push_to_all(db, title: str, body: str, tag: str = "kozbeyli", url: str = "/"):
    """Send push notification to all subscribed users."""
    if webpush is None:
        return {"sent": 0, "failed": 0, "reason": "pywebpush_not_installed"}
    if not VAPID_PRIVATE_KEY:
        logger.warning("VAPID key not configured, skipping push")
        return {"sent": 0, "failed": 0, "reason": "no_vapid_key"}

    subscriptions = await db.push_subscriptions.find({}, {"_id": 0}).to_list(500)

    sent = 0
    failed = 0

    for sub in subscriptions:
        subscription_info = sub.get("subscription", {})
        if not subscription_info.get("endpoint"):
            continue

        try:
            webpush(
                subscription_info=subscription_info,
                data=json.dumps({
                    "title": title,
                    "body": body,
                    "tag": tag,
                    "url": url,
                }),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_CLAIMS_EMAIL},
            )
            sent += 1
        except WebPushException as e:
            logger.error(f"Push failed: {e}")
            # Remove expired subscriptions (410 Gone)
            if hasattr(e, 'response') and e.response and e.response.status_code == 410:
                await db.push_subscriptions.delete_one({"endpoint": subscription_info.get("endpoint")})
            failed += 1
        except Exception as e:
            logger.error(f"Push error: {e}")
            failed += 1

    logger.info(f"Push sent: {sent}, failed: {failed}")
    return {"sent": sent, "failed": failed}


async def send_checkin_reminders(db):
    """Send push notifications for today's check-ins."""
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    checkins = await db.reservations.find({
        "check_in": today,
        "status": {"$in": ["pending", "confirmed"]},
    }, {"_id": 0, "guest_name": 1, "room_type": 1, "room_id": 1}).to_list(50)

    if checkins:
        names = ", ".join(c.get("guest_name", "Misafir") for c in checkins[:3])
        if len(checkins) > 3:
            names += f" +{len(checkins)-3}"

        await send_push_to_all(
            db,
            title=f"Bugun {len(checkins)} Check-in",
            body=f"Misafirler: {names}",
            tag="checkin-today",
        )


async def send_checkout_reminders(db):
    """Send push notifications for today's check-outs."""
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    checkouts = await db.reservations.find({
        "check_out": today,
        "status": {"$in": ["confirmed", "checked_in"]},
    }, {"_id": 0, "guest_name": 1, "room_id": 1}).to_list(50)

    if checkouts:
        rooms = ", ".join(c.get("room_id", "") for c in checkouts if c.get("room_id"))
        await send_push_to_all(
            db,
            title=f"Bugun {len(checkouts)} Check-out",
            body=f"Odalar: {rooms}" if rooms else f"{len(checkouts)} oda cikis yapacak",
            tag="checkout-today",
        )
