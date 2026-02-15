# Kozbeyli Konagi - Otel Yonetim Sistemi PRD

## Problem Statement
Kozbeyli Konagi (Izmir/Foca) butik tas otel icin kapsamli dijital yonetim ekosistemi.
GitHub repo: https://github.com/No3214/BillionDollar

## Tech Stack
- **Frontend:** React 19, TailwindCSS, Shadcn UI, Framer Motion
- **Backend:** FastAPI, Motor (async MongoDB), 24 modular routers
- **Database:** MongoDB (persistent)
- **AI:** Google Gemini 2.5 Flash (emergentintegrations)
- **Auth:** JWT + bcrypt, role-based (admin/reception/kitchen/staff)
- **Admin Theme:** Kozbeyli gold (#C4972A) on dark (#0a0a0f)
- **QR Menu Theme:** Kozbeyli Green (#515249 olive, #F8F5EF cream, Alifira font)

## Users
- 3 kisi (otel sahibi + 2 yonetici) + personel rolleri
- Misafirler (QR Menu erisimi, auth gerektirmez)

## Implementation Status

### Faz 1-4: Temel Sistem (TAMAMLANDI)
- Dashboard, Room/Guest/Reservation CRUD, AI Chatbot (Gemini)
- Staff/Shifts, Events, Housekeeping, Knowledge Base
- Restaurant Menu, WhatsApp/Instagram webhooks
- Campaigns, Foca Guide, i18n (5 dil), KVKK

### Faz 5: Google Yorum Yanitlayici (TAMAMLANDI)
- AI review response (anti-hallucination, 3 ton secenegi)

### Faz 6: Mimari Yenileme + Yeni Ozellikler (TAMAMLANDI)
- Backend refactoring: Monolitik -> 19+ modular router
- Dinamik Fiyatlama, Masa Rez., Misafir Dongusu
- Admin Auth + RBAC (4 rol), Otomasyon Botlari

### Faz 7: QR Menu Sistemi + Logo (TAMAMLANDI)
- Public menu sayfasi (/menu), beyaz logo, 16 kategori, 100 urun
- Admin menu CRUD + tema editoru

### Faz 8: QR Menu Guncel Veri + Sosyal Medya Yayinlayici (TAMAMLANDI - Feb 2026)

**QR Menu Tam Guncelleme:**
- PDF'den cikarilan guncel menu verisi: 100 urun, 16 kategori
- Yeni kategoriler: Ekstralar, Peynir Tabagi, Ara Sicaklar, Kokteyller
- Beyaz logo (KOZBEYLI_BEYAZ_LOGO.png) entegrasyonu
- Premium UI: Framer Motion animasyonlar, staggered reveal
- Arama fonksiyonu (anlik filtreleme)
- Mobil oncelikli responsive tasarim
- Yapisan kategori navigasyonu

**Sosyal Medya Yayinlayici:**
- Gonderi CRUD (olustur/duzenle/sil/yayinla)
- 5 gonderi turu: Genel, Promosyon, Etkinlik, Menu Vitrin, Duyuru
- 4 platform secimi: Instagram, Facebook, X (Twitter), WhatsApp
- Canli cerceve onizleme (5 stil: Varsayilan, Elegans, Cesur, Minimal, Senlik)
- Otomatik hashtag sablonlari
- Durum yonetimi: Taslak -> Planlanmis -> Yayinlandi
- Istatistik paneli
- Kopyalama ozelligi (icerik + hashtag)
- **NOT: Sosyal medya paylasimi MOCK - DB'de isaretler ama gercek platforma gondermez**

### Tests: Backend 15/15 (%100), Frontend %100 - Iteration 6

### Faz 9: Sosyal Medya Gelistirmeleri (TAMAMLANDI - Feb 2026)
- TikTok ve LinkedIn platformlari eklendi (toplam 6 platform)
- Gorsel: Dosya yukleme yerine Google Drive linki destegi
- Frame preview'da gorsel destegi
- QR Menu renkleri: Altin/sari tonlari kaldirildi, sadece beyaz/bej/yesil

### Faz 10: Masa Rezervasyon Sistemi Yenileme (TAMAMLANDI - Feb 2026)
- 19 masa tanimli: 13 adet 2-3 kisilik, 6 adet 4 kisilik
- Ogun bazli sure ayarlari:
  - Kahvalti: 2 saat (08:00-10:30)
  - Oglen: 2 saat (12:00-14:00)
  - Aksam: 4 saat (18:00-20:30)
- Akilli masa atama (kisi sayisina gore en uygun masa)
- Gunluk goruntuleme modu (tum masalarin durumu)
- Cakisma kontrolu (ayni masa ayni saatte iki rezervasyon olmaz)
- Ic/dis mekan ayrimi

### Faz 11: AI Bilgi Zenginlestirmesi + Mutfak Dashboard (TAMAMLANDI - Feb 2026)

**AI Asistani Bilgi Zenginlestirmesi:**
- Guncel oda fiyatlari entegre edildi (3.000-6.000 TL araliginda)
- Ozel gun fiyatlari (14 Subat, Yilbasi, Bayramlar) tanimlandi
- Detayli otel bilgi rehberi eklendi (16 oda, giris/cikis kurallari, olanaklar)
- WhatsApp mesaj sablonlari olusturuldu (fiyat bildirimi, rezervasyon onay, hatirlama)
- Banka hesap bilgileri guncellendi (Ziraat + Yapi Kredi)
- Fix Menu sablonlari ve fiyatlari eklendi
- GEMINI_SYSTEM_PROMPT zenginlestirildi (tum guncel bilgilerle)

**Mutfak Dashboard:**
- Yeni sayfa: KitchenPage.js
- Siparis olusturma (oda servisi, restoran, etkinlik, paket)
- Siparis durumu takibi (Bekliyor -> Hazirlaniyor -> Hazir -> Servis Edildi)
- Oncelik sistemi (dusuk, normal, yuksek, acil)
- Otomatik yenileme (30 saniye)
- Bildirimler (acil siparisler, 15+ dakika bekleyen siparisler)
- Gunluk ozet istatistikleri
- API: /api/kitchen/orders, /api/kitchen/summary, /api/kitchen/notifications

### Tests: Backend 17/17 (%100), Frontend %100

## Architecture
```
backend/
├── server.py          (thin orchestrator)
├── database.py        (MongoDB connection)
├── helpers.py         (utcnow, new_id, clean_doc)
├── config.py          (env vars)
├── models.py          (Pydantic models)
├── hotel_data.py      (static hotel data - UPDATED)
├── knowledge_seed_data.py  (NEW: Message templates, knowledge base)
├── menu_seed_data.py  (Updated menu data - 100 items, 16 cats)
├── gemini_service.py  (Gemini AI)
└── routers/
    ├── auth.py, hotel.py, rooms.py, guests.py
    ├── reservations.py, tasks.py, events.py
    ├── housekeeping.py, staff.py, knowledge.py
    ├── chatbot.py, messages.py, campaigns.py
    ├── reviews.py, settings.py, pricing.py
    ├── table_reservations.py, lifecycle.py
    ├── automation.py
    ├── public_menu.py    (Public QR menu)
    ├── menu_admin.py     (Admin menu CRUD)
    ├── social_media.py   (Social media publisher)
    └── kitchen.py        (NEW: Kitchen dashboard)

frontend/
├── public/
│   ├── logo.jpeg
│   ├── fonts/Alifira.ttf
│   └── brand/KOZBEYLI_BEYAZ_LOGO.png
└── src/
    ├── pages/
    │   ├── PublicMenuPage.js  (Premium QR menu with animations)
    │   ├── MenuPage.js        (Admin menu CRUD + theme editor)
    │   ├── SocialMediaPage.js (Social media publisher)
    │   ├── KitchenPage.js     (NEW: Kitchen dashboard)
    │   └── ... (21+ pages)
    └── App.js
```

## 23 Frontend Pages (+1 Public)
Dashboard, Rooms, Guests, Reservations, Chatbot, Messages,
Campaigns, Reviews, Tasks, Events, Housekeeping, Staff,
Knowledge, QR Menu (admin), Social Media, Foca Guide, Settings, Login,
Pricing, TableReservations, Lifecycle, Automation, Kitchen,
+ PublicMenuPage (public, /menu)

## Testing History
- Iteration 1-4: Base app, reviews, refactoring
- Iteration 5: Initial QR Menu + Logo
- Iteration 6: QR Menu overhaul (100 items) + Social Media Publisher - %100
- Iteration 7: Table reservations update - %100

## Bug Fixes (Feb 2026)
- **Login "undefined" Hatasi Duzeltildi:** Setup butonu sistem kuruluyken undefined gosteriyordu. Frontend'de setup response handling duzeltildi.
- **Login Bilgileri:** admin / admin123

## Mocked Features
- Email campaign sending
- WhatsApp/Instagram webhooks
- Lifecycle send
- Automation bots
- Social media publishing (marks as published, doesn't post)

## Credentials
- Admin: admin / admin123

## Guncel Oda Fiyatlari (Nakit/Havale - TL, Serpme Kahvalti Dahil)
| Oda Tipi | Fiyat |
|----------|-------|
| Tek Kisilik | 3.000 TL |
| Cift Kisilik | 3.500 TL |
| Uc Kisilik | 5.000 TL |
| Superior | 5.500 TL |
| Aile Odasi | 6.000 TL |

## Upcoming Tasks
- P1: WhatsApp Entegrasyonu (Twilio) - Otomatik hatirlama/tesekkur mesajlari
- P1: HotelRunner API entegrasyonu (API bilgileri bekleniyor)
- P2: Anti-halucinasyon modulu (chatbot)
- P2: Rate limiter (AI endpoint'leri)
- P2: Gercek zamanli resepsiyon uyarilari
- P3: Railway deployment rehberligi

## Future Tasks (Backlog)
- POS entegrasyonu
- Mobil personel uygulamasi
- WhatsApp OTP Login
