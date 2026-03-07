# KOZBEYLI KONAGI - TAM PROJE DOKUMANTASYONU
# Sifirdan Kurulum ve Tum Detaylar

---

## 1. PROJE OZETI

**Proje Adi:** Kozbeyli Konagi Otel Yonetim Sistemi
**Amac:** Izmir/Foca'daki Kozbeyli Konagi butik tas otel icin kapsamli dijital yonetim ekosistemi
**Tur:** Full-stack web uygulamasi (SPA + REST API)
**Domain:** kozbeylikonagi.com.tr

### Ne Istendi?
1. Otel oda/misafir/rezervasyon yonetimi
2. AI destekli chatbot (Turk misafirler icin)
3. WhatsApp Business API entegrasyonu (misafir iletisimi)
4. Instagram DM entegrasyonu
5. QR kodlu dijital restoran menusu (halk icin)
6. Mutfak dashboard (siparis takibi)
7. Finansal takip (gelir/gider)
8. Dinamik fiyatlandirma (sezon, doluluk, tatil)
9. Personel ve vardiya yonetimi
10. Kat hizmetleri (temizlik) yonetimi
11. Etkinlik planlama
12. Kampanya ve email pazarlama
13. Google yorum yanitlama (AI ile)
14. Sosyal medya icerik planlama
15. Misafir sadakat programi
16. Masa rezervasyonu (restoran)
17. HotelRunner kanal yoneticisi entegrasyonu
18. Gelismis analitik ve raporlama
19. Guvenlik ve audit log sistemi
20. PWA (Progressive Web App) destegi
21. 5 dil destegi (TR/EN/DE/FR/RU)
22. Push bildirimler
23. Redis onbellek
24. Otomatik zamanli gorevler (kahvalti, temizlik, check-in hatirlatma)

---

## 2. TEKNOLOJI YIGINI (TECH STACK)

### Backend
- **Dil:** Python 3.11+
- **Framework:** FastAPI 0.110.1
- **Veritabani:** MongoDB (Motor 3.3.1 - async driver)
- **Onbellek:** Redis 7.1.1
- **Zamanlayici:** APScheduler 3.11.2
- **AI:** Google Gemini
- **Auth:** JWT (PyJWT) + bcrypt sifreleme
- **Push Bildirimi:** py-vapid + pywebpush (VAPID standardi)
- **QR Kod:** qrcode[pil] 8.2
- **HTTP Client:** httpx (WhatsApp/Instagram API icin)
- **Dosya Yukleme:** python-multipart

### Frontend
- **Framework:** React 19
- **CSS:** TailwindCSS 3.4
- **UI Kutuphanesi:** Shadcn/UI (Radix UI tabanli)
- **Animasyon:** Framer Motion 12
- **Grafik:** Recharts 3.7
- **Ikonlar:** Lucide React
- **HTTP Client:** Axios
- **Router:** React Router DOM 7.5
- **Build Tool:** CRACO (Create React App Configuration Override)
- **Bildirim:** Sonner (toast)

### Altyapi
- **Veritabani:** MongoDB (localhost:27017)
- **Onbellek:** Redis (localhost:6379)
- **Backend Port:** 8001 (uvicorn)
- **Frontend Port:** 3000 (React dev server)
- **Process Manager:** Supervisor

---

## 3. KLASOR YAPISI

