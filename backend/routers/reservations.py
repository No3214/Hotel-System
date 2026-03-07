from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from models import ReservationCreate, ReservationUpdate, ReservationStatus, HousekeepingStatus
import json
from gemini_service import get_chat_response

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


# ==================== PHASE 11: AI SMART ROOM ALLOCATION ====================

@router.post("/reservations/ai-allocation")
async def ai_smart_room_allocation():
    """
    Oda tipi belli olan ama spesifik oda numarası atanmamış yaklaşan rezervasyonları,
    misafir geçmişine ve taleplerine göre boş odalarla eşleştirir.
    *HotelRunner ile çakışmaması için sadece 'room_id' (spesifik oda no) boş olanlara işlem yapar.
    """
    try:
        now_str = utcnow()[:10]
        
        # 1. Bekleyen ve oda numarasi atanmamis (sadece tipi belli) rezervasyonlari bul
        # HotelRunner'dan gelen ve odası belli olan dokunulmaz.
        unassigned_res = await db.reservations.find({
            "status": {"$in": ["confirmed", "new"]},
            "check_in": {"$gte": now_str},
            "$or": [{"room_id": None}, {"room_id": ""}, {"room_id": {"$exists": False}}]
        }, {"_id": 0}).to_list(100)
        
        if not unassigned_res:
             # Test/Eğitim amaçlı mock data ekle eğer boşsa
             unassigned_res = [
                 {"id": "RES1", "guest_name": "Ahmet Yilmaz", "room_type": "Standart Oda", "notes": "65 yasindayim, merdiven cikamiyorum.", "adults": 2},
                 {"id": "RES2", "guest_name": "Ayse Demir", "room_type": "Suit Oda", "notes": "Balayi ciftiyiz, guzel manzarali olsun.", "adults": 2}
             ]

        # 2. Temiz/Bos odalari bul
        available_rooms = await db.rooms.find({"status": "available"}, {"_id": 0, "id": 1, "floor": 1, "type": 1, "features": 1, "name_tr": 1}).to_list(100)
        
        if not available_rooms:
             available_rooms = [
                 {"id": "101", "name_tr": "101", "type": "Standart Oda", "floor": "Zemin Floor", "features": ["Engelli Uyumlu", "Kolay Erisim"]},
                 {"id": "102", "name_tr": "102", "type": "Standart Oda", "floor": "1. Kat", "features": ["Deniz Manzarali"]},
                 {"id": "304", "name_tr": "304", "type": "Suit Oda", "floor": "3. Kat", "features": ["Teras", "Deniz Manzarasi", "Jakuzi"]}
             ]

        prompt = f"""
        Sen Kozbeyli Konagi'nin AI Rezervasyon ve Tahsis uzmanisin.
        Gorevin, asagidaki oda numarasi HENUZ ATANMAMIS rezervasyonlari,
        asagidaki BOS ODALAR listesindeki en uygun odalarla 'misafir notlari ve oda ozelliklerini' mantikli sekilde karsilastirarak eslestirmek.
        
        Atanmamis Rezervasyonlar:
        {json.dumps(unassigned_res, ensure_ascii=False, indent=2)}
        
        Bos Odalar:
        {json.dumps(available_rooms, ensure_ascii=False, indent=2)}
        
        Kurallar:
        1. Rezervasyonun sectigi oda tipi (room_type) ile odanin tipi ayni veya ust segment olmali.
        2. Misafir yasli/engelli ise zemin veya kolay erisimli odayi sec. Manzara istiyorsa ona gore sec.
        3. Bir odayi sadece bir rezervasyona ata.
        
        Sadece JSON dondur:
        {{
           "allocations": [
              {{"reservation_id": "RES1", "room_id": "101", "guest_name": "Ahmet Y.", "reason": "Misafir merdiven cikamiyor, zemin kat daha uygun."}}
           ]
        }}
        """

        ai_resp = await get_chat_response("reservations", new_id(), prompt)
        
        import re
        json_match = re.search(r'```(?:json)?(.*?)```', ai_resp, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_resp
        allocation_data = json.loads(res_str)
        
        # Atamalari veritabanina yansit
        applied_count = 0
        for alloc in allocation_data.get("allocations", []):
            res_id = alloc.get("reservation_id")
            room_id = alloc.get("room_id")
            if res_id and room_id and not res_id.startswith("RES"): # mockedlari atla
               result = await db.reservations.update_one(
                   {"id": res_id},
                   {"$set": {"room_id": room_id, "ai_allocation_reason": alloc.get("reason")}}
               )
               if result.modified_count > 0:
                   applied_count += 1
                   # Odanın durumunu dolu yapma, çunku check-in olmadi, sadece tahsis edildi.
                   # Opsiyonel olarak oda üzerinde 'reserved' state tutulabilir.

        return {
            "success": True, 
            "allocations": allocation_data.get("allocations", []),
            "applied_count": applied_count,
            "message": "AI tahsisleri basariyla uretildi ve uygun olanlar sisteme kaydedildi."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Oda tahsis hatasi: {str(e)}")

# ==================== PHASE 14: AI DYNAMIC UPSELL ENGINE ====================

@router.get("/reservations/{res_id}/ai-upsell")
async def ai_dynamic_upsell(res_id: str):
    """
    Misafirin rezervasyon detaylarina ve varsa gecmisine bakarak,
    o an satilma ihtimali en yuksek olan (En kârli) 3 ekstra servisi onerir.
    Bunu resepsiyoniste veya satis ekibine "Satış Kancası" (pitch) ile sunar.
    """
    try:
        res = await db.reservations.find_one({"id": res_id}, {"_id": 0})
        if not res:
            res = {
                "guest_name": "Demo Misafir",
                "room_type": "Standart Oda",
                "adults": 2,
                "children": 0,
                "stay_duration_days": 3,
                "notes": "Yildonumu icin geliyorlar."
            }
        
        prompt = f"""
        Sen luks bir butik otelin 'Yapay Zeka Upsell (Capraz Satis) Asistani'sin.
        Gorevin, resepsiyoniste veya satis ekibine, asagidaki misafir otele giris yaparken 
        veya konaklarken 'NE SATILIRSAYSA KABUL ETME IHTIMALI EN YUKSEK OLUR' sorusunun cevabini vermek.

        Misafir ve Rezervasyon Profili:
        {json.dumps(res, ensure_ascii=False, indent=2)}

        Sistemimizde sunulan baz ekstra servisler: Odaya Sarap/Meyve Sepeti, Romantik Aksam Yemegi,
        Spa/Masaj Paketi, Gec Cikis (Late Checkout), Havalimani VIP Transfer, Ustu Acik Arac Kiralama, VIP Tekne Turu.

        Bu misafire ozel en uygun 3 UPSELL urununu sec, tahmini donusum/kabul oranini (% olarak) belirle
        ve resepsiyonistin bu urunu satarken kullanacagi 'Sihirli Cumleyi (Pitch)' yaz.

        SADECE JSON FORMATINDA DONDUR:
        {{
            "upsell_opportunities": [
                {{
                    "item": "Odaya Premium Kirmizi Sarap ve Cikolata",
                    "probability_percent": 85,
                    "pitch": "Ahmet Bey, yildonumunuzu kutlarim! Eger dilerseniz bu ozel gununuzu taclandirmak adina odaniza ozel sarap ve el yapimi cikolata servisimiz var, yalnizca X TL'ye ekleyebiliriz?",
                    "estimated_revenue_try": 1500
                }}
            ]
        }}
        """

        ai_resp = await get_chat_response("reservations", f"upsell_{res_id}", prompt)
        
        import re
        json_match = re.search(r'```(?:json)?(.*?)```', ai_resp, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_resp
        upsell_data = json.loads(res_str)

        return {
            "success": True,
            "suggestions": upsell_data.get("upsell_opportunities", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Upsell Motoru hatasi: {str(e)}")

# ==================== FAZ 25: AI HYPER-PERSONALIZED GUEST JOURNEY ====================

@router.get("/reservations/ai-guest-journey")
async def get_ai_guest_journey():
    """
    Onumuzdeki 3 gun icinde giris yapacak misafirleri analiz eder.
    Her biri icin ozel bir SMS/WhatsApp karsilama mesaji ve 
    odaya ozel ikram (welcome package) hazirlar.
    """
    try:
        from datetime import datetime, timedelta
        import json
        from gemini_service import get_chat_response
        import re

        now = datetime.now()
        start_date = now.strftime("%Y-%m-%d")
        end_date = (now + timedelta(days=3)).strftime("%Y-%m-%d")

        # 1. Onumuzdeki 3 gn icinde check-in yapacak onayli rezervasyonlar
        arriving = await db.reservations.find({
            "check_in": {"$gte": start_date, "$lte": end_date},
            "status": "confirmed"
        }, {"_id": 0, "id": 1, "guest_name": 1, "room_type": 1, "adults": 1, "children": 1, "notes": 1, "check_in": 1, "stay_duration_days": 1}).to_list(50)

        if not arriving:
            return {"success": True, "message": f"{start_date} ile {end_date} arasinda gelecek misafir bulunamadi."}

        prompt = f"""
        Sen Kozbeyli Konagi'nin 'Yapay Zeka Misafir Iliskileri (CRM) Muduru'sun.
        Gorevin, onumuzdeki 3 gun icinde otelimize giris (check-in) yapacak misafirleri agirliyoruz.
        Onlara siradan bir hizmet degil, "Hyper-Personalized" (ultra kisisellestirilmis) bir deneyim vermeliyiz.

        Asagida gelen misafirlerin listesi var:
        {json.dumps(arriving, ensure_ascii=False, indent=2)}

        Her bir misafir icin sunlari uret:
        1. "Odaya Bırakılacak Karsilama Hediyesi (welcome_package)": Misafirin yapisina (cocuklu mu, notlarinda ne yaziyor vb.) gore zekice bir jest. 
           (Orn: Notta 'Yildonumu' yaziyorsa 'Odaya sarap ve kalpli cikolata, yataga kugu havlu', cocukluysa 'Odaya oyuncak ayi ve sut/kurabiye').
        2. "Misafire Giris Gunu Gonderilecek WhatsApp Mesaji (sms_text)": Sicak, kurumsal ama samimi ve misafirin ismine, durumuna ozel 1 paragraflik "Hos geldiniz" mesaji icinde minik bir Upsell (Oda servisi veya Spa daveti) da barindirsin.

        Lutfen SADECE JSON dondur. Array icinde obje formatinda olsun:
        {{
           "journeys": [
               {{
                  "reservation_id": "string",
                  "guest_name": "string",
                  "welcome_package": "string (Aksiyon talimati)",
                  "sms_text": "string (Gonderilecek metin)"
               }}
           ]
        }}
        """

        ai_response = await get_chat_response("CRM Guest Journey", new_id(), prompt)
        
        json_match = re.search(r'```(?:json)?(.*?)```', ai_response, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_response
        journey_data = json.loads(res_str)

        return {"success": True, "data": journey_data.get("journeys", [])}

    except Exception as e:
        return {"error": f"Guest Journey uretilemedi: {str(e)}"}
