# Kozbeyli Konagi - Otel Yonetim Sistemi PRD

## Problem Statement
Kozbeyli Konagi (Izmir/Foca) butik tas otel icin kapsamli dijital yonetim ekosistemi.
GitHub repo: https://github.com/No3214/BillionDollar

## Tech Stack
- **Frontend:** React 19, TailwindCSS, Shadcn UI, Framer Motion
- **Backend:** FastAPI, Motor (async MongoDB), 21 modular routers
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

### Faz 5: Google Yorum Yanitlayici (TAMAMLANDI - Feb 2026)
- AI review response (anti-hallucination, 3 ton secenegi)
- Review CRUD + stats dashboard

### Faz 6: Mimari Yenileme + Yeni Ozellikler (TAMAMLANDI - Feb 2026)
- Backend refactoring: Monolitik → 19 modular router
- Dinamik Fiyatlama, Masa Rez., Misafir Dongusu
- Admin Auth + RBAC (4 rol)
- Otomasyon Botlari

### Faz 7: QR Menu Sistemi + Logo (TAMAMLANDI - Feb 2026)

**QR Menu Public Sayfasi (/menu):**
- Auth gerektirmeyen public menu sayfasi
- Kozbeyli Green temasi (zeytin yesili #515249 gradient arka plan)
- Alifira ozel font (basliklar icin)
- Kategori navigasyonu (12 kategori, ikon destekli)
- TR/EN dil degistirme
- Mobil uyumlu responsive tasarim
- Menu ogeleri fiyatlarla birlikte gosterim

**Admin Menu Yonetimi:**
- Menu ogesi CRUD (ekle/duzenle/sil)
- Kategori yonetimi (ekle/duzenle/sil)
- Tema editoru (renkler, arka plan, bileskenler, marka bilgileri)
- Public menu URL gosterimi ve onizleme butonu

**Logo Entegrasyonu:**
- Login sayfasinda logo goruntuleme
- Sidebar basliginda logo goruntuleme

**Teknik Detaylar:**
- Backend: 2 yeni router (public_menu.py, menu_admin.py)
- MongoDB collections: menu_items, menu_categories, theme_settings
- Otomatik veri tohumlama (ilk erisimde)
- Public endpoint: GET /api/public/menu (auth yok)
- Admin endpoints: /api/menu-admin/* (auth gerektir)

### Tests: Backend 19/19 (%100), Frontend %100 - Iteration 5

## Architecture
```
backend/
├── server.py          (thin orchestrator)
├── database.py        (MongoDB connection)
├── helpers.py         (utcnow, new_id, clean_doc)
├── config.py          (env vars)
├── models.py          (Pydantic models)
├── hotel_data.py      (static hotel data + menu seed)
├── gemini_service.py  (Gemini AI)
└── routers/
    ├── auth.py, hotel.py, rooms.py, guests.py
    ├── reservations.py, tasks.py, events.py
    ├── housekeeping.py, staff.py, knowledge.py
    ├── chatbot.py, messages.py, campaigns.py
    ├── reviews.py, settings.py, pricing.py
    ├── table_reservations.py, lifecycle.py
    ├── automation.py
    ├── public_menu.py    # NEW: Public QR menu
    └── menu_admin.py     # NEW: Admin menu CRUD

frontend/
├── public/
│   ├── logo.jpeg         # Hotel logo
│   ├── fonts/Alifira.ttf # Custom heading font
│   └── brand/            # Brand assets dir
└── src/
    ├── pages/
    │   ├── PublicMenuPage.js  # NEW: Public QR menu page
    │   ├── MenuPage.js        # UPDATED: Admin CRUD + theme editor
    │   └── ... (20+ pages)
    └── App.js  # Updated: /menu route, logo in sidebar
```

## 21 Frontend Pages (+1 Public)
Dashboard, Rooms, Guests, Reservations, Chatbot, Messages,
Campaigns, Reviews, Tasks, Events, Housekeeping, Staff,
Knowledge, QR Menu (admin), Foca Guide, Settings, Login,
Pricing, TableReservations, Lifecycle, Automation,
+ PublicMenuPage (public, /menu)

## Testing History
- Iteration 1: 24/24 backend, 10/10 frontend - Faz 1
- Iteration 2: 19/19 backend, 15/15 frontend - Faz 2-4
- Iteration 3: 16/16 backend, All frontend - Reviews
- Iteration 4: 25/25 backend, All frontend - Refactoring + New Features
- Iteration 5: 19/19 backend, All frontend - QR Menu + Logo

## Mocked Features
- Email campaign sending (counts guests, doesn't send)
- WhatsApp/Instagram webhooks (simulate incoming)
- Lifecycle send (logs to DB, simulates WhatsApp/SMS)
- Automation bots (log to DB, don't send real messages)

## API Keys (in backend/.env)
- GOOGLE_API_KEY (Gemini AI - active)
- GROQ_API_KEY, DEEPSEEK_API_KEY, OPENROUTER_API_KEY (backup)
- EMERGENT_LLM_KEY

## Credentials
- Admin: admin / kozbeyli2026

## Upcoming Tasks (P1-P2)
- P1: HotelRunner API entegrasyonu (kullanici API saglayacak)
- P1: Beyaz logo (KOZBEYLI_BEYAZ_LOGO.png) entegrasyonu (kullanici saglayacak)
- P2: Self-healing + monitoring sistemi
- P2: Anti-halucinasyon modulu (chatbot icin)
- P2: Rate limiter (ozellikle AI endpoint'leri)
- P2: WhatsApp OTP Login
- P2: Gercek zamanli resepsiyon uyarilari
- P2: Mutfak tedarik tahmini