```
/app/
├── backend/                          # Python FastAPI backend
│   ├── server.py                     # Ana sunucu dosyasi (FastAPI app + tum router baglantilari)
│   ├── config.py                     # Ortam degiskenleri yukleme
│   ├── database.py                   # MongoDB baglantisi (Motor client)
│   ├── helpers.py                    # Yardimci fonksiyonlar (utcnow, new_id, clean_doc)
│   ├── models.py                     # Pydantic veri modelleri
│   ├── hotel_data.py                 # Otel verileri (odalar, politikalar, fiyatlar, AI prompt)
│   ├── hotel_config.py               # Otel konfigurasyonu
│   ├── chatbot_engine.py             # AI chatbot motoru (intent tanima, flow yonetimi)
│   ├── gemini_service.py             # Google Gemini AI servisi
│   ├── anti_hallucination.py         # AI halucinasyon engelleme modulu
│   ├── rate_limiter.py               # Istek hiz sinirlandirma
│   ├── scheduler.py                  # Zamanli gorev yoneticisi (4 cron job)
│   ├── whatsapp_parser.py            # WhatsApp mesaj ayristirici
│   ├── menu_seed_data.py             # Menu baslangic verileri (100+ urun)
│   ├── knowledge_seed_data.py        # Bilgi bankasi baslangic verileri
│   ├── requirements.txt              # Python bagimliliklari
│   ├── .env                          # Ortam degiskenleri (API anahtarlari)
│   ├── uploads/                      # Dosya yuklemeleri
│   ├── routers/                      # API route modulleri (32 router)
│   │   ├── auth.py                   # Kimlik dogrulama (login, register, JWT)
│   │   ├── hotel.py                  # Otel bilgileri, politikalar, rehber
│   │   ├── rooms.py                  # Oda CRUD
│   │   ├── guests.py                 # Misafir CRUD
│   │   ├── reservations.py           # Rezervasyon CRUD + check-in/out
│   │   ├── tasks.py                  # Gorev yonetimi CRUD
│   │   ├── events.py                 # Etkinlik yonetimi CRUD
│   │   ├── housekeeping.py           # Kat hizmetleri (temizlik)
│   │   ├── staff.py                  # Personel + vardiya yonetimi
│   │   ├── knowledge.py              # Bilgi bankasi CRUD
│   │   ├── chatbot.py                # AI chatbot API
│   │   ├── messages.py               # Mesaj sistemi (SMS, email log)
│   │   ├── campaigns.py              # Kampanya yonetimi
│   │   ├── reviews.py                # Google yorum + AI yanit uretme
│   │   ├── settings.py               # Sistem ayarlari
│   │   ├── pricing.py                # Dinamik fiyatlandirma
│   │   ├── table_reservations.py     # Masa rezervasyonu (restoran)
│   │   ├── lifecycle.py              # Misafir yasam dongusu mesajlari
│   │   ├── automation.py             # Otomasyon botlari
│   │   ├── public_menu.py            # Halk menusu API (auth gerektirmez)
│   │   ├── menu_admin.py             # Menu yonetimi (admin)
│   │   ├── social_media.py           # Sosyal medya icerik yonetimi
│   │   ├── kitchen.py                # Mutfak dashboard + siparis
│   │   ├── whatsapp.py               # WhatsApp admin endpoint'leri
│   │   ├── webhooks.py               # WhatsApp + Instagram webhook'lari
│   │   ├── loyalty.py                # Sadakat programi
│   │   ├── revenue.py                # Gelir yonetimi + dinamik fiyat
│   │   ├── analytics.py              # Analitik dashboard KPI'lari
│   │   ├── audit.py                  # Guvenlik + audit log
│   │   ├── hotelrunner.py            # HotelRunner API entegrasyonu
│   │   ├── cache.py                  # Onbellek yonetimi
│   │   ├── notifications.py          # Push bildirim yonetimi
│   │   ├── financials.py             # Gelir/gider takibi
│   │   └── qr.py                     # QR kod uretici
│   ├── services/                     # Servis katmani
│   │   ├── whatsapp_service.py       # WhatsApp Business API servisi
│   │   ├── instagram_service.py      # Instagram Messaging API servisi
│   │   ├── whatsapp_triggers.py      # Otomatik WhatsApp bildirimleri
│   │   ├── cache_service.py          # Redis onbellek servisi
│   │   ├── database_optimizer.py     # MongoDB indeks yonetimi
│   │   └── push_service.py           # VAPID push bildirim servisi
│   └── tests/                        # Backend testleri (17 iterasyon)
│
├── frontend/                         # React frontend
│   ├── public/
│   │   ├── index.html                # SEO meta tag'leri, PWA manifest
│   │   ├── manifest.json             # PWA manifest
│   │   ├── service-worker.js         # Service worker (offline)
│   │   └── logo.jpeg                 # Otel logosu
│   ├── src/
│   │   ├── App.js                    # Ana uygulama (routing, sidebar, auth)
│   │   ├── App.css                   # Global stiller
│   │   ├── api.js                    # API client (axios, 100+ endpoint)
│   │   ├── index.js                  # React entry point
│   │   ├── index.css                 # TailwindCSS + ozel stiller
│   │   ├── hooks/
│   │   │   ├── useLanguage.js        # Coklu dil hook'u (5 dil)
│   │   │   └── use-toast.js          # Toast bildirim hook'u
│   │   ├── components/ui/            # Shadcn UI bilesenleri (40+ bilesen)
│   │   ├── pages/                    # Sayfa bilesenleri (30 sayfa)
│   │   │   ├── LoginPage.js          # Giris sayfasi
│   │   │   ├── Dashboard.js          # Ana panel (KPI, doluluk, trend)
│   │   │   ├── PublicMenuPage.js     # Halk menusu (QR ile erisim)
│   │   │   ├── RoomsPage.js          # Oda yonetimi
│   │   │   ├── GuestsPage.js         # Misafir yonetimi
│   │   │   ├── ReservationsPage.js   # Rezervasyon yonetimi
│   │   │   ├── ChatbotPage.js        # AI sohbet asistani
│   │   │   ├── WhatsAppPage.js       # Mesajlasma merkezi (WA + IG)
│   │   │   ├── KitchenPage.js        # Mutfak dashboard
│   │   │   ├── MenuPage.js           # Menu yonetimi (admin)
│   │   │   ├── FinancialsPage.js     # Finansal takip
│   │   │   ├── StaffPage.js          # Personel yonetimi
│   │   │   ├── HousekeepingPage.js   # Kat hizmetleri
│   │   │   ├── EventsPage.js         # Etkinlik planlama
│   │   │   ├── TasksPage.js          # Gorev yonetimi
│   │   │   ├── CampaignsPage.js      # Kampanya yonetimi
│   │   │   ├── ReviewsPage.js        # Google yorum yonetimi
│   │   │   ├── SocialMediaPage.js    # Sosyal medya
│   │   │   ├── LifecyclePage.js      # Misafir dongusu
│   │   │   ├── PricingPage.js        # Fiyatlandirma
│   │   │   ├── RevenueManagementPage.js # Gelir yonetimi
│   │   │   ├── AnalyticsPage.js      # Analitik dashboard
│   │   │   ├── AuditSecurityPage.js  # Guvenlik
│   │   │   ├── TableReservationsPage.js # Masa rezervasyonu
│   │   │   ├── AutomationPage.js     # Otomasyon yonetimi
│   │   │   ├── KnowledgeBasePage.js  # Bilgi bankasi
│   │   │   ├── HotelRunnerPage.js    # HotelRunner
│   │   │   ├── MessagesPage.js       # Mesajlar
│   │   │   ├── FocaGuidePage.js      # Foca rehberi
│   │   │   └── SettingsPage.js       # Ayarlar
│   │   └── lib/
│   │       └── utils.js              # CSS sinif birlestirme (cn)
│   ├── .env                          # Frontend ortam degiskenleri
│   ├── package.json                  # Node bagimliliklari
│   └── craco.config.js              # Build konfigurasyonu
│
└── memory/
    ├── PRD.md                        # Urun gereksinimleri dokumani
    └── CHANGELOG.md                  # Degisiklik gecmisi
```

