"""
Kozbeyli Konagi - Zenginlestirilmis Bilgi Bankasi
Guncel fiyatlar, mesaj sablonlari ve otel bilgileri
"""

# Guncel Oda Fiyatlari (Nakit/Havale - TL)
ROOM_PRICES_TRY = {
    "standart": 3500,
    "standart_bahce_manzarali": 3500,
    "standart_deniz_manzarali": 3500,
    "uc_kisilik": 5000,
    "aile_odasi": 6000,
    "aile_odasi_balkonlu": 6000,
    "superior": 5500,
    "superior_uc_kisilik": 5500,
}

# Ozel Gun Fiyatlari (14 Subat, Yilbasi vb.)
SPECIAL_DAY_PRICES_TRY = {
    "standart": 4500,
    "standart_bahce_manzarali": 4500,
    "standart_deniz_manzarali": 4500,
    "uc_kisilik": 5000,
    "aile_odasi": 6000,
    "aile_odasi_balkonlu": 6000,
    "superior": 5500,
    "superior_uc_kisilik": 5500,
}

# Fix Menu Fiyatlari
FIX_MENU_PRICES = {
    "standard": {
        "alkolu_menu": 2750,
        "sinirsiz_alkolu": 5500,
    },
    "sevgililer_gunu": {
        "alkolu_menu": 3500,
        "sinirsiz_alkolu": 6000,
    }
}

# Banka Bilgileri
BANK_ACCOUNTS = [
    {
        "bank": "Ziraat Bankasi",
        "account_holder": "Varol Oruk",
        "iban": "TR86 0001 0003 4454 7464 5450 08",
        "branch": "Foca Subesi",
    },
    {
        "bank": "Yapi Kredi Bankasi",
        "account_holder": "Varol Oruk",
        "iban": "TR72 0006 7010 0000 0010 5454 18",
        "branch": "Izmir",
    }
]

