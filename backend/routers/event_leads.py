from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import db
from helpers import utcnow, new_id, clean_doc

router = APIRouter(tags=["event-leads"])


# ─── Kozbeyli Konagi Etkinlik Fikirleri ───
EVENT_IDEAS = [
    {
        "id": "wine_workshop",
        "name": "Sarap Tadim Workshop",
        "category": "workshop",
        "description": "Ege saraplarinin tanitildigi, sommelier esliginde sarap tadim etkinligi. Peynir ve zeytinyagi eslesmesi ile.",
        "target_audience": ["sarap_meraklilari", "gurme", "kurumsal"],
        "best_days": ["cumartesi", "pazar"],
        "best_months": ["mart", "nisan", "mayis", "eylul", "ekim", "kasim"],
        "capacity": "15-30 kisi",
        "duration": "2-3 saat",
        "price_range": "500-1500 TL/kisi",
        "revenue_potential": "yuksek",
        "needs": ["sommelier", "sarap tedarigi", "tadim bardaklari", "peynir tabagi"],
        "social_hashtags": ["SarapTadim", "WineWorkshop", "EgeSaraplari", "KozbeyliKonagi"],
    },
    {
        "id": "yoga_retreat",
        "name": "Yoga & Wellness Sabahi",
        "category": "wellness",
        "description": "Sabah yogasi + saglikli kahvalti paketi. Bahcede veya terasta yoga seansi, sonrasinda organik kahvalti.",
        "target_audience": ["yoga_gruplari", "wellness", "saglikli_yasam"],
        "best_days": ["cumartesi", "pazar"],
        "best_months": ["nisan", "mayis", "haziran", "eylul", "ekim"],
        "capacity": "10-20 kisi",
        "duration": "3-4 saat (yoga + kahvalti)",
        "price_range": "400-800 TL/kisi",
        "revenue_potential": "orta",
        "needs": ["yoga egitmeni", "mat", "kahvalti hazirligi", "ambiyan muzik"],
        "social_hashtags": ["YogaRetreat", "WellnessSabahi", "KozbeyliYoga", "FocaYoga"],
    },
    {
        "id": "pilates_morning",
        "name": "Pilates Sabah Seansi",
        "category": "wellness",
        "description": "Acik havada pilates seansi + detox smoothie + hafif brunch. Doga icinde pilates deneyimi.",
        "target_audience": ["pilates_gruplari", "wellness", "spor_meraklilari"],
        "best_days": ["cumartesi", "pazar", "hafta_ici"],
        "best_months": ["nisan", "mayis", "haziran", "temmuz", "agustos", "eylul"],
        "capacity": "8-15 kisi",
        "duration": "2-3 saat",
        "price_range": "350-700 TL/kisi",
        "revenue_potential": "orta",
        "needs": ["pilates egitmeni", "mat", "smoothie malzemeleri", "brunch"],
        "social_hashtags": ["Pilates", "AcikHavaPilates", "KozbeyliWellness", "FocaPilates"],
    },
    {
        "id": "cigar_night",
        "name": "Puro & Viski Gecesi",
        "category": "premium",
        "description": "Ozel puro tadim gecesi, premium viski esliginde. Puro uzmani rehberliginde farkli purolar denenir.",
        "target_audience": ["puro_gruplari", "premium", "erkek_gruplari", "kurumsal"],
        "best_days": ["cuma", "cumartesi"],
        "best_months": ["ocak", "subat", "mart", "ekim", "kasim", "aralik"],
        "capacity": "10-20 kisi",
        "duration": "3-4 saat",
        "price_range": "1000-3000 TL/kisi",
        "revenue_potential": "cok_yuksek",
        "needs": ["puro tedarigi", "viski secimi", "kul tablalari", "lounge ortam"],
        "social_hashtags": ["PuroGecesi", "CigarNight", "ViskiTadim", "KozbeyliPremium"],
    },
    {
        "id": "cooking_class",
        "name": "Ege Mutfagi Yemek Atolyesi",
        "category": "workshop",
        "description": "Sefle birlikte Ege mutfagi yemekleri yapma atolyesi. Ot yemekleri, zeytinyagilar, deniz urunleri.",
        "target_audience": ["gurme", "yemek_meraklilari", "turistler", "kurumsal"],
        "best_days": ["cumartesi", "pazar"],
        "best_months": ["mart", "nisan", "mayis", "haziran", "eylul", "ekim"],
        "capacity": "8-16 kisi",
        "duration": "3-4 saat",
        "price_range": "600-1200 TL/kisi",
        "revenue_potential": "yuksek",
        "needs": ["sef", "malzemeler", "mutfak ekipmani", "onlukler"],
        "social_hashtags": ["YemekAtolyesi", "EgeMutfagi", "CookingClass", "KozbeyliMutfak"],
    },
    {
        "id": "live_music_dinner",
        "name": "Canli Muzik & Aksam Yemegi",
        "category": "entertainment",
        "description": "Canli muzik esliginde ozel aksam yemegi. Jazz, akustik veya yerel muzik gruplari.",
        "target_audience": ["ciftler", "arkadasgrubu", "genel"],
        "best_days": ["cumartesi"],
        "best_months": ["tum_yil"],
        "capacity": "30-60 kisi",
        "duration": "4-5 saat",
        "price_range": "500-1000 TL/kisi",
        "revenue_potential": "yuksek",
        "needs": ["muzik grubu", "ses sistemi", "ozel menu", "dekorasyon"],
        "social_hashtags": ["CanliMuzik", "LiveMusic", "KozbeyliGece", "FocaGece"],
    },
    {
        "id": "wedding",
        "name": "Dugun Organizasyonu",
        "category": "organization",
        "description": "Tarihi tas otelde masalsi dugun. Bahce dugun, salon resepsiyon, konaklama paketi.",
        "target_audience": ["nisan_ciftleri", "dugun_planlayicilar"],
        "best_days": ["cumartesi", "pazar"],
        "best_months": ["mayis", "haziran", "temmuz", "agustos", "eylul"],
        "capacity": "50-150 kisi",
        "duration": "tam gun",
        "price_range": "Kisi basi 800-2000 TL",
        "revenue_potential": "cok_yuksek",
        "needs": ["dekorasyon", "catering", "ses_isik", "fotografci", "konaklama"],
        "social_hashtags": ["KozbeyliDugun", "TasOtelDugun", "FocaDugun", "KirDugunu"],
    },
    {
        "id": "engagement",
        "name": "Nisan Organizasyonu",
        "category": "organization",
        "description": "Samimi ve sikli nisan toreni. Bahce veya teras nisan, ozel menu, dekorasyon.",
        "target_audience": ["nisan_ciftleri", "aileler"],
        "best_days": ["cumartesi", "pazar"],
        "best_months": ["mart", "nisan", "mayis", "haziran", "eylul", "ekim"],
        "capacity": "20-80 kisi",
        "duration": "4-6 saat",
        "price_range": "Kisi basi 500-1200 TL",
        "revenue_potential": "yuksek",
        "needs": ["dekorasyon", "menu", "pasta", "fotografci"],
        "social_hashtags": ["KozbeyliNisan", "NisanOrganizasyonu", "FocaNisan"],
    },
    {
        "id": "corporate_meeting",
        "name": "Kurumsal Toplanti & Seminer",
        "category": "corporate",
        "description": "Sirket toplantisi, seminer, board meeting icin huzurlu ortam. Proyektor, WiFi, kahve molasi, ogle yemegi.",
        "target_audience": ["kurumsal", "sirketler", "yoneticiler"],
        "best_days": ["hafta_ici"],
        "best_months": ["tum_yil"],
        "capacity": "10-40 kisi",
        "duration": "tam gun veya yarim gun",
        "price_range": "400-1000 TL/kisi",
        "revenue_potential": "yuksek",
        "needs": ["projektor", "wifi", "kahve_molasi", "ogle_yemegi", "not_defterleri"],
        "social_hashtags": ["KurumsalToplanti", "CorporateRetreat", "KozbeyliKurumsal"],
    },
    {
        "id": "team_building",
        "name": "Team Building & Workshop",
        "category": "corporate",
        "description": "Takim calismalari, yaratici workshoplar, motivasyon etkinlikleri. Dogada aktiviteler + konaklama.",
        "target_audience": ["kurumsal", "ik_departmanlari", "startup"],
        "best_days": ["hafta_ici", "cumartesi"],
        "best_months": ["mart", "nisan", "mayis", "eylul", "ekim", "kasim"],
        "capacity": "15-50 kisi",
        "duration": "1-2 gun",
        "price_range": "800-2000 TL/kisi (konaklama dahil)",
        "revenue_potential": "cok_yuksek",
        "needs": ["aktivite_malzemeleri", "fasilitator", "konaklama", "yemekler"],
        "social_hashtags": ["TeamBuilding", "KurumsalWorkshop", "KozbeyliTeam"],
    },
    {
        "id": "networking_brunch",
        "name": "Networking Brunch",
        "category": "corporate",
        "description": "Is dunyasi networking etkinligi. Zengin brunch + tanitim konusmalari + kartvizit degisimi.",
        "target_audience": ["girisimciler", "kurumsal", "freelancer", "kadin_girisimciler"],
        "best_days": ["cumartesi", "pazar"],
        "best_months": ["tum_yil"],
        "capacity": "20-40 kisi",
        "duration": "3-4 saat",
        "price_range": "400-800 TL/kisi",
        "revenue_potential": "orta",
        "needs": ["brunch_menu", "mikrofon", "kartvizit_standi", "sponsor_alani"],
        "social_hashtags": ["NetworkingBrunch", "IsAgi", "KozbeyliNetworking"],
    },
    {
        "id": "art_workshop",
        "name": "Sanat Atolyesi (Resim/Seramik)",
        "category": "workshop",
        "description": "Resim veya seramik atolyesi, sanatci rehberliginde. Sarap esliginde resim gecesi de olabilir.",
        "target_audience": ["sanat_meraklilari", "ciftler", "arkadasgrubu"],
        "best_days": ["cumartesi", "pazar"],
        "best_months": ["tum_yil"],
        "capacity": "10-20 kisi",
        "duration": "2-3 saat",
        "price_range": "400-900 TL/kisi",
        "revenue_potential": "orta",
        "needs": ["sanatci_egitmen", "malzemeler", "tuval", "sarap"],
        "social_hashtags": ["SanatAtolyesi", "PaintNight", "KozbeyliSanat"],
    },
    {
        "id": "olive_oil_tasting",
        "name": "Zeytinyagi Tadim & Tur",
        "category": "workshop",
        "description": "Yerel zeytinyagi ureticileriyle tadim, zeytin hasat turu, zeytinyagi ve peynir eslesmesi.",
        "target_audience": ["gurme", "turistler", "saglikli_yasam"],
        "best_days": ["cumartesi", "pazar"],
        "best_months": ["ekim", "kasim", "aralik", "ocak"],
        "capacity": "10-25 kisi",
        "duration": "3-4 saat",
        "price_range": "400-800 TL/kisi",
        "revenue_potential": "orta",
        "needs": ["zeytinyagi_ureticisi", "tadim_bardaklari", "peynir_tabagi"],
        "social_hashtags": ["ZeytinyagiTadim", "OliveOilTasting", "EgeZeytinyagi"],
    },
    {
        "id": "photography_tour",
        "name": "Foca Fotograf Turu",
        "category": "experience",
        "description": "Profesyonel fotografci esliginde tarihi Foca sokaklarinda fotograf turu. Konakta kahvalti + tur.",
        "target_audience": ["fotograf_gruplari", "turistler", "sosyal_medya"],
        "best_days": ["cumartesi", "pazar"],
        "best_months": ["mart", "nisan", "mayis", "eylul", "ekim"],
        "capacity": "8-15 kisi",
        "duration": "4-5 saat",
        "price_range": "500-900 TL/kisi",
        "revenue_potential": "orta",
        "needs": ["fotografci_rehber", "kahvalti", "rota_plani"],
        "social_hashtags": ["FocaFotografTuru", "PhotographyTour", "KozbeyliDeneyim"],
    },
    {
        "id": "birthday_party",
        "name": "Dogum Gunu Partisi",
        "category": "organization",
        "description": "Ozel dogum gunu kutlamasi. Kisisellestirilmis menu, pasta, dekorasyon, surpriz organizasyon.",
        "target_audience": ["bireysel", "aileler"],
        "best_days": ["cumartesi", "pazar", "hafta_ici"],
        "best_months": ["tum_yil"],
        "capacity": "10-50 kisi",
        "duration": "4-6 saat",
        "price_range": "Kisi basi 400-1000 TL",
        "revenue_potential": "orta",
        "needs": ["pasta", "dekorasyon", "ozel_menu", "muzik"],
        "social_hashtags": ["DogumGunu", "KozbeyliKutlama", "BirthdayParty"],
    },
]

