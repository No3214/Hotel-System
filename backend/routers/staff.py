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

# ==================== FAZ 19: AI AI Personel Performans ve Gisim Yoneticisi ====================

@router.get("/staff/{staff_id}/ai-performance")
async def get_ai_staff_performance(staff_id: str):
    """
    Personelin gecmis vardiyalari, departmanina atanan ve tamamlanan gorevler, 
    ve isminin gectigi misafir yorumlarini analiz ederek Gemini ile 360 derece performans degeri verir.
    """
    try:
        from datetime import datetime, timedelta
        import json
        from gemini_service import get_chat_response
        import re

        # 1. Personel bilgilerini al
        staff = await db.staff.find_one({"id": staff_id}, {"_id": 0})
        if not staff:
            raise HTTPException(404, "Personel bulunamadi")

        # Son 30 gunu hedefle
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        # 2. Son 30 gundeki vardiyalari
        shifts = await db.shifts.find({
            "staff_id": staff_id, 
            "date": {"$gte": thirty_days_ago}
        }).to_list(100)
        
        total_shifts = len([s for s in shifts if s.get("shift") != "OFF"])
        offs = len([s for s in shifts if s.get("shift") == "OFF"])

        # 3. Departmanin son 30 gundeki gorevleri (Tamamlananlar ve Bekleyenler)
        dept = staff.get("department", "")
        tasks = await db.tasks.find({
            "assignee_role": dept,
            "created_at": {"$gte": thirty_days_ago}
        }).to_list(200)

        completed_tasks = len([t for t in tasks if t.get("status") == "completed"])
        pending_tasks = len([t for t in tasks if t.get("status") == "pending"])

        # 4. Isminin gectigi yorumlar (Sadece ilk ismine de bakabilir)
        first_name = staff.get("name", "").split(" ")[0]
        reviews_mentioning = []
        if len(first_name) >= 3:
            # Case insensitive regex
            reviews_cursor = await db.reviews.find({"review_text": {"$regex": first_name, "$options": "i"}}).to_list(20)
            reviews_mentioning = [{"rating": r.get("rating"), "text": r.get("review_text")} for r in reviews_cursor]

        # 5. Gemini Prompt
        prompt = f"""
        Sen Kozbeyli Konagi'nin AI Insan Kaynaklari ve Performans Degerlendiricisisin.
        Amac: Personelin 360 derece aylik performans raporunu ve skorunu olusturmak.

        Personel Bilgileri:
        - Ad Soyad: {staff.get("name")}
        - Gorev/Departman: {staff.get("role")} / {dept}

        Son 30 Gunluk Metrikler:
        - Calistigi Vardiya Sayisi: {total_shifts}
        - İzin Kullandigi Gun Sayisi: {offs}
        - Departmaninin Tamamladigi Gorev (Task) Sayisi: {completed_tasks}
        - Departmaninin Bekleyen Gorevi: {pending_tasks}
        
        Misafir Yorumlarinda Adinin Gecmesi ({len(reviews_mentioning)} kez):
        {json.dumps(reviews_mentioning, indent=2, ensure_ascii=False) if reviews_mentioning else "Bu ay yorumlarda isminden ozel olarak bahsedilmemis."}

        Lutfen mantikli bir "Yapay Zeka Degerlendirmesi" yap ve su JSON formatinda sonuc don (Sadece JSON dondur, kod blogu icinde olsun):
        {{
            "score": 8.5,
            "summary": "1-2 cumlelik kisa, profesyonel ama cesaretlendirici yonetici ozeti.",
            "strengths": ["Girisken", "Vardiyalarina sadik"],
            "areas_of_improvement": ["Gorev tamamlama hizi artirilabilir", "Misafir yonlendirmeleri"],
            "manager_advice": "Yoneticiye bu personel hakkinda tavsiye (Ornegin: 'Odalarda daha dikkatli olmasi icin uyarilabilir' veya 'Terfi alabilir')"
        }}
        """

        ai_response = await get_chat_response(f"Performans Ozetle {staff_id}", new_id(), prompt)
        
        json_match = re.search(r'```(?:json)?(.*?)```', ai_response, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_response
        parsed_performance = json.loads(res_str)

        return {"success": True, "performance": parsed_performance}

    except Exception as e:
        return {"error": f"Performans degeri uretilemedi: {str(e)}"}

# ==================== FAZ 24: AI HR & Staff Burnout Radar ====================

@router.get("/staff/ai-hr-analytics")
async def get_ai_hr_analytics():
    """
    Tüm personelin son zamanlardaki is yukunu, vardiyalarini ve performansini 
    analiz ederek, sirket geneli bir HR(Insan Kaynaklari) Radari ve 
    Tükenmislik (Burnout) risk analizi cikarir.
    """
    try:
        from datetime import datetime, timedelta
        import json
        from gemini_service import get_chat_response
        import re

        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        # Tum aktif personeli cek
        staff_list = await db.staff.find({}, {"_id": 0}).to_list(100)
        if not staff_list:
            raise HTTPException(404, "Personel bulunamadi")

        # Son 30 gundeki tum vardiyalar
        shifts = await db.shifts.find({"date": {"$gte": thirty_days_ago}}).to_list(1000)
        
        # Son 30 gundeki tum iptal/hata kayitlari veya eksi durumlar (Eger varsa eklenecek_suan sadece vardiya uzerinden)
        
        # Personel bazinda vardiya / OFF gun dagilimi
        staff_stats = {}
        for s in staff_list:
            s_id = s.get("id")
            s_shifts = [sh for sh in shifts if sh.get("staff_id") == s_id]
            worked_days = len([sh for sh in s_shifts if sh.get("shift") != "OFF"])
            off_days = len([sh for sh in s_shifts if sh.get("shift") == "OFF"])
            
            staff_stats[s.get("name")] = {
                "department": s.get("department"),
                "worked_days_last_30": worked_days,
                "off_days_last_30": off_days,
                "overwork_flag": worked_days > 24 # Haftada maks 6 gun calismali, ayda 24.
            }

        prompt = f"""
        Sen Kozbeyli Konagi'nin 'Yapay Zeka Insan Kaynaklari (HR) Direktoru'sun.
        Asagida tüm otel personelinin son 30 gunluk is yuku, calistigi gunler ve izin (OFF) günleri listelenmistir:
        
        {json.dumps(staff_stats, ensure_ascii=False, indent=2)}

        Gorevin, bu verileri inceleyip otel geneli icin derinlemesine bir HR ve 'Tükenmişlik (Burnout) Radarı' cikarmak.

        Senden beklenenler:
        1. "Genel HR Saglik Skoru (hr_health_score)": 0-100 arasi puan ver.
        2. "Risk Altindaki Personeller (burnout_risks)": Ayda 24 günden fazla calisan veya hic/az izin yapan personeli tespit et. (Eger kimse yoksa bos liste don)
        3. "Is Yuku Dengesizlikleri (workload_imbalance)": Hangi departmanda kriz var veya daha fazla ise alim yapilmasi gerekebilir.
        4. "Motivasyon Onerileri (motivation_actions)": Risk altindaki personeller icin yoneticiye tek cümlelik nokta atisi tavsiyeler (Orn: 'Ahmet beye hafta sonu 2 gun ust uste izin yazin, performans dususu muhtemel').

        Lutfen SADECE asagidaki JSON formatinda cevap don, baska hiçbir metin ekleme:
        {{
          "hr_health_score": 80,
          "summary": "Genel olarak is yuku dengeli ancak resepsiyonda mesailer cok katilasmis...",
          "burnout_risks": [
            {{"staff_name": "Ali Veli", "department": "reception", "risk_level": "high", "reason": "Son 30 gunde 28 gun calismis."}}
          ],
          "workload_imbalance": "Housekeeping departmaninda kisi basina dusen calisma gunu sirket ortalamasinin cok uzerinde. 1 yeni personel gerekebilir.",
          "motivation_actions": [
            {{"target": "Ali Veli", "action": "Derhal 2 gun ucretli/ucretsiz izin girisi yapilmali."}}
          ]
        }}
        """

        ai_response = await get_chat_response("HR Analytics", new_id(), prompt)
        
        json_match = re.search(r'```(?:json)?(.*?)```', ai_response, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_response
        hr_report = json.loads(res_str)

        return {"success": True, "report": hr_report}

    except Exception as e:
        return {"error": f"HR Radari hesaplanamadi: {str(e)}"}
