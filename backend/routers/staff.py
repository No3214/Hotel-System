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


# ==================== FAZ 5: AI Smart Shift Manager ====================

@router.get("/staff/ai-shifts")
async def generate_ai_shifts(start_date: str):
    """
    Belirtilen haftanin (start_date) yogunlugunu tahmin ederek
    yapay zeka (Gemini) tabanli optimum personel vardiya cizelgesi olustur.
    HotelRunner'da OLMAYAN, tamamen otel ici operasyona yonelik bir zekadir.
    """
    try:
        from datetime import datetime, timedelta
        import json
        import logging
        from gemini_service import get_chat_response
        
        logger = logging.getLogger(__name__)
        
        # 1. 7 gunluk tarih araligini belirle
        start = datetime.fromisoformat(start_date[:10])
        end = start + timedelta(days=7)
        end_str = end.strftime("%Y-%m-%d")
        
        # 2. Gelecek hafta icin beklenen yogunluk (Rezervasyonlar)
        upcoming_res = await db.reservations.find({
            "check_in": {"$lte": end_str},
            "check_out": {"$gte": start_date},
            "status": {"$in": ["confirmed", "checked_in"]}
        }).to_list(100)
        
        # 3. Gelecek haftaki etkinlikler (Dugun, toplanti vb.)
        upcoming_events = await db.events.find({
            "date": {"$gte": start_date, "$lt": end_str}
        }).to_list(100)
        
        # 4. Aktif Personel Listesi
        staff_list = await db.staff.find({}, {"_id": 0}).to_list(100)
        if not staff_list:
            return {"error": "Personel bulunamadi, vardiya uretilemez."}
            
        staff_summary = [{"id": s.get("id"), "name": s.get("name"), "role": s.get("role"), "department": s.get("department")} for s in staff_list]
        
        # Ozet metinler
        res_summary = f"Bu hafta {len(upcoming_res)} oda rezervasyonu bekleniyor."
        event_summary = f"Bu hafta {len(upcoming_events)} etkinlik (dugun/toplanti vb.) var."
        if upcoming_events:
            event_summary += " Etkinlik tarihleri: " + ", ".join([e.get("date", "") for e in upcoming_events])
            
        prompt = f"""
        Sen Kozbeyli Konagi'nin AI Insan Kaynaklari ve Operasyon yoneticisisin.
        Amac: Gelecek 1 hafta icin {start_date} ile {end_str} arasinda optimum personel vardiyasini yazmak.
        
        Durum:
        - {res_summary}
        - {event_summary}
        
        Personel Listesi:
        {json.dumps(staff_summary, indent=2)}
        
        Kural: 
        - Resepsiyonist 7/24 olmali (Sabah 08:00-16:00, Aksam 16:00-00:00, Gece 00:00-08:00).
        - Temizlik personeli check-out'larin yogun oldugu gunlere odaklanmali.
        - Etkinlik olan gunler mutfak ve garson sayisi artirilmali.
        - Her personele insani sekilde 1 veya 2 gun haftalik izin yazilmalidir (Vardiya saati: 'OFF' olacak).
        
        Bana sadece asagidaki JSON formatinda sonuc don. (Markdown icinde)
        [
          {{
            "staff_id": "string",
            "staff_name": "string",
            "date": "YYYY-MM-DD",
            "shift": "08:00 - 16:00" | "OFF" | "Diger",
            "reason": "Yapay zekanin bu vardiyayi yazma sebebi (Orn: Dugun oldugu icin gunduz destek, veya haftalik izin)"
          }}, ...
        ]
        """
        
        ai_response = await get_chat_response("Vardiya uret", new_id(), prompt)
        
        import re
        json_match = re.search(r'```(?:json)?(.*?)```', ai_response, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_response
        parsed_shifts = json.loads(res_str)
        
        # Olusturulan vardiyalari gecici bir id ile don
        for sh in parsed_shifts:
            sh["id"] = new_id()
            
        return {
            "ai_shifts": parsed_shifts,
            "analysis": f"{res_summary} {event_summary} Bu veriler isiginda optimum vardiya dagilimi AI ile hazirlandi."
        }
        
    except Exception as e:
        return {"error": str(e)}