# ─── Hedef Kitle Gruplari (Lead Kaynaklari) ───
TARGET_GROUPS = [
    {"id": "yoga_gruplari", "name": "Yoga Gruplari", "platforms": ["instagram", "facebook", "whatsapp"], "search_tags": ["yoga izmir", "yoga foca", "yoga grubu", "kundalini yoga", "hatha yoga"], "message_tone": "huzurlu_davetkar"},
    {"id": "pilates_gruplari", "name": "Pilates Gruplari", "platforms": ["instagram", "facebook", "whatsapp"], "search_tags": ["pilates izmir", "reformer pilates", "mat pilates", "pilates studyo"], "message_tone": "enerjik_davetkar"},
    {"id": "puro_gruplari", "name": "Puro & Viski Meraklilari", "platforms": ["instagram", "facebook", "whatsapp"], "search_tags": ["puro kulup", "cigar club izmir", "viski tadim", "premium yasam"], "message_tone": "premium_ozel"},
    {"id": "sarap_meraklilari", "name": "Sarap Meraklilari", "platforms": ["instagram", "facebook"], "search_tags": ["sarap kulup", "wine tasting izmir", "sarap tadim", "sommelier"], "message_tone": "sofistike"},
    {"id": "kurumsal", "name": "Kurumsal Sirketler", "platforms": ["linkedin", "email"], "search_tags": ["sirket etkinlik", "kurumsal toplanti", "team building izmir", "offsite meeting"], "message_tone": "profesyonel"},
    {"id": "dugun_planlayicilar", "name": "Dugun Planlayicilari", "platforms": ["instagram", "whatsapp"], "search_tags": ["dugun organizasyon izmir", "wedding planner", "kir dugunu"], "message_tone": "romantik_sikli"},
    {"id": "nisan_ciftleri", "name": "Nisan Ciftleri", "platforms": ["instagram", "facebook"], "search_tags": ["nisan organizasyon", "nisan mekan izmir", "nisan yemegi"], "message_tone": "sicak_davetkar"},
    {"id": "gurme", "name": "Gurme & Yemek Meraklilari", "platforms": ["instagram", "tiktok", "facebook"], "search_tags": ["gurme izmir", "yemek atolyesi", "food lover", "ege mutfagi"], "message_tone": "lezzetli_cazip"},
    {"id": "sanat_meraklilari", "name": "Sanat Topluluklari", "platforms": ["instagram", "facebook"], "search_tags": ["resim atolyesi izmir", "seramik kursu", "sanat etkinlik"], "message_tone": "yaratici"},
    {"id": "fotograf_gruplari", "name": "Fotograf Gruplari", "platforms": ["instagram", "facebook"], "search_tags": ["fotograf grubu izmir", "street photography", "foca fotograf"], "message_tone": "gorsel_cazip"},
    {"id": "kadin_girisimciler", "name": "Kadin Girisimciler", "platforms": ["instagram", "linkedin"], "search_tags": ["kadin girisimci", "women in business izmir", "she means business"], "message_tone": "guclu_davetkar"},
    {"id": "startup", "name": "Startup & Teknoloji", "platforms": ["linkedin", "twitter"], "search_tags": ["startup izmir", "tech meetup", "girisimcilik", "hackathon"], "message_tone": "yenilikci"},
]

