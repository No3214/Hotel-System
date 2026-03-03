# KOZBEYLI KONAGI - KURULUM VE DEPLOYMENT REHBERI

---

## 1. RAILWAY DEPLOYMENT (Onerilir)

Railway, projeniz icin **iyi bir secim**. Nedenleri:
- MongoDB, Redis dahili plugin olarak sunuluyor
- Git push ile otomatik deploy
- SSL otomatik
- Fiyati makul: ~$5-15/ay (dusuk trafik)

### Adim Adim Kurulum

#### 1.1 Hesap Acma
1. `railway.app` adresine gidin
2. GitHub hesabinizla giris yapin
3. Hobby plan secin ($5/ay)

#### 1.2 Yeni Proje Olusturun
1. "New Project" tiklayin
2. "Deploy from GitHub" secin
3. Repository'nizi secin

#### 1.3 MongoDB Ekleyin
1. "+ New" butonuna tiklayin
2. "Database" → "MongoDB" secin
3. Otomatik olusturulacak
4. `MONGO_URL` otomatik eklenir

#### 1.4 Redis Ekleyin
1. "+ New" → "Database" → "Redis" secin
2. `REDIS_URL` otomatik eklenir

#### 1.5 Backend Servisi
1. "+ New" → "GitHub Repo" → ayni repo secin
2. Ayarlar:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
3. Environment Variables ekleyin:
   - `PORT` = 8001
   - `MONGO_URL` = (MongoDB servisinden referans: ${{MongoDB.MONGO_URL}})
   - `REDIS_URL` = (Redis servisinden referans: ${{Redis.REDIS_URL}})
   - `DB_NAME` = vericevir_hotel
   - `CORS_ORIGINS` = https://kozbeylikonagi.com.tr
   - `GOOGLE_API_KEY` = (AI icin)
   - `WHATSAPP_VERIFY_TOKEN` = kozbeyli_verify_2026
   - Diger .env degiskenleri...

#### 1.6 Frontend Servisi
1. "+ New" → "GitHub Repo" → ayni repo secin
2. Ayarlar:
   - Root Directory: `frontend`
   - Build Command: `yarn install && yarn build`
   - Start Command: `npx serve -s build -l $PORT`
