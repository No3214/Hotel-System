# Kozbeyli Konagi - Otel Bilgileri ve Konfigurasyonu

# Temel Bilgiler
HOTEL_INFO = {
    "name": "Kozbeyli Konagi",
    "name_en": "Kozbeyli Mansion",
    "tagline": "Dogayla Ic Ice Butik Otel",
    "tagline_en": "Boutique Hotel Intertwined with Nature",
    "type": "Butik Otel & Restoran",
    "established": "14. yuzyil Osmanli donemi koyunde",
    
    # İletişim
    "phone": "+90 232 812 23 23",
    "whatsapp": "+90 532 XXX XX XX",  # Güncellenecek
    "email": "info@kozbeylikonagi.com",
    "website": "https://kozbeylikonagi.com",
    
    # Adres
    "address": {
        "full": "Kozbeyli Köyü, Kozbeyli Küme Evleri No:188, 35680 Foça, İzmir",
        "village": "Kozbeyli Köyü",
        "district": "Foça",
        "city": "İzmir",
        "postal_code": "35680",
        "country": "Türkiye",
    },
    
    # Konum
    "location": {
        "latitude": 38.7589,
        "longitude": 26.7844,
        "google_maps": "https://maps.google.com/?q=Kozbeyli+Konagi+Foca",
        "yandex_maps": "https://yandex.com.tr/maps/org/kozbeyli_konagi/198385038584/",
    },
    
    # Uzaklıklar
    "distances": {
        "yeni_foca_limani": "7.3 km",
        "foca_merkez": "19-20 km",
        "izmir_merkez": "70 km",
        "adnan_menderes_havalimani": "81.6 km",
    },
    
    # Sosyal Medya
    "social_media": {
        "instagram": "https://instagram.com/kozbeylikonagi",
        "facebook": "https://facebook.com/kozbeylikonagi",
        "tripadvisor": "https://www.tripadvisor.com.tr/Hotel_Review-g10920533-d4298328-Reviews-Kozbeyli_KonagI",
        "google_reviews": "https://g.page/kozbeylikonagi/review",
        "booking": "https://www.booking.com/hotel/tr/kozbeyli-konagi.html",
    },
    
    # WiFi
    "wifi": {
        "network": "KozbeyliKonagi_Guest",
        "password": "GUNCELLENECEK",  # Kullanıcı verecek
    },
    
    # Check-in/out
    "check_in": "14:00",
    "check_out": "12:00",
    
    # Olanaklar
    "amenities": [
        "Ucretsiz WiFi",
        "Ucretsiz Otopark",
        "Havuz",
        "Cati Terasi (Deniz/Dag Manzarali)",
        "Restoran (Kahvalti & Aksam Yemegi)",
        "12 Saat Resepsiyon",
        "Gunluk Temizlik",
        "Camasir & Utu Hizmeti",
        "Evcil Hayvan Kabul",
        "Cocuk Dostu (4 yasa kadar ucretsiz)",
        "Oyun Odasi",
        "Kutuphane",
    ],
    
    # Puanlar
    "ratings": {
        "tripadvisor": 3.7,
        "google": 4.5,  # Tahmini
    },
}

# Oda Tipleri (16 oda)
ROOM_TYPES = [
    {
        "id": "quadruple",
        "name": "4 Kisilik Oda",
        "name_en": "Quadruple Room",
        "capacity": 4,
        "count": 4,
        "description": "Aileler ve arkadas gruplari icin ideal, genis alan ve konfor.",
        "amenities": ["Klima", "TV", "Ozel Banyo", "Balkon", "Deniz Manzarasi"],
        "view": "mixed",
    },
    {
        "id": "superior",
        "name": "Superior Oda",
        "name_en": "Superior Room",
        "capacity": 2,
        "count": 2,
        "description": "Konfor ve lukusun birlestigi, genis ve ferah oda.",
        "amenities": ["Klima", "TV", "Ozel Banyo", "Balkon", "Dag Manzarasi"],
        "view": "mountain",
    },
    {
        "id": "triple",
        "name": "3 Kisilik Oda", 
        "name_en": "Triple Room",
        "capacity": 3,
        "count": 2,
        "description": "Romantik kacamak veya kucuk gruplar icin tasarlandi.",
        "amenities": ["Klima", "TV", "Ozel Banyo", "Balkon"],
        "view": "mixed",
    },
    {
        "id": "standard_sea",
        "name": "Standart Oda (Manzarali)",
        "name_en": "Standard Room (Sea View)",
        "capacity": 2,
        "count": 4,
        "description": "Deniz manzarali, konforlu konaklama deneyimi.",
        "amenities": ["Klima", "TV", "Ozel Banyo", "Balkon", "Deniz Manzarasi"],
        "view": "sea",
    },
    {
        "id": "standard_land",
        "name": "Standart Oda (Kara Manzarali)",
        "name_en": "Standard Room (Land View)",
        "capacity": 2,
        "count": 4,
        "description": "Huzurlu koy manzarali, rahat konaklama.",
        "amenities": ["Klima", "TV", "Ozel Banyo", "Balkon", "Koy Manzarasi"],
        "view": "land",
    },
]