# ─── Mesaj Sablonlari ───
MESSAGE_TEMPLATES = {
    "huzurlu_davetkar": {
        "whatsapp": "Merhaba {group_name} ailesi 🧘‍♀️\n\nKozbeyli Konagi'nin huzurlu bahcesinde, dogayla ic ice bir {event_name} duzenliyoruz.\n\n📅 {date}\n⏰ {time}\n📍 Kozbeyli Konagi, Foca\n\nDoganin icinde, tarihi tas yapinin enerjisiyle muhteşem bir deneyim sizi bekliyor.\n\nDetaylar ve yer ayirtma icin bize yazin.\n\n🌿 Kozbeyli Konagi",
        "instagram": "Dogayla ic ice {event_name} deneyimi 🧘‍♀️✨\n\nKozbeyli Konagi'nin bahcesinde huzur dolu bir gun sizi bekliyor.\n\nBilgi icin DM atabilirsiniz.\n\n#KozbeyliKonagi #{event_tag} #FocaWellness",
    },
    "enerjik_davetkar": {
        "whatsapp": "Merhaba {group_name} 💪\n\nKozbeyli Konagi'nda acik havada {event_name} etkinligimiz var!\n\n📅 {date}\n⏰ {time}\n📍 Kozbeyli Konagi, Foca\n\nEgzersiz sonrasi saglikli brunch dahil!\n\nYer sinirli, hemen yerinizi ayirtin.\n\n💚 Kozbeyli Konagi",
        "instagram": "Acik havada {event_name} + saglikli brunch 🥗💪\n\nKozbeyli Konagi'nda enerji dolu bir gun!\n\nKatilim icin DM.\n\n#KozbeyliWellness #{event_tag} #AcikHava",
    },
    "premium_ozel": {
        "whatsapp": "Sayin {group_name} uyeleri,\n\nKozbeyli Konagi'nda ozel bir {event_name} duzenlemekten mutluluk duyariz.\n\n📅 {date}\n⏰ {time}\n📍 Kozbeyli Konagi Lounge, Foca\n\nSinirli kontenjan. Premium bir aksam icin yerinizi ayirtin.\n\n🏛️ Kozbeyli Konagi",
        "instagram": "Ozel {event_name} gecesi 🥃\n\nKozbeyli Konagi'nin tarihi atmosferinde premium bir deneyim.\n\nSinirli kontenjan - DM ile bilgi alin.\n\n#KozbeyliPremium #{event_tag} #PremiumDeneyim",
    },
    "sofistike": {
        "whatsapp": "Merhaba {group_name} 🍷\n\nKozbeyli Konagi'nda ozel bir {event_name} duzenliyoruz.\n\n📅 {date}\n⏰ {time}\n📍 Kozbeyli Konagi, Foca\n\nUzman esliginde essiz bir tadim deneyimi sizi bekliyor.\n\n🍇 Kozbeyli Konagi",
        "instagram": "Essiz bir {event_name} deneyimi 🍷✨\n\nKozbeyli Konagi'nda uzman esliginde unutulmaz bir etkinlik.\n\n#KozbeyliKonagi #{event_tag} #TadimDeneyimi",
    },
    "profesyonel": {
        "whatsapp": "Sayin {group_name},\n\nKozbeyli Konagi, kurumsal etkinlikleriniz icin essiz bir mekan sunuyor.\n\n{event_name} icin ozel paketlerimiz hakkinda bilgi almak ister misiniz?\n\n📍 Tarihi Foca'da huzurlu ortam\n🏨 Konaklama + toplanti salonu\n🍽️ Ozel menu secenekleri\n\nDetaylar icin bize ulasin.\n\n🏛️ Kozbeyli Konagi",
        "linkedin": "{event_name} icin ideal mekan: Kozbeyli Konagi\n\nFoca'nin tarihi dokusunda, huzurlu ortamda verimli toplanti ve etkinlikler.\n\n✅ Toplanti salonu + ekipman\n✅ Konaklama paketi\n✅ Ozel menu\n\nKurumsal tekliflerimiz icin iletisime gecin.\n\n#KurumsalEtkinlik #TeamBuilding #KozbeyliKonagi",
    },
    "romantik_sikli": {
        "whatsapp": "Merhaba {group_name} 💒\n\nHayalinizdeki {event_name} icin Kozbeyli Konagi'ni kesfetmenizi isteriz.\n\nTarihi tas yapimiz, masalsi bahcemiz ve ozel hizmetlerimizle unutulmaz bir gun yasayin.\n\n📸 Mekan gezisi icin randevu alin\n\n💐 Kozbeyli Konagi",
        "instagram": "Hayalinizdeki {event_name} burada gercek oluyor 💒✨\n\nKozbeyli Konagi'nin masalsi atmosferi sizi bekliyor.\n\nMekan gezisi icin DM atin.\n\n#KozbeyliDugun #{event_tag} #HayalMekan",
    },
    "sicak_davetkar": {
        "whatsapp": "Merhaba 🌸\n\n{event_name} icin Kozbeyli Konagi'ni dusunur musunuz?\n\nSamimi, sikli ve huzurlu bir ortamda ozel gununuzu kutlayin.\n\nMekan gezisi ve fiyat bilgisi icin bize yazin.\n\n🌺 Kozbeyli Konagi",
        "instagram": "Ozel gununuz icin ozel mekan 🌸\n\nKozbeyli Konagi'nda {event_name}.\n\nDM ile bilgi alin.\n\n#KozbeyliKonagi #{event_tag} #OzelGun",
    },
    "lezzetli_cazip": {
        "whatsapp": "Merhaba {group_name} 👨‍🍳\n\nKozbeyli Konagi'nda {event_name} duzenliyoruz!\n\n📅 {date}\n⏰ {time}\n📍 Kozbeyli Konagi Mutfagi, Foca\n\nSefimiz esliginde Ege lezzetlerini ogrenin ve tadini cikarin.\n\n🫒 Kozbeyli Konagi",
        "instagram": "Ege lezzetleri atolyesi 👨‍🍳🫒\n\n{event_name} - Kozbeyli Konagi'nda\n\nKatilim icin DM.\n\n#KozbeyliMutfak #{event_tag} #EgeLezzetleri",
    },
    "yaratici": {
        "whatsapp": "Merhaba {group_name} 🎨\n\nKozbeyli Konagi'nda ilham verici bir {event_name} etkinligimiz var!\n\n📅 {date}\n⏰ {time}\n📍 Kozbeyli Konagi, Foca\n\nSarap esliginde yaraticilik!\n\n🎭 Kozbeyli Konagi",
        "instagram": "Yaraticilik + tarihi atmosfer 🎨\n\n{event_name} - Kozbeyli Konagi'nda\n\nKatilim icin DM.\n\n#KozbeyliSanat #{event_tag} #Yaraticilik",
    },
    "gorsel_cazip": {
        "whatsapp": "Merhaba {group_name} 📸\n\nKozbeyli Konagi + tarihi Foca sokaklari = mukemmel kareler!\n\n{event_name} icin profesyonel eslik + kahvalti dahil.\n\n📅 {date}\n📍 Kozbeyli Konagi, Foca\n\nYerinizi ayirtin.\n\n📷 Kozbeyli Konagi",
        "instagram": "Fotograf tutkunleri icin ozel tur 📸\n\n{event_name} - Kozbeyli Konagi & Foca\n\nKatilim icin DM.\n\n#FocaFotograf #{event_tag} #KozbeyliKareler",
    },
    "guclu_davetkar": {
        "whatsapp": "Merhaba {group_name} 💼\n\nKozbeyli Konagi'nda guclendirici bir {event_name} duzenliyoruz.\n\n📅 {date}\n📍 Kozbeyli Konagi, Foca\n\nIlham verici konusmalar + networking + brunch.\n\nKatilim icin yazin.\n\n✨ Kozbeyli Konagi",
        "instagram": "{event_name} - Guclu kadinlar bir arada 💼✨\n\nKozbeyli Konagi'nda networking.\n\nBilgi icin DM.\n\n#KadinGirisimci #{event_tag} #Networking",
    },
    "yenilikci": {
        "whatsapp": "Merhaba {group_name} 🚀\n\nKozbeyli Konagi'nda {event_name} organizasyonu planliyoruz.\n\nTarihi mekanda yenilikci fikirler!\n\n📅 {date}\n📍 Foca, Izmir\n\nDetaylar icin yazin.\n\n💡 Kozbeyli Konagi",
        "instagram": "Inovasyon tarihi mekanla bulusuyor 🚀\n\n{event_name} - Kozbeyli Konagi'nda\n\nDM ile bilgi.\n\n#Startup #{event_tag} #KozbeyliInovasyon",
    },
}


