# Kozbeyli Konagi - Otel Yonetim Sistemi PRD

## Tech Stack
- **Frontend:** React 19, TailwindCSS, Shadcn UI, Framer Motion
- **Backend:** FastAPI, Motor (async MongoDB)
- **Database:** MongoDB | **Task Queue:** Celery + Redis
- **AI:** Google Gemini | **Auth:** JWT + bcrypt

## Tamamlanan Ozellikler
- Dashboard, Room/Guest/Reservation CRUD, AI Chatbot
- Staff/Shifts, Events, Housekeeping, Knowledge Base
- QR Menu (100+ urun), Sosyal Medya, Sadakat
- WhatsApp Bot + Instagram DM (mock) + Webhook Router
- Coklu Dil, PWA, Redis Caching, Push Notifications
- Celery Task Queue (6 zamanli + 2 on-demand)
- Analitik Dashboard, Guvenlik/Audit
- **Gorsel Masa Yerlesim Plani** (20 masa, 5 bolge, 106 kapasite)
- **Organizasyon Yonetimi** (dugun/nisan talebi, chatbot entegrasyonu, PDF paylasim)
- **Railway + WhatsApp Kurulum Rehberi**
- **Teklif Yonetimi (Proposal Management)** (3 Mart 2026)
  - Backend: Full CRUD API (/api/proposals) - create, list, get, update, delete, duplicate, stats
  - Frontend: ProposalsPage.js - listing, search/filter, expandable details, creation dialog
  - Auto-generated proposal numbers (TKL-YYYY-NNN format)
  - Status workflow: draft -> sent -> accepted/rejected/expired
  - Stats dashboard with conversion rate tracking
  - Accommodation, meal options, extra services detail sections

## Organizasyon Modulu (3 Mart 2026)
- organization_data.py: Dugun/nisan verileri, menu, dekorasyon, foto, muzik paketleri
- routers/organization.py: CRUD + bilgi formu + istatistik API
- OrganizationPage.js: Admin panel, talep yonetimi, durum takibi, PDF link
- Chatbot: "dugun/nisan/organizasyon" intent → otomatik bilgi + PDF link
- 8 organizasyon turu, 2 dekorasyon paketi, 3 muzik secenegi
- PDF sunumlari otomatik paylasiliyor

## Masa Yerlesim Plani
- 5 bolge: Somine (M1-3,A-C), Sahne (M5-8), Manzara (M10-13), Ara (S1-4), Bar (BAR1-2)
- Floor-plan API: /api/table-reservations/floor-plan
- Birlestirilebilir masa gruplari (max 24 kisi)

## Credentials: admin / admin123

## Upcoming Tasks
- P0: HotelRunner API (anahtarlar bekleniyor)
- P1: Online odeme (Stripe/Iyzico)
- P1: Startup Strateji Danismanligi (marka, pazarlama, Ar-Ge)
- P2: Misafir Self-Servis Portali

## Key API Endpoints
- POST/GET /api/proposals - Create/List proposals
- GET /api/proposals/stats/summary - Proposal statistics
- PATCH /api/proposals/{id} - Update proposal status
- POST /api/proposals/{id}/duplicate - Duplicate proposal
- DELETE /api/proposals/{id} - Delete proposal