---

## 4. VERITABANI SEMALARI (MongoDB Koleksiyonlari)

### 4.1 rooms (Odalar)
```json
{
  "id": "uuid",
  "number": "101",
  "name": "Tek Kisilik",
  "type": "single",           // single, double, suite, family
  "capacity": 2,
  "base_price": 3500,
  "status": "available",      // available, occupied, cleaning, maintenance
  "floor": 1,
  "amenities": ["wifi", "klima", "minibar"],
  "description": "...",
  "created_at": "ISO datetime"
}
```

### 4.2 guests (Misafirler)
```json
{
  "id": "uuid",
  "name": "Ali Yilmaz",
  "email": "ali@email.com",
  "phone": "+905321234567",
  "nationality": "TR",
  "id_number": "12345678901",
  "notes": "...",
  "tags": ["vip", "returning"],
  "total_stays": 3,
  "total_spent": 15000,
  "loyalty_level": "gold",
  "loyalty_points": 150,
  "created_at": "ISO datetime"
}
```

### 4.3 reservations (Rezervasyonlar)
```json
{
  "id": "uuid",
  "guest_id": "uuid",
  "guest_name": "Ali Yilmaz",
  "guest_phone": "+905321234567",
  "guest_email": "ali@email.com",
  "room_id": "uuid",
  "room_type": "double",
  "check_in": "2026-03-15",
  "check_out": "2026-03-18",
  "guests_count": 2,
  "status": "confirmed",      // pending, confirmed, checked_in, checked_out, cancelled, no_show
  "source": "booking.com",    // direct, booking.com, airbnb, phone, whatsapp
  "total_price": 10500,
  "paid_amount": 5000,
  "payment_status": "partial", // pending, partial, paid
  "notes": "...",
  "special_requests": "Deniz manzarali oda",
  "reminder_sent": false,
  "thanks_sent": false,
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime"
}
```

### 4.4 staff (Personel)
```json
{
  "id": "uuid",
  "name": "Ayse Kaya",
  "role": "reception",        // reception, housekeeping, kitchen, manager, security
  "phone": "+905551234567",
  "email": "ayse@hotel.com",
  "schedule": "08:00-16:00",
  "status": "active",
  "created_at": "ISO datetime"
}
```

### 4.5 shifts (Vardiyalar)
```json
{
  "id": "uuid",
  "staff_id": "uuid",
  "staff_name": "Ayse Kaya",
  "date": "2026-03-15",
  "shift_type": "morning",    // morning, afternoon, night
  "start_time": "08:00",
  "end_time": "16:00",
  "notes": "",
  "created_at": "ISO datetime"
}
```

### 4.6 tasks (Gorevler)
```json
{
  "id": "uuid",
  "title": "Havuz temizligi",
  "description": "...",
  "priority": "high",         // low, normal, high, urgent
  "status": "pending",        // pending, in_progress, completed, cancelled
  "assigned_to": "Ayse Kaya",
  "due_date": "2026-03-15",
  "category": "maintenance",
  "created_at": "ISO datetime"
}
```

### 4.7 events (Etkinlikler)
```json
{
  "id": "uuid",
  "title": "Canli Muzik Gecesi",
  "description": "...",
  "date": "2026-03-20",
  "start_time": "20:00",
  "end_time": "23:00",
  "location": "Bahce",
  "capacity": 50,
  "registered": 12,
  "status": "upcoming",
  "category": "entertainment",
  "created_at": "ISO datetime"
}
```

### 4.8 housekeeping (Kat Hizmetleri)
```json
{
  "id": "uuid",
  "room_id": "uuid",
  "room_number": "101",
  "assigned_to": "Fatma",
  "status": "pending",        // pending, in_progress, completed, inspected
  "priority": "normal",
  "task_type": "checkout",    // daily, checkout, deep_clean
  "notes": "",
  "started_at": null,
  "completed_at": null,
  "created_at": "ISO datetime"
}
```

### 4.9 knowledge (Bilgi Bankasi)
```json
{
  "id": "uuid",
  "title": "Iptal Politikasi",
  "content": "7 gun oncesine kadar ucretsiz iptal...",
  "category": "policy",       // policy, service, faq, guide
  "tags": ["iptal", "ceza"],
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime"
}
```

