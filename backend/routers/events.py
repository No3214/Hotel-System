from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from models import EventCreate
import json
from gemini_service import get_chat_response

router = APIRouter(tags=["events"])


@router.get("/events")
async def list_events(active_only: bool = False):
    query = {"is_active": True} if active_only else {}
    events = await db.events.find(query, {"_id": 0}).sort("event_date", 1).to_list(100)
    return {"events": events}


@router.post("/events")
async def create_event(data: EventCreate):
    event = {
        "id": new_id(),
        **data.model_dump(),
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "registrations": 0,
    }
    await db.events.insert_one(event)
    return clean_doc(event)


@router.patch("/events/{event_id}")
async def update_event(event_id: str, data: dict):
    data["updated_at"] = utcnow()
    result = await db.events.update_one({"id": event_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(404, "Etkinlik bulunamadi")
    return {"success": True}


@router.delete("/events/{event_id}")
async def delete_event(event_id: str):
    result = await db.events.delete_one({"id": event_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Etkinlik bulunamadi")
    return {"success": True}


@router.post("/events/seed-samples")
async def seed_sample_events():
    """Ornek etkinlikleri yukle"""
    sample_events = [
        {
            "id": new_id(),
            "title": "Canli Muzik - Ece Yazar",
            "description": "Kozbeyli Konagi'nda canli muzik gecesi. Ece Yazar sahne alacak. Fix Menu: Antakya'dan Zahter, Mezeler (Havuc Tarator, Visneli Yaprak Sarma, Antakya Biberli Atom, Deniz Borulcesi), Roka Salatasi, Pastirmali Kasarli Pacanga Boregi, Konak Kofte (200g) veya Konak Sac Kavurma (150g), Antep Fistikli Kaymakli Kunefe.",
            "event_type": "live_music",
            "event_date": "2026-02-07",
            "start_time": "20:30",
            "end_time": "23:59",
            "capacity": 60,
            "price_per_person": 2750,
            "is_active": True,
            "artist": "Ece Yazar",
            "menu_type": "fix_menu",
            "menu_details": {
                "baslangiclar": ["Antakya'dan Zahter", "Koy Usulu Kirma Yesil Zeytin ve Soguk Sikim Zeytinyagi"],
                "mezeler": ["Havuc Tarator", "Visneli Yaprak Sarma", "Antakya Biberli Atom", "Zeytinyagi & Domatesli Deniz Borulcesi"],
                "salata": "Roka Salatasi (Kuru Incir, Ezine Peyniri, Ceviz, Balsamic Glaze Sos)",
                "ara_sicak": "Pastirmali Kars Kasarli Pacanga Boregi",
                "ana_yemek": "Konak Kofte (200g) veya Konak Sac Kavurma (150g) - Patates Puresi Tabani, Biberiye ve Kavrulmus File Badem ile",
                "tatli": "Antep Fistikli Kaymakli Kunefe",
                "icki_secenekleri": {
                    "alkolu_menu": "35cl Raki (Efe Gold/Beylerbeyi Mavi) veya 70cl Kirmizi Sarap",
                    "sinirsiz_menu": "70cl Raki veya 2 Adet 70cl Kirmizi Sarap"
                }
            },
            "pricing": {
                "alkolu_menu": 2750,
                "sinirsiz_alkolu_menu": 5500
            },
            "cover_image": "https://customer-assets.emergentagent.com/job_eefe8292-3bc3-43c2-a988-596565102f4c/artifacts/wezbaewp_image.png",
            "created_at": utcnow(),
            "updated_at": utcnow(),
            "registrations": 0,
        },
        {
            "id": new_id(),
            "title": "Sevgililer Gunu - GORAY Akustik",
            "description": "Kozbeyli Konagi'nda Sevgililer Gunu ozel aksam yemegi ve akustik canli muzik. Sanatci: GORAY. Ozel menu: Antakya'dan Zahter, Mezeler (Humus, Visneli Yaprak Sarma, Antakya Biberli Atom, Deniz Borulcesi), Roka Salatasi, Pastirmali Kasarli Pacanga Boregi, Konak Kofte veya Konak Sac Kavurma, Kunefe. Kontenjan sinirlidir!",
            "event_type": "special_dinner",
            "event_date": "2026-02-14",
            "start_time": "20:30",
            "end_time": "23:59",
            "capacity": 40,
            "price_per_person": 3500,
            "is_active": True,
            "artist": "GORAY",
            "menu_type": "sevgililer_gunu_menu",
            "menu_details": {
                "baslangiclar": ["Antakya'dan Zahter", "Koy Usulu Kirma Yesil Zeytin ve Soguk Sikim Zeytinyagi"],
                "mezeler": ["Humus", "Visneli Yaprak Sarma", "Antakya Biberli Atom", "Zeytinyagi & Domatesli Deniz Borulcesi"],
                "salata": "Roka Salatasi (Kuru Incir, Ezine Peyniri, Ceviz, Balsamic Glaze Sos)",
                "ara_sicak": "Pastirmali Kasarli Pacanga Boregi",
                "ana_yemek": "Konak Kofte (200g) veya Konak Sac Kavurma (150g) - Patates Puresi Tabani, Biberiye ve Kavrulmus File Badem ile",
                "tatli": "Antep Fistikli Kaymakli Kunefe",
                "icki_secenekleri": {
                    "alkolu_menu": "2x 35cl Raki (Efe Gold/Beylerbeyi Mavi) veya 70cl Kirmizi Sarap",
                    "sinirsiz_menu": "2x 70cl Raki veya 2 Adet 70cl Kirmizi Sarap"
                }
            },
            "pricing": {
                "alkolu_menu": 3500,
                "sinirsiz_alkolu_menu": 6000
            },
            "cover_image": "https://customer-assets.emergentagent.com/job_eefe8292-3bc3-43c2-a988-596565102f4c/artifacts/ufyjexba_image.png",
            "created_at": utcnow(),
            "updated_at": utcnow(),
            "registrations": 0,
        },
    ]

    inserted = 0
    for event in sample_events:
        existing = await db.events.find_one({"title": event["title"]})
        if not existing:
            await db.events.insert_one(event)
            inserted += 1

    return {"success": True, "inserted": inserted, "total_samples": len(sample_events)}

# ==================== PHASE 14: AI EVENT PLANNER ====================

@router.post("/events/ai-planner")
async def ai_event_planner(plan_params: dict):
    """
    Parametreler: event_type, headcount, budget_level (low/med/high), special_requests
    Otel icin (dugun, toplanti, yoga kampi vb.) detayli saatlik akis, menu onerisi ve personel tahmini uretir.
    """
    event_type = plan_params.get("event_type", "Kurumsal Toplanti")
    headcount = plan_params.get("headcount", 50)
    budget = plan_params.get("budget_level", "medium")
    special = plan_params.get("special_requests", "")

    try:
        prompt = f"""
        Sen luks bir butik otelin (Kozbeyli Konagi) Bas Etkinlik ve Ziyafet Planlayicisisin (AI Event Planner).
        Musteri soyle bir etkinlik talebinde bulundu:
        - Etkinlik Tipi: {event_type}
        - Kisi Sayisi: {headcount}
        - Butce Seviyesi: {budget}
        - Ozel Istekler: {special}

        Gorevin, bu parametrelere uygun, satisi kapatacak kadar estetik, detayli ve gercekci bir etkinlik plani sunmak.
        SADECE JSON FORMATINDA dondur:
        {{
           "event_title": "...",
           "theme_concept": "...",
           "recommended_menu": [
              {{"course": "Baslangic", "item": "..."}},
              {{"course": "Ana Yemek", "item": "..."}}
           ],
           "schedule": [
              {{"time": "14:00", "activity": "Karsilama ve Hosgeldin Kokteyli"}},
              {{"time": "15:00", "activity": "..."}}
           ],
           "staff_requirements": "Orn: 3 Garson, 1 Sef, 1 Etkinlik Yoneticisi",
           "estimated_cost_try": 25000,
           "ai_advice": "Satisi kapatmak icin musteriye sunulacak ozel bir jest veya tavsiye"
        }}
        """
        ai_resp = await get_chat_response("events", f"plan_{headcount}", prompt)
        
        import re
        json_match = re.search(r'```(?:json)?(.*?)```', ai_resp, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_resp
        plan_data = json.loads(res_str)

        return {
            "success": True,
            "plan": plan_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Event Planner hatasi: {str(e)}")
