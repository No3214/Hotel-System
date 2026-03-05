"""
Kozbeyli Konagi - Kurumsal Kimlik & Marka Rehberi
Sosyal medya, chatbot, ve tum iletisimde kullanilacak marka standartlari.
"""

# ==================== MARKA KIMLIGi ====================
BRAND = {
    "name": "Kozbeyli Konagi",
    "name_en": "Kozbeyli Mansion",
    "slogan_tr": "Tarihi Tas Otel & Restoran",
    "slogan_en": "Historic Stone Hotel & Restaurant",
    "tagline_tr": "Dogayla ic ice, huzurun adresi",
    "tagline_en": "Embraced by nature, home of serenity",
    "mission_tr": "Foca'nin essiz dogasi ve Antakya'nin zengin mutfak kulturunu bulusturarak, misafirlerimize unutulmaz bir konaklama ve gastronomi deneyimi sunmak.",
    "vision_tr": "Ege'nin en ozel butik otel deneyimini sunarak, Foca'yi dunya capinda bir destinasyon haline getirmek.",
    "values_tr": [
        "Misafirperverlik - Her misafir ailemizin bir parcasi",
        "Otantiklik - Tarihi dokuyu koruyarak modern konfor",
        "Lezzet - Antakya mutfaginin en iyi temsilcisi",
        "Surdurulebilirlik - Dogaya saygi, yerel urunlerle calisma",
        "Aile sicakligi - 14 yillik aile isletmesi gelenegimiz",
    ],
    "story_tr": "2011'den bu yana Inci & Varol Oruk tarafindan isletilen Kozbeyli Konagi, Foca'nin essiz dogal guzelligine sahip Kozbeyli Koyu'nde, tamamen yerel Foca tasindan insa edilmis tarihi bir konaktir. 16 odali butik otelimiz ve Antakya Sofrasi restoranımız ile misafirlerimize dogayla ic ice, autentik bir Ege deneyimi sunuyoruz.",
}

# ==================== RENK PALETI ====================
BRAND_COLORS = {
    "primary": "#C4972A",       # Altin / Gold - Ana marka rengi
    "primary_dark": "#A87A1F",  # Koyu altin
    "secondary": "#515249",     # Tas gri - Foca tasi rengi
    "accent": "#8FAA86",        # Zeytin yesili - Doga
    "background": "#1a1a22",    # Koyu arka plan
    "surface": "#F8F5EF",       # Krem - Sicak yuzey
    "text_dark": "#1E1B16",     # Koyu metin
    "text_light": "#F8F5EF",    # Acik metin
    "error": "#D32F2F",
    "success": "#4CAF50",
}

# ==================== TIPOGRAFI ====================
BRAND_FONTS = {
    "heading": "Playfair Display, Georgia, serif",
    "body": "Inter, -apple-system, sans-serif",
    "accent": "Cormorant Garamond, serif",
}

# ==================== SOSYAL MEDYA REHBERI ====================
SOCIAL_MEDIA_GUIDE = {
    "tone_of_voice": {
        "tr": "Sicak, samimi ama profesyonel. Misafirperver ve davetkar. Turkce karakterler kullanilmali. Emoji kullanimi olculu - her mesajda 1-2 emoji yeterli.",
        "en": "Warm, genuine yet professional. Hospitable and inviting.",
    },
    "do": [
        "Dogal gorseller kullanin - filtreli degil, gercek guzellik",
        "Misafirlerin izniyle deneyim paylasimlari yapin",
        "Yerel kulturel ogeler ve Foca guzelliklerini on plana cikarin",
        "Mevsimsel icerikler paylasin (zeytinyagi hasadi, balik sezonu vb.)",
        "Restoran lezzetlerini gorselleriyle paylasın",
        "Gundogumu/gunbatimi manzaralarini sik paylasın",
        "Hikaye anlatarak baglantin kurun",
    ],
    "dont": [
        "Asiri ticari dil kullanmayin",
        "Rakip oteller hakkinda yorum yapmayin",
        "Politik veya tartismali konulara girmeyin",
        "Dusuk kaliteli gorsel paylasmyin",
        "Cok fazla emoji veya buyuk harf kullanmayin",
        "Yanlislarina veya uydurma bilgi vermeyin",
    ],
    "best_times_tr": {
        "instagram": ["08:00-09:00", "12:00-13:00", "19:00-21:00"],
        "facebook": ["09:00-11:00", "13:00-15:00", "19:00-20:00"],
        "x": ["08:00-10:00", "12:00-13:00", "17:00-18:00"],
        "linkedin": ["08:00-10:00", "12:00-13:00"],
        "tiktok": ["19:00-22:00", "12:00-14:00"],
        "pinterest": ["14:00-16:00", "20:00-22:00"],
    },
    "frequency": {
        "instagram": "Gunluk 1 post + 3-5 story",
        "facebook": "Haftada 3-4 post",
        "x": "Gunluk 2-3 tweet",
        "linkedin": "Haftada 1-2 post (kurumsal, organizasyon)",
        "tiktok": "Haftada 2-3 video (mutfak, oda turu, manzara)",
        "pinterest": "Haftada 5-7 pin (gorsel agirlikli)",
        "google_business": "Haftada 1-2 post + etkinlik",
    },
}