### 4.10 chat_messages (Chatbot Mesajlari)
```json
{
  "id": "uuid",
  "session_id": "uuid",
  "platform": "web",          // web, whatsapp, instagram
  "from_number": "+905321234567",
  "sender_name": "Ali",
  "message": "Bos odaniz var mi?",
  "response": "Evet, su anda...",
  "intent": "room_availability",
  "language": "tr",
  "ai_model": "gemini",
  "created_at": "ISO datetime"
}
```

### 4.11 whatsapp_messages (WhatsApp Mesajlari)
```json
{
  "id": "uuid",
  "session_id": "wa_905321234567",
  "message_id": "wamid.xxx",
  "from": "905321234567",      // gelen mesajlar icin
  "to": "905321234567",        // giden mesajlar icin
  "contact_name": "Ali",
  "text": "Merhaba",
  "type": "text",              // text, interactive, image, template
  "template_name": "",         // sablon mesajlar icin
  "wa_message_id": "",
  "direction": "incoming",     // incoming, outgoing
  "status": "sent",            // sent, delivered, read, failed, mock_sent
  "created_at": "ISO datetime"
}
```

### 4.12 instagram_messages (Instagram Mesajlari)
```json
{
  "id": "uuid",
  "session_id": "ig_123456",
  "user_id": "123456",
  "ig_message_id": "mid.xxx",
  "text": "Merhaba",
  "direction": "incoming",
  "status": "sent",
  "created_at": "ISO datetime"
}
```

### 4.13 group_notifications (Grup Bildirimleri)
```json
{
  "id": "uuid",
  "type": "breakfast_prep",    // breakfast_prep, morning_checkin_reminder, checkout_cleaning, evening_room_check, table_reservation, cleaning
  "message": "Sabah 3 oda kahvalti var...",
  "reservation_id": "",
  "status": "sent",
  "source": "scheduler",
  "created_at": "ISO datetime"
}
```

### 4.14 campaigns (Kampanyalar)
```json
{
  "id": "uuid",
  "title": "Kis Indirimi",
  "content": "...",
  "type": "email",
  "target_audience": "all",
  "discount_rate": 20,
  "start_date": "2026-01-01",
  "end_date": "2026-02-28",
  "status": "active",
  "sent_count": 0,
  "created_at": "ISO datetime"
}
```

### 4.15 reviews (Yorumlar)
```json
{
  "id": "uuid",
  "platform": "google",       // google, booking, tripadvisor
  "guest_name": "Ali Y.",
  "rating": 5,
  "content": "Harika bir deneyim...",
  "ai_response": "Tesekkur ederiz...",
  "response_tone": "professional",
  "status": "pending",        // pending, responded, archived
  "created_at": "ISO datetime"
}
```

### 4.16 incomes (Gelirler)
```json
{
  "id": "uuid",
  "date": "2026-03-15",
  "category": "room_revenue",  // room_revenue, restaurant, bar, spa, parking, event, other
  "amount": 5000,
  "currency": "TRY",
  "source": "booking.com",
  "gross_amount": 5500,
  "commission_rate": 15,
  "commission_amount": 825,
  "net_amount": 4675,
  "description": "Oda 101 - 3 gece",
  "created_at": "ISO datetime"
}
```

### 4.17 expenses (Giderler)
```json
{
  "id": "uuid",
  "date": "2026-03-15",
  "category": "food_supplies", // food_supplies, cleaning, utilities, salary, maintenance, marketing, insurance, tax, rent, equipment, fuel, communication, office, decoration, garden, laundry, other
  "amount": 2500,
  "currency": "TRY",
  "description": "Haftalik market alisverisi",
  "is_paid": true,
  "created_at": "ISO datetime"
}
```

### 4.18 table_reservations (Masa Rezervasyonlari)
```json
{
  "id": "uuid",
  "guest_name": "Mehmet",
  "phone": "+905551234567",
  "date": "2026-03-15",
  "time": "19:00",
  "party_size": 4,
  "table_name": "Bahce Masa 3",
  "status": "confirmed",
  "special_requests": "Dogum gunu",
  "source": "whatsapp",
  "created_at": "ISO datetime"
}
```

### 4.19 menu_items (Menu Urunleri)
```json
{
  "id": "uuid",
  "name": "Gurme Serpme Kahvalti",
  "description": "Sahanda tereyagli sucuklu...",
  "price": 750,
  "category_id": "uuid",
  "is_available": true,
  "is_vegetarian": false,
  "is_vegan": false,
  "allergens": [],
  "sort_order": 1,
  "created_at": "ISO datetime"
}
```

### 4.20 menu_categories (Menu Kategorileri)
```json
{
  "id": "uuid",
  "name": "Kahvalti",
  "slug": "kahvalti",
  "sort_order": 1,
  "is_active": true,
  "created_at": "ISO datetime"
}
```

### 4.21 social_posts (Sosyal Medya Gonderileri)
```json
{
  "id": "uuid",
  "title": "Bahar Fotografi",
  "content": "...",
  "platform": "instagram",
  "image_url": "",
  "scheduled_date": "2026-03-20",
  "status": "draft",
  "hashtags": ["#kozbeylikonagi", "#foca"],
  "created_at": "ISO datetime"
}
```