3. Environment Variables:
   - `REACT_APP_BACKEND_URL` = (Backend servisinin URL'si)

#### 1.7 Domain Baglama
1. Frontend servisine gidin → Settings → Custom Domain
2. `kozbeylikonagi.com.tr` ekleyin
3. Domain panelinizde (domain aldigeniz yer):
   - CNAME kaydi ekleyin: `kozbeylikonagi.com.tr` → Railway'in verdigi deger
4. SSL otomatik aktif olacak

#### 1.8 Celery Worker (Opsiyonel)
Celery worker icin ayri servis:
1. "+ New" → "GitHub Repo" → ayni repo
2. Root Directory: `backend`
3. Start Command: `celery -A celery_app worker --beat --loglevel=info`
4. Ayni environment variable'lari ekleyin

### Tahmini Maliyet
| Kaynak | Tutar |
|--------|-------|
| Hobby Plan | $5/ay |
| MongoDB (~1GB) | ~$1.50/ay |
| Redis (~256MB) | ~$2.50/ay |
| Backend (~0.5 vCPU) | ~$5/ay |
| Frontend (~256MB) | ~$2.50/ay |
| **TOPLAM** | **~$15-20/ay** |

---

## 2. WHATSAPP BUSINESS API KURULUM REHBERI

### Yontem 1: Meta Developer Portal (Ucretsiz)

#### Adim 1: Meta Business Hesabi
1. `business.facebook.com` adresine gidin
2. "Hesap Olustur" tiklayin
3. Isletme bilgilerinizi girin:
   - Isletme Adi: Kozbeyli Konagi
   - Adres: Kozbeyli Koyu No:188 Foca/Izmir
   - Kategori: Konaklama
4. **ONEMLI:** "Yazilim sirketi" SEC**ME**YIN! "Kendi isletmem icin" secin

#### Adim 2: Developer Uygulamasi
1. `developers.facebook.com` adresine gidin
2. "Uygulamalarimi" → "Uygulama Olustur" tiklayin
3. Tur olarak "Business" secin
4. Uygulama adi: "Kozbeyli Konagi Bot"
5. Isletme hesabinizi baglayın

#### Adim 3: WhatsApp Urunu Ekleyin
1. Dashboard'da "Urun Ekle" → "WhatsApp" → "Kur" tiklayin
2. "Baslangic" sayfasinda test telefon numarasi verilecek
3. Su bilgileri kopyalayin:
   - **Phone Number ID** → .env WHATSAPP_PHONE_NUMBER_ID
   - **WhatsApp Business Account ID** → .env WHATSAPP_BUSINESS_ACCOUNT_ID
4. "API Kurulumu" → "Gecici Erisim Tokeni Olustur"
   - Bu tokeni kopyalayin → .env WHATSAPP_ACCESS_TOKEN

#### Adim 4: Kalici Token (Onemli!)
Gecici token 24 saatte sona erer. Kalici token icin:
1. Uygulama ayarlari → "Temel" → App Secret kopyalayin → .env WHATSAPP_APP_SECRET
2. Business Settings → System Users → yeni "System User" olusturun
3. "Token Olustur" tiklayin
4. Izinler: whatsapp_business_management, whatsapp_business_messaging
5. Bu kalici tokeni .env'ye koyun

#### Adim 5: Webhook Ayarlari
1. WhatsApp → Yapilandirma → Webhook
2. Callback URL: `https://kozbeylikonagi.com.tr/api/webhooks/whatsapp`
3. Dogrulama Tokeni: `kozbeyli_verify_2026`
4. Abone olunacak alanlar:
   - messages ✅
   - messaging_postbacks ✅

#### Adim 6: Isletme Numaranizi Ekleyin
1. WhatsApp → Telefon Numaralari → "Telefon Numarasi Ekle"
2. +90 532 234 26 86 numaranizi girin
3. SMS veya arama ile dogrulama kodu alin
4. Artik gercek numaranizdan mesaj gonderebilirsiniz

#### Adim 7: Mesaj Sablonlari (Onemli!)
WhatsApp kuralina gore, 24 saat disindaki mesajlar icin **onaylanmis sablon** gerekir:
1. WhatsApp → Mesaj Sablonlari → "Sablon Olustur"
2. Sistemde tanimli 5 sablon icin:
   - `checkout_thanks_review` - Tesekkur mesaji
   - `reservation_reminder_1day` - Hatirlatma
   - `welcome_checkin` - Hos geldiniz
   - `cleaning_notification` - Temizlik
   - `room_ready_notification` - Oda hazir
3. Her sablon icin Turkce icerik yazin
4. Meta onay süreci: 1-3 gun

### Yontem 2: WATI.io (Kolay, Ucretli - Onerilir)

WATI, Meta'nin resmi is ortagi. Siz Meta ile ugrasmak zorunda kalmazsiniz:
1. `wati.io` adresine gidin
2. Turkce destek var
3. Hesap acin (~$49/ay)
4. Telefon numaranizi baglayın
5. WATI size API anahtarlarini verir
6. .env dosyasina ekleyin

**WATI Avantajlari:**
- Meta dogrulama surecini sizin yerinize yapar
- Hazir sablon yonetimi
- Dashboard ile mesaj takibi
- Turkce musteri destegi
- Meta'nin "yazilim firmasi" sorularindan kurtulursunuz

### Yontem 3: 360dialog (Orta, Ucretli)
1. `360dialog.com` adresine gidin
2. ~$5/ay + mesaj basina ucret
3. Daha teknik ama daha ucuz
4. API anahtarlarini alip .env'ye ekleyin

---

## 3. INSTAGRAM DM KURULUM

Instagram DM API, WhatsApp ile ayni Meta uygulamasinda:
1. Developer Portal → ayni uygulamaniz → "Instagram" urunu ekleyin
2. Instagram Business hesabinizi baglayın
3. Webhook URL: `https://kozbeylikonagi.com.tr/api/webhooks/instagram`
4. Dogrulama: `kozbeyli_ig_verify_2026`
5. Token: WhatsApp ile ayni Page Access Token

---

## 4. HIZLI BASLANGIC KONTROL LISTESI

- [ ] GitHub'a push (Save to GitHub butonu)
- [ ] Railway hesabi ac
- [ ] MongoDB + Redis ekle
- [ ] Backend deploy
- [ ] Frontend deploy
- [ ] Domain bagla (kozbeylikonagi.com.tr)
- [ ] WATI.io hesabi ac (WhatsApp icin)
- [ ] Telefon numaranizi baglayın
- [ ] Test mesaji gonderin
- [ ] Sablonlari olusturun

---

## 5. ONERILEN STRATEJI

### Neden WATI.io Onerilir?
Meta Developer Portal'da karsilastiginiz sorunlar (yazilim firmasi sorusu, dogrulama sureci) WATI ile tamamen ortadan kalkar. WATI:
- Meta'nin resmi BSP'si (Business Solution Provider)
- Dogrulama surecini sizin icin yapar
- Hazir sablon yonetimi sunar
- $49/ay ile 1000 mesaj/ay dahil
- Turkce destek hatti var

### Railway vs Alternatifler
| Platform | Fiyat | Kolaylik | MongoDB | Redis |
|----------|-------|----------|---------|-------|
| **Railway** | ~$15-20/ay | Kolay | Dahili | Dahili |
| Render | ~$20-30/ay | Kolay | Harici | Harici |
| DigitalOcean | ~$15-25/ay | Orta | Yonetimli | Yonetimli |
| VPS (Hetzner) | ~$5-10/ay | Zor | Manuel | Manuel |
| Vercel | ~$20/ay | Kolay | Harici | Harici |

**Railway onerilir** cunku MongoDB ve Redis dahili, tek yerden yonetim.
