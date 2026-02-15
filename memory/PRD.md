# Kozbeyli Konagi - Otel Yonetim Sistemi PRD

## Problem Statement
Kozbeyli Konagi (Izmir/Foca) butik tas otel icin kapsamli dijital yonetim ekosistemi.
GitHub repo: https://github.com/No3214/BillionDollar

## Tech Stack
- **Frontend:** React 19, TailwindCSS, Shadcn UI, Framer Motion
- **Backend:** FastAPI, Motor (async MongoDB), 19 modular routers
- **Database:** MongoDB (persistent)
- **AI:** Google Gemini 2.5 Flash (emergentintegrations)
- **Auth:** JWT + bcrypt, role-based (admin/reception/kitchen/staff)
- **Theme:** Kozbeyli gold (#C4972A) on dark (#0a0a0f)

## Users
- 3 kisi (otel sahibi + 2 yonetici) + personel rolleri

## Implementation Status

### Faz 1-4: Temel Sistem (TAMAMLANDI)
- Dashboard, Room/Guest/Reservation CRUD, AI Chatbot (Gemini)
- Staff/Shifts, Events, Housekeeping, Knowledge Base
- Restaurant Menu, WhatsApp/Instagram webhooks
- Campaigns, Foca Guide, i18n (5 dil), KVKK

### Faz 5: Google Yorum Yanitlayici (TAMAMLANDI - Feb 2026)
- AI review response (anti-hallucination, 3 ton secenegi)
- Review CRUD + stats dashboard
- Tests: 16/16 backend (100%)

### Faz 6: Mimari Yenileme + Yeni Ozellikler (TAMAMLANDI - Feb 2026)

**Backend Refactoring:**
- Monolitik server.py (950 satir) → 19 modular router dosyasi
- Shared database.py + helpers.py modulleri
- Temiz, bakim yapilabilir mimari

**Dinamik Fiyatlama Sistemi:**
- Sezon carpanlari (yuksek x1.4, orta x1.0, dusuk x0.8)
- 14 Turk tatil gunu carpanlari
- Hafta sonu carpani (Cuma-Cumartesi x1.2)
- Doluluk bazli dinamik ayarlama (%90+ → +%25)
- Konaklama maliyet hesaplayici (tarih araligi)

**Masa Rezervasyon Sistemi:**
- Antakya Sofrasi restoran yonetimi (15 masa, 60 kapasite)
- 9 saat dilimi musaitlik kontrolu
- Durum akisi: bekliyor→onay→oturdu→tamamlandi
- Ozel gun secenekleri (dogum gunu, yildonumu, is yemegi)

**Misafir Yasam Dongusu:**
- 6 mesaj sablonu (rezervasyon→varis→check-in→konaklama→check-out→takip)
- WhatsApp/SMS onizleme ve gonderim
- Degisken bazli kisisellestirilmis mesajlar

**Admin Auth + Rol Sistemi:**
- JWT kimlik dogrulama (login/register/me)
- 4 rol: Admin, Resepsiyon, Mutfak, Personel
- Rol bazli sidebar filtreleme
- Profesyonel login sayfasi
- Default admin: admin / kozbeyli2026

**Otomasyon Botlari:**
- Cumartesi odeme hatirlatma botu
- Iptal ceza hesaplama denetcisi
- 7 gunluk mutfak tahmin sistemi
- Otomasyon log ve ozet paneli

### Tests: Backend 25/25 (%100), Frontend %100 - Iteration 4

## Architecture (After Refactoring)
```
backend/
├── server.py          (thin orchestrator, ~100 lines)
├── database.py        (MongoDB connection)
├── helpers.py         (utcnow, new_id, clean_doc)
├── config.py          (env vars)
├── models.py          (Pydantic models)
├── hotel_data.py      (static hotel data)
├── gemini_service.py  (Gemini AI)
└── routers/
    ├── auth.py, hotel.py, rooms.py, guests.py
    ├── reservations.py, tasks.py, events.py
    ├── housekeeping.py, staff.py, knowledge.py
    ├── chatbot.py, messages.py, campaigns.py
    ├── reviews.py, settings.py, pricing.py
    ├── table_reservations.py, lifecycle.py
    └── automation.py
```

## 20 Frontend Pages
Dashboard, Rooms, Guests, Reservations, Chatbot, Messages,
Campaigns, Reviews, Tasks, Events, Housekeeping, Staff,
Knowledge, Menu, Foca Guide, Settings, Login,
Pricing, TableReservations, Lifecycle, Automation

## Testing History
- Iteration 1: 24/24 backend, 10/10 frontend - Faz 1
- Iteration 2: 19/19 backend, 15/15 frontend - Faz 2-4
- Iteration 3: 16/16 backend, All frontend - Reviews
- Iteration 4: 25/25 backend, All frontend - Refactoring + New Features

## Mocked Features
- Email campaign sending (counts guests, doesn't send)
- WhatsApp/Instagram webhooks (simulate incoming)
- Lifecycle send (logs to DB, simulates WhatsApp/SMS)
- Automation bots (log to DB, don't send real messages)

## API Keys (in backend/.env)
- GOOGLE_API_KEY (Gemini AI - active)
- GROQ_API_KEY, DEEPSEEK_API_KEY, OPENROUTER_API_KEY (backup)

## Upcoming Tasks (P1-P2)
- P1: HotelRunner API entegrasyonu (kullanici API saglayacak)
- P2: Self-healing + monitoring sistemi
- P2: QR Menu entegrasyonu (mevcut Vercel projesiyle baglanti)
- P2: Anti-halucinasyon modulu (chatbot icin)
- P2: Rate limiter (ozellikle AI endpoint'leri)