### 4.22 kitchen_orders (Mutfak Siparisleri)
```json
{
  "id": "uuid",
  "room_number": "101",
  "guest_name": "Ali",
  "items": [{"name": "Menemen", "quantity": 2}],
  "status": "preparing",      // new, preparing, ready, delivered, cancelled
  "priority": "normal",
  "notes": "",
  "created_at": "ISO datetime"
}
```

### 4.23 audit_logs (Denetim Kayitlari)
```json
{
  "id": "uuid",
  "action": "create",         // create, update, delete, login, logout
  "entity": "reservation",
  "entity_id": "uuid",
  "user_id": "uuid",
  "user_name": "admin",
  "details": {},
  "ip_address": "1.2.3.4",
  "created_at": "ISO datetime"
}
```

### 4.24 users (Kullanicilar)
```json
{
  "id": "uuid",
  "username": "admin",
  "name": "Sistem Yoneticisi",
  "email": "admin@hotel.com",
  "password_hash": "bcrypt hash",
  "role": "admin",            // admin, reception, kitchen, staff
  "permissions": ["*"],
  "is_active": true,
  "created_at": "ISO datetime"
}
```

### 4.25 push_subscriptions (Push Abonelikleri)
```json
{
  "id": "uuid",
  "endpoint": "https://fcm.googleapis.com/...",
  "keys": {"p256dh": "...", "auth": "..."},
  "user_id": "admin",
  "created_at": "ISO datetime"
}
```

---

## 5. API ENDPOINT'LERI (Tum 200+ endpoint)

### 5.1 Kimlik Dogrulama (/api/auth)
| Metod | Endpoint | Aciklama |
|-------|----------|----------|
| POST | /api/auth/login | Giris yap (username + password → JWT token) |
| POST | /api/auth/register | Yeni kullanici olustur (sadece admin) |
| POST | /api/auth/setup | Ilk admin kullanici olustur |
| GET | /api/auth/me | Oturum acmis kullanici bilgisi |
| GET | /api/auth/users | Tum kullanicilari listele |
| GET | /api/auth/roles | Mevcut rolleri listele |
| DELETE | /api/auth/users/{id} | Kullanici sil |

### 5.2 Odalar (/api/rooms)
| Metod | Endpoint | Aciklama |
|-------|----------|----------|
| GET | /api/rooms | Tum odalari listele |
| GET | /api/rooms/{id} | Oda detayi |
| POST | /api/rooms | Yeni oda ekle |
| PATCH | /api/rooms/{id} | Oda guncelle |
| DELETE | /api/rooms/{id} | Oda sil |

### 5.3 Misafirler (/api/guests)
| Metod | Endpoint | Aciklama |
|-------|----------|----------|
| GET | /api/guests | Misafir listesi (arama, filtreleme) |
| GET | /api/guests/{id} | Misafir detayi |
| POST | /api/guests | Yeni misafir ekle |
| PATCH | /api/guests/{id} | Misafir guncelle |

### 5.4 Rezervasyonlar (/api/reservations)
| Metod | Endpoint | Aciklama |
|-------|----------|----------|
| GET | /api/reservations | Rezervasyon listesi (tarih, durum filtresi) |
| GET | /api/reservations/{id} | Rezervasyon detayi |
| POST | /api/reservations | Yeni rezervasyon olustur |
| PATCH | /api/reservations/{id} | Rezervasyon guncelle |
| PATCH | /api/reservations/{id}/status | Durum degistir (check-in, check-out, iptal) |
| DELETE | /api/reservations/{id} | Rezervasyon sil |

### 5.5 AI Chatbot (/api/chatbot)
| Metod | Endpoint | Aciklama |
|-------|----------|----------|
| POST | /api/chatbot | Mesaj gonder, AI yanit al |
| GET | /api/chatbot/history/{session_id} | Sohbet gecmisi |
| DELETE | /api/chatbot/session/{session_id} | Sohbet temizle |

### 5.6 WhatsApp (/api/whatsapp + /api/webhooks)
| Metod | Endpoint | Aciklama |
|-------|----------|----------|
| GET | /api/webhooks/whatsapp | Webhook dogrulama (Meta handshake) |
| POST | /api/webhooks/whatsapp | Gelen WhatsApp mesaji isleme |
| GET | /api/webhooks/status | WhatsApp + Instagram platform durumu |
| POST | /api/whatsapp/send | Manuel metin mesaji gonder |
| POST | /api/whatsapp/send-template | Sablon mesaji gonder |
| POST | /api/whatsapp/send-checkout-thanks | Check-out tesekkur mesaji |
| POST | /api/whatsapp/send-reservation-reminder | Rezervasyon hatirlatma |
| POST | /api/whatsapp/send-welcome | Check-in hos geldiniz |
| POST | /api/whatsapp/notify-cleaning | Temizlik ekibi bildirimi |
| POST | /api/whatsapp/send-room-ready | Oda hazir bildirimi |
| GET | /api/whatsapp/templates | Sablon listesi |
| GET | /api/whatsapp/config | API yapilandirma durumu |
| GET | /api/whatsapp/sessions | WhatsApp konusmalari |
| GET | /api/whatsapp/messages | Mesaj listesi |
| GET | /api/whatsapp/notifications | Grup bildirimleri |

