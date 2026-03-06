from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from database import db
from helpers import utcnow, new_id, clean_doc
from models import HousekeepingCreate, HousekeepingStatus, ReservationStatus
from gemini_service import get_chat_response
import json

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
        existing = await db.housekeeping.find_one({
            "room_number": res.get("room_type", ""),
            "status": {"$in": [HousekeepingStatus.PENDING, HousekeepingStatus.IN_PROGRESS]},
        })
        if not existing:
            log = {
                "id": new_id(),
                "room_number": res.get("room_type", "unknown"),
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

@router.get("/housekeeping/ai-routing")
async def get_ai_routing():
    """Gemini ile Kat Hizmetleri Rota Optimizasyonu"""
    
    # Bekleyen gorevleri cek
    pending_tasks = await db.housekeeping.find(
        {"status": {"$in": [HousekeepingStatus.PENDING, HousekeepingStatus.IN_PROGRESS]}}, 
        {"_id": 0}
    ).to_list(100)
    
    if not pending_tasks:
        return {"success": True, "routing": {"plan_name": "Rutin Kontrol", "summary": "Su an bekleyen acil temizlik gorevi bulunmuyor. Genel alan kontrolleri yapilabilir.", "optimized_route": []}}
    
    # Ozetle
    context = "SU ANKI TEMIZLIK BEKLEYEN ODALAR VE GOREVLER:\n"
    for t in pending_tasks:
        context += f"- Oda: {t.get('room_number', '?')} | Tur: {t.get('task_type', '')} | Not: {t.get('notes', '')}\n"
        
    system_prompt = """
    Sen Kozbeyli Konagi'nin Kat Hizmetleri Sefisin (Housekeeping AI).
    Onundeki temizlik listesini en optimize sekilde siralaman gerekiyor. 
    Genel kurallar:
    1. Check-out (checkout_clean) odalar onceliklidir.
    2. Ayni kattaki/yan yanaki odalari pes pese sirala (Orn: 101, 102, 103).
    3. Normal temizlikler (standard_clean) daha az onceliklidir.
    
    Senden sadece asagidaki JSON formatinda sonuc uretmeni istiyorum:
    {
      "plan_name": "Sabah Hizli Plan",
      "summary": "Bu rotayi neden sectigini kisaca acikla (2 cumle)",
      "optimized_route": [
        {"room_number": "101", "task": "Check-out Temizligi", "reason": "Yeni misafir girisi ihtimaline karsi en oncelikli", "estimated_mins": 30},
        {"room_number": "102", "task": "Standart Temizlik", "reason": "Ayni koridorda oldugu icin pesine eklendi", "estimated_mins": 15}
      ]
    }
    """
    
    try:
        response_text = await get_chat_response(
            message="Bekleyen gorevleri sirala ve optimize bir rota ver.",
            session_id=new_id(),
            system_prompt=system_prompt,
            context=context
        )
        clean_json = response_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        return {"success": True, "routing": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Rotalama hatasi: {str(e)}")