class LeadCreate(BaseModel):
    group_name: str
    group_type: str  # yoga_gruplari, pilates_gruplari, etc.
    platform: str  # instagram, facebook, whatsapp, linkedin
    contact_info: str = ""  # username, phone, email
    notes: Optional[str] = None
    target_event: Optional[str] = None  # event idea id


class LeadUpdate(BaseModel):
    group_name: Optional[str] = None
    status: Optional[str] = None  # new, contacted, interested, booked, lost
    notes: Optional[str] = None
    target_event: Optional[str] = None
    last_contact_date: Optional[str] = None
    next_followup: Optional[str] = None


class OutreachRequest(BaseModel):
    lead_id: str
    event_id: str
    platform: str  # whatsapp, instagram, linkedin
    date: Optional[str] = None
    time: Optional[str] = None


# ─── Endpoints ───

@router.get("/event-leads/ideas")
async def get_event_ideas(category: Optional[str] = None):
    """Get all event ideas with optional category filter"""
    ideas = EVENT_IDEAS
    if category:
        ideas = [i for i in ideas if i["category"] == category]
    categories = list(set(i["category"] for i in EVENT_IDEAS))
    return {"ideas": ideas, "categories": categories}


@router.get("/event-leads/target-groups")
async def get_target_groups():
    """Get all target audience groups"""
    return {"groups": TARGET_GROUPS}


