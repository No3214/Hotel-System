from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from models import CampaignCreate, CampaignStatus

router = APIRouter(tags=["campaigns"])


@router.get("/campaigns")
async def list_campaigns(status: Optional[str] = None, limit: int = 50):
    query = {"status": status} if status else {}
    items = await db.campaigns.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    total = await db.campaigns.count_documents(query)
    return {"campaigns": items, "total": total}


@router.post("/campaigns")
async def create_campaign(data: CampaignCreate):
    campaign = {
        "id": new_id(),
        **data.model_dump(),
        "status": CampaignStatus.DRAFT,
        "recipients_count": 0,
        "opened_count": 0,
        "clicked_count": 0,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.campaigns.insert_one(campaign)
    return clean_doc(campaign)


@router.patch("/campaigns/{campaign_id}/status")
async def update_campaign_status(campaign_id: str, status: str):
    update = {"status": status, "updated_at": utcnow()}
    if status == CampaignStatus.SENT:
        update["sent_at"] = utcnow()
        guest_count = await db.guests.count_documents({})
        update["recipients_count"] = guest_count
    result = await db.campaigns.update_one({"id": campaign_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(404, "Kampanya bulunamadi")
    return {"success": True, "recipients": update.get("recipients_count", 0)}


@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    result = await db.campaigns.delete_one({"id": campaign_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Kampanya bulunamadi")
    return {"success": True}