### 5.7 Instagram (/api/webhooks/instagram)
| Metod | Endpoint | Aciklama |
|-------|----------|----------|
| GET | /api/webhooks/instagram | Webhook dogrulama |
| POST | /api/webhooks/instagram | Gelen Instagram DM isleme |
| GET | /api/webhooks/instagram/sessions | Instagram konusmalari |
| GET | /api/webhooks/instagram/messages | Instagram mesajlari |

### 5.8 Finansal Takip (/api/financials)
| Metod | Endpoint | Aciklama |
|-------|----------|----------|
| POST | /api/financials/income | Gelir ekle |
| POST | /api/financials/expense | Gider ekle |
| GET | /api/financials/income | Gelir listesi |
| GET | /api/financials/expense | Gider listesi |
| GET | /api/financials/categories | Kategori listesi |
| GET | /api/financials/daily/{date} | Gunluk ozet |
| GET | /api/financials/monthly | Aylik rapor |
| DELETE | /api/financials/{id} | Kayit sil |

### 5.9 Menu (/api/public + /api/menu-admin)
| Metod | Endpoint | Aciklama |
|-------|----------|----------|
| GET | /api/public/menu | Halk menusu (auth yok) |
| GET | /api/public/theme | Menu temasi |
| GET | /api/menu-admin/items | Menu urunleri |
| POST | /api/menu-admin/items | Urun ekle |
| PATCH | /api/menu-admin/items/{id} | Urun guncelle |
| DELETE | /api/menu-admin/items/{id} | Urun sil |
| GET | /api/menu-admin/categories | Kategoriler |
| POST | /api/menu-admin/categories | Kategori ekle |
| PATCH | /api/menu-admin/theme | Tema guncelle |

### 5.10 Analitik + Gelir + Fiyatlandirma
| Metod | Endpoint | Aciklama |
|-------|----------|----------|
| GET | /api/analytics/dashboard/kpi | KPI metrikleri |
| GET | /api/analytics/revenue/trend | Gelir trendi |
| GET | /api/analytics/bookings/sources | Kaynak dagilimi |
| GET | /api/analytics/occupancy/heatmap | Doluluk isi haritasi |
| GET | /api/analytics/rooms/performance | Oda performansi |
| GET | /api/revenue/pricing/calculate | Dinamik fiyat hesapla |
| GET | /api/revenue/pricing/calendar | Fiyat takvimi |
| POST | /api/revenue/pricing/update-all | Tum fiyatlari guncelle |
| GET | /api/revenue/forecast | Gelir tahmini |

### 5.11 Diger Onemli Endpoint'ler
| Metod | Endpoint | Aciklama |
|-------|----------|----------|
| GET | /api/health | Sunucu sagligi |
| POST | /api/seed | Baslangic verilerini yukle |
| GET | /api/qr | QR kod uret (PNG) |
| GET | /api/cache/stats | Onbellek istatistikleri |
| POST | /api/cache/clear | Onbellek temizle |
| GET | /api/audit/logs | Denetim kayitlari |
| POST | /api/audit/check-security | Guvenlik kontrolu calistir |
| POST | /api/notifications/subscribe | Push bildirim abone ol |
| GET | /api/notifications/vapid-key | VAPID public key |

---

## 6. ORTAM DEGISKENLERI (.env)

### Backend (.env)
```bash
# Veritabani
MONGO_URL="mongodb://localhost:27017"
DB_NAME="vericevir_hotel"
CORS_ORIGINS="*"

# AI Anahtarlari
GOOGLE_API_KEY=AIzaSy...                    # Google Gemini AI

# Push Bildirim (VAPID)
VAPID_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----
...PEM formati...
-----END PRIVATE KEY-----
VAPID_PUBLIC_KEY=BD5gh8...
VAPID_CLAIMS_EMAIL=mailto:info@kozbeylikonagi.com

# Onbellek
REDIS_URL=redis://localhost:6379/0

# WhatsApp Business API (Meta)
WHATSAPP_ACCESS_TOKEN=                      # Meta'dan alinacak
WHATSAPP_PHONE_NUMBER_ID=                   # Meta'dan alinacak
WHATSAPP_BUSINESS_ACCOUNT_ID=               # Meta'dan alinacak
WHATSAPP_APP_SECRET=                        # Meta'dan alinacak
WHATSAPP_VERIFY_TOKEN=kozbeyli_verify_2026  # Kendi belirlediginiz token
WHATSAPP_GROUP_NUMBER=                      # Bildirim gonderilecek grup/numara

# Instagram API (Meta)
INSTAGRAM_ACCESS_TOKEN=                     # Meta'dan alinacak
INSTAGRAM_PAGE_ID=                          # Meta'dan alinacak
INSTAGRAM_VERIFY_TOKEN=kozbeyli_ig_verify_2026
```

### Frontend (.env)
```bash
REACT_APP_BACKEND_URL=https://kozbeylikonagi.com.tr   # Production URL
REACT_APP_VAPID_PUBLIC_KEY=BD5gh8...                    # Push bildirim icin
```

---

## 7. SIFIRDAN KURULUM REHBERI