# ==================== HASHTAG STRATEJISI ====================
HASHTAG_SETS = {
    "always": ["KozbeyliKonagi", "FocaOtel", "ButikOtel"],
    "location": ["Foca", "FocaIzmir", "Izmir", "EgedenEsintiler", "KozbeyliKoyu", "EgeTatil"],
    "hotel": ["TasOtel", "TarihiKonak", "ButikOtelTurkiye", "HotelTurkey", "BoutiqueHotel"],
    "food": ["AntakyaSofrasi", "AntakyaMutfagi", "FocaLezzet", "EgeMutfagi", "GastroTurizm", "TurkishCuisine"],
    "nature": ["DogaIleBirlkte", "HuzurluTatil", "ZeytinliklerdeBirKonak", "DoğaKaçamağı"],
    "event": ["DugunMekani", "KirDugunu", "NisanOrganizasyonu", "EtkinlikMekani", "RusticWedding"],
    "seasonal": {
        "yaz": ["YazTatili", "EgeSahilleri", "DenizManzarasi", "HavuzBasinda"],
        "sonbahar": ["SonbaharHuzuru", "ZeytinHasadi", "KisHazırlıkları"],
        "kis": ["KisTatili", "YilbasiKacamagi", "ŞömineBasi"],
        "ilkbahar": ["BaharGeldi", "CicekActi", "DoğaUyanıyor"],
    },
    "engagement": ["KesfetFoca", "GeziyorumFoca", "TatilOnerisi", "HaftasonuKacamagi", "ButikOtelOnerileri"],
}

# ==================== ICERIK TAKIMI ====================
CONTENT_CALENDAR_THEMES = {
    "pazartesi": {"theme": "Motivasyon Pazartesi", "type": "quote", "desc": "Haftaya guzel baslat - dogal manzara + motive edici cumle"},
    "sali": {"theme": "Lezzet Salisi", "type": "food", "desc": "Antakya Sofrasi'ndan bir lezzet tanitimi"},
    "carsamba": {"theme": "Oda Turu", "type": "room", "desc": "Bir oda/suite detayli tanitim"},
    "persembe": {"theme": "Misafir Yorumu", "type": "review", "desc": "Misafir memnuniyeti paylasimi"},
    "cuma": {"theme": "Haftasonu Planı", "type": "promo", "desc": "Haftasonu icin ozel teklif/davet"},
    "cumartesi": {"theme": "Etkinlik/Manzara", "type": "event", "desc": "Canli etkinlik veya manzara paylasimi"},
    "pazar": {"theme": "Brunch & Huzur", "type": "lifestyle", "desc": "Kahvalti ve huzurlu bir gun paylasimi"},
}

