# Kozbeyli Konagi - Otel Yonetim Sistemi PRD

## Problem Statement
Kozbeyli Konagi (Izmir/Foca) butik tas otel icin kapsamli dijital yonetim ekosistemi.
Domain: kozbeylikonagi.com.tr

## Tech Stack
- **Frontend:** React 19, TailwindCSS, Shadcn UI, Framer Motion
- **Backend:** FastAPI, Motor (async MongoDB)
- **Database:** MongoDB
- **Task Queue:** Celery + Redis (6 zamanli gorev + on-demand)
- **AI:** Google Gemini (emergentintegrations)
- **Auth:** JWT + bcrypt
- **Caching:** Redis
- **Push Notifications:** VAPID (pywebpush)

## Silinen Moduller (3 Mart 2026)
- ~~Mutfak Dashboard (Kitchen)~~ - SILINDI
- ~~Finansal Takip (Financials)~~ - SILINDI
- ~~Dinamik Fiyatlandirma (Pricing/Revenue)~~ - SILINDI

## Celery Task Queue (3 Mart 2026 - EKLENDI)
APScheduler yerine Celery + Redis entegrasyonu:
- 6 zamanli gorev (beat): kahvalti, sabah hatirlama, temizlik, aksam kontrol, WA hatirlatma, WA tesekkur
- 2 on-demand gorev: WA bildirim, audit alert
- Worker: 2 concurrent, celery+scheduled queues
- Beat: Europe/Istanbul timezone

## Implementation Status

### Tamamlanan Ozellikler
- Dashboard, Room/Guest/Reservation CRUD, AI Chatbot (Gemini)
- Staff/Shifts, Events, Housekeeping, Knowledge Base
- QR Menu (100+ urun), Sosyal Medya, Masa Rez.
- WhatsApp Bot + Instagram DM (mock mod)
- Unified Webhook Router (WA + IG)
- Anti-Halucinasyon, Rate Limiter, Sadakat Sistemi
- Coklu Dil (5 dil), PWA, Redis Caching, Push Notifications
- Domain Routing (/admin, / = public menu), SEO, QR Kod
- Celery Task Queue (6 zamanli + 2 on-demand)
- Analitik Dashboard, Guvenlik/Audit

### Test Durumu
- Iteration 17: WA/IG entegrasyonu %100
- Iteration 18: Modul silme + Celery %100

## Credentials
- Admin: admin / admin123

## Upcoming Tasks
- P0: Vercel Deployment Rehberi (kozbeylikonagi.com.tr)
- P0: WhatsApp API Edinme Rehberi
- P0: HotelRunner API (anahtarlar bekleniyor)
- P1: Online odeme (Stripe/Iyzico)
- P2: Misafir Self-Servis Portali
