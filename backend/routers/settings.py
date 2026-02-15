from fastapi import APIRouter
from database import db
from helpers import utcnow, new_id
from hotel_data import (
    HOTEL_INFO, HOTEL_POLICIES, HOTEL_RATINGS, ROOMS,
    RESTAURANT_MENU,
)
from models import ReservationStatus, TaskStatus, HousekeepingStatus

router = APIRouter(tags=["settings"])

TRANSLATIONS = {
    "tr": {
        "dashboard": "Dashboard", "rooms": "Odalar", "guests": "Misafirler",
        "chatbot": "AI Asistan", "messages": "Mesajlar", "tasks": "Gorevler",
        "events": "Etkinlikler", "housekeeping": "Kat Hizmetleri",
        "knowledge": "Bilgi Bankasi", "menu": "Restoran Menu",
        "reservations": "Rezervasyonlar", "staff": "Personel",
        "campaigns": "Kampanyalar", "settings": "Ayarlar",
        "welcome": "Hos Geldiniz", "occupancy": "Doluluk Orani",
        "add": "Ekle", "save": "Kaydet", "delete": "Sil", "cancel": "Iptal",
        "search": "Ara", "total": "Toplam", "available": "Musait",
        "occupied": "Dolu", "pending": "Bekleyen", "completed": "Tamamlanan",
    },
    "en": {
        "dashboard": "Dashboard", "rooms": "Rooms", "guests": "Guests",
        "chatbot": "AI Assistant", "messages": "Messages", "tasks": "Tasks",
        "events": "Events", "housekeeping": "Housekeeping",
        "knowledge": "Knowledge Base", "menu": "Restaurant Menu",
        "reservations": "Reservations", "staff": "Staff",
        "campaigns": "Campaigns", "settings": "Settings",
        "welcome": "Welcome", "occupancy": "Occupancy Rate",
        "add": "Add", "save": "Save", "delete": "Delete", "cancel": "Cancel",
        "search": "Search", "total": "Total", "available": "Available",
        "occupied": "Occupied", "pending": "Pending", "completed": "Completed",
    },
    "de": {
        "dashboard": "Dashboard", "rooms": "Zimmer", "guests": "Gaste",
        "chatbot": "KI-Assistent", "messages": "Nachrichten", "tasks": "Aufgaben",
        "events": "Veranstaltungen", "housekeeping": "Housekeeping",
        "knowledge": "Wissensdatenbank", "menu": "Speisekarte",
        "reservations": "Reservierungen", "staff": "Personal",
        "campaigns": "Kampagnen", "settings": "Einstellungen",
        "welcome": "Willkommen", "occupancy": "Belegungsrate",
        "add": "Hinzufugen", "save": "Speichern", "delete": "Loschen", "cancel": "Abbrechen",
        "search": "Suchen", "total": "Gesamt", "available": "Verfugbar",
        "occupied": "Belegt", "pending": "Ausstehend", "completed": "Abgeschlossen",
    },
    "fr": {
        "dashboard": "Tableau de Bord", "rooms": "Chambres", "guests": "Clients",
        "chatbot": "Assistant IA", "messages": "Messages", "tasks": "Taches",
        "events": "Evenements", "housekeeping": "Menage",
        "knowledge": "Base de Connaissances", "menu": "Menu Restaurant",
        "reservations": "Reservations", "staff": "Personnel",
        "campaigns": "Campagnes", "settings": "Parametres",
        "welcome": "Bienvenue", "occupancy": "Taux d'Occupation",
        "add": "Ajouter", "save": "Sauvegarder", "delete": "Supprimer", "cancel": "Annuler",
        "search": "Rechercher", "total": "Total", "available": "Disponible",
        "occupied": "Occupe", "pending": "En Attente", "completed": "Termine",
    },
    "ru": {
        "dashboard": "Panel Upravleniya", "rooms": "Nomera", "guests": "Gosti",
        "chatbot": "AI Assistent", "messages": "Soobsheniya", "tasks": "Zadachi",
        "events": "Meropriyatiya", "housekeeping": "Uborka",
        "knowledge": "Baza Znaniy", "menu": "Menyu Restorana",
        "reservations": "Bronirovanie", "staff": "Personal",
        "campaigns": "Kampanii", "settings": "Nastroyki",
        "welcome": "Dobro Pozhalovat", "occupancy": "Zanyatost",
        "add": "Dobavit", "save": "Sokhranit", "delete": "Udalit", "cancel": "Otmena",
        "search": "Poisk", "total": "Vsego", "available": "Dostupno",
        "occupied": "Zanyato", "pending": "V Ozhidanii", "completed": "Zaversheno",
    },
}


