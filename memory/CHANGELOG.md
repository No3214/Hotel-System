# Kozbeyli Konagi - Degisiklik Gunlugu

## [2026-02-15] - Aksam Oda Kontrolu + Dinamik Dashboard + Coklu Dil

### Eklendi
- **18:00 Aksam Oda Kontrolu:** Check-out odalarda klima/isik kontrol hatirlatmasi (CronTrigger 18:00)
- **Dinamik Gercek Zamanli Dashboard:**
  - 4 KPI karti (doluluk, giris/cikis, gelir)
  - Haftalik doluluk trendi bar grafigi
  - Oda durum gridi (renk kodlu)
  - Platform puanlari, son aktiviteler
  - 30s otomatik yenileme + CANLI gostergesi
- **Coklu Dil Destegi (5 dil):**
  - TR, EN, DE, FR, RU
  - LanguageProvider context + sidebar dil secici
  - 67 anahtar/dil, localStorage'da tercih kaydi

### Test Sonuclari
- Backend: 20/20 (%100) - Iteration 10
- Frontend: Tum ozellikler calisir durumda (%100)

---


## [2026-02-15] - Guvenlik + Sadakat Sistemi

### Eklendi
- **Anti-Halucinasyon Modulu:** AI yanitlarinda fiyat/telefon/hizmet dogrulamasi, confidence score
- **Rate Limiter:** Session bazli istek siniri (chatbot: 15/dk, reviews: 10/dk), 429 yaniti
- **Musteri Sadakat Sistemi:**
  - 4 seviye: Bronz (0%), Gumus (%5), Altin (%10), Platin (%15)
  - Telefon/email ile tekrar gelen misafir eslestirme
  - Misafir profili + konaklama gecmisi
  - VIP misafir listesi
- **GuestsPage:** Sadakat kartlari, VIP tab, detay dialog

### Test Sonuclari
- Backend: 19/19 (%100)
- Frontend: Tum sayfalar calisir durumda (%100)

---

## [2026-02-15] - Operasyonel Otomasyon + Etkinlik Yonetimi

### Eklendi
- **Zamanli Gorev Sistemi (APScheduler):**
  - Kahvalti Hazirligi: Her gece 01:00
  - Sabah Hatirlama: Her gun 08:30 (tuvalet temizlik + check-in hazirligi)
  - Check-out Temizlik: Her gun 12:30
- **6 Otomasyon Botu:** Kahvalti, Sabah Hatirlama, Temizlik, Odeme, Iptal, Mutfak Tahmini
- **Otomasyon Dashboard:** 3 tab (Botlar, Grup Bildirimleri, Islem Gecmisi)
- **Etkinlikler:**
  - 7 Subat Canli Muzik - Ece Yazar (Alkolu 2750 TL, Sinirsiz 5500 TL)
  - 14 Subat Sevgililer Gunu - GORAY Akustik (Alkolu 3500 TL, Sinirsiz 6000 TL)
  - Kapak gorseli, menu detaylari, sanatci bilgisi destegi
- **Yeni API Endpoint'leri:** breakfast-notification, morning-reminders, cleaning-notification, scheduled-jobs, group-notifications, seed-samples

### Test Sonuclari
- Backend: 30/30 (%100)
- Frontend: Tum sayfalar calisir durumda (%100)

---

## [2026-02-15] - QR Menu Footer Guncellemesi

### Eklendi
- WiFi sifresi gosterimi (KozbeyliKonagi2024)
- Sosyal medya linkleri: Instagram, Facebook
- Google Maps konum linki
- Telefon linki (tek tikla ara)
- "Bizi Degerlendirin" butonu (Google Reviews)

---

## [2026-02-15] - Oda Yapilandirmasi Guncellemesi

### Degistirildi
- 16 oda yeni yapilandirma:
  - 4 adet 4 kisilik oda
  - 2 adet Superior oda  
  - 2 adet 3 kisilik oda
  - 4 adet Standart (Deniz Manzarali)
  - 4 adet Standart (Kara Manzarali)

---

## [2026-02-15] - Masa Rezervasyon Sistemi v2

### Eklendi
- **Masa Yapilandirmasi Guncellendi:**
  - 9 adet 2 kisilik masa
  - 4 adet 3 kisilik masa
  - 6 adet 4 kisilik masa
  - Toplam: 19 masa

- **Buyuk Grup Destegi (5-12 kisi):**
  - Masa birlestirme ozelligi
  - Masa 14-15 birlestirme (8 kisi, ic mekan)
  - Masa 17-18 birlestirme (8 kisi, dis mekan)
  - Masa 14-15-16 birlestirme (12 kisi, ic mekan)

