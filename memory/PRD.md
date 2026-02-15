# Kozbeyli Konagi - Otel Yonetim Sistemi PRD

## Problem Statement
Kozbeyli Konagi (Izmir/Foca) butik tas otel icin kapsamli bir dijital yonetim ekosistemi. GitHub repo: https://github.com/No3214/BillionDollar

Orijinal proje Next.js 16 + Supabase + Gemini AI ile yapilmisti. Emergent platformunda React + FastAPI + MongoDB ile yeniden insa edildi.

## Tech Stack
- **Frontend:** React 19, TailwindCSS, Shadcn UI, Framer Motion
- **Backend:** FastAPI, Motor (async MongoDB)
- **Database:** MongoDB
- **AI:** Google Gemini 2.5 Flash (emergentintegrations)
- **Theme:** Kozbeyli gold (#C4972A) on dark (#0a0a0f)

## Users
- 3 kisi (otel sahibi + 2 yonetici)

## Core Requirements
1. Hotel management dashboard with real-time stats
2. Room management (4 types, 16 rooms)
3. Guest management (CRUD)
4. AI Chatbot (Gemini) for hotel assistant
5. Task management with priorities
6. Event management
7. Housekeeping automation
8. Knowledge base
9. Restaurant menu (QR ready)
10. WhatsApp/Instagram message handling

## What's Implemented (Faz 1) - Feb 2026

### Backend (19+ API endpoints)
- /api/health, /api/dashboard/stats
- /api/rooms (CRUD)
- /api/hotel/info, /api/hotel/awards, /api/hotel/policies, /api/hotel/history, /api/hotel/guide
- /api/guests (CRUD + search)
- /api/reservations (CRUD + status)
- /api/tasks (CRUD + filter)
- /api/events (CRUD)
- /api/housekeeping (CRUD + status flow)
- /api/staff (CRUD)
- /api/knowledge (CRUD + search)
- /api/chatbot (Gemini AI + history + session management)
- /api/whatsapp/webhook (AI-powered response)
- /api/instagram/webhook (AI-powered response)
- /api/messages (all platform messages)
- /api/menu (restaurant menu)
- /api/seed (database seeding)

### Frontend (10 pages)
1. Dashboard - Stats, occupancy bar, ratings, recent tasks
2. Rooms - 4 room types with features and pricing
3. Guests - Add/search guests
4. AI Chatbot - Chat interface with Gemini, quick messages
5. Messages - WhatsApp/Instagram message viewer + test
6. Tasks - Create/filter/complete/delete tasks
7. Events - Create/delete events
8. Housekeeping - Task flow (pending -> in_progress -> completed -> inspected)
9. Knowledge Base - Add/search/delete knowledge items
10. Menu - Restaurant menu with 12 categories

### Testing
- 24/24 backend tests passed (100%)
- All 10 frontend pages functional (100%)
- AI Chatbot responds in Turkish with hotel-specific knowledge

## Pending Tasks (Faz 2-4)

### P0 - Faz 2: Iletisim & Otomasyon
- [ ] Real WhatsApp Business API integration (user will provide keys)
- [ ] Real Instagram webhook integration
- [ ] Housekeeping automation (auto-schedule after checkout)
- [ ] Email campaign system

### P1 - Faz 3: Gelismis Ozellikler
- [ ] Multi-social media chatbot unified panel
- [ ] HotelRunner API integration
- [ ] Reservation system improvements
- [ ] Staff management with shifts
- [ ] KVKK compliance module

### P2 - Faz 4: Polish & UX
- [ ] Loading animations and transitions
- [ ] Multi-language support (TR, EN, DE, FR, RU)
- [ ] Foca local guide integration in UI
- [ ] QR code generation for menu
- [ ] Mobile responsive improvements
- [ ] Role-based access control

## Database Collections
- rooms, guests, reservations, tasks, events
- housekeeping, staff, knowledge, chat_messages, messages

## API Keys (in backend/.env)
- GOOGLE_API_KEY (Gemini AI - active, working)
- GROQ_API_KEY (backup)
- DEEPSEEK_API_KEY (backup)
- OPENROUTER_API_KEY (backup)
