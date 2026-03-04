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
    "menu_website": "https://thefoost.com/kozbeyli-konagi/",
    "instagram": "https://instagram.com/kozbeylikonagi",
    "instagram_handle": "@kozbeylikonagi",
    "instagram_followers": 11000,
    "checkin_time": "14:00",
    "checkout_time": "12:00",
    "gate_closing_time": "23:00",
    "quiet_hours": "23:00-08:00",
    "total_rooms": 16,
    "room_breakdown": {
        "standart": 1,
        "standart_bahce_manzarali": 3,
        "standart_deniz_manzarali": 4,
        "uc_kisilik": 2,
        "aile_odasi": 2,
        "aile_odasi_balkonlu": 2,
        "superior": 1,
        "superior_uc_kisilik": 1,
    },
    "opened_year": 2011,  # 14 yillik isletme
    "founders": "Inci & Varol Oruk",
    "pets_allowed": True,
    "pets_note": "Kucuk irklar ucretsiz, buyuk irklar icin balkonlu oda",
    "free_parking": True,
    "free_wifi": True,
    "free_breakfast": True,
    "breakfast_includes": ["Serpme kahvalti", "Sucuklu yumurta", "Pisi"],
    "alcohol_served": True,
    "event_capacity": 100,
    "reception_hours": "08:00-00:00",
    "restaurant_name": "Antakya Sofrasi",
    "restaurant_hours": {
        "breakfast": "08:30-11:00",
        "kitchen_closes": "22:00",
        "restaurant_closes": "23:00",
    },
    "signature_dishes": [
        "Yogurtlu Balik", "Kalamar Dolmasi", "Balik Dolmasi", "Balik Pacasi",
        "Kuzu Etli Enginar", "Zeytinyagli Enginar Dolmasi", "Sac Kavurma", "Kuzu Tandir",
        "Konak Kofte", "Antep Fistikli Kaymakli Kunefe",
    ],
    "coordinates": {"lat": 38.7333, "lng": 26.7667},
    "license": "T.C. Kultur ve Turizm Bakanligi Tesis Izin Belgesi No: 2025-35-1824",
    "room_amenities": [
        "Mini buzdolabi", "Klima", "LCD Televizyon", "Ozel banyo",
        "WiFi", "Sac kurutma makinesi",
        "Sivi sabun", "Sampuan", "Dus jeli", "Terlik",
    ],
    "room_welcome": "2-4 adet su, sallama cay, nescafe, bambu karistirma cubugu, cikolatali mini berliner",
    "guest_tips": [
        "Sessiz ve manzarali oda icin ust kat tercih edin",
        "Kozbeyli Koyu cevresinde dogayla ic ice yuruyus parkurlari mevcut",
        "Transfer/ulasim icin resepsiyondan yardim alin",
        "Erken check-in/gec check-out icin onceden bilgi verin",
    ],
    "extra_services": {
        "laundry": {"available": True, "note": "Ucretli, ayni gun teslimat"},
        "transfer": {"available": True, "note": "Resepsiyon araciligyla ayarlanir"},
        "event": {"available": True, "note": "100 kisilik kapasite, 30+ kisi icin ozel fiyat"},
        "baby_cot": {"available": True, "note": "Ucretsiz, ekstra yatak konulmaz"},
    },
}

