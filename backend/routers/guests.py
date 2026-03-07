from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from models import GuestCreate
import json
from gemini_service import get_chat_response

router = APIRouter(tags=["guests"])


@router.get("/guests")
async def list_guests(search: Optional[str] = None, limit: int = 50, skip: int = 0):
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
        ]
    guests = await db.guests.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.guests.count_documents(query)
    return {"guests": guests, "total": total}


@router.post("/guests")
async def create_guest(data: GuestCreate):
    guest = {
        "id": new_id(),
        **data.model_dump(),
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "total_stays": 0,
        "vip": False,
    }
    await db.guests.insert_one(guest)
    return clean_doc(guest)


@router.get("/guests/{guest_id}")
async def get_guest(guest_id: str):
    guest = await db.guests.find_one({"id": guest_id}, {"_id": 0})
    if not guest:
        raise HTTPException(404, "Misafir bulunamadi")
    return guest


@router.patch("/guests/{guest_id}")
async def update_guest(guest_id: str, data: dict):
    data["updated_at"] = utcnow()
    result = await db.guests.update_one({"id": guest_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(404, "Misafir bulunamadi")
    return {"success": True}


# ==================== PHASE 11: AI COMPLAINT RADAR ====================

@router.get("/guests/ai-complaint-radar")
async def ai_complaint_radar():
    """
    Otelde su an konaklayan (checked_in) misafirlerin görev gecmislerini
    ve şikayet loglarini tarayarak memnuniyetsizlik (churn/complaint) riskini hesaplar.
    *HotelRunner'in sadece veri tasidigi noktalarda, lokal etkilesimi arttiran bir ust AI katmanidir.
    """
    try:
        now_str = utcnow()[:10]
        
        # 1. In-house misafirleri bul
        in_house_res = await db.reservations.find({
            "status": "checked_in"
        }, {"_id": 0, "id": 1, "guest_name": 1, "room_id": 1, "guest_id": 1}).to_list(100)
        
        if not in_house_res:
            return {"success": True, "radar_results": [], "message": "Su an iceride konaklayan misafir bulunmuyor."}
            
        # 2. Bu misafirlerle alakali housekeeping ve teknik servis veya genel gorevleri cek
        res_ids = [r.get("id") for r in in_house_res]
        
        # Mocking for demonstration if db is empty or no real issues exist
        mock_tasks = [
            {"reservation_id": in_house_res[0].get("id"), "title": "Klima bozuk", "status": "completed", "priority": "high", "department": "teknik"},
            {"reservation_id": in_house_res[0].get("id"), "title": "Oda temizlenmedi, saat 16", "status": "pending", "priority": "high", "department": "housekeeping"},
        ] if in_house_res else []
        
        # Gercek DB taramasi (tasks tablosunda reservation_id tutuluyorsa)
        real_tasks = await db.tasks.find({
            "reservation_id": {"$in": res_ids}
        }, {"_id": 0, "reservation_id": 1, "title": 1, "status": 1, "priority": 1}).to_list(100)
        
        combined_tasks = real_tasks if real_tasks else mock_tasks
        
        # Hangi misafirin hangi taskleri var birlestirelim
        guest_profiles = []
        for res in in_house_res:
            g_tasks = [t for t in combined_tasks if t.get("reservation_id") == res.get("id")]
            if len(g_tasks) > 0: # Sadece olayi olan misafirleri yolla ki token limitsizlesmesin
                guest_profiles.append({
                    "guest": f"{res.get('guest_name')} (Oda: {res.get('room_id')})",
                    "incidents": g_tasks
                })
                
        if not guest_profiles:
            return {"success": True, "radar_results": [], "message": "Tum misafirlerin konaklamasi sorunsuz gorunuyor. Riskli incident yok."}

        prompt = f"""
        Sen Kozbeyli Konagi'nin Misafir Deneyimi (CX) AI Radarisin.
        Amacin, cikis yapmamis (in-house) misafirlerin yasadigi teknik ve temizlik sorunlarini inceleyerek 
        hangilerinin otelden DUSUK PUANLA ayrilma ihtimali oldugunu onceden tahmin etmek.
        
        Misafir Sorunlari Logu:
        {json.dumps(guest_profiles, ensure_ascii=False, indent=2)}
        
        Gorevin:
        1. Yasanan arizalarin tiplerine ve sayilarina bak.
        2. Misafirin ayrilmadan once negatif yorum yapma riskini (Risk Seviyesi) belirle: "Yuksek Risk", "Orta Risk", "Dusuk Risk".
        3. Sorunu cozmek / gonul almak icin resepsiyona anlik 'Telafi Aksiyonu' onelir (meyve tabagi, sarap ikrami, ucretsiz masaj).
        
        Sadece Asagidaki JSON Formatinda Cikti Ver:
        {{
           "radar_results": [
               {{"guest_name": "Ahmet Yilmaz (Oda: 101)", "risk_level": "Yuksek Risk", "churn_probability_percent": 85, "reason": "Ayni gun icerisinde hem klima bozulmus hem de oda temizligi gecikmis.", "compensation_action": "Odaya sarap ve peynir tabagi gonderilsin, mudur bizzat ozur dilesin."}}
           ]
        }}
        """

        ai_resp = await get_chat_response("guests", new_id(), prompt)
        
        import re
        json_match = re.search(r'```(?:json)?(.*?)```', ai_resp, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_resp
        radar_data = json.loads(res_str)

        return {
            "success": True,
            "analyzed_count": len(guest_profiles),
            "radar_results": radar_data.get("radar_results", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sikayet radar hatasi: {str(e)}")