@router.post("/event-leads/generate-message")
async def generate_outreach_message(data: OutreachRequest):
    """Generate an outreach message for a lead + event combo"""
    # Find the lead
    lead = await db.event_leads.find_one({"id": data.lead_id}, {"_id": 0})
    if not lead:
        raise HTTPException(404, "Lead bulunamadi")

    # Find event idea
    event = next((e for e in EVENT_IDEAS if e["id"] == data.event_id), None)
    if not event:
        raise HTTPException(404, "Etkinlik fikri bulunamadi")

    # Find target group for tone
    group = next((g for g in TARGET_GROUPS if g["id"] == lead.get("group_type")), None)
    tone = group["message_tone"] if group else "sicak_davetkar"

    # Get template
    templates = MESSAGE_TEMPLATES.get(tone, MESSAGE_TEMPLATES["sicak_davetkar"])
    platform = data.platform
    if platform not in templates:
        platform = list(templates.keys())[0]

    message = templates[platform]
    message = message.replace("{group_name}", lead.get("group_name", ""))
    message = message.replace("{event_name}", event["name"])
    message = message.replace("{event_tag}", event["social_hashtags"][0] if event["social_hashtags"] else "KozbeyliKonagi")
    message = message.replace("{date}", data.date or "[Tarih belirlenecek]")
    message = message.replace("{time}", data.time or "[Saat belirlenecek]")

    return {
        "message": message,
        "platform": platform,
        "tone": tone,
        "event": event["name"],
        "lead": lead["group_name"],
    }


