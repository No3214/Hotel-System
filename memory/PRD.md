# Kozbeyli Konagi - Otel Yonetim Sistemi PRD

## Problem Statement
Kozbeyli Konagi (Izmir/Foca) butik tas otel icin kapsamli dijital yonetim ekosistemi.
GitHub repo: https://github.com/No3214/BillionDollar

## Tech Stack
- **Frontend:** React 19, TailwindCSS, Shadcn UI, Framer Motion
- **Backend:** FastAPI, Motor (async MongoDB)
- **Database:** MongoDB
- **AI:** Google Gemini 2.5 Flash (emergentintegrations)
- **Theme:** Kozbeyli gold (#C4972A) on dark (#0a0a0f)

## Users
- 3 kisi (otel sahibi + 2 yonetici)

## Implementation Status

### Faz 1: Temel Altyapi (TAMAMLANDI - Feb 2026)
- Dashboard with real-time stats (occupancy, ratings, tasks)
- Room management (4 types, 16 rooms, TL/EUR prices)
- Guest management (CRUD + search)
- AI Chatbot (Gemini 2.5 Flash, Turkish/English, hotel-specific knowledge)
- Task management (create/filter/complete/delete, priorities)
- Event management (CRUD)
- Housekeeping (CRUD + status flow)
- Knowledge base (CRUD + search)
- Restaurant menu (12 categories, 80+ items)
- WhatsApp/Instagram message handling with AI auto-reply

### Faz 2: Iletisim & Otomasyon (TAMAMLANDI - Feb 2026)
- Email campaigns (create, target segments, send simulation, analytics)
- Housekeeping automation (auto-create on checkout)
- Improved reservations (status flow: pending->confirmed->checked_in->checked_out)
- WhatsApp webhook with AI-powered responses
- Instagram webhook with AI-powered responses

### Faz 3: Gelismis Ozellikler (TAMAMLANDI - Feb 2026)
- Staff management with departments (CRUD)
- Shift management (create/delete, per staff/date)
- KVKK compliance (6-section privacy policy)
- Settings page (toggles for integrations, AI config, security info)
- Improved reservation system with auto-housekeeping on checkout

### Faz 4: Polish & UX (TAMAMLANDI - Feb 2026)
- i18n support (Turkish, English, German, French, Russian)
- Foca local guide (Beaches, Historical, Family activities, Couple activities, Village history timeline)
- Categorized sidebar navigation (5 sections: Genel, Iletisim, Operasyon, Bilgi, Sistem)
- Smooth page transitions with Framer Motion
- Gold/dark Kozbeyli theme throughout

### Faz 5: Google Yorum Yanitlayici (TAMAMLANDI - Feb 2026)
- AI-powered Google Business review response generation (Gemini 2.5 Flash)
- Anti-hallucination system prompt with strict hotel-only facts
- 3 tone options: Professional, Friendly, Formal
- Review CRUD with stats dashboard (total, avg rating, responded, pending, by_rating)
- Editable AI responses with copy-to-clipboard
- Regeneration with different tones
- Full backend tests: 16/16 passed (100%)
- Full frontend tests: All CRUD + AI operations verified (100%)

## Architecture
- 16 frontend pages in categorized sidebar
- 45+ backend API endpoints
- MongoDB collections: rooms, guests, reservations, tasks, events, housekeeping, staff, shifts, knowledge, chat_messages, messages, campaigns, settings, reviews

## Testing
- Iteration 1: 24/24 backend (100%), 10/10 frontend (100%) - Faz 1
- Iteration 2: 19/19 backend (100%), 15/15 frontend (100%) - Faz 2-4
- Iteration 3: 16/16 backend (100%), All frontend (100%) - Google Reviews

## Mocked Features
- Email campaign sending (counts guests but doesn't send actual emails)
- WhatsApp/Instagram webhooks (simulate incoming messages for testing)

## API Keys (in backend/.env)
- GOOGLE_API_KEY (Gemini AI - active, working)
- GROQ_API_KEY (backup)
- DEEPSEEK_API_KEY (backup)
- OPENROUTER_API_KEY (backup)
- EMERGENT_LLM_KEY (universal key)

## Upcoming Tasks (P0-P2)
- P1: Backend refactoring (break server.py into modular routers)
- P1: Admin login & role-based access (Admin, Reception, Kitchen)
- P2: HotelRunner API integration (OTA bookings)
- P2: Automation bots (payment reminders, cancellation enforcement)
- P2: WhatsApp OTP login
- P2: System health monitoring