### 7.1 Gereksinimler
- Python 3.11+
- Node.js 18+
- MongoDB 6+
- Redis 7+
- Yarn paket yoneticisi

### 7.2 Backend Kurulumu
```bash
# 1. Klasore git
cd backend

# 2. Virtual environment olustur
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Bagimliliklari yukle
pip install -r requirements.txt

# 4. .env dosyasini olustur (yukaridaki sablona gore)
cp .env.example .env
# .env dosyasini duzenle

# 5. MongoDB'nin calistigindan emin ol
mongosh --eval "db.adminCommand('ping')"

# 6. Redis'in calistigindan emin ol
redis-cli ping

# 7. Sunucuyu baslat
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# 8. Baslangic verilerini yukle
curl -X POST http://localhost:8001/api/seed
```

### 7.3 Frontend Kurulumu
```bash
# 1. Klasore git
cd frontend

# 2. Bagimliliklari yukle
yarn install

# 3. .env dosyasini olustur
echo 'REACT_APP_BACKEND_URL=http://localhost:8001' > .env

# 4. Gelistirme sunucusunu baslat
yarn start
```

### 7.4 Ilk Giris
- Tarayicida `http://localhost:3000/admin` adresine gidin
- "Ilk kurulum? Admin olustur" linkine tiklayin
- Varsayilan giris: `admin` / `admin123` (veya kozbeyli2026)

---

## 8. ZAMANLI GOREVLER (SCHEDULER)

Sistem 4 otomatik zamanli gorev calistirir:

| Saat | Gorev | Aciklama |
|------|-------|----------|
| 01:00 | Kahvalti Hazirligi | Kac kisi kahvalti edecek, bildirimi olusturur |
| 08:30 | Sabah Hatirlama | Tuvalet temizlik + check-in odalari hazirligi |
| 12:30 | Check-out Temizlik | Cikis yapan odalarin temizlik listesi |
| 18:00 | Aksam Oda Kontrolu | Bos odalarda klima/isik kontrolu |

---

## 9. AI CHATBOT MOTORU

### Nasil Calisir?
1. Kullanici mesaj gonderir (web, WhatsApp veya Instagram)
2. `chatbot_engine.py` mesaji isler:
   a. Yasakli konu kontrolu (siyaset, din, kisisel bilgi)
   b. Intent (niyet) tanima (oda sorgusu, fiyat, konum, menu, rezervasyon)
   c. Conversation flow kontrolu (masa rezervasyonu adim adim)
   d. Otomatik yanit eslestirme
3. Eslesen yanit yoksa → Google Gemini AI'ya gonderilir
4. Gemini, otel verilerini iceren system prompt ile yanitlar

### Desteklenen Intent'ler
- `room_info` - Oda bilgisi sorgusu
- `price_inquiry` - Fiyat sorgusu
- `reservation` - Rezervasyon yapma istegi
- `table_reservation` - Masa rezervasyonu (flow baslatiyor)
- `location` - Konum/adres bilgisi
- `breakfast` - Kahvalti bilgisi
- `menu` - Menu sorgusu
- `pool` - Havuz bilgisi
- `pet_policy` - Evcil hayvan politikasi
- `check_times` - Check-in/out saatleri
- `wifi` - WiFi bilgisi
- `parking` - Park bilgisi
- `transfer` - Transfer hizmeti
- `contact` - Iletisim bilgisi
- `complaint` - Sikayet (eskalasyon)
- `forbidden` - Yasakli konu (reddedilir)

---

## 10. WHATSAPP BUSINESS API ENTEGRASYONU

### Mevcut Durum
- **Sistem tamamen hazir**, mock modda calisiyor
- API anahtarlari girildiginde otomatik aktif olacak

### WhatsApp API Anahtari Nasil Alinir?

#### Yontem 1: Meta Business (Ucretsiz ama teknik)
1. `developers.facebook.com` adresine gidin
2. "Create App" → "Business" secin
3. "Kendi isletmem icin" secenegini secin (yazilim firmasi secmeyin!)
4. WhatsApp urununu ekleyin
5. Test numarasi alinir, asagidaki bilgileri kopyalayin:
   - **Phone Number ID** → `WHATSAPP_PHONE_NUMBER_ID`
   - **Access Token** → `WHATSAPP_ACCESS_TOKEN`
   - **App Secret** (Settings → Basic) → `WHATSAPP_APP_SECRET`
6. Webhook URL olarak ayarlayin: `https://kozbeylikonagi.com.tr/api/webhooks/whatsapp`
7. Verify Token: `kozbeyli_verify_2026`

#### Yontem 2: BSP Kullanmak (Kolay ama ucretli)
- **WATI.io** (Turkce destek, aylik ~$49)
- **360dialog** (Daha ucuz, teknik)
- **Twilio** (Uluslararasi, guvenilir)

Bu firmalar size hazir API anahtarlari verir, Meta'ya siz basvurmak zorunda kalmazsiniz.

### 5 Hazir WhatsApp Sablonu
1. **checkout_thanks_review** - Check-out tesekkur + yorum istegi
2. **reservation_reminder_1day** - Rezervasyon hatirlatma (1 gun once)
3. **welcome_checkin** - Check-in hos geldiniz
4. **cleaning_notification** - Temizlik ekibi bildirimi
5. **room_ready_notification** - Oda hazir bildirimi