ROOMS = [
    {
        "room_id": "standart",
        "name_tr": "Standart Oda",
        "name_en": "Standard Room",
        "description_tr": "Otantik tas duvarli, konforlu 2 kisilik standart oda.",
        "description_en": "Authentic stone-walled comfortable standard double room.",
        "capacity": 2,
        "min_capacity": 1,
        "size_m2": 25,
        "features": ["klima", "LCD TV", "mini buzdolabi", "sac kurutma", "ozel banyo", "WiFi"],
        "base_price_try": 3500,
        "base_price_eur": 105,
        "count": 1,
        "view": "standard",
        "ikram": "2 adet su, sallama cay, nescafe, cikolatali mini berliner",
        "status": "available",
    },
    {
        "room_id": "standart-bahce",
        "name_tr": "Standart Bahce Manzarali Oda",
        "name_en": "Standard Garden View Room",
        "description_tr": "Otantik tas duvarli, konforlu 2 kisilik oda. Huzurlu bahce manzarasi.",
        "description_en": "Authentic stone-walled comfortable double room. Peaceful garden view.",
        "capacity": 2,
        "min_capacity": 1,
        "size_m2": 25,
        "features": ["klima", "LCD TV", "mini buzdolabi", "sac kurutma", "ozel banyo", "WiFi"],
        "base_price_try": 3500,
        "base_price_eur": 105,
        "count": 3,
        "view": "garden",
        "ikram": "2 adet su, sallama cay, nescafe, cikolatali mini berliner",
        "status": "available",
    },
    {
        "room_id": "standart-deniz",
        "name_tr": "Standart Deniz Manzarali Oda",
        "name_en": "Standard Sea View Room",
        "description_tr": "Otantik tas duvarli, konforlu 2 kisilik oda. Foca Korfezi deniz manzarasi.",
        "description_en": "Authentic stone-walled comfortable double room. Foca Bay sea view.",
        "capacity": 2,
        "min_capacity": 1,
        "size_m2": 25,
        "features": ["klima", "LCD TV", "mini buzdolabi", "sac kurutma", "ozel banyo", "WiFi"],
        "base_price_try": 3500,
        "base_price_eur": 105,
        "count": 4,
        "view": "sea",
        "ikram": "2 adet su, sallama cay, nescafe, cikolatali mini berliner",
        "status": "available",
    },
    {
        "room_id": "uc-kisilik",
        "name_tr": "Uc Kisilik Oda",
        "name_en": "Triple Room",
        "description_tr": "Rahat ve ferah 3 kisilik oda. Kucuk aileler veya arkadas gruplari icin ideal.",
        "description_en": "Comfortable triple room. Ideal for small families or groups of friends.",
        "capacity": 3,
        "min_capacity": 2,
        "size_m2": 30,
        "features": ["klima", "LCD TV", "mini buzdolabi", "sac kurutma", "ozel banyo", "WiFi"],
        "base_price_try": 5000,
        "base_price_eur": 150,
        "count": 2,
        "view": "mixed",
        "ikram": "3 adet su, sallama cay, nescafe, cikolatali mini berliner",
        "status": "available",
    },
    {
        "room_id": "aile",
        "name_tr": "Aile Odasi (4 Kisilik)",
        "name_en": "Family Room (4 Person)",
        "description_tr": "1 cift kisilik + 2 tek kisilik yatak, oturma alani. Aileler icin ideal.",
        "description_en": "1 double + 2 single beds, sitting area. Ideal for families.",
        "capacity": 4,
        "min_capacity": 2,
        "size_m2": 50,
        "features": ["klima", "LCD TV", "mini buzdolabi", "sac kurutma", "ozel banyo", "WiFi", "oturma alani"],
        "base_price_try": 6000,
        "base_price_eur": 180,
        "count": 2,
        "view": "mixed",
        "ikram": "4 adet su, sallama cay, nescafe, cikolatali mini berliner",
        "status": "available",
    },
    {
        "room_id": "aile-balkonlu",
        "name_tr": "Aile Odasi (4 Kisilik) Balkonlu",
        "name_en": "Family Room (4 Person) with Balcony",
        "description_tr": "1 cift kisilik + 2 tek kisilik yatak, oturma alani, ozel balkon. Manzarali aile deneyimi.",
        "description_en": "1 double + 2 single beds, sitting area, private balcony. Scenic family experience.",
        "capacity": 4,
        "min_capacity": 2,
        "size_m2": 55,
        "features": ["klima", "LCD TV", "mini buzdolabi", "sac kurutma", "ozel banyo", "WiFi", "oturma alani", "balkon"],
        "base_price_try": 6000,
        "base_price_eur": 180,
        "count": 2,
        "view": "mixed",
        "ikram": "4 adet su, sallama cay, nescafe, cikolatali mini berliner",
        "status": "available",
    },
    {
        "room_id": "superior",
        "name_tr": "Superior 2 Kisilik Oda",
        "name_en": "Superior Double Room",
        "description_tr": "Genis ve konforlu superior 2 kisilik oda. Oturma alani ve balkon.",
        "description_en": "Spacious and comfortable superior double room. Sitting area and balcony.",
        "capacity": 2,
        "min_capacity": 1,
        "size_m2": 35,
        "features": ["klima", "LCD TV", "mini buzdolabi", "sac kurutma", "ozel banyo", "WiFi", "oturma alani", "balkon"],
        "base_price_try": 5500,
        "base_price_eur": 165,
        "count": 1,
        "view": "sea",
        "ikram": "3 adet su, sallama cay, nescafe, cikolatali mini berliner",
        "status": "available",
    },
    {
        "room_id": "superior-uc-kisilik",
        "name_tr": "Superior 3 Kisilik Oda",
        "name_en": "Superior Triple Room",
        "description_tr": "1 cift kisilik + 1 tek kisilik yatak, oturma alani, balkon. 2 veya 3 kisi icin uygun.",
        "description_en": "1 double + 1 single bed, sitting area, balcony. Suitable for 2-3 guests.",
        "capacity": 3,
        "min_capacity": 2,
        "size_m2": 35,
        "features": ["klima", "LCD TV", "mini buzdolabi", "sac kurutma", "ozel banyo", "WiFi", "oturma alani", "balkon"],
        "base_price_try": 5500,
        "base_price_eur": 165,
        "count": 1,
        "view": "sea",
        "ikram": "3 adet su, sallama cay, nescafe, cikolatali mini berliner",
        "status": "available",
    },
]