@router.get("/event-leads/leads")
async def list_leads(status: Optional[str] = None, group_type: Optional[str] = None):
    query = {}
    if status:
        query["status"] = status
    if group_type:
        query["group_type"] = group_type
    leads = await db.event_leads.find(query, {"_id": 0}).sort("created_at", -1).to_list(200)
    return {"leads": leads}


@router.post("/event-leads/leads")
async def create_lead(data: LeadCreate):
    lead = {
        "id": new_id(),
        **data.model_dump(),
        "status": "new",
        "last_contact_date": None,
        "next_followup": None,
        "messages_sent": 0,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    await db.event_leads.insert_one(lead)
    return clean_doc(lead)


@router.patch("/event-leads/leads/{lead_id}")
async def update_lead(lead_id: str, data: LeadUpdate):
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(400, "Guncellenecek alan yok")
    updates["updated_at"] = utcnow()
    result = await db.event_leads.update_one({"id": lead_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(404, "Lead bulunamadi")
    return await db.event_leads.find_one({"id": lead_id}, {"_id": 0})


@router.delete("/event-leads/leads/{lead_id}")
async def delete_lead(lead_id: str):
    result = await db.event_leads.delete_one({"id": lead_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Lead bulunamadi")
    return {"success": True}


@router.post("/event-leads/leads/{lead_id}/log-contact")
async def log_contact(lead_id: str):
    """Log that a message was sent to this lead"""
    result = await db.event_leads.update_one(
        {"id": lead_id},
        {
            "$set": {"last_contact_date": utcnow(), "status": "contacted", "updated_at": utcnow()},
            "$inc": {"messages_sent": 1},
        }
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Lead bulunamadi")
    return await db.event_leads.find_one({"id": lead_id}, {"_id": 0})


@router.get("/event-leads/stats")
async def get_lead_stats():
    total = await db.event_leads.count_documents({})
    new = await db.event_leads.count_documents({"status": "new"})
    contacted = await db.event_leads.count_documents({"status": "contacted"})
    interested = await db.event_leads.count_documents({"status": "interested"})
    booked = await db.event_leads.count_documents({"status": "booked"})
    lost = await db.event_leads.count_documents({"status": "lost"})

    # Group type breakdown
    pipeline = [
        {"$group": {"_id": "$group_type", "count": {"$sum": 1}}},
    ]
    group_counts = {}
    async for doc in db.event_leads.aggregate(pipeline):
        group_counts[doc["_id"]] = doc["count"]

    return {
        "total": total,
        "new": new,
        "contacted": contacted,
        "interested": interested,
        "booked": booked,
        "lost": lost,
        "by_group": group_counts,
    }


@router.get("/event-leads/suggestions")
async def get_event_suggestions():
    """Get AI-powered event suggestions based on current month and day"""
    from datetime import datetime
    now = datetime.now()
    month = now.strftime("%B").lower()
    month_tr_map = {
        "january": "ocak", "february": "subat", "march": "mart",
        "april": "nisan", "may": "mayis", "june": "haziran",
        "july": "temmuz", "august": "agustos", "september": "eylul",
        "october": "ekim", "november": "kasim", "december": "aralik",
    }
    current_month = month_tr_map.get(month, "mart")
    day_of_week = now.weekday()  # 0=Monday
    is_weekend = day_of_week >= 4  # Friday+

    suggested = []
    for idea in EVENT_IDEAS:
        months = idea.get("best_months", [])
        if "tum_yil" in months or current_month in months:
            score = 0
            if idea["revenue_potential"] == "cok_yuksek":
                score += 3
            elif idea["revenue_potential"] == "yuksek":
                score += 2
            else:
                score += 1

            days = idea.get("best_days", [])
            if is_weekend and ("cumartesi" in days or "cuma" in days):
                score += 1
            if not is_weekend and "hafta_ici" in days:
                score += 1

            suggested.append({**idea, "score": score})

    suggested.sort(key=lambda x: x["score"], reverse=True)
    return {"suggestions": suggested[:8], "current_month": current_month}
