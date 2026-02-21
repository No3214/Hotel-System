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
        "knowledge": "Bilgi Bankasi", "menu": "QR Menu",
        "reservations": "Rezervasyonlar", "staff": "Personel",
        "campaigns": "Kampanyalar", "settings": "Ayarlar",
        "welcome": "Hos Geldiniz", "occupancy": "Doluluk Orani",
        "add": "Ekle", "save": "Kaydet", "delete": "Sil", "cancel": "Iptal",
        "search": "Ara", "total": "Toplam", "available": "Musait",
        "occupied": "Dolu", "pending": "Bekleyen", "completed": "Tamamlanan",
        "whatsapp": "WhatsApp", "pricing": "Fiyatlama", "reviews": "Google Yorumlari",
        "lifecycle": "Misafir Dongusu", "social": "Sosyal Medya",
        "table_reservations": "Masa Rez.", "kitchen": "Mutfak",
        "guide": "Foca Rehberi", "automation": "Otomasyon",
        "general": "Genel", "communication": "Iletisim", "operations": "Operasyon",
        "information": "Bilgi", "system": "Sistem",
        "hotel_management": "Otel Yonetim Paneli",
        "occupancy_rate": "Doluluk Orani", "total_rooms": "Toplam Oda",
        "occupied_rooms": "Dolu Oda", "available_rooms": "Bos Oda",
        "todays_checkins": "Bugunun Girisleri", "todays_checkouts": "Bugunun Cikislari",
        "revenue": "Gelir", "monthly_revenue": "Aylik Gelir",
        "weekly_trend": "Haftalik Doluluk Trendi",
        "recent_activity": "Son Aktiviteler", "recent_tasks": "Son Gorevler",
        "platform_ratings": "Platform Puanlari",
        "room_status": "Oda Durumu", "live": "Canli",
        "logout": "Cikis Yap", "admin": "Admin", "reception": "Resepsiyon",
        "language": "Dil", "no_data": "Henuz veri yok",
        "confirmed": "Onaylandi", "checked_in": "Giris Yapti", "checked_out": "Cikis Yapti",
        "cancelled": "Iptal Edildi", "cleaning": "Temizlik",
        "today": "Bugun", "this_month": "Bu Ay",
        "analytics": "Analitik", "audit": "Guvenlik", "hotelrunner": "HotelRunner",
        "integrations": "Entegrasyonlar", "financials": "Finansal",
    },
    "en": {
        "dashboard": "Dashboard", "rooms": "Rooms", "guests": "Guests",
        "chatbot": "AI Assistant", "messages": "Messages", "tasks": "Tasks",
        "events": "Events", "housekeeping": "Housekeeping",
        "knowledge": "Knowledge Base", "menu": "QR Menu",
        "reservations": "Reservations", "staff": "Staff",
        "campaigns": "Campaigns", "settings": "Settings",
        "welcome": "Welcome", "occupancy": "Occupancy Rate",
        "add": "Add", "save": "Save", "delete": "Delete", "cancel": "Cancel",
        "search": "Search", "total": "Total", "available": "Available",
        "occupied": "Occupied", "pending": "Pending", "completed": "Completed",
        "whatsapp": "WhatsApp", "pricing": "Pricing", "reviews": "Google Reviews",
        "lifecycle": "Guest Lifecycle", "social": "Social Media",
        "table_reservations": "Table Res.", "kitchen": "Kitchen",
        "guide": "Foca Guide", "automation": "Automation",
        "general": "General", "communication": "Communication", "operations": "Operations",
        "information": "Information", "system": "System",
        "hotel_management": "Hotel Management Panel",
        "occupancy_rate": "Occupancy Rate", "total_rooms": "Total Rooms",
        "occupied_rooms": "Occupied Rooms", "available_rooms": "Available Rooms",
        "todays_checkins": "Today's Check-ins", "todays_checkouts": "Today's Check-outs",
        "revenue": "Revenue", "monthly_revenue": "Monthly Revenue",
        "weekly_trend": "Weekly Occupancy Trend",
        "recent_activity": "Recent Activity", "recent_tasks": "Recent Tasks",
        "platform_ratings": "Platform Ratings",
        "room_status": "Room Status", "live": "Live",
        "logout": "Logout", "admin": "Admin", "reception": "Reception",
        "language": "Language", "no_data": "No data yet",
        "confirmed": "Confirmed", "checked_in": "Checked In", "checked_out": "Checked Out",
        "cancelled": "Cancelled", "cleaning": "Cleaning",
        "today": "Today", "this_month": "This Month",
        "analytics": "Analytics", "audit": "Security", "hotelrunner": "HotelRunner",
        "integrations": "Integrations", "financials": "Financials",
    },
    "de": {
        "dashboard": "Dashboard", "rooms": "Zimmer", "guests": "Gaste",
        "chatbot": "KI-Assistent", "messages": "Nachrichten", "tasks": "Aufgaben",
        "events": "Veranstaltungen", "housekeeping": "Housekeeping",
        "knowledge": "Wissensdatenbank", "menu": "QR-Menu",
        "reservations": "Reservierungen", "staff": "Personal",
        "campaigns": "Kampagnen", "settings": "Einstellungen",
        "welcome": "Willkommen", "occupancy": "Belegungsrate",
        "add": "Hinzufugen", "save": "Speichern", "delete": "Loschen", "cancel": "Abbrechen",
        "search": "Suchen", "total": "Gesamt", "available": "Verfugbar",
        "occupied": "Belegt", "pending": "Ausstehend", "completed": "Abgeschlossen",
        "whatsapp": "WhatsApp", "pricing": "Preisgestaltung", "reviews": "Google Bewertungen",
        "lifecycle": "Gastezyklus", "social": "Soziale Medien",
        "table_reservations": "Tischres.", "kitchen": "Kuche",
        "guide": "Foca Reisefuhrer", "automation": "Automatisierung",
        "general": "Allgemein", "communication": "Kommunikation", "operations": "Betrieb",
        "information": "Information", "system": "System",
        "hotel_management": "Hotel-Verwaltung",
        "occupancy_rate": "Belegungsrate", "total_rooms": "Zimmer Gesamt",
        "occupied_rooms": "Belegte Zimmer", "available_rooms": "Freie Zimmer",
        "todays_checkins": "Heutige Anreisen", "todays_checkouts": "Heutige Abreisen",
        "revenue": "Umsatz", "monthly_revenue": "Monatlicher Umsatz",
        "weekly_trend": "Wochentlicher Belegungstrend",
        "recent_activity": "Letzte Aktivitaten", "recent_tasks": "Letzte Aufgaben",
        "platform_ratings": "Plattform-Bewertungen",
        "room_status": "Zimmerstatus", "live": "Live",
        "logout": "Abmelden", "admin": "Admin", "reception": "Rezeption",
        "language": "Sprache", "no_data": "Noch keine Daten",
        "confirmed": "Bestatigt", "checked_in": "Eingecheckt", "checked_out": "Ausgecheckt",
        "cancelled": "Storniert", "cleaning": "Reinigung",
        "today": "Heute", "this_month": "Dieser Monat",
        "analytics": "Analytik", "audit": "Sicherheit", "hotelrunner": "HotelRunner",
        "integrations": "Integrationen", "financials": "Finanzen",
    },
    "fr": {
        "dashboard": "Tableau de Bord", "rooms": "Chambres", "guests": "Clients",
        "chatbot": "Assistant IA", "messages": "Messages", "tasks": "Taches",
        "events": "Evenements", "housekeeping": "Menage",
        "knowledge": "Base de Connaissances", "menu": "Menu QR",
        "reservations": "Reservations", "staff": "Personnel",
        "campaigns": "Campagnes", "settings": "Parametres",
        "welcome": "Bienvenue", "occupancy": "Taux d'Occupation",
        "add": "Ajouter", "save": "Sauvegarder", "delete": "Supprimer", "cancel": "Annuler",
        "search": "Rechercher", "total": "Total", "available": "Disponible",
        "occupied": "Occupe", "pending": "En Attente", "completed": "Termine",
        "whatsapp": "WhatsApp", "pricing": "Tarification", "reviews": "Avis Google",
        "lifecycle": "Cycle Client", "social": "Reseaux Sociaux",
        "table_reservations": "Res. Table", "kitchen": "Cuisine",
        "guide": "Guide Foca", "automation": "Automatisation",
        "general": "General", "communication": "Communication", "operations": "Operations",
        "information": "Information", "system": "Systeme",
        "hotel_management": "Gestion Hoteliere",
        "occupancy_rate": "Taux d'Occupation", "total_rooms": "Chambres Totales",
        "occupied_rooms": "Chambres Occupees", "available_rooms": "Chambres Libres",
        "todays_checkins": "Arrivees du Jour", "todays_checkouts": "Departs du Jour",
        "revenue": "Revenu", "monthly_revenue": "Revenu Mensuel",
        "weekly_trend": "Tendance Hebdomadaire",
        "recent_activity": "Activites Recentes", "recent_tasks": "Taches Recentes",
        "platform_ratings": "Notes des Plateformes",
        "room_status": "Statut des Chambres", "live": "En Direct",
        "logout": "Deconnexion", "admin": "Admin", "reception": "Reception",
        "language": "Langue", "no_data": "Pas encore de donnees",
        "confirmed": "Confirme", "checked_in": "Arrive", "checked_out": "Parti",
        "cancelled": "Annule", "cleaning": "Nettoyage",
        "today": "Aujourd'hui", "this_month": "Ce Mois",
        "analytics": "Analytique", "audit": "Securite", "hotelrunner": "HotelRunner",
        "integrations": "Integrations", "financials": "Finances",
    },
    "ru": {
        "dashboard": "Panel Upravleniya", "rooms": "Nomera", "guests": "Gosti",
        "chatbot": "AI Assistent", "messages": "Soobsheniya", "tasks": "Zadachi",
        "events": "Meropriyatiya", "housekeeping": "Uborka",
        "knowledge": "Baza Znaniy", "menu": "QR Menyu",
        "reservations": "Bronirovanie", "staff": "Personal",
        "campaigns": "Kampanii", "settings": "Nastroyki",
        "welcome": "Dobro Pozhalovat", "occupancy": "Zanyatost",
        "add": "Dobavit", "save": "Sokhranit", "delete": "Udalit", "cancel": "Otmena",
        "search": "Poisk", "total": "Vsego", "available": "Dostupno",
        "occupied": "Zanyato", "pending": "V Ozhidanii", "completed": "Zaversheno",
        "whatsapp": "WhatsApp", "pricing": "Tseny", "reviews": "Otzyvy Google",
        "lifecycle": "Tsikl Gostya", "social": "Sotsialnye Seti",
        "table_reservations": "Rez. Stolov", "kitchen": "Kukhnya",
        "guide": "Gid po Foca", "automation": "Avtomatizatsiya",
        "general": "Obshchee", "communication": "Kommunikatsiya", "operations": "Operatsii",
        "information": "Informatsiya", "system": "Sistema",
        "hotel_management": "Panel Upravleniya Otelem",
        "occupancy_rate": "Zanyatost", "total_rooms": "Vsego Nomerov",
        "occupied_rooms": "Zanyatye Nomera", "available_rooms": "Svobodnye Nomera",
        "todays_checkins": "Segodnyashnie Zaezdy", "todays_checkouts": "Segodnyashnie Vyezdy",
        "revenue": "Dokhod", "monthly_revenue": "Mesyachnyy Dokhod",
        "weekly_trend": "Nedelnaya Zanyatost",
        "recent_activity": "Poslednie Deystviya", "recent_tasks": "Poslednie Zadachi",
        "platform_ratings": "Reytingi Platform",
        "room_status": "Status Nomerov", "live": "Pryamoy Efir",
        "logout": "Vyyti", "admin": "Admin", "reception": "Retseptsiya",
        "language": "Yazyk", "no_data": "Dannykh poka net",
        "confirmed": "Podtverzhdeno", "checked_in": "Zaekhal", "checked_out": "Vyekhal",
        "cancelled": "Otmeneno", "cleaning": "Uborka",
        "today": "Segodnya", "this_month": "Etot Mesyats",
        "analytics": "Analitika", "audit": "Bezopasnost", "hotelrunner": "HotelRunner",
        "integrations": "Integratsii", "financials": "Finansy",
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

    # Today's data
    from datetime import datetime, timedelta, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    todays_checkins = await db.reservations.count_documents({
        "check_in": today,
        "status": {"$in": ["pending", "confirmed", "checked_in"]},
    })
    todays_checkouts = await db.reservations.count_documents({
        "check_out": today,
        "status": {"$in": ["confirmed", "checked_in"]},
    })

    # Revenue from reservations
    all_res = await db.reservations.find(
        {"status": {"$in": ["confirmed", "checked_in", "checked_out"]}},
        {"_id": 0, "total_price": 1, "check_in": 1, "status": 1}
    ).to_list(1000)
    total_revenue = sum(r.get("total_price", 0) or 0 for r in all_res)
    monthly_revenue = sum(
        r.get("total_price", 0) or 0 for r in all_res
        if r.get("check_in", "").startswith(today[:7])
    )

    # Weekly occupancy trend (last 7 days)
    now = datetime.now(timezone.utc)
    weekly_trend = []
    day_names_tr = ["Pzt", "Sal", "Car", "Per", "Cum", "Cmt", "Paz"]
    for i in range(6, -1, -1):
        d = now - timedelta(days=i)
        date_str = d.strftime("%Y-%m-%d")
        day_occupied = await db.reservations.count_documents({
            "status": {"$in": ["confirmed", "checked_in"]},
            "check_in": {"$lte": date_str},
            "check_out": {"$gte": date_str},
        })
        weekly_trend.append({
            "date": date_str,
            "day": day_names_tr[d.weekday()],
            "occupied": day_occupied,
            "rate": round((day_occupied / total_rooms) * 100) if total_rooms else 0,
        })

    # Room status breakdown
    rooms_list = await db.rooms.find({}, {"_id": 0, "room_id": 1, "name_tr": 1, "status": 1}).to_list(50)
    room_status_counts = {}
    for rm in rooms_list:
        st = rm.get("status", "available")
        room_status_counts[st] = room_status_counts.get(st, 0) + 1

    # Recent activity feed (last 10 actions from automation_logs + group_notifications)
    recent_activity = await db.automation_logs.find(
        {}, {"_id": 0, "type": 1, "message": 1, "created_at": 1, "status": 1}
    ).sort("created_at", -1).limit(5).to_list(5)

    recent_reservations = await db.reservations.find(
        {}, {"_id": 0, "id": 1, "guest_name": 1, "room_id": 1, "status": 1, "check_in": 1, "check_out": 1, "created_at": 1}
    ).sort("created_at", -1).limit(5).to_list(5)

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
        "todays_checkins": todays_checkins,
        "todays_checkouts": todays_checkouts,
        "total_revenue": total_revenue,
        "monthly_revenue": monthly_revenue,
        "weekly_trend": weekly_trend,
        "room_status_counts": room_status_counts,
        "recent_activity": recent_activity,
        "recent_reservations": recent_reservations,
        "rooms_list": rooms_list,
    }


from fastapi import HTTPException
