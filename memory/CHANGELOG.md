# Kozbeyli Konagi - Changelog

## [2026-03-03] Modul Silme + Celery Task Queue
- **Silindi:** Mutfak Dashboard (kitchen router + KitchenPage), Finansal Takip (financials router + FinancialsPage), Dinamik Fiyatlandirma (pricing + revenue routers, PricingPage + RevenueManagementPage)
- **Eklendi:** Celery Task Queue - APScheduler yerine Redis-backed dagitik gorev kuyrugu
  - `celery_app.py`: Celery konfigurasyonu, 6 beat zamanlama, worker/beat subprocess yonetimi
  - `celery_tasks.py`: 8 gorev (6 zamanli + 2 on-demand), pymongo sync DB erisimi
  - `routers/automation.py` guncellendi: Celery .delay() ile gorev tetikleme
  - `server.py` guncellendi: scheduler → celery_app
- **Frontend:** App.js'den 4 sayfa (kitchen, financials, pricing, revenue) + nav linkleri kaldirildi
- Test: Backend 15/15 (%100), Frontend %100 - Iteration 18
- **WhatsApp Business API Service** (`services/whatsapp_service.py`): Production-grade WhatsApp Cloud API entegrasyonu, mock mod, 5 otel sablon metodu
- **Instagram Messaging API Service** (`services/instagram_service.py`): Instagram DM islemesi, mock mod destegi
- **Unified Webhook Router** (`routers/webhooks.py`): WhatsApp + Instagram webhook isleme, HMAC dogrulama, chatbot entegrasyonu
- **WhatsApp Admin Endpoints** guncellendi: sablon gondirme, temizlik bildirimi, check-out tesekkur, hos geldiniz mesajlari
- **WhatsApp Triggers** (`services/whatsapp_triggers.py`): Otomatik hatirlatma, tesekkur, temizlik bildirimleri
- **Frontend** `WhatsAppPage.js` tamamen yeniden yazildi: 6 tab, cift platform, sablon yonetimi, mesaj gondirme
- **DB Indeksleri** guncellendi: whatsapp_messages, instagram_messages
- **.env** guncellendi: 10 yeni ortam degiskeni (WA + IG)
- Test: 15/15 backend (%100), frontend %100

## [2026-02-16] Faz 19: Domain + SEO + QR + Chatbot
- / → PublicMenuPage, /admin → Yonetim paneli
- SEO meta tags, Open Graph, JSON-LD Hotel schema
- QR kod sistemi (altin/koyu renk)
- Chatbot: yasakli konu tespiti, eskalasyon protokolu, ek hizmetler

## [2026-02-16] Faz 18: Redis + VAPID + Finansal Modul
- Redis caching layer (in-memory fallback)
- VAPID push notification (pywebpush)
- Gelir/Gider takip modulu (7 gelir, 17 gider kategorisi)
- HotelRunner iptal politikasi + webhook + kanal yonetimi

## [2026-02-16] Faz 17: Caching + Lazy Loading + Push
- In-memory TTLCache + Redis gecisi
- React.lazy() ile 25+ sayfa lazy loading
- PWA push notification handler

## [2026-02-16] Faz 16: Database Indexing + PWA
- 13 koleksiyon icin MongoDB indeksleri
- PWA manifest, service worker, offline destek

## [2026-02-15] Faz 15: Aksam Kontrolu + Dashboard + Dil
- 18:00 aksam oda kontrolu
- Dinamik real-time dashboard (30s refresh)
- 5 dil destegi (TR/EN/DE/FR/RU)

## [2026-02-15] Faz 14: Guvenlik + Sadakat
- Anti-halucinasyon modulu
- Rate limiter (session bazli)
- 4 seviyeli sadakat sistemi

## [2026-02-15] Faz 13: Otomasyon + Etkinlikler
- APScheduler: 4 zamanli gorev
- 6 otomasyon botu
- Etkinlik yonetimi

## [Earlier] Faz 1-12: Temel Sistem
- Tum temel CRUD, AI chatbot, QR menu, sosyal medya, mutfak dashboard
