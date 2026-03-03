# Kozbeyli Konagi - Otel Yonetim Sistemi PRD

## Tech Stack
- **Frontend:** React 19, TailwindCSS, Shadcn UI, Framer Motion
- **Backend:** FastAPI, Motor (async MongoDB), ReportLab (PDF)
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
  - Backend: Full CRUD API (/api/proposals) + PDF generation endpoint
  - Frontend: ProposalsPage.js - listing, search/filter, expandable details, creation dialog
  - PDF export: Professional branded PDF with logo, tables, totals
  - Auto-generated proposal numbers (TKL-YYYY-NNN format)
  - Status workflow: draft -> sent -> accepted/rejected/expired
  - Stats dashboard with conversion rate tracking
- **Startup Strateji Plani** (3 Mart 2026)
  - /app/STARTUP_STRATEJI_PLANI.md - 10 bolumlu kapsamli strateji dokumani

## Credentials: admin / admin123

## Upcoming Tasks
- P0: HotelRunner API (anahtarlar bekleniyor)
- P0: WhatsApp Business API canli entegrasyon
- P1: Online odeme (Stripe/Iyzico)
- P1: Misafir Self-Servis Portal (check-in/out)
- P2: White-label SaaS donusumu

## Key API Endpoints
- POST/GET /api/proposals - Create/List proposals
- GET /api/proposals/stats/summary - Proposal statistics
- GET /api/proposals/{id}/pdf - Download proposal as PDF
- PATCH /api/proposals/{id} - Update proposal status
- POST /api/proposals/{id}/duplicate - Duplicate proposal
