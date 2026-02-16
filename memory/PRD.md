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
- service-worker.js: Network-first cache stratejisi, offline destek, push notification handler
- Ana ekrana ekleme ozelligi
- Sayfa basligi: "Kozbeyli Konagi"

### Faz 17: Caching + Lazy Loading + Push Notifications (TAMAMLANDI - 16 Feb 2026)

**In-Memory Caching Layer (services/cache_service.py):**
- TTLCache: short (30s), medium (5dk), long (30dk) sureler
- Onbelleklenen endpointler: rooms (medium), analytics KPI (short), revenue KPI (short)
- Cache istatistikleri: GET /api/cache/stats (hit rate, sizes)
- Cache temizleme: POST /api/cache/clear
- Dekorator tabanlı kullanım: @cached(key_prefix, duration)

**Lazy Loading + Gorsel Optimizasyonu:**
- React.lazy() ile tum sayfa bilesenlerinin tembel yuklenmesi (25+ sayfa)
- Suspense fallback: Altın renkli spinner animasyonu
- Dashboard ve Login direkt yuklenir, diger sayfalar ihtiyac durumunda yuklenir

**PWA Push Notifications:**
- Service Worker push event handler
- Sidebar bildirim zili butonu (Bildirimleri Ac/Aktif)
- Bugunun check-in/check-out bildirimleri: GET /api/notifications/today
- Bildirim aboneligi: POST /api/notifications/subscribe
- Test bildirimi: POST /api/notifications/send-test

### Faz 18: Redis + VAPID Push + Finansal Modul + HotelRunner Iyilestirme (TAMAMLANDI - 16 Feb 2026)

**Redis Caching Layer:**
- In-memory TTLCache yerine Redis'e gecis
- Redis baglanti ve otomatik fallback (Redis cokerse in-memory devam eder)
- Cache backend: redis (GET /api/cache/stats ile dogrulanabilir)

**VAPID Push Notification:**
- pywebpush ile server-side push notification
- VAPID anahtar cifti olusturuldu ve .env'e eklendi
- GET /api/notifications/vapid-key ile frontend'e public key saglanir
- POST /api/notifications/send-push ile tum abonelere bildirim gonderilebilir
- Suresi gecen abonelikler otomatik temizlenir (410 Gone)

**Gelir/Gider Takip Modulu:**
- 7 gelir kategorisi: Oda, Restoran, Bar, Etkinlik, Minibar, Ekstra Hizmet, Diger
- 17 gider kategorisi: Gida, Icecek, Temizlik, Enerji, Maas, Sigorta, Bakim, Pazarlama, Komisyon, Vergi, Kira, Ekipman, Camasir, Bahce, Eglence, Yazilim, Diger
- OTA komisyon hesaplama (brut, komisyon tutari, net tutar)
- Gunluk/Aylik rapor: Kategori bazli dagilim, kanal bazli gelir, KPI'lar
- KPI'lar: Doluluk orani, ADR, RevPAR
- Gunluk trend grafigi (gelir/gider bar chart)
- Frontend sayfasi: 3 tab (Genel Bakis, Gelir, Gider) + CRUD

**HotelRunner Iyilestirme:**
- Iptal politikasi motoru: Ozel gun (%100 ceza), normal gun (3 gun kurali)
- Ozel gunler: Hafta sonu, resmi bayramlar, 14 Subat, Yilbasi
- Webhook isleme: reservation.created/cancelled/modified
- OTA kanal yonetimi: 5 kanal (Booking %15, Expedia %18, Airbnb %3, Google %12, Trivago %10)
- Senkronizasyon log sistemi
- POST /api/hotelrunner/sync/full ile toplu senkronizasyon (mock mod)

### Faz 19: Domain Hazirligi + SEO + QR + Chatbot Iyilestirme (TAMAMLANDI - 16 Feb 2026)

**Domain Routing:**
- / (root URL) → PublicMenuPage (kozbeylikonagi.com.tr acilinca menu gelecek)
- /menu → Ayni menu sayfasi (geriye uyumluluk)
- /admin → Yonetim paneli (login sayfasi)

**SEO Optimizasyonu:**
- Title: "Kozbeyli Konagi | Butik Tas Otel - Foca, Izmir"
- Open Graph: og:title, og:description, og:image, og:url
- Twitter Card meta tags
- JSON-LD: Hotel schema (adres, koordinat, amenities, fiyat araligi)

**QR Kod Sistemi:**
- GET /api/qr/menu → PNG formatinda QR kod (boyut ayarlanabilir: 100-1000px)
- Altin renk (#C4972A) koyu arka plan (#0a0a0f) - masalara yerlestirmek icin
- Hedef URL: https://kozbeylikonagi.com.tr

**Chatbot Guncellemesi:**
- Yasakli konu tespiti: siyaset, din, tartismali konular, tibbi/hukuki, rakipler, uygunsuz icerik
- Eskalasyon protokolu: 30+ kisi grup, acil durum, sikayet, fiyat anlasmzligi
- Yeni auto-reply: ek hizmetler (camasir, transfer, otopark, bebek yatagi)
- Fiyat/oda bilgisi: Oda detaylari zenginlestirildi (amenity, hos geldin ikrami)
- False positive duzeltme: "iptal politikasi" artik siyaset olarak algilanmiyor
- Profesyonel ton: Emoji kullanimi azaltildi

### Tests: Backend 14/14 (%100), Frontend %100 - Iteration 16

## Upcoming Tasks
- P0: WhatsApp Business API canli entegrasyonu (Meta Developer Portal bilgileri bekleniyor)
- P0: HotelRunner API canli entegrasyonu (API anahtarlari bekleniyor - mock altyapi hazir)
- P3: POS entegrasyonu, Mobil personel uygulamasi
- P3: Online odeme entegrasyonu (Stripe/Iyzico)

## Tamamlanan (Eski Planlananlar)
- Musteri sadakat programi (4 seviye: Bronz→Platin)
- Ozel gun takibi (dogum gunu/yil donumu)
- Coklu dil destegi (5 dil: TR, EN, DE, FR, RU)
- Database indeksleme optimizasyonu (16+ koleksiyon)
- PWA + offline erisim
- Push notifications (VAPID server-side)
- Redis Caching Layer
- Lazy loading (25+ sayfa)
- Anti-halussinasyon modulu
- Rate limiter
- Dinamik gercek zamanli dashboard
- Gelir/Gider takip modulu
- HotelRunner iptal politikasi + webhook + kanal yonetimi
