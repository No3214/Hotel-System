# Kozbeyli Konagi - Otel Yonetim Sistemi PRD

## Problem Statement
Kozbeyli Konagi (Izmir/Foca) butik tas otel icin kapsamli dijital yonetim ekosistemi.

## Tech Stack
- **Frontend:** React 19, TailwindCSS, Shadcn UI, Framer Motion
- **Backend:** FastAPI, Motor (async MongoDB), 25 modular routers
- **Database:** MongoDB (persistent)
- **AI:** Google Gemini 2.5 Flash (emergentintegrations)
- **Auth:** JWT + bcrypt, role-based (admin/reception/kitchen/staff)
- **Scheduler:** APScheduler (4 zamanli gorev)
- **Security:** Anti-Hallucination Module, Rate Limiter

## Implementation Status

### Faz 1-12: Temel Sistem (TAMAMLANDI - onceki oturumlar)
- Dashboard, Room/Guest/Reservation CRUD, AI Chatbot (Gemini)
- Staff/Shifts, Events, Housekeeping, Knowledge Base
- QR Menu (100+ urun, 16 kategori), Sosyal Medya (6 platform)
- Masa Rez. (19 masa), Mutfak Dashboard, WhatsApp Bot (mock)
- Konusamali Rezervasyon Akisi, Google Yorum Yanitlayici

### Faz 13: Operasyonel Otomasyon + Etkinlik Yonetimi (TAMAMLANDI - 15 Feb 2026)
- APScheduler: Kahvalti (01:00), Sabah Hatirlama (08:30), Check-out Temizlik (12:30)
- 6 Otomasyon Botu, Grup Bildirimleri (mock WhatsApp)
- Etkinlikler: 7 Subat Ece Yazar + 14 Subat GORAY (kapak gorseli, menu, fiyat)

### Faz 14: Guvenlik + Sadakat Sistemi (TAMAMLANDI - 15 Feb 2026)

**Anti-Halucinasyon Modulu (anti_hallucination.py):**
- AI yanitlarinda otel disi bilgi uretimini engelleyen kontrol katmani
- Fiyat dogrulama: hotel_data.py'deki bilinen fiyatlarla karsilastirma
- Olmayan hizmet tespiti: havuz, spa, sauna, oda servisi vb.
- Yanlis telefon/IBAN/oda sayisi kontrol
- Confidence score (0-1 arasi guven skoru)
- Kritik sorunlarda otomatik uyari ekleme

**Rate Limiter (rate_limiter.py):**
- Session bazli istek sinirlamasi
- Chatbot: 15 istek/dakika, Reviews: 10 istek/dakika
- 429 HTTP yaniti + retry_after bilgisi
- In-memory sayac ile dusuk gecikmeli kontrol

**Musteri Sadakat Sistemi (routers/loyalty.py):**
- 4 Seviye: Bronz (1-2, %0), Gumus (3-4, %5), Altin (5-9, %10), Platin (10+, %15)
- Telefon/email ile tekrar gelen misafir eslesme
- Misafir profili: toplam konaklama, harcama, son ziyaret
- Sonraki seviye bilgisi ve gerekli konaklama sayisi
- VIP misafir listesi, sadakat istatistikleri
- Check-out sonrasi otomatik guncelleme endpoint'i

**Yeni API Endpoint'leri:**
- GET /api/loyalty/levels, /api/loyalty/stats, /api/loyalty/guests
- GET /api/loyalty/guest/{id}
- POST /api/loyalty/update-guest/{id}, /api/loyalty/match-guest

**Frontend Guncellemesi (GuestsPage.js):**
- Sadakat istatistik kartlari (Toplam, Tekrar Gelen, Seviye Dagilimi, VIP)
- Tumu / VIP tab filtreleri
- Misafir detay dialog'u: iletisim bilgileri + sadakat karti
- Konaklama gecmisi, sonraki seviye bilgisi

### Tests: Backend 19/19 (%100), Frontend %100 - Iteration 9

### Faz 15: Aksam Oda Kontrolu + Dinamik Dashboard + Coklu Dil (TAMAMLANDI - 15 Feb 2026)

