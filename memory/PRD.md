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

## Implementation Status - ALL PHASES COMPLETE

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

## Architecture
- 15 frontend pages in categorized sidebar
- 40+ backend API endpoints
- MongoDB collections: rooms, guests, reservations, tasks, events, housekeeping, staff, shifts, knowledge, chat_messages, messages, campaigns, settings

## Testing
- Iteration 1: 24/24 backend (100%), 10/10 frontend (100%)
- Iteration 2: 19/19 backend (100%), 15/15 frontend (100%)
- Total: 43/43 backend tests passed

## Mocked Features
- Email campaign sending (counts guests but doesn't send actual emails)
- WhatsApp/Instagram webhooks (simulate incoming messages for testing)

## API Keys (in backend/.env)
- GOOGLE_API_KEY (Gemini AI - active, working)
- GROQ_API_KEY (backup)
- DEEPSEEK_API_KEY (backup)
- OPENROUTER_API_KEY (backup)
