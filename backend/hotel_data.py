"""
Kozbeyli Konagi - Complete Hotel Data
All hotel information, rooms, menu, policies, history
"""

HOTEL_INFO = {
    "name": "Kozbeyli Konagi",
    "name_en": "Kozbeyli Mansion",
    "type": "Butik Tas Otel & Restoran",
    "tagline_tr": "14 yillik aile isletmesi. Foca tasindan insa edilmis konagimizda dogayla ic ice butik otel & restoran deneyimi",
    "tagline_en": "14-year family business. Boutique hotel & restaurant experience in a mansion built from Foca stone",
    "location": "Kozbeyli Koyu Kume Evleri No:188, 35680 Foca/Izmir",
    "phone": "+90 232 826 11 12",
    "phone_booking": "+90 532 234 26 86",
    "whatsapp": "+90 532 234 26 86",
    "email": "info@kozbeylikonagi.com",
    "website": "https://kozbeylikonagi.com",
    "menu_website": "https://www.kozbeylikonagi.com.tr/menu/",
    "restaurant_name": "Antakya Sofrasi",
    "total_rooms": 16,
    "founders": "Varol Oruk",
    "checkin_time": "14:00",
    "checkout_time": "12:00",
}

HOTEL_RATINGS = {
    "booking_com": 9.2,
    "tripadvisor": 4.5,
    "google": 4.8,
    "hotels_com": 9.0
}

ROOM_PRICES = {
    "tek_kisilik": 3000,
    "cift_kisilik": 3500,
    "uc_kisilik": 5000,
    "superior": 5500,
    "aile_odasi": 6000,
}

SPECIAL_DAY_PRICES = {
    "cift_kisilik": 4500,
    "uc_kisilik": 5500,
    "superior": 6000,
    "aile_odasi": 7000,
}

ROOMS = [
    {
        "room_id": "single",
        "name_tr": "Tek Kisilik Oda",
        "name_en": "Single Room",
        "base_price_try": 3000,
        "base_price_eur": 85,
        "capacity": 1,
        "amenities": ["Klima", "TV", "WiFi", "Minibar"]
    },
    {
        "room_id": "double",
        "name_tr": "Cift Kisilik Oda",
        "name_en": "Double Room",
        "base_price_try": 3500,
        "base_price_eur": 100,
        "capacity": 2,
        "amenities": ["Klima", "TV", "WiFi", "Minibar", "Balkon"]
    },
    {
        "room_id": "triple",
        "name_tr": "Uc Kisilik Oda",
        "name_en": "Triple Room",
        "base_price_try": 5000,
        "base_price_eur": 140,
        "capacity": 3,
        "amenities": ["Klima", "TV", "WiFi", "Minibar", "Balkon"]
    },
    {
        "room_id": "superior",
        "name_tr": "Superior Oda",
        "name_en": "Superior Room",
        "base_price_try": 5500,
        "base_price_eur": 160,
        "capacity": 3,
        "amenities": ["Klima", "TV", "WiFi", "Minibar", "Oturma Alani", "Deniz Manzarasi"]
    }
]

HOTEL_POLICIES = {
    "cancellation": {
        "tr": "72 saat oncesine kadar ucretsiz iptal. Sonrasinda %100 ceza.",
        "en": "Free cancellation up to 72 hours before. 100% penalty thereafter."
    },
    "no_show": {
        "tr": "Gelmeyen misafirlerden %100 ucret tahsil edilir.",
        "en": "No-show guests will be charged 100%."
    },
    "saturday_payment": {
        "tr": "Cumartesi konaklamalari icin %100 on odeme gereklidir.",
        "en": "100% prepayment is required for Saturday stays."
    },
    "breakfast": "Gurme serpme kahvalti fiyata dahildir (08:30-11:00).",
    "pets": "Kucuk irk evcil hayvanlar kabul edilir.",
    "children": "0-4 yas ucretsiz, ek yatak konulmaz."
}

HOTEL_AWARDS = [
    "Tripadvisor Travellers' Choice 2023",
    "Booking.com Traveller Review Awards 2024",
    "Foca'nin En Iyi Butik Oteli 2022"
]

HOTEL_HISTORY = "Kozbeyli Konagi, 14 yildir Oruk ailesi tarafindan isletilen, tarihi Foca taslarindan restore edilmis bir konaktir."

FOCA_LOCAL_GUIDE = "Kozbeyli Koyu tarihi dokusu, dibek kahvesi ve essiz manzarasiyla meshurdur. Foca merkez 10-15 dakika mesafededir."

RESTAURANT_MENU = {
    "kahvalti": [
        {"name": "Gurme Serpme Kahvalti", "price_try": 750},
        {"name": "Pisi Tabagi", "price_try": 400}
    ],
    "ana_yemek": [
        {"name": "Konak Kofte", "price_try": 800},
        {"name": "Sac Kavurma", "price_try": 1000}
    ],
    "meze": [
        {"name": "Atom", "price_try": 300},
        {"name": "Haydari", "price_try": 300}
    ],
    "tatli": [
        {"name": "Antakya Kunefe", "price_try": 400},
        {"name": "Katmer", "price_try": 400}
    ]
}

GEMINI_SYSTEM_PROMPT = """Sen Kozbeyli Konagi'nin akilli asistanisin. Misafirlere otel, restoran ve cevre hakkinda yardimci olursun.
Kibar, profesyonel ve yardimseversin. Sadece sana verilen bilgilere dayanarak cevap ver.
Bilmedigin konularda uydurma, resepsiyona yonlendir (+90 232 826 11 12)."""

INTENT_KEYWORDS = {
    "rooms": ["oda", "konaklama", "yatak", "oda tipi", "superior", "single", "double", "triple"],
    "menu": ["menu", "yemek", "restoran", "kahvalti", "aksam yemegi", "ne yenir"],
    "cancellation": ["iptal", "iade", "degisiklik", "policy", "politika"],
    "local_guide": ["foca", "gezi", "plaj", "ulasim", "nereye gidilir", "kozbeyli"],
    "events": ["etkinlik", "dugun", "nisan", "organizasyon", "kutlama"],
    "greeting": ["merhaba", "selam", "gunaydin", "iyi gunler"],
    "thanks": ["tesekkur", "sagol", "eyvallah"],
    "price": ["fiyat", "ucret", "kac para", "gecelik", "tl", "eur"]
}