---

## 11. HOTELRUNNER ENTEGRASYONU

### Mevcut Durum
- Altyapi hazir, mock modda
- HotelRunner API anahtarlari gerekiyor

### HotelRunner API Nasil Alinir?
1. `hotelrunner.com/tr` adresine gidin
2. **Otel hesabi** acin (yazilim firmasi olarak degil, otel sahibi olarak!)
3. Destek hattini arayin: "Otelim icin API erisimi istiyorum" deyin
4. Size `API_KEY` ve `API_SECRET` verecekler
5. .env dosyasina ekleyin

---

## 12. VERCEL DEPLOYMENT REHBERI

### Adim 1: Projeyi GitHub'a Yukleyin
Chat alanindaki "Save to Github" butonunu kullanin.

### Adim 2: Vercel Hesabi Olusturun
1. `vercel.com` adresine gidin
2. GitHub hesabinizla giris yapin

### Adim 3: Proje Import
1. "Import Project" → GitHub repo'nuzu secin
2. Framework: "Other" secin (monorepo oldugu icin)

### Adim 4: Backend Deploy (Vercel Serverless Functions)
```
# vercel.json (root'a ekleyin)
{
  "builds": [
    { "src": "backend/server.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "backend/server.py" }
  ]
}
```

### Adim 5: Frontend Deploy
```
# Build ayarlari:
Root Directory: frontend
Build Command: yarn build
Output Directory: build
```

### Adim 6: Ortam Degiskenleri
Vercel Dashboard → Settings → Environment Variables:
- Tum backend .env degiskenlerini ekleyin
- `MONGO_URL` icin MongoDB Atlas kullanin (bulut veritabani)
- `REDIS_URL` icin Redis Cloud (upstash.com) kullanin

### Adim 7: Domain Baglama
1. Vercel Dashboard → Domains → "kozbeylikonagi.com.tr" ekleyin
2. Domain panelinizde (domain satin aldiginiz yer):
   - A Record: `76.76.21.21` (Vercel IP)
   - CNAME: `cname.vercel-dns.com`
3. SSL otomatik aktif olacak

### Alternatif: VPS Deploy (Daha Kontrol)
Eger Vercel yerine kendi sunucunuzu kullanmak isterseniz:
```bash
# Sunucuda:
apt update && apt install -y python3-pip nodejs npm mongodb redis-server nginx

# Backend
cd backend
pip install -r requirements.txt
# systemd service olusturun: uvicorn server:app --host 0.0.0.0 --port 8001

# Frontend
cd frontend
yarn install && yarn build
# nginx ile /var/www/html/ altina kopyalayin

# Nginx config:
# / → frontend build
# /api → proxy_pass http://localhost:8001/api
```

---

## 13. GIRIS BILGILERI

| Kullanici | Sifre | Rol |
|-----------|-------|-----|
| admin | admin123 | Sistem Yoneticisi (tam yetki) |

Yeni kullanici eklemek icin: Admin Panel → Ayarlar → Kullanici Yonetimi

### Roller ve Yetkiler
- **admin**: Tum sayfalara erisim
- **reception**: Rezervasyon, misafir, oda, check-in/out
- **kitchen**: Mutfak dashboard, siparis, menu
- **staff**: Gorevler, kat hizmetleri

---

## 14. ROUTING YAPISI

| URL | Ne Gosterir |
|-----|-------------|
| `/` | Halk menusu (QR ile erisilen restoran menusu) |
| `/menu` | Halk menusu (alternatif URL) |
| `/admin` | Yonetim paneli giris sayfasi |
| `/admin` (giris yapilinca) | Dashboard + 30 sayfa |

---

## 15. ONEMLI NOTLAR

1. **Mock Mod**: WhatsApp, Instagram ve HotelRunner API'leri su anda mock modda calisiyor. Mesajlar veritabaninda saklanir ama gercek gonderim yapilmaz. API anahtarlari girildiginde otomatik aktif olur.

2. **Redis**: Redis sunucusu calismiyorsa, sistem otomatik olarak in-memory onbellege geri doner.

3. **AI Chatbot**: Google Gemini AI kullanir. GOOGLE_API_KEY olmadan AI yanit uretmez.

4. **Push Bildirimleri**: VAPID anahtarlari .env dosyasinda tanimli. Tarayici izni gerektirir.

5. **PWA**: Uygulama Progressive Web App olarak calisir. Mobil cihazlarda "Ana ekrana ekle" secenegi ile kullanilabilir.

6. **Menu**: 100+ urun, 16 kategori (Kahvalti, Extralar, Baslangic, Pizza, Peynir Tabagi, Ana Yemek, Ara Sicaklar, Mezeler, Tatlilar, Sicak Icecekler, Soguk Icecekler, Saraplar, Kokteyller, Biralar, Viskiler).

---

## 16. DESTEK VE ILETISIM

- **Teknik Sorunlar**: GitHub Issues uzerinden bildirin
- **WhatsApp API Yardim**: WATI.io destek hattini arayin (en kolay yontem)
- **HotelRunner**: hotelrunner.com/tr destek hattini arayin
- **Domain**: Domain saginizdan Vercel DNS ayarlarini yapin
