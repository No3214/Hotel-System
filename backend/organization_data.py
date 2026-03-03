"""
Kozbeyli Konagi - Organizasyon (Dugun/Nisan) Verileri
Dugun, nisan, soz, ozel kutlama organizasyonlari icin tum detaylar.
PDF sunumlarindan cikarilmis bilgiler.
"""

# Organizasyon turleri
ORGANIZATION_TYPES = [
    {"id": "dugun", "name": "Dugun"},
    {"id": "nisan", "name": "Nisan"},
    {"id": "soz", "name": "Soz Kesme"},
    {"id": "kina", "name": "Kina Gecesi"},
    {"id": "dogum_gunu", "name": "Dogum Gunu"},
    {"id": "yil_donumu", "name": "Yil Donumu"},
    {"id": "kurumsal", "name": "Kurumsal Etkinlik"},
    {"id": "diger", "name": "Diger"},
]

# Konaklama bilgileri
ACCOMMODATION_INFO = {
    "total_rooms": 16,
    "room_types": [
        {"type": "double", "name": "2 Kisilik (Double)", "count": 9, "capacity": 2},
        {"type": "triple", "name": "3 Kisilik (Triple)", "count": 3, "capacity": 3},
        {"type": "family", "name": "4 Kisilik (King/Aile)", "count": 4, "capacity": 4},
    ],
    "total_capacity": 9*2 + 3*3 + 4*4,  # 43 kisi
    "included_rooms": 3,  # Menu paketine dahil 3 oda (6 kisi)
    "breakfast_included": True,
    "note": "Tum konaklama fiyatlarina kisi basi gurme serpme kahvalti dahildir.",
}

# Kokteyl menusu detaylari
COCKTAIL_MENU = {
    "name": "Kokteyl Menusu",
    "cocktails_per_person": 2,
    "items": [
        "Pizzalar (Margarita/Karisik)",
        "Peynir Tabagi",
        "Kizarmis Tavuk ve Baharatli Patates Kizartmasi",
        "Mini Pesto Kanepe",
        "Zeytin Ezmeli Kanepe",
        "Serit Salata ve Havuc Dilimleri",
    ],
}

# Yemekli gala menusu
DINNER_MENU = {
    "name": "Yemekli Gala Menusu",
    "courses": [
        {"name": "Meze", "description": "Cesitli mezeler"},
        {"name": "Kisiye Ozel Salata", "description": "Taze salata"},
        {"name": "Pacanga Boregi", "description": "Sicak baslangic"},
        {"name": "Ana Yemek", "description": "Levrek, Kofte veya Tavuk Sis (secmeli)"},
        {"name": "Meyve Tabagi", "description": "Mevsim meyveleri"},
    ],
    "note": "Icecekler bu menuye dahil degildir.",
    "dietary_options": ["Vejetaryen", "Vegan", "Glutensiz", "Laktozsuz"],
}

# Susleme paketleri
DECORATION_PACKAGES = [
    {
        "id": "standart",
        "name": "Standart Paket",
        "includes": [
            "Arka plan tag",
            "Cicek susleme",
            "Isiklandirma",
            "Nisan tepsisi/makasi",
            "Damat fincani",
            "Isteme kosesi",
            "Masa fanus-mum",
            "Giris isimlik",
            "Aksesuarlar",
        ],
    },
    {
        "id": "vip",
        "name": "VIP Paket",
        "includes": [
            "Standart paket icerigi",
            "Kisiye ozel arka plan",
            "Canli cicek",
            "Giris ayna karsilama",
            "Isim karti",
            "Menu karti",
            "Kumas pecete",
            "Isimli kagit pecete",
            "Hediyelik",
        ],
    },
]

# Fotograf/video paketleri
PHOTO_VIDEO_PACKAGES = [
    {"id": "photo", "name": "Fotograf Cekimi", "description": "Hazirliktan torene tum anlar"},
    {"id": "photo_after", "name": "Fotograf + After Movie", "description": "Fotograf + 1 dk After Movie video"},
    {"id": "cinematic", "name": "Sinematik Dugun Cekimi", "description": "Artistik sinematik tarzi"},
    {"id": "drone", "name": "Drone Cekimi", "description": "Havadan cekim (opsiyonel)"},
]