# WhatsApp Mesaj Sablonlari
MESSAGE_TEMPLATES = {
    "standart_fiyat_bilgisi": """Merhabalar efendim,
menumuz asagidaki baglanti uzerinden incelenebilmektedir.

Konaklama fiyatlarimiz (serpme kahvalti dahil):
* Standart Oda: {standart} TL
* Standart Bahce Manzarali Oda: {standart_bahce_manzarali} TL
* Standart Deniz Manzarali Oda: {standart_deniz_manzarali} TL
* Uc Kisilik Oda: {uc_kisilik} TL
* Aile Odasi (4 Kisilik): {aile_odasi} TL
* Aile Odasi (4 Kisilik) Balkonlu: {aile_odasi_balkonlu} TL
* Superior Oda: {superior} TL
* Superior 3 Kisilik Oda: {superior_uc_kisilik} TL

Tum oda fiyatlarimiza serpme kahvalti, sucuklu yumurta ve pisi dahildir.

Otel web sitemiz:
https://kozbeylikonagi.com/tr-tr/

Restoran menumuz:
https://thefoost.com/kozbeyli-konagi/

Dilerseniz rezervasyon ve detaylar icin memnuniyetle yardimci olabilirim.""",

    "sevgililer_gunu": """Merhabalar efendim,
14 Subat Sevgililer Gunu icin ozel olarak hazirladigimiz menumuzu asagidaki baglanti uzerinden inceleyebilirsiniz.
Bu ozel gunde restoranimizda yalnizca fix menu hizmeti sunulacak olup, alakart servis bulunmamaktadir.

14 Subat Fix Menu Fiyati:
* Kisi basi alkol ve yemek dahil: 3.500 TL

Konaklama fiyatlarimiz (kahvalti dahil):
* Standart / Bahce / Deniz Manzarali Oda: 4.500 TL
* Uc Kisilik Oda: 5.000 TL
* Superior / Superior 3 Kisilik Oda: 5.500 TL
* Aile Odasi / Aile Odasi Balkonlu: 6.000 TL

Tum oda fiyatlarimiza serpme kahvalti, sucuklu yumurta ve pisi dahildir.

Otel web sitemiz:
https://kozbeylikonagi.com/tr-tr/

Restoran menumuz:
https://thefoost.com/kozbeyli-konagi/

Dilerseniz 14 Subat rezervasyonlari ve detaylar icin memnuniyetle yardimci olabilirim.""",

    "etkinlik_bildirimi": """Merhabalar efendim,
{tarih} tarihinde duzenlenecek etkinligimiz icin hazirladigimiz menuyu asagidaki baglanti uzerinden inceleyebilirsiniz.

Bu tarihte restoranimizda fix menu hizmeti sunulacaktir.

{tarih} Fix Menu Fiyatlari:
* Kisi basi yemek menusu: {yemek_fiyat} TL
* Kisi basi sinirsiz alkolu yemek menusu: {alkol_fiyat} TL

Konaklama fiyatlarimiz (kahvalti dahil):
* Standart / Bahce / Deniz Manzarali Oda: {standart} TL
* Uc Kisilik Oda: {uc_kisilik} TL
* Superior / Superior 3 Kisilik Oda: {superior} TL
* Aile Odasi / Aile Odasi Balkonlu: {aile_odasi} TL

Tum oda fiyatlarimiza serpme kahvalti, sucuklu yumurta ve pisi dahildir.

Otel web sitemiz:
https://kozbeylikonagi.com/tr-tr/

Restoran menumuz:
https://thefoost.com/kozbeyli-konagi/

Dilerseniz {tarih} rezervasyonlari ve detaylar icin memnuniyetle yardimci olabilirim.""",

    "rezervasyon_onay": """Tabii efendim, {tarih} icin {kisi_sayisi} kisilik oda & kahvalti konaklamanizi sizler adina ayiriyorum.

Toplam {toplam_ucret} TL tutarindaki ucretin tamaminim on odeme olarak iletilmesini rica ederiz. Odeme sonrasi dekontu paylasmanizi, aciklama kismi bos birakilmanizi onemle rica ederiz.

Ayrica aksam yemegi icin masanizi manzara tarafinda mi yoksa somine yaninda mi tercih edersiniz, bildirmenizi rica ederim.

Alkol tercihiniz raki mi yoksa sarap mi olacaktir efendim?
Hazirligimizi buna gore yapabilmemiz icin bilgilendirmenizi rica ederiz.""",

    "check_out_tesekkur": """Degerli Misafirimiz,

Kozbeyli Konagi'nda bizimle gecirilecek gunu sectiginiz icin tesekkur ederiz.

Deneyiminizle ilgili geri bildiriminizi almak isteriz. Google yorumlariniz bizim icin cok degerlidir:
[Google Maps Linki]

Tekrar gorusmek dilegiyle,
Kozbeyli Konagi Ailesi""",

    "hatirlama": """Sayin {misafir_adi},

Kozbeyli Konagi'ndaki {tarih} tarihli rezervasyonunuzu hatirlatmak isteriz.

Giris saatimiz: 14:00
Cikis saatimiz: 12:00

Herhangi bir sorunuz veya ozel talebiniz icin bizimle iletisime gecebilirsiniz.

Gorusmek uzere!
Kozbeyli Konagi"""
}

