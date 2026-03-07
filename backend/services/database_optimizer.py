import logging
from database import db

logger = logging.getLogger(__name__)


async def apply_indexes():
    """Create MongoDB indexes for performance optimization."""
    try:
        # Reservations - frequently queried by date, room, guest, status
        await db.reservations.create_index("check_in")
        await db.reservations.create_index("check_out")
        await db.reservations.create_index("room_id")
        await db.reservations.create_index("guest_id")
        await db.reservations.create_index("status")
        await db.reservations.create_index([("check_in", 1), ("check_out", 1)])

        # Guests - searched by name, phone, email
        await db.guests.create_index("name")
        await db.guests.create_index("phone")
        await db.guests.create_index("email")

        # Rooms - queried by status, type
        await db.rooms.create_index("status")
        await db.rooms.create_index("type")

        # Audit logs - queried by timestamp, user, action
        await db.audit_logs.create_index("timestamp")
        await db.audit_logs.create_index("user")
        await db.audit_logs.create_index("action")
        await db.audit_logs.create_index([("timestamp", -1)])

        # Tasks - queried by status, assigned_to
        await db.tasks.create_index("status")
        await db.tasks.create_index("assigned_to")

        # Events - queried by date
        await db.events.create_index("date")

        # Housekeeping - queried by room, status, date
        await db.housekeeping.create_index("room_id")
        await db.housekeeping.create_index("status")

        # Table reservations - queried by date, status
        await db.table_reservations.create_index("date")
        await db.table_reservations.create_index("status")

        # Messages / Campaigns
        await db.messages.create_index("created_at")
        await db.campaigns.create_index("created_at")

        # Staff / Shifts
        await db.staff.create_index("role")

        # Loyalty
        await db.loyalty.create_index("guest_id")
        await db.loyalty.create_index("level")

        # Revenue / Pricing rules
        await db.dynamic_pricing_rules.create_index("start_date")
        await db.dynamic_pricing_rules.create_index("end_date")

        # Financials
        await db.financials.create_index("type")
        await db.financials.create_index("date")
        await db.financials.create_index([("type", 1), ("date", -1)])
        await db.financials.create_index("category")

        # Push subscriptions
        await db.push_subscriptions.create_index("endpoint")

        # Sync logs
        await db.sync_logs.create_index("timestamp")
        await db.sync_logs.create_index("sync_type")

        # WhatsApp messages
        await db.whatsapp_messages.create_index("session_id")
        await db.whatsapp_messages.create_index("direction")
        await db.whatsapp_messages.create_index([("created_at", -1)])

        # Instagram messages
        await db.instagram_messages.create_index("session_id")
        await db.instagram_messages.create_index("direction")
        await db.instagram_messages.create_index([("created_at", -1)])

        # AI Usage Log - queried by created_at + provider + task_type
        await db.ai_usage_log.create_index([("created_at", -1)])
        await db.ai_usage_log.create_index("provider")
        await db.ai_usage_log.create_index("task_type")

        # Marketing Reports
        await db.marketing_reports.create_index("type")
        await db.marketing_reports.create_index([("created_at", -1)])

        # Reputation Reviews
        await db.reputation_reviews.create_index("platform")
        await db.reputation_reviews.create_index("sentiment")
        await db.reputation_reviews.create_index([("created_at", -1)])

        # Meta Campaigns
        await db.meta_campaigns.create_index("status")
        await db.meta_campaigns.create_index([("created_at", -1)])

        # Google Campaigns
        await db.google_campaigns.create_index("status")
        await db.google_campaigns.create_index("campaign_type")
        await db.google_campaigns.create_index([("created_at", -1)])

        # Competitors
        await db.competitors.create_index("id", unique=True, sparse=True)

        # Presence Audits
        await db.presence_audits.create_index([("created_at", -1)])

        # Social Posts
        await db.social_posts.create_index([("created_at", -1)])
        await db.social_posts.create_index("platform")

        # Lifecycle Messages
        await db.lifecycle_messages.create_index([("created_at", -1)])

        logger.info("Database indexes applied successfully")
    except Exception as e:
        logger.error(f"Error applying database indexes: {e}")
