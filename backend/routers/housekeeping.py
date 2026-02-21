from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from models import HousekeepingCreate, HousekeepingStatus, ReservationStatus

router = APIRouter(tags=["housekeeping"])


@router.get("/housekeeping")
async def list_housekeeping(status: Optional[str] = None):
    query = {"status": status} if status else {}
    logs = await db.housekeeping.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"logs": logs}


@router.post("/housekeeping")
async def create_housekeeping(data: HousekeepingCreate):
    log = {
        "id": new_id(),
        **data.model_dump(),
        "status": HousekeepingStatus.PENDING,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.housekeeping.insert_one(log)
    return clean_doc(log)


@router.patch("/housekeeping/{log_id}/status")
async def update_housekeeping(log_id: str, status: str):
    update = {"status": status, "updated_at": utcnow()}
    if status == HousekeepingStatus.COMPLETED:
        update["completed_at"] = utcnow()
    result = await db.housekeeping.update_one({"id": log_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(404, "Kayit bulunamadi")
    return {"success": True}


@router.post("/housekeeping/auto-schedule")
async def auto_schedule_housekeeping():
    checked_out = await db.reservations.find(
        {"status": ReservationStatus.CHECKED_OUT}, {"_id": 0}
    ).to_list(100)

    created = 0
    for res in checked_out:
        room_num = res.get("room_id") or res.get("room_number") or res.get("room_type", "unknown")
        existing = await db.housekeeping.find_one({
            "room_number": room_num,
            "status": {"$in": [HousekeepingStatus.PENDING, HousekeepingStatus.IN_PROGRESS]},
        })
        if not existing:
            log = {
                "id": new_id(),
                "room_number": room_num,
                "task_type": "checkout_clean",
                "priority": "high",
                "assigned_to": None,
                "notes": f"Oto-olusturuldu: Misafir checkout - Rez: {res.get('id', '')}",
                "status": HousekeepingStatus.PENDING,
                "reservation_id": res.get("id"),
                "created_at": utcnow(),
                "updated_at": utcnow(),
            }
            await db.housekeeping.insert_one(log)
            created += 1

    return {"success": True, "created": created}