# İptal Politikası
CANCELLATION_POLICY = {
    "standard": {
        "free_cancellation_days": 3,  # 3 gun oncesine kadar ucretsiz
        "penalty_within_days": 100,   # 3 gun icinde %100 ceza
        "description": "Rezervasyondan 3 gun oncesine kadar ucretsiz iptal. 3 gun icinde iptal halinde %100 cezai islem.",
    },
    "special_days": {
        "requires_prepayment": True,
        "prepayment_percent": 100,
        "applicable_days": ["saturday", "sunday"],
        "applicable_events": ["bayram", "yilbasi", "ozel_etkinlik"],
        "description": "Cumartesi, Pazar, Bayram ve ozel etkinlik gunleri icin on odemesiz rezervasyon kabul edilmez. Tam odeme gereklidir.",
    },
}

# WhatsApp Mesaj Şablonları
WHATSAPP_TEMPLATES = {
    "welcome": {
        "name": "Hosgeldiniz",
        "trigger": "check_in_day",
        "hours_before": 4,
        "message": """Merhaba {guest_name} 🌿

Kozbeyli Konagi'na hosgeldiniz! 

📍 Adresimiz: Kozbeyli Köyü, Küme Evleri No:188, Foça/İzmir
🕐 Check-in: 14:00'den itibaren
🅿️ Ücretsiz otopark mevcuttur

Yolculugunuz hayirli olsun, gorusuruz! 🏡""",
    },
    
    "checkout_thanks": {
        "name": "Tesekkur & Yorum",
        "trigger": "check_out",
        "hours_after": 2,
        "message": """Merhaba {guest_name} 🌿

Kozbeyli Konagi'nda misafirimiz oldugunuz icin tesekkur ederiz! 🙏

Deneyiminizi bizimle paylasmak ister misiniz? Yorumunuz bizim icin cok degerli:

⭐ Google: {google_review_link}
⭐ TripAdvisor: {tripadvisor_link}

Tekrar gorusmek uzere! 🏡
Kozbeyli Konagi Ailesi""",
    },
    
    "cleaning_notification": {
        "name": "Temizlik Bildirimi",
        "trigger": "check_out",
        "target": "staff_group",
        "message": """🧹 TEMIZLIK BILDIRIMI

Oda: {room_number} - {room_type}
Cikis Yapan: {guest_name}
Cikis Saati: {checkout_time}

Lutfen temizlige baslayin! ✅""",
    },
    
    "organization_inquiry": {
        "name": "Organizasyon Bilgi",
        "trigger": "keyword:organizasyon,dugun,nisan,kutlama",
        "message": """Merhaba! 🌿

Kozbeyli Konagi'nda ozel gunleriniz icin hizmetinizdeyiz:
💒 Dugun
💍 Nisan & Soz
🎂 Dogum Gunu
🎉 Ozel Kutlamalar

📸 Organizasyon gorsellerimiz: {drive_link}
📞 Detayli bilgi: +90 232 812 23 23

Size nasil yardimci olabiliriz?""",
    },
    
    "reservation_reminder": {
        "name": "Rezervasyon Hatirlatma",
        "trigger": "reservation_date",
        "hours_before": 24,
        "message": """Merhaba {guest_name} 🌿

Yarin {reservation_date} tarihli rezervasyonunuzu hatirlatiriz:

🍽️ {meal_type} - Saat: {time}
👥 {party_size} kisi
🪑 {table_name}

Gorusmek uzere! 🏡
Kozbeyli Konagi""",
    },
}

# Restoran Bilgileri (Menu icin)
RESTAURANT_INFO = {
    "name": "Antakya Sofrasi",
    "cuisine": "Turk & Ege Mutfagi",
    "specialties": [
        "Serpme Kahvalti",
        "Kuzu Tandir",
        "Sac Kavurma", 
        "Mezeler",
        "Tas Firin Pizza",
    ],
    "alcohol": True,
    "wifi": HOTEL_INFO["wifi"],
    "social_media": HOTEL_INFO["social_media"],
    "location": HOTEL_INFO["location"],
    "review_links": {
        "google": HOTEL_INFO["social_media"]["google_reviews"],
        "tripadvisor": HOTEL_INFO["social_media"]["tripadvisor"],
    },
}
