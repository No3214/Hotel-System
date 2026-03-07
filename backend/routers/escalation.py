from fastapi import APIRouter
from typing import Optional
from database import db
from helpers import utcnow

router = APIRouter(tags=["escalation"])


@router.get("/escalations")
async def list_escalations(status: Optional[str] = None, severity: Optional[str] = None, limit: int = 50):
    """Escalation kayitlarini listele"""
    query = {}
    if status:
        query["status"] = status
    if severity:
        query["severity"] = severity
    items = await db.escalation_log.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    total = await db.escalation_log.count_documents(query)

    # Stats
    open_count = await db.escalation_log.count_documents({"status": "open"})
    high_count = await db.escalation_log.count_documents({"status": "open", "severity": "HIGH"})

    return {
        "escalations": items,
        "total": total,
        "open_count": open_count,
        "high_priority": high_count,
    }


@router.patch("/escalations/{escalation_id}/resolve")
async def resolve_escalation(escalation_id: str, notes: str = ""):
    """Escalation'i cozuldu olarak isaretle"""
    result = await db.escalation_log.update_one(
        {"id": escalation_id},
        {"$set": {"status": "resolved", "resolved_at": utcnow(), "resolution_notes": notes}}
    )
    if result.matched_count == 0:
        from fastapi import HTTPException
        raise HTTPException(404, "Escalation bulunamadi")
    return {"success": True}


@router.get("/escalations/stats")
async def escalation_stats():
    """Escalation istatistikleri"""
    total = await db.escalation_log.count_documents({})
    open_count = await db.escalation_log.count_documents({"status": "open"})
    resolved = await db.escalation_log.count_documents({"status": "resolved"})

    pipeline = [
        {"$group": {"_id": "$severity", "count": {"$sum": 1}}},
    ]
    severity_counts = {}
    async for doc in db.escalation_log.aggregate(pipeline):
        severity_counts[doc["_id"]] = doc["count"]

    type_pipeline = [
        {"$group": {"_id": "$escalation_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    type_counts = {}
    async for doc in db.escalation_log.aggregate(type_pipeline):
        type_counts[doc["_id"]] = doc["count"]

    return {
        "total": total,
        "open": open_count,
        "resolved": resolved,
        "by_severity": severity_counts,
        "by_type": type_counts,
    }