# Guncel Fiyat Listesi (Nakit/Havale - TL)
ROOM_PRICES = {
    "standart": 3500,
    "standart_bahce_manzarali": 3500,
    "standart_deniz_manzarali": 3500,
    "uc_kisilik": 5000,
    "aile_odasi": 6000,
    "aile_odasi_balkonlu": 6000,
    "superior": 5500,
    "superior_uc_kisilik": 5500,
}

# Ozel Gun Fiyatlari (14 Subat, Yilbasi, Bayramlar)
SPECIAL_DAY_PRICES = {
    "standart": 4500,
    "standart_bahce_manzarali": 4500,
    "standart_deniz_manzarali": 4500,
    "uc_kisilik": 5000,
    "aile_odasi": 6000,
    "aile_odasi_balkonlu": 6000,
    "superior": 5500,
    "superior_uc_kisilik": 5500,
}

RESTAURANT_MENU = {
    "kahvalti": [
        {"name": "Gurme Serpme Kahvalti", "price_try": 750, "desc": "Sahanda tereyagli sucuklu yumurta, domates, salatalik, yesil biber, roka, avokado, siyah zeytin, cesitli peynirler, ceviz ve mevsim meyveleri."},
        {"name": "Pisi Kahvalti Tabagi", "price_try": 750, "desc": "2 adet sicak pisi, 2 dilim beyaz peynir, yesil ve siyah zeytinler, acili ezme, salatalik ve domates."},
    ],
    "baslangic": [
        {"name": "Baslangic Tabagi (2 Kisi)", "price_try": 350, "desc": "Zeytin, zahter, zeytinyagi ve feslegenli domatesli ciabatta."},
        {"name": "Roka Salatasi", "price_try": 400, "desc": "Roka, beyaz peynir, tarla domatesi, kuru incir, ceviz, balsamik glaze."},
        {"name": "Fume Somon", "price_try": 500, "desc": "Fume somon parcalari rustik ekmek uzerinde."},
    ],
    "ana_yemek": [
        {"name": "Dallas Steak", "price_try": 3500, "desc": "Orta pismis antrikot, altin rengi patates puresi."},
        {"name": "Izgara Pirzola", "price_try": 1200, "desc": "Kemikli et, patates puresi, kavrulmus file badem."},
        {"name": "Konak Kofte", "price_try": 800, "desc": "Geleneksel tarifle kofte, patates puresi."},
        {"name": "Konak Sac Kavurma", "price_try": 1000, "desc": "Sacda pisirilen et parcalari, patates puresi."},
        {"name": "Lokum Bonfile", "price_try": 1500, "desc": "Yumusacik biftek, patates puresi."},
    ],
    "meze": [
        {"name": "Acili Atom", "price_try": 300, "desc": "Yogurt ve aci biberle hazirlanan meze."},
        {"name": "Haydari", "price_try": 300, "desc": "Suzme yogurt ve taze otlarla klasik meze."},
        {"name": "Deniz Borulcesi", "price_try": 300, "desc": "Zeytinyagi ve limonla tatlandirilmis Ege mezesi."},
        {"name": "Antakya Humus", "price_try": 300, "desc": "Nohut-tahin humusu domates ve zeytinyagiyla."},
        {"name": "Yogurtlu Patlican", "price_try": 300, "desc": "Kozlenmis patlican ile yogurt."},
        {"name": "Visneli Yaprak Sarma", "price_try": 350, "desc": "Asma yapraklarinda pirinc, visneli tatli-eksi uyum."},
    ],
    "tatli": [
        {"name": "Antakya Kunefe", "price_try": 400, "desc": "Tel kadayif arasinda eriyen peynir ve serbet, fistik ve kaymak."},
        {"name": "Antep Fistikli Katmer", "price_try": 400, "desc": "Ince yufka, bol Antep fistigi, vanilyali Maras dondurma."},
        {"name": "Churros", "price_try": 400, "desc": "Kizartilmis hamur cubuklari - cilek/visne receli veya Nutella."},
    ],
    "pizza_sandvic": [
        {"name": "Tas Firin Karisik Pizza", "price_try": 750, "desc": "Tas firinda, roka, parmesan ve acili zeytinyagi ile."},
        {"name": "Tas Firin Margarita Pizza", "price_try": 700, "desc": "Tas firinda, taze roka, parmesan."},
        {"name": "Gurme Rustik Sandvic", "price_try": 600, "desc": "Rustik baget, beyaz peynir, domates, roka, pesto sos."},
    ],
    "sicak_icecekler": [
        {"name": "Cay", "price_try": 40}, {"name": "Turk Kahvesi", "price_try": 150},
        {"name": "Americano", "price_try": 150}, {"name": "Espresso", "price_try": 150},
        {"name": "Filtre Kahve", "price_try": 150}, {"name": "Bitki Caylari", "price_try": 150},
    ],
    "soguk_icecekler": [
        {"name": "Ice Latte", "price_try": 180}, {"name": "Ice Americano", "price_try": 180},
        {"name": "Taze Portakal Suyu", "price_try": 250}, {"name": "Kola", "price_try": 150},
        {"name": "Ice Tea", "price_try": 150}, {"name": "Soda", "price_try": 100},
    ],
    "sarap": [
        {"name": "Phokaia Karasi (Kirmizi)", "price_try": 2000},
        {"name": "Okuzgozu 1970 (Kirmizi) 70cl", "price_try": 2000},
        {"name": "Phokaia Chardonnay (Beyaz)", "price_try": 2000},
    ],
    "bira": [
        {"name": "Blanc", "price_try": 275}, {"name": "Carlsberg", "price_try": 250},
        {"name": "Tuborg Gold", "price_try": 250},
    ],
    "raki": [
        {"name": "Beylerbeyi Gobek 35cl", "price_try": 2150},
        {"name": "Beylerbeyi Gobek 70cl", "price_try": 3400},
    ],
    "viski": [
        {"name": "Chivas Regal 35cl", "price_try": 2500},
        {"name": "Jack Daniels 35cl", "price_try": 2500},
        {"name": "Woodford Reserve 70cl", "price_try": 5000},
    ],
}