@router.get("/settings")
async def get_settings():
    settings = await db.settings.find_one({"type": "global"}, {"_id": 0})
    if not settings:
        settings = {
            "type": "global",
            "hotel_name": HOTEL_INFO["name"],
            "phone": HOTEL_INFO["phone"],
            "email": HOTEL_INFO["email"],
            "whatsapp_enabled": True,
            "instagram_enabled": True,
            "auto_reply_enabled": True,
            "auto_housekeeping": True,
            "notification_channels": ["whatsapp", "email"],
            "language": "tr",
            "timezone": "Europe/Istanbul",
        }
    return settings


@router.patch("/settings")
async def update_settings(data: dict):
    data["updated_at"] = utcnow()
    await db.settings.update_one(
        {"type": "global"},
        {"$set": data},
        upsert=True,
    )
    return {"success": True}


@router.get("/kvkk/policy")
async def get_kvkk_policy():
    return {
        "title": "Kisisel Verilerin Korunmasi Kanunu (KVKK) Politikasi",
        "hotel": HOTEL_INFO["name"],
        "data_controller": HOTEL_INFO["founders"],
        "sections": [
            {"title": "Veri Sorumlusu", "content": f"{HOTEL_INFO['name']} - {HOTEL_INFO['location']}"},
            {"title": "Toplanan Veriler", "content": "Ad soyad, telefon, e-posta, kimlik/pasaport bilgileri, konaklama gecmisi, odeme bilgileri."},
            {"title": "Veri Isleme Amaci", "content": "Konaklama hizmetlerinin sunulmasi, rezervasyon yonetimi, muhasebe ve faturalandirma, yasal yukumluluklerin yerine getirilmesi."},
            {"title": "Veri Saklama Suresi", "content": "Konaklama verileri 10 yil, muhasebe verileri yasal sure boyunca saklanir."},
            {"title": "Haklariniz", "content": "KVKK m.11 kapsaminda: Verilerinizin islenip islenmedigini ogrenme, islenmisse bilgi talep etme, isleme amacini ogrenme, yurtici/yurtdisi 3. kisilere aktarilip aktarilmadigini ogrenme, duzeltilmesini/silinmesini isteme haklariniz bulunmaktadir."},
            {"title": "Iletisim", "content": f"E-posta: {HOTEL_INFO['email']} | Telefon: {HOTEL_INFO['phone']}"},
        ],
    }


@router.get("/i18n/{lang}")
async def get_translations(lang: str):
    if lang not in TRANSLATIONS:
        lang = "tr"
    return {"language": lang, "translations": TRANSLATIONS[lang]}


@router.get("/i18n")
async def list_languages():
    return {
        "languages": [
            {"code": "tr", "name": "Turkce", "flag": "TR"},
            {"code": "en", "name": "English", "flag": "GB"},
            {"code": "de", "name": "Deutsch", "flag": "DE"},
            {"code": "fr", "name": "Francais", "flag": "FR"},
            {"code": "ru", "name": "Russkiy", "flag": "RU"},
        ],
        "default": "tr",
    }


@router.get("/menu")
async def get_menu():
    return {"menu": RESTAURANT_MENU, "restaurant": HOTEL_INFO["restaurant_name"]}


@router.get("/menu/{category}")
async def get_menu_category(category: str):
    if category not in RESTAURANT_MENU:
        raise HTTPException(404, f"Kategori bulunamadi: {category}")
    return {"category": category, "items": RESTAURANT_MENU[category]}


# ==================== DASHBOARD ====================

@router.get("/dashboard/stats")
async def dashboard_stats():
    total_rooms = HOTEL_INFO["total_rooms"]
    occupied = await db.reservations.count_documents({"status": ReservationStatus.CHECKED_IN})
    total_guests = await db.guests.count_documents({})
    total_tasks = await db.tasks.count_documents({})
    pending_tasks = await db.tasks.count_documents({"status": TaskStatus.PENDING})
    total_reservations = await db.reservations.count_documents({})
    active_events = await db.events.count_documents({"is_active": True})
    housekeeping_pending = await db.housekeeping.count_documents({"status": HousekeepingStatus.PENDING})

    recent = await db.tasks.find({}, {"_id": 0}).sort("created_at", -1).limit(5).to_list(5)

    return {
        "total_rooms": total_rooms,
        "occupied_rooms": occupied,
        "available_rooms": total_rooms - occupied,
        "occupancy_rate": round((occupied / total_rooms) * 100, 1) if total_rooms else 0,
        "total_guests": total_guests,
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "total_reservations": total_reservations,
        "active_events": active_events,
        "housekeeping_pending": housekeeping_pending,
        "ratings": HOTEL_RATINGS,
        "recent_tasks": recent,
    }


from fastapi import HTTPException