# ==================== BIO SABLONLARI ====================
PLATFORM_BIOS = {
    "instagram": "🏨 Tarihi Tas Otel & Restoran | Foca, Izmir\n🍽️ Antakya Sofrasi\n📍 Kozbeyli Koyu\n📞 +90 532 234 26 86\n🌐 kozbeylikonagi.com",
    "facebook": "Kozbeyli Konagi - 14 yillik aile isletmesi. Foca tasindan insa edilmis butik otel ve Antakya Sofrasi restoran. Dugun, nisan, organizasyon icin ideal mekan. Rezervasyon: +90 532 234 26 86",
    "x": "Foca'nin kalbinde tarihi tas otel & Antakya Sofrasi 🏨🍽️ | Butik konaklama, dugun & organizasyon | Rez: 0532 234 26 86 | #KozbeyliKonagi",
    "linkedin": "Kozbeyli Konagi | Tarihi Butik Otel & Restoran | 14 yillik aile isletmesi | Foca, Izmir | Kurumsal etkinlikler, toplanti ve organizasyonlar icin ideal mekan | www.kozbeylikonagi.com",
    "tiktok": "Foca'nin en ozel butik oteli 🏨✨ Antakya Sofrasi lezzetleri 🍽️ Rezervasyon bio'da 👇",
    "pinterest": "Kozbeyli Konagi | Tarihi Tas Otel & Restoran | Foca, Izmir | Ilham veren mekanlar, lezzetler ve anlar",
    "google_business": "Foca'nin Kozbeyli Koyu'nde tarihi Foca tasindan insa edilmis butik otel. 16 oda, Antakya Sofrasi restoran, 100 kisilik organizasyon kapasitesi. Ucretsiz kahvalti, WiFi ve otopark.",
}

# ==================== OTOMATIK POST SABLONLARI ====================
AUTO_POST_TEMPLATES = {
    "yeni_rezervasyon_kutlama": {
        "title": "Yeni Misafirler Bekliyoruz",
        "content": "Kozbeyli Konagi'nda sizi agirlayacagiz! Dogayla ic ice, huzur dolu bir tatil icin yerinizi ayirtin.",
        "hashtags": ["KozbeyliKonagi", "ButikOtel", "FocaOtel", "HuzurluTatil"],
        "platforms": ["instagram", "facebook"],
    },
    "gunbatimi": {
        "title": "Gun Batimi @ Kozbeyli",
        "content": "Her gun batimi Kozbeyli Konagi'nda ayri bir guzel... Dogayla ic ice huzurun adresi.",
        "hashtags": ["KozbeyliKonagi", "GunBatimi", "Foca", "DogaIleBirlikte"],
        "platforms": ["instagram", "facebook", "pinterest"],
    },
    "menu_tanitim": {
        "title": "Antakya Sofrasi",
        "content": "Antakya'nin zengin lezzetleri Kozbeyli Konagi'nin masasinda. Gelin, tadina bakin!",
        "hashtags": ["AntakyaSofrasi", "FocaLezzet", "KozbeyliKonagi", "GastroTurizm"],
        "platforms": ["instagram", "facebook", "x", "pinterest"],
    },
    "oda_tanitim": {
        "title": "Oda Turu",
        "content": "Tarihi Foca tasindan insa edilmis odalarimizda dogayla ic ice bir gece gecirin.",
        "hashtags": ["KozbeyliKonagi", "ButikOtel", "TasOtel", "OdaTuru"],
        "platforms": ["instagram", "tiktok", "pinterest"],
    },
    "organizasyon": {
        "title": "Hayalinizdeki Organizasyon",
        "content": "Dugun, nisan, soz, kutlama... Kozbeyli Konagi'nda hayalinizdeki organizasyonu gerceklestirin. 100 kisilik kapasite.",
        "hashtags": ["KozbeyliKonagi", "DugunMekani", "KirDugunu", "NisanOrganizasyonu"],
        "platforms": ["instagram", "facebook", "linkedin", "pinterest"],
    },
    "misafir_yorumu": {
        "title": "Misafirlerimiz Ne Diyor?",
        "content": "En buyuk odulumuz, misafirlerimizin mutlulugu.",
        "hashtags": ["KozbeyliKonagi", "MisafirMemnuniyeti", "ButikOtel"],
        "platforms": ["instagram", "facebook", "google_business"],
    },
}