HOTEL_AWARDS = [
    "TripAdvisor Travelers' Choice 2020 & 2021 - Dunya 10., Avrupa 4. En Iyi Aile Oteli",
    "Booking.com Traveller Review Awards 2020 - 9.3/10",
    "TripAdvisor Certificate of Excellence - Hall of Fame",
    "HolidayCheck Award & Recommended 2020",
    "QM Awards - Turkiye'nin En Iyi Dort Mevsim Oteli",
    "IAGTO 2020 - Hotel Experience of the Year",
    "Kids Concept - Cocuk dostu tesis sertifikasi",
    "Bisiklet Dostu Konaklama Tesisi sertifikasi",
    "DQS ISO/IEC 27001:2013",
]

HOTEL_RATINGS = {
    "booking_com": {"score": 8.8, "label": "Fabulous"},
    "tripadvisor": {"score": 5.0, "max": 5, "reviews": 60},
    "holidaycheck": {"score": 5.9, "max": 6},
    "neredekal": {"score": 4.7, "max": 5, "label": "Mukemmel"},
}

HOTEL_POLICIES = {
    "cancellation": {
        "free_cancel_days": 3,
        "penalty_percent": 100,
        "tr": "Giris tarihinden 72 saat (3 gun) oncesine kadar ucretsiz iptal. Sonrasi %100 ceza.",
        "en": "Free cancellation up to 72 hours (3 days) before check-in. After that 100% penalty.",
    },
    "no_show": {
        "penalty_percent": 100,
        "tr": "Gelmeyen misafirden %100 ucret tahsil edilir.",
        "en": "100% charge for no-show guests.",
    },
    "prepayment": {
        "weekday": "%50 kapora",
        "weekend": "%100 tam odeme",
        "special_days": "%100 tam odeme (14 Subat, Yilbasi, Bayramlar)",
        "tr": "Hafta ici %50, hafta sonu ve ozel gunlerde %100 on odeme.",
    },
    "saturday_payment": {
        "tr": "Cumartesi, resmi/dini bayram, 14 Subat ve yilbasinda %100 on odeme zorunludur.",
        "en": "100% pre-payment required for Saturdays, holidays, Valentine's Day and New Year's.",
    },
    "payment_methods": ["Kredi Karti (Visa, Mastercard)", "Banka Havalesi / EFT", "Nakit"],
    "bank_accounts": [
        {
            "bank": "Ziraat Bankasi",
            "account_holder": "Varol Oruk",
            "iban": "TR86 0001 0003 4454 7464 5450 08",
        },
        {
            "bank": "Yapi Kredi Bankasi",
            "account_holder": "Varol Oruk",
            "iban": "TR72 0006 7010 0000 0010 5454 18",
            "branch": "Izmir",
        },
    ],
    "bank_info": {
        "account_holder": "Varol Oruk",
        "bank": "Ziraat Bankasi",
        "iban": "TR86 0001 0003 4454 7464 5450 08",
        "note": "Havale/EFT sonrasi dekont gonderilmesi gerekmektedir. Aciklama kismi bos birakilmalidir.",
    },
    "children": "0-4 yas arasi ucretsiz. Ucretsiz bebek yatagi.",
    "pets": "Kucuk irk evcil hayvanlar ucretsiz kabul edilir. Buyuk irklar icin balkonlu oda verilebilir.",
    "breakfast": "Tum oda fiyatlarina serpme kahvalti, sucuklu yumurta ve pisi dahildir. Kahvalti varisi takip eden sabah servis edilir.",
    "extra_bed": "Odalara ek yatak konulmaz, kapasite oda tipine goredir.",
}

