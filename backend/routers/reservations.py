from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from models import ReservationCreate, ReservationUpdate, ReservationStatus, HousekeepingStatus

router = APIRouter(tags=["reservations"])


@router.get("/reservations")
async def list_reservations(status: Optional[str] = None, limit: int = 50, skip: int = 0):
    query = {}
    if status:
        query["status"] = status
    items = await db.reservations.find(query, {"_id": 0}).sort("check_in", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.reservations.count_documents(query)
    return {"reservations": items, "total": total}


@router.post("/reservations")
async def create_reservation(data: ReservationCreate):
    reservation = {
        "id": new_id(),
        **data.model_dump(),
        "status": ReservationStatus.PENDING,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.reservations.insert_one(reservation)
    return clean_doc(reservation)


@router.get("/reservations/{res_id}")
async def get_reservation(res_id: str):
    res = await db.reservations.find_one({"id": res_id}, {"_id": 0})
    if not res:
        raise HTTPException(404, "Rezervasyon bulunamadi")
    return res


@router.patch("/reservations/{res_id}/status")
async def update_reservation_status(res_id: str, status: str):
    update = {"status": status, "updated_at": utcnow()}
    if status == ReservationStatus.CHECKED_OUT:
        update["checked_out_at"] = utcnow()
    result = await db.reservations.update_one({"id": res_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(404, "Rezervasyon bulunamadi")
    return {"success": True}


@router.patch("/reservations/{res_id}")
async def update_reservation(res_id: str, data: ReservationUpdate):
    update = {k: v for k, v in data.model_dump().items() if v is not None}
    update["updated_at"] = utcnow()

    if data.status == ReservationStatus.CHECKED_IN:
        update["checked_in_at"] = utcnow()
    elif data.status == ReservationStatus.CHECKED_OUT:
        update["checked_out_at"] = utcnow()

    result = await db.reservations.update_one({"id": res_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(404, "Rezervasyon bulunamadi")

    # Auto-create housekeeping on checkout
    if data.status == ReservationStatus.CHECKED_OUT:
        res = await db.reservations.find_one({"id": res_id}, {"_id": 0})
        if res:
            log = {
                "id": new_id(),
                "room_number": res.get("room_type", ""),
                "task_type": "checkout_clean",
                "priority": "high",
                "assigned_to": None,
                "notes": "Oto-olusturuldu: Check-out temizligi",
                "status": HousekeepingStatus.PENDING,
                "reservation_id": res_id,
                "created_at": utcnow(),
                "updated_at": utcnow(),
            }
            await db.housekeeping.insert_one(log)

    return {"success": True}


@router.delete("/reservations/{res_id}")
async def delete_reservation(res_id: str):
    result = await db.reservations.delete_one({"id": res_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Rezervasyon bulunamadi")
    return {"success": True}
