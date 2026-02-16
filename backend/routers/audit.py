from fastapi import APIRouter, Query, Request
from typing import Optional, Dict, Any
from datetime import date, datetime, timedelta, timezone
from database import db
from helpers import utcnow, new_id
import copy
import logging

router = APIRouter(tags=["audit"])
logger = logging.getLogger(__name__)

# Sensitive fields for KVKK masking
SENSITIVE_FIELDS = {
    "password", "credit_card", "cvv", "card_number",
    "phone", "email", "tc_kimlik", "passport", "id_number",
    "bank_account", "iban",
}


def mask_sensitive_data(data: Optional[Dict]) -> Optional[Dict]:
    if not data:
        return None
    masked = copy.deepcopy(data)
    for field in SENSITIVE_FIELDS:
        if field in masked:
            val = masked[field]
            if isinstance(val, str) and len(val) > 6:
                masked[field] = val[:2] + "***" + val[-2:]
            else:
                masked[field] = "***"
    return masked


async def log_audit(
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    user_id: str = "system",
    user_email: str = "system",
    old_values: Optional[Dict] = None,
    new_values: Optional[Dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    metadata: Optional[Dict] = None,
):
    try:
        log_entry = {
            "id": new_id(),
            "timestamp": utcnow(),
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "user_id": user_id,
            "user_email": user_email,
            "old_values": mask_sensitive_data(old_values),
            "new_values": mask_sensitive_data(new_values),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "success": success,
            "error_message": error_message,
            "metadata": metadata,
        }
        await db.audit_logs.insert_one(log_entry)
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")


# ==================== SECURITY RULES ====================

SECURITY_RULES = [
    {"id": "failed_login", "name": "Basarisiz Giris Denemeleri", "type": "FAILED_LOGIN", "threshold": 5, "window_minutes": 60, "severity": "HIGH"},
    {"id": "unusual_hours", "name": "Olagandisi Saat Aktivitesi", "type": "UNUSUAL_HOURS", "threshold": 10, "window_minutes": 1440, "severity": "MEDIUM"},
    {"id": "bulk_deletion", "name": "Toplu Silme", "type": "BULK_DELETION", "threshold": 10, "window_minutes": 60, "severity": "HIGH"},
    {"id": "multiple_ips", "name": "Coklu IP Adresi", "type": "MULTIPLE_IPS", "threshold": 3, "window_minutes": 60, "severity": "MEDIUM"},
]


async def check_security_rules(user_id: str = None):
    alerts = []
    for rule in SECURITY_RULES:
        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=rule["window_minutes"])).isoformat()
        query = {"timestamp": {"$gte": cutoff}}
        if user_id:
            query["user_id"] = user_id

        if rule["type"] == "FAILED_LOGIN":
            query["action"] = "LOGIN_FAILED"
            count = await db.audit_logs.count_documents(query)
            if count >= rule["threshold"]:
                alerts.append({
                    "type": rule["type"],
                    "severity": rule["severity"],
                    "message": f"{rule['window_minutes']} dakikada {count} basarisiz giris denemesi",
                    "count": count,
                    "threshold": rule["threshold"],
                })

        elif rule["type"] == "BULK_DELETION":
            query["action"] = "DELETE"
            count = await db.audit_logs.count_documents(query)
            if count >= rule["threshold"]:
                alerts.append({
                    "type": rule["type"],
                    "severity": rule["severity"],
                    "message": f"{rule['window_minutes']} dakikada {count} silme islemi",
                    "count": count,
                    "threshold": rule["threshold"],
                })

    return alerts


# ==================== API ENDPOINTS ====================

@router.get("/audit/logs")
async def get_audit_logs(
    entity_type: Optional[str] = Query(default=None),
    action: Optional[str] = Query(default=None),
    user_id: Optional[str] = Query(default=None),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
):
    query = {}
    if entity_type:
        query["entity_type"] = entity_type
    if action:
        query["action"] = action
    if user_id:
        query["user_id"] = user_id
    if date_from:
        query["timestamp"] = {"$gte": date_from.isoformat()}
    if date_to:
        if "timestamp" in query:
            query["timestamp"]["$lte"] = date_to.isoformat() + "T23:59:59"
        else:
            query["timestamp"] = {"$lte": date_to.isoformat() + "T23:59:59"}

    total = await db.audit_logs.count_documents(query)
    skip = (page - 1) * limit
    logs = await db.audit_logs.find(query, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)

    return {
        "total": total,
        "page": page,
        "pages": max(1, (total + limit - 1) // limit),
        "logs": logs,
    }


@router.get("/audit/logs/{entity_type}/{entity_id}")
async def get_entity_history(entity_type: str, entity_id: str):
    logs = await db.audit_logs.find(
        {"entity_type": entity_type, "entity_id": entity_id},
        {"_id": 0},
    ).sort("timestamp", 1).to_list(500)
    return {"entity_type": entity_type, "entity_id": entity_id, "history": logs}


@router.get("/audit/alerts")
async def get_security_alerts(
    severity: Optional[str] = Query(default=None),
    resolved: Optional[bool] = Query(default=None),
):
    query = {}
    if severity:
        query["severity"] = severity
    if resolved is not None:
        query["resolved"] = resolved

    alerts = await db.security_alerts.find(query, {"_id": 0}).sort("timestamp", -1).limit(100).to_list(100)
    return {"alerts": alerts}


@router.post("/audit/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    result = await db.security_alerts.update_one(
        {"id": alert_id},
        {"$set": {"resolved": True, "resolved_at": utcnow()}},
    )
    if result.modified_count == 0:
        return {"error": "Alert bulunamadi"}
    return {"success": True, "alert_id": alert_id}


@router.get("/audit/stats")
async def get_audit_stats(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
):
    if not date_from:
        date_from = date.today() - timedelta(days=30)
    if not date_to:
        date_to = date.today()

    query = {"timestamp": {"$gte": date_from.isoformat(), "$lte": date_to.isoformat() + "T23:59:59"}}
    logs = await db.audit_logs.find(query, {"_id": 0, "action": 1, "entity_type": 1, "success": 1}).to_list(10000)

    action_counts = {}
    entity_counts = {}
    failed_count = 0

    for log in logs:
        action = log.get("action", "unknown")
        entity = log.get("entity_type", "unknown")
        action_counts[action] = action_counts.get(action, 0) + 1
        entity_counts[entity] = entity_counts.get(entity, 0) + 1
        if not log.get("success", True):
            failed_count += 1

    total = len(logs)
    return {
        "period": {"from": date_from.isoformat(), "to": date_to.isoformat()},
        "total_logs": total,
        "action_counts": action_counts,
        "entity_counts": entity_counts,
        "failed_operations": failed_count,
        "success_rate": round((total - failed_count) / total * 100, 1) if total > 0 else 100,
    }


@router.post("/audit/check-security")
async def run_security_check(user_id: Optional[str] = Query(default=None)):
    alerts = await check_security_rules(user_id)
    # Save new alerts
    for alert_data in alerts:
        existing = await db.security_alerts.find_one({
            "alert_type": alert_data["type"],
            "resolved": False,
        })
        if not existing:
            await db.security_alerts.insert_one({
                "id": new_id(),
                "timestamp": utcnow(),
                "alert_type": alert_data["type"],
                "severity": alert_data["severity"],
                "message": alert_data["message"],
                "user_id": user_id,
                "details": alert_data,
                "resolved": False,
            })
    return {"alerts_found": len(alerts), "alerts": alerts}