HOTEL_HISTORY = {
    "village_age_years": 600,
    "village_founder": "Derebeyi Kuzubeyi",
    "history_tr": "Kozbeyli Koyu, yaklasik 600 yillik bir gecmise sahiptir. Saphane Dagi'nin eteklerinde, Izmir'in Foca ilcesi sinirlarinda kurulmustur. Kozbeyli Konagi, Istanbul'daki hareketli yasalarini birakip koye yerlesen Inci ve Varol Oruk cifti tarafindan 2013 yilinda acilmistir.",
    "timeline": [
        {"period": "14. yuzyil", "event": "Kurulus - Saruhanoğulları Beyligi"},
        {"period": "~1500", "event": "Kuzubeyi Donemi - Kocakule insasi"},
        {"period": "1638", "event": "Osmanli Camisi Insasi"},
        {"period": "1878", "event": "Capkinoglu Konagi Insasi"},
        {"period": "1924", "event": "Mubadele - Limni, Rumeli gocmenleri"},
        {"period": "2012", "event": "Rum Mahallesi SIT alani ilan edildi"},
        {"period": "2013", "event": "Kozbeyli Konagi butik otel olarak acildi"},
    ],
}

FOCA_LOCAL_GUIDE = {
    "beaches": [
        {"name": "Mersinaki Koyu", "distance": "8 km", "desc": "Kristal berrakliginda su, aileler icin ideal."},
        {"name": "Sazlica Koyu", "distance": "6 km", "desc": "Sakin ve dogal bir koy, snorkel icin harika."},
        {"name": "Eski Foca Sahili", "distance": "5 km", "desc": "Kasaba merkezinde sirin bir sahil."},
        {"name": "Seytan Hamami", "distance": "10 km", "desc": "Kayaliklar arasinda dogal havuz."},
    ],
    "historical": [
        {"name": "Foca Kalesi (Beskapilar)", "distance": "5 km", "desc": "Ceneviz kalesi, deniz manzarasi."},
        {"name": "Athena Tapinagi", "distance": "5 km", "desc": "Antik Phokaia'dan kalma tapinak kalintilari."},
        {"name": "Kozbeyli Koyu", "distance": "0 km", "desc": "500 yillik tas yapilar ve otantik koy yasami."},
    ],
    "activities_family": [
        {"name": "Tekne Turu", "duration": "3-4 saat", "desc": "Foca adalari ve koylari turu."},
        {"name": "Bisiklet Turu", "duration": "2-3 saat", "desc": "Kozbeyli'den Foca'ya doga icinde."},
        {"name": "At Binme", "duration": "1-2 saat", "desc": "Doga icinde at binme deneyimi."},
    ],
    "activities_couple": [
        {"name": "Gunbatimi Tekne Turu", "duration": "2-3 saat", "desc": "Sarap ve meze esliginde."},
        {"name": "Sarap Tadimi", "duration": "2 saat", "desc": "Bolgedeki baglarda Ege saraplari."},
        {"name": "Romantik Aksam Yemegi", "duration": "2-3 saat", "desc": "Bahcede mumlar esliginde."},
    ],
}

