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
- **Scheduler:** APScheduler (3 zamanli gorev)
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
- PDF'den cikarilan guncel menu verisi: 100 urun, 16 kategori
- Sosyal Medya Yayinlayici (6 platform, 5 gonderi turu, canli onizleme)

### Faz 9: Sosyal Medya Gelistirmeleri (TAMAMLANDI - Feb 2026)
- TikTok ve LinkedIn platformlari eklendi (toplam 6 platform)
- Google Drive linki destegi, QR Menu renk guncellemesi

### Faz 10: Masa Rezervasyon Sistemi Yenileme (TAMAMLANDI - Feb 2026)
- 19 masa tanimli, ogun bazli sure ayarlari, akilli masa atama

### Faz 11: AI Bilgi Zenginlestirmesi + Mutfak Dashboard (TAMAMLANDI - Feb 2026)
- Guncel oda fiyatlari, ozel gun fiyatlari, WhatsApp mesaj sablonlari
- Mutfak Dashboard: siparis olusturma, durum takibi, bildirimler

### Faz 12: WhatsApp Entegrasyonu + Akilli Chatbot (TAMAMLANDI - Feb 2026)
- Multi-Agent Router, Intent Detection, Auto-Reply Engine
- Tam otomatik masa rezervasyonu akisi (WhatsApp bot)
- WhatsApp Admin Sayfasi (mock mod)

### Faz 13: Operasyonel Otomasyon + Etkinlik Yonetimi (TAMAMLANDI - Feb 2026)

**Zamanli Gorev Sistemi (scheduler.py - APScheduler):**
- Kahvalti Hazirligi: Her gece 01:00 - Misafir sayisi ve oda tiplerine gore kahvalti bildirimi
- Sabah Hatirlama: Her gun 08:30 - Tuvalet temizlik/stok kontrolu + check-in odasi hazirligi
- Check-out Temizlik: Her gun 12:30 - Cikis yapan odalarin temizlik listesi
- Tum bildirimler WhatsApp grubuna (mock modda DB'ye kaydedilir)
- Manuel tetikleme: Her 3 bot tek tikla calistiriabilir

**Otomasyon Dashboard Guncellemesi:**
- 6 bot karti: Kahvalti, Sabah Hatirlama, Temizlik, Odeme, Iptal, Mutfak Tahmini
- Zamanli gorev durumu paneli (sonraki calisma zamani + aktif/durduruldu)
- 3 tab: Botlar, Grup Bildirimleri, Islem Gecmisi
- Summary kartlari: Toplam, Kahvalti, Temizlik, Hatirlama, Odeme, Iptal

**Etkinlik Sistemi Guncellemesi:**
- 7 Subat Canli Muzik - Ece Yazar (Fix Menu, Alkolu 2750 TL, Sinirsiz 5500 TL)
- 14 Subat Sevgililer Gunu - GORAY Akustik (Ozel menu, Alkolu 3500 TL, Sinirsiz 6000 TL)
- Kapak gorseli destegi, menu detaylari, sanatci bilgisi
- POST /api/events/seed-samples endpoint

### Tests: Backend 30/30 (%100), Frontend %100 - Iteration 8

## Architecture
```
backend/
├── server.py          (thin orchestrator)
├── database.py        (MongoDB connection)
├── helpers.py         (utcnow, new_id, clean_doc)
├── config.py          (env vars)
├── models.py          (Pydantic models)
├── hotel_data.py      (static hotel data)
├── knowledge_seed_data.py  (Message templates, knowledge base)
├── chatbot_engine.py       (Multi-agent router, auto-reply, conversation flow)
├── scheduler.py            (NEW: APScheduler - 3 zamanli gorev)
├── menu_seed_data.py  (Updated menu data - 100 items, 16 cats)
├── gemini_service.py  (Gemini AI)
└── routers/
    ├── auth.py, hotel.py, rooms.py, guests.py
    ├── reservations.py, tasks.py, events.py (UPDATED: seed-samples)
    ├── housekeeping.py, staff.py, knowledge.py
    ├── chatbot.py, messages.py, campaigns.py
    ├── reviews.py, settings.py, pricing.py
    ├── table_reservations.py, lifecycle.py
    ├── automation.py       (UPDATED: 5 yeni endpoint)
    ├── public_menu.py, menu_admin.py
    ├── social_media.py
    ├── kitchen.py
    └── whatsapp.py

frontend/src/
├── pages/
│   ├── AutomationPage.js  (UPDATED: 6 bot, zamanli gorevler, 3 tab)
│   ├── EventsPage.js      (UPDATED: kapak gorseli, menu detaylari, fiyatlar)
│   └── ... (22+ pages)
├── api.js                 (UPDATED: yeni endpoint fonksiyonlari)
└── App.js
```

## 25 Frontend Pages (+1 Public)
Dashboard, Rooms, Guests, Reservations, Chatbot, Messages, WhatsApp,
Campaigns, Reviews, Tasks, Events, Housekeeping, Staff,
Knowledge, QR Menu (admin), Social Media, Foca Guide, Settings, Login,
Pricing, TableReservations, Lifecycle, Automation, Kitchen,
+ PublicMenuPage (public, /menu)

## Testing History
- Iteration 1-4: Base app, reviews, refactoring
- Iteration 5: Initial QR Menu + Logo
- Iteration 6: QR Menu overhaul (100 items) + Social Media Publisher - %100
- Iteration 7: Table reservations update - %100
- Iteration 8: Comprehensive monkey test (otomasyon + etkinlikler) - %100

## Credentials
- Admin: admin / admin123

## Mocked Features
- Email campaign sending
- WhatsApp/Instagram webhooks (mock modda DB'ye kaydeder)
- Lifecycle send
- Automation bots (WhatsApp grup bildirimleri mock modda)
- Social media publishing (marks as published, doesn't post)

## Upcoming Tasks
- P1: WhatsApp Business API Yapilandirmasi (Meta Developer Portal ayarlari bekleniyor)
- P1: HotelRunner API entegrasyonu (API bilgileri bekleniyor)
- P2: Anti-halucinasyon modulu (chatbot)
- P2: Rate limiter (AI endpoint'leri)
- P2: Gercek zamanli resepsiyon uyarilari
- P3: Railway deployment rehberligi

## Future Tasks (Backlog)
- POS entegrasyonu
- Mobil personel uygulamasi
- WhatsApp OTP Login
