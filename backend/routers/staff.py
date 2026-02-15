from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from models import StaffCreate, ShiftCreate

router = APIRouter(tags=["staff"])


@router.get("/staff")
async def list_staff():
    staff = await db.staff.find({}, {"_id": 0}).to_list(100)
    return {"staff": staff}


@router.post("/staff")
async def create_staff(data: StaffCreate):
    member = {
        "id": new_id(),
        **data.model_dump(),
        "created_at": utcnow(),
    }
    await db.staff.insert_one(member)
    return clean_doc(member)


@router.patch("/staff/{staff_id}")
async def update_staff(staff_id: str, data: dict):
    data["updated_at"] = utcnow()
    result = await db.staff.update_one({"id": staff_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(404, "Personel bulunamadi")
    return {"success": True}


@router.delete("/staff/{staff_id}")
async def delete_staff(staff_id: str):
    result = await db.staff.delete_one({"id": staff_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Personel bulunamadi")
    return {"success": True}


# ==================== SHIFTS ====================

@router.get("/shifts")
async def list_shifts(date: Optional[str] = None, staff_id: Optional[str] = None):
    query = {}
    if date:
        query["date"] = date
    if staff_id:
        query["staff_id"] = staff_id
    shifts = await db.shifts.find(query, {"_id": 0}).sort("date", -1).to_list(200)
    return {"shifts": shifts}


@router.post("/shifts")
async def create_shift(data: ShiftCreate):
    shift = {
        "id": new_id(),
        **data.model_dump(),
        "created_at": utcnow(),
    }
    await db.shifts.insert_one(shift)
    return clean_doc(shift)


@router.delete("/shifts/{shift_id}")
async def delete_shift(shift_id: str):
    result = await db.shifts.delete_one({"id": shift_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Vardiya bulunamadi")
    return {"success": True}