# Detayli Otel Bilgi Rehberi
HOTEL_KNOWLEDGE_BASE = {
    "genel_bilgiler": {
        "isim": "Kozbeyli Konagi",
        "tur": "Butik Tas Otel",
        "adres": "Kozbeyli Koyu, Kozbeyli Kume Evleri No:188, Foca, Izmir, Turkiye",
        "telefon": "+90 (232) 826 11 12",
        "gsm": "+90 532 234 26 86",
        "email": "info@kozbeylikonagi.com",
        "website": "www.kozbeylikonagi.com",
        "instagram": "@kozbeylikonagi",
        "tarihce": "14 yillik bir aile isletmesiyiz. Konagimiz tamamen Foca tasindan insa edilmistir.",
        "konsept": "Misafirlerimiz, otel musterisi olmasalar dahi restoranimizdan ogle, aksam yemegi ve serpme kahvalti hizmetlerinden faydalanabilirler.",
        "manzara": "Otelimiz, Kozbeyli Koyu'nun tepelerinde yer almakta olup Foca Korfezi'ne panoramik bir manzara sunmaktadir.",
    },

    "oda_bilgileri": {
        "toplam_oda": 16,
        "dagilim": {
            "standart": 1,
            "standart_bahce_manzarali": 3,
            "standart_deniz_manzarali": 4,
            "uc_kisilik": 2,
            "aile_odasi": 2,
            "aile_odasi_balkonlu": 2,
            "superior": 1,
            "superior_uc_kisilik": 1,
        },
        "kahvalti_konsepti": "Oda + serpme kahvalti seklinde hizmet verilmektedir. Kahvalti yalnizca konaklamanizi takip eden sabah servis edilir.",
        "ek_yatak": "Odalara ek yatak konulmaz; kapasite oda tipine goredir. Bebek yatagi ucretsizdir.",
    },

    "oda_tipleri": {
        "standart": {
            "metrekare": 25,
            "yatak": "1 adet cift kisilik yatak",
            "manzara": "Standart",
            "ozellikler": ["Mini buzdolabi", "Klima", "Televizyon", "Ozel banyo"],
            "ikram": "2 adet su, sallama cay, nescafe, cikolatali mini berliner",
            "fiyat": 3500,
            "adet": 1,
        },
        "standart_bahce_manzarali": {
            "metrekare": 25,
            "yatak": "1 adet cift kisilik yatak",
            "manzara": "Bahce manzarasi",
            "ozellikler": ["Mini buzdolabi", "Klima", "Televizyon", "Ozel banyo"],
            "ikram": "2 adet su, sallama cay, nescafe, cikolatali mini berliner",
            "fiyat": 3500,
            "adet": 3,
        },
        "standart_deniz_manzarali": {
            "metrekare": 25,
            "yatak": "1 adet cift kisilik yatak",
            "manzara": "Foca Korfezi deniz manzarasi",
            "ozellikler": ["Mini buzdolabi", "Klima", "Televizyon", "Ozel banyo"],
            "ikram": "2 adet su, sallama cay, nescafe, cikolatali mini berliner",
            "fiyat": 3500,
            "adet": 4,
        },
        "uc_kisilik": {
            "metrekare": 30,
            "yatak": "Uc kisilik yatak duzeni",
            "manzara": "Karisik",
            "ozellikler": ["Mini buzdolabi", "Klima", "Televizyon", "Ozel banyo"],
            "ikram": "3 adet su, sallama cay, nescafe, cikolatali mini berliner",
            "fiyat": 5000,
            "adet": 2,
        },
        "aile_odasi": {
            "metrekare": 50,
            "yatak": "1 cift kisilik + 2 tek kisilik yatak",
            "manzara": "Karisik",
            "ozellikler": ["Mini buzdolabi", "Klima", "Televizyon", "Ozel banyo", "Oturma alani"],
            "ikram": "4 adet su, sallama cay, nescafe, cikolatali mini berliner",
            "fiyat": 6000,
            "adet": 2,
        },
        "aile_odasi_balkonlu": {
            "metrekare": 55,
            "yatak": "1 cift kisilik + 2 tek kisilik yatak",
            "manzara": "Karisik",
            "ozellikler": ["Mini buzdolabi", "Klima", "Televizyon", "Ozel banyo", "Oturma alani", "Balkon"],
            "ikram": "4 adet su, sallama cay, nescafe, cikolatali mini berliner",
            "fiyat": 6000,
            "adet": 2,
        },
        "superior": {
            "metrekare": 35,
            "yatak": "1 cift kisilik yatak",
            "manzara": "Deniz manzarasi",
            "ozellikler": ["Mini buzdolabi", "Klima", "Televizyon", "Ozel banyo", "Oturma alani", "Balkon"],
            "ikram": "3 adet su, sallama cay, nescafe, cikolatali mini berliner",
            "fiyat": 5500,
            "adet": 1,
        },
        "superior_uc_kisilik": {
            "metrekare": 35,
            "yatak": "1 cift kisilik + 1 tek kisilik yatak",
            "manzara": "Deniz manzarasi",
            "ozellikler": ["Mini buzdolabi", "Klima", "Televizyon", "Ozel banyo", "Oturma alani", "Balkon"],
            "ikram": "3 adet su, sallama cay, nescafe, cikolatali mini berliner",
            "fiyat": 5500,
            "adet": 1,
        },
    },

    "giris_cikis": {
        "giris_saati": "14:00",
        "cikis_saati": "12:00",
        "erken_giris": "Resepsiyonun musaitlik durumuna gore, ek ucrete tabi olabilir",
        "gec_cikis": "Resepsiyonun musaitlik durumuna gore, ek ucrete tabi olabilir",
        "guvenlik": "Otelimizin giris kapilari guvenlik nedeniyle saat 23:00'ten sonra kapanmaktadir.",
        "gece_girisi": "23:00 sonrasi girislerde, oda anahtarinizin arkasinda yer alan cep telefonu numarasini arayarak kapinin otomatik acilmasini saglayabilirsiniz.",
    },

    "rezervasyon_odeme": {
        "on_odeme_hafta_ici": "%50 kapora",
        "on_odeme_hafta_sonu": "%100 tam odeme",
        "odeme_yontemleri": ["Visa", "Mastercard", "Havale", "EFT"],
        "iptal_politikasi": "Varisden 72 saat oncesine kadar ucretsiz iptal. Sonrasinda yapilan iptallerde ucret iadesi yapilmaz.",
    },

    "otel_kurallari": {
        "sigara": "Odalar ve kapali alanlarda sigara icmek yasaktir. Acik alanda belirlenen sigara alanlari mevcuttur.",
        "evcil_hayvan": "Kucuk irk evcil hayvanlar kabul edilmektedir. Buyuk irklar icin balkonlu odalar verilebilir.",
        "gurultu": "23:00 - 08:00 saatleri arasi sessizlik saatidir.",
    },

    "olanaklar": {
        "bahce": "Genis bahcemizde salincak, hamak ve ozel fotograf cekim koseleri vardir.",
        "restoran": {
            "kahvalti": "08:30-11:00",
            "mutfak_kapaniş": "22:00",
            "restoran_kapaniş": "23:00",
        },
        "wifi": "Tesis genelinde ucretsiz hizli internet erisimi",
        "otopark": "Misafirlerimiz icin ucretsiz otopark",
        "guvenlik": "7/24 kamera sistemi ve guvenlik personeliyle hizmet",
    },

    "yakin_yerler": {
        "foca_plajlari": "10-15 dk aracla",
        "kozbeyli_merkez": "Tarihi tas evler, el yapimi hediyelik esya dukkanlari, yerel pazarlar, dibek kahvesi",
        "tarihi_yerler": "Pers Mezarlari, Foca Kalesi, antik kalintilar",
    },

    "ek_hizmetler": {
        "camasirhane": "Ucretli, genelde ayni gun teslim",
        "organizasyon": "Dugun, nisan, toplanti ve grup yemekleri icin bahce & restoran kapasitesi (100 kisilik)",
    },

    "acil_durumlar": {
        "eskalasyon_kosullari": [
            "30+ kisilik grup/organizasyon",
            "Fiyat/komisyon anlasmazligi",
            "Overbooking",
            "Hukuki/medyatik durum",
            "Elektrik, su, gaz kesintisi",
            "Guvenlik veya saglik acilleri",
        ],
        "yonetici_hatti": "+90 (232) 826 11 12 / +90 532 234 26 86",
    },
}

