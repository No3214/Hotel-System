# Kozbeyli Konagi - Otel Yonetim Sistemi PRD

## Problem Statement
Kozbeyli Konagi (Izmir/Foca) butik tas otel icin kapsamli dijital yonetim ekosistemi.

## Tech Stack
- **Frontend:** React 19, TailwindCSS, Shadcn UI, Framer Motion
- **Backend:** FastAPI, Motor (async MongoDB), 26 modular routers
- **Database:** MongoDB (persistent)
- **AI:** Google Gemini 2.5 Flash (emergentintegrations)
- **Auth:** JWT + bcrypt, role-based (admin/reception/kitchen/staff)
- **Scheduler:** APScheduler (4 zamanli gorev)
- **Security:** Anti-Hallucination Module, Rate Limiter
- **Caching:** Redis
- **Push Notifications:** VAPID (pywebpush)

## Implementation Status

### Faz 1-19: Temel Sistem + Optimizasyonlar (TAMAMLANDI)
- Dashboard, Room/Guest/Reservation CRUD, AI Chatbot (Gemini)
- Staff/Shifts, Events, Housekeeping, Knowledge Base
- QR Menu (100+ urun), Sosyal Medya, Masa Rez., Mutfak Dashboard
- WhatsApp Bot, Konusamali Rez., Google Yorum Yanitlayici
- Anti-Halucinasyon, Rate Limiter, Sadakat Sistemi
- Coklu Dil (5 dil), PWA, Redis Caching, Push Notifications
- Finansal Takip, Revenue Management, Analytics
- Domain Routing (/admin, / = public menu), SEO, QR Kod

### Faz 20: WhatsApp & Instagram Entegrasyonu (TAMAMLANDI - 17 Feb 2026)

**WhatsApp Business API Service (services/whatsapp_service.py):**
- Production-grade WhatsApp Cloud API entegrasyonu
- Mock mod: API anahtarlari yoksa mesajlar DB'ye kaydedilir
- Metin, sablon, interaktif buton, medya mesaj destegi
- Telefon numarasi normalizasyonu (0532xxx → 90532xxx)
- 5 otel-spesifik sablon metodu: checkout_thanks, reservation_reminder, welcome_checkin, notify_cleaning, room_ready
- Otomatik mesaj loglama

**Instagram Messaging API Service (services/instagram_service.py):**
- Instagram DM islemesi icin Meta Graph API entegrasyonu
- Mock mod destegi
- Metin ve quick reply mesaj gondirme

**Unified Webhook Router (routers/webhooks.py):**
- WhatsApp webhook: GET (dogrulama) + POST (mesaj isleme)
- Instagram webhook: GET (dogrulama) + POST (DM isleme)
- HMAC signature dogrulama (WhatsApp APP_SECRET ile)
- Gelen mesajlari chatbot engine uzerinden isler
- Metin, interaktif buton, gorsel, konum mesaj tipleri
- Mesaj durum guncellemeleri (sent, delivered, read, failed)
- Grup bildirim sistemi (rezervasyon olusturulunca)

**WhatsApp Admin Endpoints (routers/whatsapp.py - guncellendi):**
- POST /api/whatsapp/send - Manuel mesaj gondirme
- POST /api/whatsapp/send-template - Sablon mesaj gondirme
- POST /api/whatsapp/send-checkout-thanks - Check-out tesekkur
- POST /api/whatsapp/send-reservation-reminder - Hatirlatma
- POST /api/whatsapp/send-welcome - Hos geldiniz
- POST /api/whatsapp/notify-cleaning - Temizlik bildirimi
- POST /api/whatsapp/send-room-ready - Oda hazir
- GET /api/whatsapp/templates - Kullanilabilir sablon listesi
- GET /api/whatsapp/config - API yapilandirma durumu

**WhatsApp Triggers (services/whatsapp_triggers.py):**
- trigger_reservation_reminders(): Yarin check-in yapacak misafirlere hatirlatma
- trigger_checkout_thanks(): Check-out yapan misafirlere tesekkur
- trigger_cleaning_notification(): Temizlik ekibine bildirim

**Frontend Mesajlasma Merkezi (WhatsAppPage.js - yeniden yazildi):**
- 6 tab: Bildirimler, WhatsApp, Instagram, Sablonlar, Mesaj Gonder, Ayarlar
- Cift platform destek (WhatsApp + Instagram)
- Manuel mesaj gondirme formu
- Sablon listesi ve parametreleri
- Webhook URL gosterimi (Meta konfigurasyon icin)
- Platform durumu (Mock/API Bagli) gostergesi
- Istatistik kartlari: WA Mesaj, IG Mesaj, Toplam Konusma, Bildirim

**Veritabani Indeksleri (database_optimizer.py - guncellendi):**
- whatsapp_messages: session_id, direction, created_at
- instagram_messages: session_id, direction, created_at

**Ortam Degiskenleri (.env - guncellendi):**
- WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_BUSINESS_ACCOUNT_ID
- WHATSAPP_APP_SECRET, WHATSAPP_VERIFY_TOKEN, WHATSAPP_GROUP_NUMBER
- INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_PAGE_ID, INSTAGRAM_VERIFY_TOKEN

### Tests: Backend 15/15 (%100), Frontend %100 - Iteration 17

## Architecture
```
backend/
├── server.py                    (FastAPI + 26 router)
├── config.py                    (UPDATED: WA/IG env vars)
├── chatbot_engine.py            (UPDATED: multi-platform)
├── hotel_data.py                (Otel verileri)
├── routers/
│   ├── webhooks.py              (NEW: Unified WA+IG webhooks)
│   ├── whatsapp.py              (UPDATED: Admin + template endpoints)
│   └── ... (24 diger router)
├── services/
│   ├── whatsapp_service.py      (NEW: WA Business API service)
│   ├── instagram_service.py     (NEW: IG messaging service)
│   ├── whatsapp_triggers.py     (NEW: Otomatik bildirim tetikleyicileri)
│   ├── cache_service.py         (Redis caching)
│   ├── database_optimizer.py    (UPDATED: WA/IG indexing)
│   └── push_service.py          (VAPID push)
└── .env                         (UPDATED: WA/IG credentials)

frontend/src/
├── pages/
│   ├── WhatsAppPage.js          (REWRITTEN: Mesajlasma Merkezi)
│   └── ... (24+ sayfa)
├── api.js
└── App.js
```

## Credentials
- Admin: admin / admin123

## Mocked Features
- WhatsApp Business API (mock modda DB'ye kaydeder, gercek API anahtari verilince aktif olur)
- Instagram Messaging API (mock modda DB'ye kaydeder)
- Sosyal medya paylasim
- Email kampanya gonderimi
- Otomasyon bildirimleri

## Key API Endpoints (Yeni)
- GET /api/webhooks/status - Her iki platformun durumu
- GET/POST /api/webhooks/whatsapp - WhatsApp webhook
- GET/POST /api/webhooks/instagram - Instagram webhook
- POST /api/whatsapp/send - Manuel mesaj
- POST /api/whatsapp/send-template - Sablon mesaj
- GET /api/whatsapp/templates - Sablon listesi

## Upcoming Tasks
- P0: Vercel Deployment Rehberi (kozbeylikonagi.com.tr icin)
- P0: WhatsApp API Edinme Rehberi (Meta Developer Portal)
- P0: HotelRunner API canli entegrasyonu (API anahtarlari bekleniyor)
- P1: Online odeme entegrasyonu (Stripe/Iyzico)
- P1: APScheduler → Celery migrasyonu
- P2: Misafir Self-Servis Portali
