from fastapi import APIRouter
from typing import Optional
from database import db
from helpers import utcnow, new_id
from hotel_data import HOTEL_INFO

router = APIRouter(tags=["lifecycle"])

# Misafir yaşam döngüsü mesaj şablonları
MESSAGE_TEMPLATES = {
    "booking_confirmation": {
        "tr": """Sayin {guest_name},

Kozbeyli Konagi'nda {check_in} - {check_out} tarihleri arasindaki rezervasyonunuz onaylanmistir.

Oda: {room_type}
Kisi: {guests_count}
Tutar: {total_price} TL

Check-in: 14:00 | Check-out: 12:00

Banka Bilgileri (On Odeme):
Yapi Kredi - TR72 0006 7010 0000 0025 0736 77
Hesap Sahibi: Varol Oruk
*Dekont gondermeyi unutmayin*

Kozbeyli Koyu, Foca/Izmir
{hotel_phone}

Sizi agirlamak icin sabrsizlaniyoruz!""",
    },
    "pre_arrival": {
        "tr": """Sayin {guest_name},

Yarin sizi Kozbeyli Konagi'nda agirliyoruz!

Check-in: 14:00'den itibaren
Adres: Kozbeyli Koyu Kume Evleri No:188, 35680 Foca/Izmir
Google Maps: maps.google.com/?q=38.7333,26.7667

Yol tarifi: Izmir-Foca yolundan Kozbeyli tabelasini takip edin.

WiFi: Konakta ucretsiz WiFi mevcuttur.
Otopark: Ucretsiz acik otopark.
Kahvalti: 08:30-11:00 (organik koy kahvaltisi dahil)

Soru icin: {hotel_phone}

Gorusme k!""",
    },
    "welcome_checkin": {
        "tr": """Hos geldiniz {guest_name}!

Kozbeyli Konagi'na hosgeldiniz. Konaklama suresince ihtiyaciniz olan her sey icin bize ulasabilirsiniz.

WiFi Sifresi: KozbeyliKonagi2026
Restoran: 08:30-23:00 (Mutfak 22:00'de kapanir)
Resepsiyon: 08:00-00:00
Sessiz saatler: 23:00-08:00

Oneriler:
- Mersinaki Koyu (8 km) - Muhtesem plaj
- Foca Kalesi - Tarihi gezinti
- Aksam restoran bahcemizde mumlarin esliginde yemek

Keyifli bir konaklama dileriz!
{hotel_phone}""",
    },
    "during_stay_day2": {
        "tr": """Sayin {guest_name},

Konaklamaniz nasil gidiyor? Umariz keyif aliyorsunuz!

Bugunun onerisi:
- Tekne turu: Foca adalari (3-4 saat)
- Restoran ozel menumuz: Dallas Steak (3500 TL)

Restoran masa rezervasyonu icin resepsiyona bilgi verebilirsiniz.

Herhangi bir istginiz veya oneriniz olursa, lutfen cekinmeden bize ulasin.
{hotel_phone}""",
    },
    "checkout_thankyou": {
        "tr": """Sayin {guest_name},

Kozbeyli Konagi'nda sizi agirlama firsati bulduğumuz icin tesekkur ederiz!

Size kucuk bir ricamiz var: Google veya TripAdvisor'da deneyiminizi paylasmaniz bizi cok mutlu eder.

Google: g.page/kozbeylikonagi/review
TripAdvisor: tripadvisor.com/kozbeylikonagi

Sizi tekrar agirlamak dilegiyle,
Kozbeyli Konagi Ailesi
{hotel_phone}""",
    },
    "post_stay_followup": {
        "tr": """Sayin {guest_name},

Kozbeyli Konagi'ndaki konaklamanizdan bu yana 1 hafta oldu. Umariz guzel anilarla donmussinuzdur.

Size ozel %10 indirimli tekrar konaklama firsatimiz var! Kod: TEKRAR10

Rezervasyon: {hotel_phone}

Sevgilerle,
Kozbeyli Konagi""",
    },
}


@router.get("/lifecycle/templates")
async def list_templates():
    templates = []
    for key, langs in MESSAGE_TEMPLATES.items():
        templates.append({
            "key": key,
            "name": key.replace("_", " ").title(),
            "content": langs.get("tr", ""),
            "variables": _extract_variables(langs.get("tr", "")),
        })
    return {"templates": templates}


@router.get("/lifecycle/templates/{template_key}")
async def get_template(template_key: str):
    if template_key not in MESSAGE_TEMPLATES:
        from fastapi import HTTPException
        raise HTTPException(404, "Sablon bulunamadi")
    return {
        "key": template_key,
        "content": MESSAGE_TEMPLATES[template_key].get("tr", ""),
        "variables": _extract_variables(MESSAGE_TEMPLATES[template_key].get("tr", "")),
    }


@router.post("/lifecycle/preview")
async def preview_message(template_key: str, reservation_id: Optional[str] = None, custom_data: Optional[dict] = None):
    if template_key not in MESSAGE_TEMPLATES:
        from fastapi import HTTPException
        raise HTTPException(404, "Sablon bulunamadi")

    template = MESSAGE_TEMPLATES[template_key]["tr"]

    # Get data from reservation if provided
    data = {
        "guest_name": "Misafir",
        "check_in": "",
        "check_out": "",
        "room_type": "",
        "guests_count": "2",
        "total_price": "",
        "hotel_phone": HOTEL_INFO["phone"],
    }

    if reservation_id:
        res = await db.reservations.find_one({"id": reservation_id}, {"_id": 0})
        if res:
            guest = await db.guests.find_one({"id": res.get("guest_id", "")}, {"_id": 0})
            data.update({
                "guest_name": guest.get("name", "Misafir") if guest else "Misafir",
                "check_in": res.get("check_in", ""),
                "check_out": res.get("check_out", ""),
                "room_type": res.get("room_type", ""),
                "guests_count": str(res.get("guests_count", 2)),
                "total_price": str(res.get("total_price", "")),
            })

    if custom_data:
        data.update(custom_data)

    try:
        message = template.format(**data)
    except KeyError:
        message = template

    return {
        "template_key": template_key,
        "message": message,
        "data": data,
    }


@router.post("/lifecycle/send")
async def send_lifecycle_message(template_key: str, reservation_id: str, channel: str = "whatsapp"):
    """Send a lifecycle message (logs to DB, actual sending is simulated)"""
    if template_key not in MESSAGE_TEMPLATES:
        from fastapi import HTTPException
        raise HTTPException(404, "Sablon bulunamadi")

    # Preview the message
    preview = await preview_message(template_key, reservation_id)

    log = {
        "id": new_id(),
        "template_key": template_key,
        "reservation_id": reservation_id,
        "channel": channel,
        "message": preview["message"],
        "guest_name": preview["data"].get("guest_name", ""),
        "status": "sent",
        "created_at": utcnow(),
    }
    await db.lifecycle_messages.insert_one(log)

    return {"success": True, "message": preview["message"], "channel": channel}


@router.get("/lifecycle/history")
async def lifecycle_history(reservation_id: Optional[str] = None, limit: int = 50):
    query = {"reservation_id": reservation_id} if reservation_id else {}
    items = await db.lifecycle_messages.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return {"messages": items}


def _extract_variables(template: str) -> list:
    import re
    return list(set(re.findall(r'\{(\w+)\}', template)))