# Fix Menu Icerik Sablonu
FIX_MENU_TEMPLATE = {
    "baslangiclar": [
        "Antakya'dan Zahter",
        "Koy Usulu Kirma Yesil Zeytin ve Soguk Sikim Zeytinyagi",
        "(Kizarmis Rustik Koy Ekmegi ile Servis Edilir.)",
    ],
    "mezeler": [
        "Havuc Tarator",
        "Visneli Yaprak Sarma",
        "Antakya Biberli Atom",
        "Zeytinyagli & Domatesli Deniz Borulcesi",
    ],
    "salata": [
        "Roka Salatasi",
        "(Kuru Incir, Ezine Peyniri, Ceviz)",
        "Balsamic Glaze Sos ile Servis Edilir.",
    ],
    "ara_sicak": [
        "Pastirmali Kars Kasarli Pacanga Boregi",
    ],
    "ana_yemek": [
        "Konak Kofte (200g) veya Konak Sac Kavurma (150g)",
        "(Patates Puresi Tabani, Biberiye ve Kavrulmus File Badem ile Servis Edilir.)",
    ],
    "tatli": [
        "Antep Fistikli Kaymakli Kunefe",
    ],
    "alkol_seenekleri": {
        "2_kisi": "35 cl Raki (Efe Gold/Beylerbeyi Mavi) veya 70 cl Kirmizi Sarap",
        "3_kisi": "50 cl Raki (Efe Gold/Beylerbeyi Mavi)",
        "4_kisi": "70 cl Raki (Efe Gold/Beylerbeyi Mavi) veya 2 Adet 70 cl Kirmizi Sarap",
    },
}