**18:00 Aksam Oda Kontrolu (scheduler.py):**
- Check-out yapan misafirlerin odalarinda klima/isik kontrolu hatirlatmasi
- CronTrigger(hour=18, minute=0) ile zamanlanmis
- Manuel tetikleme: POST /api/automation/evening-room-check
- Otomasyon ozet sayfasinda evening_checks sayaci

**Dinamik Gercek Zamanli Dashboard (Dashboard.js):**
- 4 KPI karti: Doluluk, Bugunun Giris/Cikislari, Aylik Gelir
- Haftalik doluluk trendi bar grafikler (son 7 gun)
- Oda durum gridi (renk kodlu: musait/dolu/bakim/temizlik)
- Platform puanlari (Booking, Tripadvisor, vb.)
- Son aktiviteler feed'i
- 30 saniye otomatik yenileme + CANLI gostergesi
- Manuel yenileme butonu

**Coklu Dil Destegi (5 dil):**
- Turkce, English, Deutsch, Francais, Russkiy
- LanguageProvider context (hooks/useLanguage.js)
- Sidebar dil secici (Globe ikonu)
- localStorage'da tercih kaydi
- 67 anahtar/dil cevirileri
- Sidebar navigasyon, dashboard, genel UI etiketleri

### Tests: Backend 20/20 (%100), Frontend %100 - Iteration 10

## Architecture
```
backend/
├── server.py                    (FastAPI + 25 router)
├── anti_hallucination.py        (NEW: AI guvenlik katmani)
├── rate_limiter.py              (NEW: Istek sinirlamasi)
├── scheduler.py                 (APScheduler - 3 gorev)
├── gemini_service.py            (Gemini AI)
├── chatbot_engine.py            (Multi-agent router)
├── hotel_data.py                (Otel verileri)
└── routers/
    ├── loyalty.py               (NEW: Sadakat sistemi)
    ├── automation.py            (6 bot + zamanli gorevler)
    ├── chatbot.py               (UPDATED: rate limit + anti-hal)
    ├── events.py                (Etkinlikler + seed)
    └── ... (21 diger router)

frontend/src/
├── pages/
│   ├── GuestsPage.js            (UPDATED: Sadakat entegrasyonu)
│   └── ... (24+ sayfa)
├── api.js                       (UPDATED: loyalty endpoint'leri)
└── App.js
```

## Credentials
- Admin: admin / admin123

## Mocked Features
- WhatsApp Business API (mock modda DB'ye kaydeder)
- Sosyal medya paylasim (published olarak isaretler)
- Email kampanya gonderimi
- Otomasyon bildirimleri (grup bildirim mock)

### Faz 16: P2 Optimizasyonlar - Database Indexing + PWA (TAMAMLANDI - 16 Feb 2026)

**Database Indexing Optimizasyonu:**
- MongoDB koleksiyonlarina performans indeksleri eklendi
- 13 koleksiyon: reservations, guests, rooms, audit_logs, tasks, events, housekeeping, table_reservations, messages, campaigns, staff, loyalty, dynamic_pricing_rules
- Backend startup'inda otomatik uygulama (services/database_optimizer.py)

**PWA (Progressive Web App):**
- manifest.json: Ad, ikon, tema rengi, standalone gorunum
- service-worker.js: Network-first cache stratejisi, offline destek
- Ana ekrana ekleme ozelligi
- Sayfa basligi: "Kozbeyli Konagi"

### Tests: Backend 21/22 (%95 - 1 test script hatasi), Frontend %100 - Iteration 12

## Upcoming Tasks
- P0: WhatsApp Business API canli entegrasyonu (Meta Developer Portal bilgileri bekleniyor)
- P0: HotelRunner API entegrasyonu (API bilgileri bekleniyor)
- P0: Gelir/Gider Takibi & Finansal Raporlama (kullanicinin paylastigi referans belgeden)
- P2: Redis Caching Layer
- P2: CDN ile Gorsel Optimizasyonu
- P2: Lazy Loading implementasyonu
- P3: POS entegrasyonu, Mobil personel uygulamasi
- P3: Online odeme entegrasyonu (Stripe/Iyzico)