# Muzik secenekleri
MUSIC_OPTIONS = [
    {"id": "dj", "name": "Canli Muzik - DJ Performans", "duration": "2 saat", "genres": "House, Afro House"},
    {"id": "acoustic", "name": "Canli Muzik - Akustik", "duration": "Degisken", "genres": "Pop, Jazz"},
    {"id": "after_party", "name": "After Party", "duration": "Degisken", "genres": "Cesitli"},
]

# Odeme kosullari
PAYMENT_TERMS = {
    "deposit_percentage": 50,
    "deposit_note": "Toplam bedelin %50'si organizasyon konfirme oldugunda",
    "balance_note": "Kalan tutar etkinlik tarihinden 1 hafta once tahsil edilir",
    "extras_note": "Ek kisi ve ekstra tuketimler organizasyon bitiminde ayrica faturalandirilir",
    "methods": ["Nakit", "Kredi Karti"],
    "offer_validity_days": 7,
}

# PDF linkleri (sunumlar)
PRESENTATION_PDFS = [
    {
        "id": "sunum1",
        "name": "Kozbeyli Konagi Dugun/Nisan Sunumu (Detayli)",
        "description": "Menu, konaklama, dekorasyon, fotograf paketleri",
        "url": "https://customer-assets.emergentagent.com/job_e29b4400-d18a-4432-ac3e-18354239605f/artifacts/uqcifk8d_1%20Kozbeyli%20Kona%C4%9F%C4%B1%20D%C3%BC%C4%9F%C3%BCn%20Ni%C5%9Fan%20Sunum.pdf",
    },
    {
        "id": "sunum2",
        "name": "Kozbeyli Konagi Organizasyon Tanitimi",
        "description": "Genel tanitim, atmosfer, isbirligi firsatlari",
        "url": "https://customer-assets.emergentagent.com/job_e29b4400-d18a-4432-ac3e-18354239605f/artifacts/tfig0pqg_2%20Kozbeyli%20Kona%C4%9F%C4%B1%20D%C3%BC%C4%9F%C3%BCn%20Ni%C5%9Fan%20Sunum.pdf",
    },
]

# Organizasyon bilgi formu alanlari
ORGANIZATION_FORM_FIELDS = {
    "personal": ["guest_name", "phone", "email", "second_contact", "address"],
    "event": ["org_type", "date", "alt_date", "day_preference", "start_time", "end_time",
              "guest_count_estimate", "guest_count_final", "child_0_6", "child_7_12", "extra_guests"],
    "accommodation": ["needs_accommodation", "checkin_date", "checkout_date", "nights",
                       "double_rooms", "triple_rooms", "family_rooms", "bridal_suite"],
    "menu": ["menu_type", "drink_preference", "drink_details", "dietary_needs", "menu_tasting", "menu_notes"],
    "decoration": ["decoration_package", "decoration_notes"],
    "photo_video": ["wants_photo_video", "photo_video_details"],
    "music": ["music_preference", "music_details"],
    "coordination": ["wants_coordination", "coordination_notes"],
    "budget": ["budget_min", "budget_max", "payment_method"],
    "extra": ["extra_notes", "referral_source"],
}

# Chatbot icin organizasyon auto-reply
ORGANIZATION_AUTO_REPLY = """Merhaba! Kozbeyli Konagi'nda dugun, nisan veya ozel organizasyon planladiginizi duydugumuza cok sevindik!

Organizasyonlarimiz hakkinda kisa bilgi:
- Tarihi tas otel atmosferinde essiz kutlamalar
- 16 oda, 43 kisi konaklama kapasitesi
- Kokteyl veya Yemekli Gala menu secenekleri
- Profesyonel dekorasyon (Standart/VIP paket)
- Fotograf, video, drone cekimi
- DJ performans veya akustik canli muzik

Detayli bilgi icin sunumlarimizi inceleyebilirsiniz:

Size en dogru teklifi hazirlayabilmemiz icin kisa bir bilgi formunu doldurmanizi rica ederiz. Formda organizasyon tarihini, misafir sayisini, menu ve konaklama tercihlerinizi belirtmeniz yeterli.

Iletisim: +90 532 234 26 86
E-posta: info@kozbeylikonagi.com"""
