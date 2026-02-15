from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc
from models import EventCreate

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
