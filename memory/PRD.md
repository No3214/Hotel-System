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
- ~~Mutfak Dashboard~~ - ~~Finansal Takip~~ - ~~Dinamik Fiyatlandirma~~

## Tamamlanan Ozellikler
- Dashboard, Room/Guest/Reservation CRUD, AI Chatbot (Gemini)
- Staff/Shifts, Events, Housekeeping, Knowledge Base
- QR Menu (100+ urun), Sosyal Medya
- WhatsApp Bot + Instagram DM (mock mod) + Unified Webhook Router
- Anti-Halucinasyon, Rate Limiter, Sadakat Sistemi
- Coklu Dil (5 dil), PWA, Redis Caching, Push Notifications
- Domain Routing (/admin, / = public menu), SEO, QR Kod
- Celery Task Queue (6 zamanli + 2 on-demand)
- Analitik Dashboard, Guvenlik/Audit
- **Gorsel Masa Yerlsim Plani** (20 masa, 5 bolge, 106 kapasite, gercek PDF'den)
- **Railway + WhatsApp Kurulum Rehberi** (KURULUM_REHBERI.md)

## Masa Yerlsim Plani (3 Mart 2026)
- Somine Bolgesi: M1, M2, M3 (dikdortgen) + A, B, C (yuvarlak)
- Sahne Bolgesi: M5, M6, M7, M8
- Manzara Bolgesi: M10, M11, M12, M13
- Ara Bolge: S1, S2, S3, S4 (kucuk)
- Bar Bolgesi: BAR1, BAR2
- Birlestirilebilir masa gruplari (max 24 kisi)
- Floor-plan API: /api/table-reservations/floor-plan

## Credentials
- Admin: admin / admin123

## Upcoming Tasks
- P0: HotelRunner API (anahtarlar bekleniyor)
- P1: Online odeme (Stripe/Iyzico)
- P2: Misafir Self-Servis Portali