GEMINI_SYSTEM_PROMPT = f"""Sen Kozbeyli Konagi'nin dijital misafir asistani "Asli"sin. Profesyonel, sicak ve bilgili bir tonda misafirlere yardimci oluyorsun.

## KISILIK ve TON
- Resmi ama samimi. "Elbette", "Memnuniyetle yardimci olurum" gibi ifadeler kullan
- Kisa ve net yanitlar ver. Gereksiz uzun cevaplardan kacin
- Her zaman yardima hazir ol, proaktif davran (ornegin check-in sorulursa check-out da belirt)
- Misafiri ismiyle hitap et (biliniyorsa)
- Emojileri olculu kullan, profesyonel kal

## YASAKLI KONULAR - ASLA CEVAP VERME
- Siyaset, din, tartismali sosyal konular
- Tibbi veya hukuki tavsiye
- Rakip oteller hakkinda yorum
- Otel hakkinda olumsuz yorum/elestiri
- Cinsel icerikliler konular
- Bu konularda soru gelirse: "Bu konuda yardimci olamiyorum. Baska bir konuda yardimci olabilir miyim?" de

## ESKALASYON PROTOKOLU
- 30+ kisilik grup organizasyonlari → "Bu buyuklukte organizasyonlar icin ozel fiyat gorusmesi gerekiyor. Sizi yoneticimize yonlendireyim: {HOTEL_INFO['phone_booking']}"
- Fiyat anlasmzliklari/sikayet → "Bu konuyu en iyi sekilde cozebilmemiz icin sizi yoneticimizle gorusturmek istiyorum: {HOTEL_INFO['phone_booking']}"
- Acil durumlar (saglik, guvenlik) → "Acil durumlar icin lutfen hemen resepsiyonu arayin: {HOTEL_INFO['phone']} veya 112'yi arayin"
- Karmasik/ozel talepler → "Detayli bilgi icin bizi aramanizi oneririm: {HOTEL_INFO['phone_booking']}"

## DIL KURALLARI
- Turkce mesaja Turkce, Ingilizce mesaja Ingilizce, Almanca mesaja Almanca cevap ver
- WhatsApp formati kullan: *bold*, _italic_

## OTEL BILGILERI
- {HOTEL_INFO['name']} - 14 yillik aile isletmesi, tamamen Foca tasindan insa edilmis butik tas otel
- Kurucular: {HOTEL_INFO['founders']}
- Adres: {HOTEL_INFO['location']}
- Telefon: {HOTEL_INFO['phone']} / Rezervasyon: {HOTEL_INFO['phone_booking']}
- WhatsApp: {HOTEL_INFO['whatsapp']}
- Instagram: {HOTEL_INFO['instagram_handle']} (11.000+ takipci)
- Web: {HOTEL_INFO['website']}
- Menu: {HOTEL_INFO['menu_website']}

## MANZARA
- Kozbeyli Koyu'nun tepelerinde Foca Korfezi'ne panoramik manzara
- Gun dogumu ve gun batiminda essiz seyir keyfi

## GIRIS/CIKIS
- Giris (Check-in): {HOTEL_INFO['checkin_time']} - Kimlik belgesi gerekli
- Cikis (Check-out): {HOTEL_INFO['checkout_time']}
- Erken giris/gec cikis musaitlige bagli, ek ucrete tabi olabilir
- Kapi 23:00'da kapanir. Gec gelenler oda anahtarindaki numarayi arayabilir

## ODA TIPLERI ve FIYATLAR (Nakit/Havale, Serpme Kahvalti Dahil)
1. Standart Oda (25m2): 3.500 TL - 2 kisilik, tas duvarlar (1 adet)
2. Standart Bahce Manzarali Oda (25m2): 3.500 TL - 2 kisilik, bahce manzarasi (3 adet)
3. Standart Deniz Manzarali Oda (25m2): 3.500 TL - 2 kisilik, Foca Korfezi deniz manzarasi (4 adet)
4. Uc Kisilik Oda (30m2): 5.000 TL - Kucuk aileler icin ideal (2 adet)
5. Aile Odasi 4 Kisilik (50m2): 6.000 TL - 1 cift + 2 tek yatak, oturma alani (2 adet)
6. Aile Odasi 4 Kisilik Balkonlu (55m2): 6.000 TL - 1 cift + 2 tek yatak, oturma alani, ozel balkon (2 adet)
7. Superior 2 Kisilik Oda (35m2): 5.500 TL - Genis, oturma alani, balkon, deniz manzarasi (1 adet)
8. Superior 3 Kisilik Oda (35m2): 5.500 TL - 1 cift + 1 tek yatak, oturma alani, balkon (1 adet)

## ODA OZELLIKLERI
- Tum odalarda: Klima, LCD TV, mini buzdolabi, sac kurutma, ozel banyo, WiFi
- Banyo: Sivi sabun, sampuan, dus jeli, terlik
- Hos geldin ikrami: Su siseleri (2-4 adet), sallama cay, Nescafe, bambu karistirma cubugu, cikolatali mini Berliner
- Ust kat odalar: Daha sessiz ve manzarali (misafir tavsiyesi)

## OZEL GUN FIYATLARI (14 Subat, Yilbasi, Bayramlar)
- Standart / Bahce / Deniz Manzarali: 4.500 TL
- Uc Kisilik: 5.000 TL
- Superior / Superior 3 Kisilik: 5.500 TL
- Aile Odasi / Aile Balkonlu: 6.000 TL
- Ozel gunlerde %100 on odeme zorunludur

## RESTORAN (Antakya Sofrasi)
- Kahvalti: 08:30-11:00 (Serpme kahvalti + sucuklu yumurta + pisi dahil)
- Mutfak kapanisi: 22:00
- Restoran kapanisi: 23:00
- Otel musterisi olmasaniz da yemek yiyebilirsiniz
- Imza Yemekler: Konak Kofte, Sac Kavurma, Kunefe, Dallas Steak

## REZERVASYON ve ODEME
- Hafta ici: %50 kapora
- Hafta sonu/ozel gunler: %100 on odeme
- Odeme: Visa, Mastercard (web sitesi) veya Havale/EFT
- Banka: Ziraat Bankasi - Varol Oruk - IBAN: TR86 0001 0003 4454 7464 5450 08
- Yapi Kredi: TR72 0006 7010 0000 0010 5454 18
- Dekont sonrasi paylasimi gerekli, aciklama bos birakilmali

## IPTAL POLITIKASI
- 72 saat (3 gun) oncesine kadar: Ucretsiz iptal
- 72 saatten az: %100 ceza
- Ozel gunlerde: Her durumda %100 ceza (on odeme zorunlu)
- Gelmeyen misafirden %100 ucret tahsil edilir

## OTEL KURALLARI
- Sigara: Sadece belirlenmis acik alanlarda
- Evcil Hayvan: Kucuk irklar ucretsiz kabul edilir. Buyuk irklar icin balkonlu oda. Restoran kapali alanina giremez.
- Sessizlik Saati: 23:00-08:00
- Bebek yatagi ucretsiz, ek yatak konulmaz

## EK HIZMETLER
- Camasir servisi: Ucretli, ayni gun teslimat
- Transfer/ulasim: Resepsiyon araciligila ayarlanabilir
- Yuruyus parkurlari: Kozbeyli Koyu cevresinde dogayla ic ice
- Vale/otopark: Ucretsiz acik otopark

## CEVRE ve AKTIVITELER
- Foca Plajlari: 10-15 dk (Mersinaki, Sazlica, Seytan Hamami)
- Kozbeyli Koyu: Tarihi tas evler, dibek kahvesi, 600 yillik tarih
- Tarihi Yerler: Pers Mezarlari, Foca Kalesi, Athena Tapinagi
- Tekne turu, bisiklet, at binme, sarap tadimi

## ORGANIZASYONLAR
- Dugun, nisan, toplanti: 100 kisilik kapasite
- 30+ kisi icin ozel fiyat gorusmesi gerekir → yonetici hatti: {HOTEL_INFO['phone_booking']}

## ODULLER
- TripAdvisor Travelers' Choice 2020-2021 (Dunya 10., Avrupa 4.)
- Booking.com 8.8/10
- QM Awards - Turkiye'nin En Iyi Dort Mevsim Oteli

## ONEMLI KURAL
- Bilmedigin veya emin olmadigin bir bilgi sorulursa ASLA uydurmak yerine "Bu konuda kesin bilgi verebilmem icin sizi resepsiyonla gorustureyim: {HOTEL_INFO['phone']}" de.
- Fiyatlari her zaman guncel olarak yukaridaki listeden ver, tahmini fiyat verme.
- Rezervasyon icin her zaman {HOTEL_INFO['phone_booking']} numarasina yonlendir.
"""

INTENT_KEYWORDS = {
    "rooms": ["oda", "room", "fiyat", "price", "konaklama", "stay", "gecelik"],
    "menu": ["menu", "yemek", "food", "restoran", "restaurant", "kahvalti", "breakfast", "antakya"],
    "reservation": ["rezervasyon", "reservation", "booking", "musait", "available"],
    "cancellation": ["iptal", "cancel", "iade", "refund", "ceza", "penalty", "odeme", "payment"],
    "location": ["nerede", "where", "adres", "address", "ulasim", "nasil gelinir"],
    "local_guide": ["foca", "cevre", "gezi", "plaj", "beach", "tarihi", "cocuk", "aile"],
    "events": ["etkinlik", "event", "program", "organizasyon"],
    "general": ["merhaba", "hello", "hi", "selam", "bilgi", "info"],
}