- **Ogun Bazli Sureler:**
  - Kahvalti: 2 saat (08:00-10:30)
  - Oglen yemegi: 2 saat (12:00-14:00)
  - Aksam yemegi: 4 saat (18:00-20:30)

### Degistirildi
- Masa secimi artik kisi sayisina gore akilli calisiyor
- Cakisma kontrolu guncellendi (birlesik masalar icin)

---

## [2026-02-15] - Sosyal Medya Publisher v2

### Eklendi
- TikTok platformu destegi
- LinkedIn platformu destegi
- Google Drive linki ile gorsel ekleme
- Frame preview'da gorsel gosterimi

### Kaldirildi
- Dosya yukleme ozelligi (5MB limiti yetersizdi)

### Degistirildi
- Toplam 6 platform: Instagram, Facebook, X, TikTok, LinkedIn, WhatsApp

---

## [2026-02-15] - QR Menu Renk Guncellemesi

### Degistirildi
- Altin/sari renkler kaldirildi
- Yeni palet: Beyaz, Bej (#F5F2ED), Yesil (#7A8B6F)
- Fiyatlar beyaz renkte
- Kategori butonlari beyaz/bej tonlarinda

---

## [2026-02-15] - Login Duzeltmesi

### Duzeltildi
- "Admin olustur" butonundaki "undefined" hatasi
- Setup response handling duzeltildi

### Degistirildi
- Varsayilan sifre: admin123

---

## Onceki Surumler

### [2026-02-14] - QR Menu Sistemi
- 100+ menu ogesi
- Mobil uyumlu tasarim
- Animasyonlu UI (Framer Motion)
- Admin panelinden tam CRUD

### [2026-02-14] - Sosyal Medya Publisher v1
- Instagram, Facebook, X, WhatsApp destegi
- 5 farkli cerceve stili
- Canli onizleme

### [2026-02-13] - Temel Otel Sistemi
- Oda yonetimi (16 oda)
- Rezervasyon sistemi
- Misafir yonetimi
- AI Asistan (Gemini)
- Google Yorum Yanit Uretici
- Fiyatlama modulu
- Gorev yonetimi
- Etkinlik takvimi
- Personel yonetimi
- Bilgi bankasi

---

## Gelecek Guncellemeler (Planlanan)

### P0 - Yuksek Oncelik
- [ ] HotelRunner API entegrasyonu (OTA senkronizasyonu)
- [ ] WhatsApp Business API entegrasyonu
  - Check-out sonrasi tesekkur + yorum istegi
  - Temizlik ekibine bildirim
  - Rezervasyon hatirlatma (1 gun once)
  - Organizasyon sorularinda otomatik bilgi

### P1 - Orta Oncelik  
- [ ] Musteri sadakat programi (sik gelen misafirlere indirim)
- [ ] Ozel gun takibi (dogum gunu/yildonumu hatirlatma)

### P2 - Dusuk Oncelik
- [ ] Coklu dil destegi (EN, DE, RU)

---

## Deploy Onerileri (Teknik Bilgi Gerekmez)

### En Ucuz & Kolay: Railway.app
- Maliyet: ~$5-10/ay
- Tek tikla deploy
- MongoDB dahil
- SSL otomatik

### Alternatif: Render.com
- Maliyet: Ucretsiz baslangic, ~$7/ay pro
- Kolay kullanim
- Otomatik olceklendirme

### Profesyonel: DigitalOcean App Platform
- Maliyet: ~$12/ay
- Daha guvenilir
- Turkiye'ye yakin sunucu

---

## WhatsApp Entegrasyonu Icin Gerekenler

1. **Meta Business Hesabi** (Ucretsiz)
   - business.facebook.com adresinden olusturulur
   - Isletme dogrulama gerekli (1-3 gun)

2. **WhatsApp Business API**
   - Aylik ~$15-50 (mesaj sayisina gore)
   - Alternatif: 360dialog, Twilio WhatsApp

3. **Webhook Kurulumu**
   - Mesaj gelince otomatik islem
   - Check-out bilgisi gelince temizlik bildirimi

---

## Iptal Politikasi (Sisteme Eklendi)

### Normal Gunler
- 3 gun oncesine kadar: Ucretsiz iptal
- 3 gun icinde: %100 ceza

### Ozel Gunler (On Odeme Zorunlu)
- Cumartesi
- Pazar
- Resmi/Dini Bayramlar
- 14 Subat
- Yilbasi
- Ozel Etkinlik Gunleri
