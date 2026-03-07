"""
Kozbeyli Konagi - AI Copywriter Service
Corey Haines / Conversion Factory'den ilham: Donusum odakli icerik yazimi

Ozellikler:
- CTA Optimization: Tek, net, guclu CTA
- Consumer Psychology: FOMO, social proof, urgency
- Platform-specific copy: Her platform icin optimize
- A/B variant generation: Ayni icerik icin 2 farkli versiyon
- Brand voice consistency: Tutarli marka sesi
"""
import logging
from typing import Optional, Dict, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# ==================== COPYWRITING RULES ====================

COPY_RULES = {
    "cta_principles": [
        "Her gonderide TEK bir CTA olsun",
        "Aksiyon odakli fiil kullan: 'Rezervasyon Yap', 'Kesfet', 'Dene'",
        "Belirsiz CTA kullanma: 'Daha Fazla Bilgi' yerine 'Odalarimizi Incele'",
        "Aciliyet ekle: 'Son 2 oda', 'Bu hafta sonu', 'Sinirli kontenjan'",
    ],
    "psychology_triggers": {
        "social_proof": "Misafir yorumlari, '500+ mutlu misafir', puanlar",
        "scarcity": "'Son 2 oda', 'Bu ay sinirli', 'Sadece hafta sonu'",
        "urgency": "'Bu hafta sonu', 'Yarin son gun', 'Hemen'",
        "authority": "'14 yillik deneyim', 'Foca'nin en iyi butik oteli'",
        "reciprocity": "Ucretsiz organik kahvalti, hosgeldin ikrami",
        "fomo": "'Gec kalanlar kacirir', 'Gecen hafta doldu'",
    },
    "brand_voice": {
        "tone": "Samimi ama profesyonel, sicak, davet edici",
        "avoid": ["Resmi devlet dili", "Klise pazarlama jargonu", "Asiri emoji", "Uzun cumleler"],
        "use": ["Dogal konusma dili", "Duyusal kelimeler (koku, lezzet, huzur)", "Yerel referanslar"],
        "personality": "Bir arkadas gibi - bilgili, sicak, guvenilir",
    },
}

# Platform-specific rules
PLATFORM_COPY_RULES = {
    "instagram": {
        "max_chars": 2200,
        "ideal_chars": "150-250",
        "style": "Gorsel odakli, emoji ile zenginlestirilmis, hashtag bolumu ayri",
        "cta_style": "Bio'daki linke yonlendir veya DM iste",
        "hashtag_count": "5-10",
        "first_line": "Dikkat cekici ilk cumle - feed'de gorunur",
    },
    "facebook": {
        "max_chars": 63206,
        "ideal_chars": "100-200",
        "style": "Hikaye anlat, soru sor, etkilesim davet et",
        "cta_style": "Link paylasimi veya yorum davet",
        "hashtag_count": "2-3",
        "first_line": "Etkilesim sorusu veya dikkat cekici ifade",
    },
    "twitter": {
        "max_chars": 280,
        "ideal_chars": "200-260",
        "style": "Kisa, etkili, punchline tarzi",
        "cta_style": "Link veya thread daveti",
        "hashtag_count": "1-2",
        "first_line": "Hook - tek cumlede mesaj",
    },
    "linkedin": {
        "max_chars": 3000,
        "ideal_chars": "200-400",
        "style": "Profesyonel, hikaye odakli, deger sunan",
        "cta_style": "Yorum yazmaya davet, website linki",
        "hashtag_count": "3-5",
        "first_line": "Profesyonel hook - sektörel iç görü",
    },
    "whatsapp": {
        "max_chars": 1024,
        "ideal_chars": "100-200",
        "style": "Kisisel, samimi, direkt",
        "cta_style": "Yanit ver veya ara",
        "hashtag_count": "0",
        "first_line": "Selamlama + isim",
    },
    "pinterest": {
        "max_chars": 500,
        "ideal_chars": "150-300",
        "style": "Gorsel odakli, ilham verici, arama dostu",
        "cta_style": "Pin kaydet, web sitesine yonlendir",
        "hashtag_count": "2-5",
        "first_line": "Arama anahtar kelimesi ile basla",
        "seo_focus": True,
        "best_for": "Dugun, dekorasyon, yemek, mekan gorselleri",
    },
}

# A/B Test varyant stratejileri
AB_STRATEGIES = {
    "headline": ["Soru ile basla", "Istatistik ile basla", "Hikaye ile basla", "FOMO ile basla"],
    "cta": ["Direkt aksiyon", "Merak uyandiran", "Sosyal kanit ile", "Faydayi vurgulayan"],
    "tone": ["Samimi", "Profesyonel", "Heyecanli", "Sakin/huzurlu"],
}


# ==================== SYSTEM PROMPTS ====================

COPYWRITER_SYSTEM_PROMPT = """Sen Kozbeyli Konagi'nin dönüşüm odaklı reklam yazarısın (conversion copywriter).
Görevin: Yüksek dönüşüm oranı sağlayan, müşteri psikolojisini kullanan metinler yazmak.

MUTLAK KURALLAR:
1. Her metinde TEK bir CTA (Call-to-Action) olacak
2. İlk cümle dikkat çekici olacak (hook)
3. Müşterinin dilini kullan - onların kullandığı kelimeler
4. Özellik değil FAYDA sat ("5 oda" değil "huzurlu uyku")
5. Sosyal kanıt ekle (misafir yorumu, puan, sayı)
6. Aciliyet veya kıtlık unsuru kullan
7. Duyusal kelimeler kullan (koku, lezzet, dokunuş, görüntü, ses)

MARKA SESİ - Kozbeyli Konağı:
- Foça/İzmir'de 14 yıllık aile işletmesi butik taş otel ve restoran
- 5 benzersiz oda: Nar, Zeytin, Taş, Badem, Asma
- Organik bahçe kahvaltısı, yerel Ege mutfağı
- Doğayla iç içe, huzurlu, otantik
- Düğün/nişan/özel etkinlik alanı

PSIKOLOJI TETIKLEYICILERI:
- Social Proof: "500+ mutlu misafir", "4.8/5 Google puanı"
- Scarcity: "Son 2 oda", "Bu ay sınırlı"
- FOMO: "Geçen hafta sonu doldu", "Erken rezervasyon avantajı"
- Authority: "14 yıllık deneyim", "Foça'nın en iyi butik oteli"

ÇIKTI FORMATI (JSON):
{
  "headline": "Ana başlık",
  "body": "Ana metin",
  "cta": "Tek CTA butonu/mesajı",
  "cta_url_suggestion": "Önerilen link (opsiyonel)",
  "hashtags": ["hashtag1", "hashtag2"],
  "psychology_used": ["kullanılan psikoloji teknikleri"],
  "hook_type": "soru/istatistik/hikaye/fomo",
  "estimated_engagement": "düşük/orta/yüksek"
}
"""

WHATSAPP_SEQUENCE_SYSTEM_PROMPT = """Sen Kozbeyli Konağı'nın WhatsApp pazarlama uzmanısın.
Görevin: Misafir dönüşümü ve sadakat artıran WhatsApp mesaj dizileri oluşturmak.

MUTLAK KURALLAR:
1. Her mesajın TEK bir amacı ve TEK bir CTA'sı olacak
2. Mesajlar KISA olacak (max 200 karakter ideal)
3. Kişiselleştirme kullan: {guest_name}, {room_type}
4. Exit koşulları tanımla: Müşteri yanıt verdiyse veya rezervasyon yaptıysa diziyi durdur
5. Gönderim zamanlaması öner (gün + saat)
6. WhatsApp'a uygun ton: samimi, kısa, emoji az

MESAJ TÜRLERİ:
- welcome: Hoş geldin (hemen, rezervasyon sonrası)
- reminder: Hatırlatma (check-in öncesi gün)
- during_stay: Konaklama sırasında (2. gün)
- checkout: Teşekkür + yorum isteği
- follow_up: Takip (1 hafta sonra, indirim kodu)
- seasonal: Mevsimsel teklif (1-2 ayda bir)
- win_back: Geri kazan (3 ay sonra)

ÇIKTI FORMATI (JSON):
{
  "sequence_name": "Dizi adı",
  "channel": "whatsapp",
  "trigger": "Diziyi başlatan olay",
  "exit_conditions": ["Diziyi durduran koşullar"],
  "messages": [
    {
      "order": 1,
      "type": "welcome/reminder/offer",
      "delay_days": 0,
      "send_time": "10:00",
      "message": "WhatsApp mesaj içeriği",
      "cta": "Yanıt beklenen aksiyon",
      "purpose": "Bu mesajın amacı"
    }
  ]
}
"""

PINTEREST_SYSTEM_PROMPT = """Sen Kozbeyli Konağı'nın Pinterest pazarlama uzmanısın.
Görevin: Düğün, etkinlik ve konaklama görselleri için Pinterest SEO odaklı pin açıklamaları yazmak.

PINTEREST SEO KURALLARI:
1. Pin başlığı arama anahtar kelimesiyle başlasın
2. Açıklama ilk 50 karakterde ana anahtar kelimeyi içersin
3. Türkçe + İngilizce anahtar kelimeler kullan (uluslararası erişim)
4. Her pin bir board'a ait olsun
5. Rich Pin formatı için yapısal veri öner

BOARD KATEGORILERI:
- "Düğün Mekanları İzmir" / "Wedding Venues Izmir"
- "Butik Otel Foça" / "Boutique Hotel Foca"
- "Ege Mutfağı" / "Aegean Cuisine"
- "Kır Düğünü" / "Rustic Wedding"
- "Romantik Kaçamak" / "Romantic Getaway"

ÇIKTI FORMATI (JSON):
{
  "pin_title": "SEO odaklı başlık",
  "pin_description": "Açıklama (150-300 karakter)",
  "board": "Board adı",
  "keywords_tr": ["türkçe", "anahtar", "kelimeler"],
  "keywords_en": ["english", "keywords"],
  "alt_text": "Görsel alt metni (erişilebilirlik + SEO)",
  "link": "Yönlendirme linki"
}
"""

CONTENT_STRATEGY_SYSTEM_PROMPT = """Sen Kozbeyli Konağı'nın içerik stratejistisin.
Görevin: Aylık/haftalık içerik planları oluşturmak ve her içeriğin bir iş hedefine hizmet etmesini sağlamak.

İÇERIK STRATEJİSI ÇERÇEVESİ:
1. %40 Değer içeriği (bilgi, eğlence, ilham)
2. %30 Etkileşim içeriği (soru, anket, UGC)
3. %20 Satış/CTA içeriği (teklif, promosyon)
4. %10 Marka hikayesi (behind-the-scenes, ekip)

İÇERIK SÜTUNLARI (Content Pillars):
1. LEZZET: Ege mutfağı, organik kahvaltı, restoran
2. HUZUR: Doğa, taş konak, oda atmosferi
3. KEŞIF: Foça, yerel rehber, gezi önerileri
4. DENEYİM: Misafir hikayeleri, etkinlikler, düğünler
5. KÜLTÜR: Tarih, Foça mirası, yerel zanaatlar

MEVSIMSEL TAKVİM:
- Ocak-Mart: Kış kaçamağı, şömine, sıcak çorba
- Nisan-Haziran: Bahar açılışı, bahçe, çiçekler, düğün sezonu başı
- Temmuz-Eylül: Yaz doruk, deniz, tekne, gece yemekleri
- Ekim-Aralık: Sonbahar renkleri, bağ bozumu, yılbaşı

ÇIKTI FORMATI (JSON):
{
  "period": "haftalık/aylık",
  "theme": "Dönem teması",
  "content_plan": [
    {
      "day": "Pazartesi",
      "date": "2026-03-09",
      "pillar": "LEZZET/HUZUR/KEŞIF/DENEYİM/KÜLTÜR",
      "content_type": "değer/etkileşim/satış/hikaye",
      "topic": "Konu",
      "platform": "instagram",
      "format": "post/reel/story/carousel",
      "caption_brief": "İçerik özeti",
      "cta": "CTA önerisi",
      "visual_brief": "Görsel açıklaması",
      "optimal_time": "19:00",
      "kpi": "Hedef metrik (like/kaydetme/link tıklaması)"
    }
  ],
  "monthly_goals": {
    "posts": 20,
    "reels": 4,
    "stories": 30,
    "engagement_target": "5%"
  }
}
"""


# ==================== SERVICE FUNCTIONS ====================

async def generate_conversion_copy(
    topic: str,
    platform: str = "instagram",
    psychology: str = None,
    tone: str = "warm",
    include_ab: bool = False,
) -> Dict:
    """
    Dönüşüm odaklı reklam metni üret.
    Corey Haines copywriting skill mantığı.
    """
    from helpers import new_id

    platform_rules = PLATFORM_COPY_RULES.get(platform, PLATFORM_COPY_RULES["instagram"])

    prompt = f"""Asagidaki konu icin {platform} platformuna uygun, donusum odakli bir gonderi metni yaz.

KONU: {topic}
PLATFORM: {platform}
IDEAL UZUNLUK: {platform_rules['ideal_chars']} karakter
STIL: {platform_rules['style']}
CTA STILI: {platform_rules['cta_style']}
HASHTAG SAYISI: {platform_rules['hashtag_count']}
TON: {tone}
"""

    if psychology:
        trigger_desc = COPY_RULES["psychology_triggers"].get(psychology, "")
        prompt += f"\nPSIKOLOJI TETIKLEYICISI: {psychology} - {trigger_desc}\n"

    if include_ab:
        prompt += "\nAyrica bir A/B test varyanti daha olustur. Farkli bir hook/CTA yaklasimiyla.\n"

    prompt += "\nJSON formatinda yanit ver."

    try:
        from services.ai_provider_service import ai_request
        result = await ai_request(message=prompt, system_prompt=COPYWRITER_SYSTEM_PROMPT, task_type="marketing_copy")
        response = result["response"]
    except Exception:
        from gemini_service import get_chat_response
        session_id = f"copywriter-{new_id()}"
        response = await get_chat_response(prompt, session_id, COPYWRITER_SYSTEM_PROMPT)

    return {
        "id": new_id(),
        "topic": topic,
        "platform": platform,
        "psychology": psychology,
        "tone": tone,
        "raw_response": response,
        "platform_rules": platform_rules,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


async def optimize_cta(current_cta: str, context: str = "") -> Dict:
    """Mevcut CTA'yı optimize et - daha güçlü, daha net, daha dönüşüm odaklı."""
    from helpers import new_id

    prompt = f"""Mevcut CTA: "{current_cta}"
Bağlam: {context}

Bu CTA'yi optimize et. 5 alternatif olustur:
1. Direkt aksiyon odakli
2. Fayda vurgulayan
3. Aciliyet ekleyen
4. Merak uyandiran
5. Sosyal kanit kullanan

Her birinin neden daha etkili oldugunu 1 cumleyle acikla.
JSON formatinda yanit ver: {{"alternatives": [{{"cta": "...", "type": "...", "reason": "..."}}]}}
"""

    try:
        from services.ai_provider_service import ai_request
        result = await ai_request(message=prompt, system_prompt=COPYWRITER_SYSTEM_PROMPT, task_type="marketing_copy")
        response = result["response"]
    except Exception:
        from gemini_service import get_chat_response
        session_id = f"cta-opt-{new_id()}"
        response = await get_chat_response(prompt, session_id, COPYWRITER_SYSTEM_PROMPT)

    return {
        "original_cta": current_cta,
        "optimized": response,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


async def generate_whatsapp_sequence(
    sequence_type: str = "welcome",
    target_audience: str = "new_guest",
    message_count: int = 5,
) -> Dict:
    """
    WhatsApp mesaj dizisi üret - trigger + exit koşullu.
    Butik otel için mesajlaşma odaklı pazarlama.
    """
    from helpers import new_id

    SEQUENCE_TYPES = {
        "welcome": "Yeni misafir hosgeldin - ilk rezervasyondan sonra",
        "pre_arrival": "Check-in oncesi hatirlatma ve bilgilendirme",
        "during_stay": "Konaklama sirasinda engagement",
        "post_stay": "Konaklama sonrasi - tesekkur, yorum isteme",
        "win_back": "Uzun suredir gelmeyen misafirleri geri kazanma",
        "seasonal": "Mevsimsel kampanya - sezona ozel teklif",
        "wedding": "Dugun/nisan teklifi ve takip",
        "loyalty": "Sadik misafir odul/teklif dizisi",
    }

    desc = SEQUENCE_TYPES.get(sequence_type, SEQUENCE_TYPES["welcome"])

    prompt = f"""Asagidaki WhatsApp mesaj dizisini olustur:

DIZI TURU: {sequence_type} - {desc}
HEDEF KITLE: {target_audience}
MESAJ SAYISI: {message_count}
OTEL: Kozbeyli Konagi, Foca/Izmir butik tas otel (16 oda)

ONEMLI:
- Her mesaj KISA ve SAMIMI olsun (max 200 karakter)
- TEK bir CTA olsun
- Exit kosullari tanimla (yanit verdiyse, rezervasyon yaptiysa dur)
- Gonderim zamani oner (gun + saat)
- Kisiselleştirme degiskenleri: {{guest_name}}, {{room_type}}, {{check_in}}
- WhatsApp tonuna uygun: samimi, kisa, emojili ama abartisiz

JSON formatinda yanit ver.
"""

    try:
        from services.ai_provider_service import ai_request
        result = await ai_request(message=prompt, system_prompt=WHATSAPP_SEQUENCE_SYSTEM_PROMPT, task_type="marketing_copy")
        response = result["response"]
    except Exception:
        from gemini_service import get_chat_response
        session_id = f"wa-seq-{new_id()}"
        response = await get_chat_response(prompt, session_id, WHATSAPP_SEQUENCE_SYSTEM_PROMPT)

    return {
        "id": new_id(),
        "sequence_type": sequence_type,
        "channel": "whatsapp",
        "target_audience": target_audience,
        "message_count": message_count,
        "raw_response": response,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


async def generate_pinterest_pins(
    category: str = "wedding",
    count: int = 5,
    image_descriptions: List[str] = None,
) -> Dict:
    """
    Pinterest pin açıklamaları ve SEO metadata üret.
    Düğün, etkinlik, yemek görselleri için.
    """
    from helpers import new_id

    CATEGORIES = {
        "wedding": "Dugun/nisan/kir dugunu mekan gorselleri",
        "food": "Ege mutfagi, organik kahvalti, restoran gorselleri",
        "venue": "Otel mekani, odalar, bahce, havuz alani",
        "local": "Foca, deniz, yerel kultur, dogal guzellikler",
        "decor": "Dekorasyon, cicek, aydinlatma, masa duzeni",
    }

    cat_desc = CATEGORIES.get(category, CATEGORIES["wedding"])

    prompt = f"""Kozbeyli Konagi icin {count} adet Pinterest pin aciklamasi olustur.

KATEGORI: {category} - {cat_desc}
GORSEL ACIKLAMALARI: {image_descriptions or ['Genel otel/mekan gorselleri']}

Her pin icin:
- SEO odakli baslik (Turkce + Ingilizce anahtar kelime)
- 150-300 karakter aciklama
- Board onerisi
- Turkce ve Ingilizce anahtar kelimeler
- Alt text (erisilebilirlik + SEO)
- Link onerisi

ONEMLI: Pinterest SEO icin ilk 50 karakterde ana anahtar kelime olsun.
Dugun icerikleri icin hem Turkce hem Ingilizce kelimeler kullan (uluslararasi gelinler).

JSON formatinda yanit ver: {{"pins": [...]}}
"""

    try:
        from services.ai_provider_service import ai_request
        result = await ai_request(message=prompt, system_prompt=PINTEREST_SYSTEM_PROMPT, task_type="marketing_copy")
        response = result["response"]
    except Exception:
        from gemini_service import get_chat_response
        session_id = f"pinterest-{new_id()}"
        response = await get_chat_response(prompt, session_id, PINTEREST_SYSTEM_PROMPT)

    return {
        "id": new_id(),
        "category": category,
        "count": count,
        "raw_response": response,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


async def generate_content_strategy(
    period: str = "weekly",
    focus: str = None,
    platforms: List[str] = None,
) -> Dict:
    """
    Haftalık/aylık içerik stratejisi oluştur.
    Corey Haines content-strategy skill mantığı.
    """
    from helpers import new_id

    if not platforms:
        platforms = ["instagram", "facebook"]

    now = datetime.now(timezone.utc)
    month_names_tr = ["Ocak", "Subat", "Mart", "Nisan", "Mayis", "Haziran",
                      "Temmuz", "Agustos", "Eylul", "Ekim", "Kasim", "Aralik"]
    current_month = month_names_tr[now.month - 1]

    prompt = f"""Kozbeyli Konagi icin {period} icerik stratejisi olustur.

DONEM: {current_month} {now.year}
PLATFORMLAR: {', '.join(platforms)}
ODAK: {focus or 'Genel - tum icerik sutunlari'}

Icerik dagılımı kurali:
- %40 Deger icerigi (bilgi, ilham)
- %30 Etkilesim icerigi (soru, anket)
- %20 Satis/CTA icerigi (teklif, promosyon)
- %10 Marka hikayesi (behind-the-scenes)

Her gonderi icin belirt:
- Gun ve tarih
- Icerik sutunu (LEZZET/HUZUR/KESIF/DENEYIM/KULTUR)
- Platform ve format (post/reel/story/carousel)
- Kisa icerik ozeti
- CTA onerisi
- Optimal paylasim saati
- Hedef metrik

JSON formatinda yanit ver.
"""

    try:
        from services.ai_provider_service import ai_request
        result = await ai_request(message=prompt, system_prompt=CONTENT_STRATEGY_SYSTEM_PROMPT, task_type="data_analysis")
        response = result["response"]
    except Exception:
        from gemini_service import get_chat_response
        session_id = f"strategy-{new_id()}"
        response = await get_chat_response(prompt, session_id, CONTENT_STRATEGY_SYSTEM_PROMPT)

    return {
        "id": new_id(),
        "period": period,
        "focus": focus,
        "platforms": platforms,
        "month": current_month,
        "raw_response": response,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


async def rewrite_for_conversion(
    original_text: str,
    platform: str = "instagram",
    goal: str = "reservation",
) -> Dict:
    """Mevcut bir metni dönüşüm odaklı olarak yeniden yaz."""
    from helpers import new_id

    GOALS = {
        "reservation": "Rezervasyon yaptirmak",
        "engagement": "Yorum/begeni/paylasim almak",
        "awareness": "Marka bilinirligini artirmak",
        "event": "Etkinlige katilim saglamak",
        "review": "Yorum/degerlendirme almak",
    }

    goal_desc = GOALS.get(goal, GOALS["reservation"])

    prompt = f"""Asagidaki metni donusum odakli olarak yeniden yaz.

ORIJINAL METIN:
{original_text}

PLATFORM: {platform}
HEDEF: {goal_desc}

Yeniden yazarken:
1. Tek ve guclu bir CTA ekle
2. Hook (dikkat cekici ilk cumle) ekle
3. Psikoloji tetikleyicisi kullan (FOMO, social proof, scarcity)
4. Platform kuralina uy (uzunluk, hashtag, stil)
5. Orijinal mesaji kaybet ama daha etkili hale getir

JSON formatinda yanit ver:
{{"original": "...", "rewritten": "...", "improvements": ["..."], "cta": "...", "psychology_used": ["..."]}}
"""

    try:
        from services.ai_provider_service import ai_request
        result = await ai_request(message=prompt, system_prompt=COPYWRITER_SYSTEM_PROMPT, task_type="marketing_copy")
        response = result["response"]
    except Exception:
        from gemini_service import get_chat_response
        session_id = f"rewrite-{new_id()}"
        response = await get_chat_response(prompt, session_id, COPYWRITER_SYSTEM_PROMPT)

    return {
        "original": original_text,
        "platform": platform,
        "goal": goal,
        "raw_response": response,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


# ==================== MARKETING PSYCHOLOGY ====================

async def get_psychology_suggestions(post_type: str, target: str = "couples") -> Dict:
    """Gönderi tipi ve hedef kitleye göre psikoloji önerileri."""
    TARGETS = {
        "couples": {
            "triggers": ["social_proof", "fomo", "reciprocity"],
            "tone": "Romantik, rüya gibi, kaçış",
            "keywords": ["baş başa", "romantik", "özel an", "kaçamak", "sürpriz"],
        },
        "families": {
            "triggers": ["authority", "social_proof", "reciprocity"],
            "tone": "Güvenli, eğlenceli, rahatlatıcı",
            "keywords": ["aile", "çocuk dostu", "güvenli", "doğa", "anı"],
        },
        "business": {
            "triggers": ["authority", "scarcity"],
            "tone": "Profesyonel, değer odaklı, verimli",
            "keywords": ["toplantı", "offsite", "verimlilik", "huzurlu ortam"],
        },
        "solo": {
            "triggers": ["fomo", "social_proof"],
            "tone": "Keşifçi, özgür, yenileyici",
            "keywords": ["kendinize zaman", "keşif", "yenilenme", "dijital detoks"],
        },
        "wedding": {
            "triggers": ["scarcity", "social_proof", "authority"],
            "tone": "Zarif, duygusal, unutulmaz",
            "keywords": ["rüya düğün", "özel gün", "masal gibi", "benzersiz mekan"],
        },
    }

    target_info = TARGETS.get(target, TARGETS["couples"])

    suggestions = []
    for trigger in target_info["triggers"]:
        trigger_detail = COPY_RULES["psychology_triggers"].get(trigger, "")
        suggestions.append({
            "trigger": trigger,
            "description": trigger_detail,
            "example_for_hotel": _get_trigger_example(trigger, post_type),
        })

    return {
        "target_audience": target,
        "tone": target_info["tone"],
        "keywords": target_info["keywords"],
        "psychology_suggestions": suggestions,
        "copy_rules": COPY_RULES["cta_principles"],
    }


def _get_trigger_example(trigger: str, post_type: str) -> str:
    """Trigger ve post türüne göre otel özel örneği."""
    examples = {
        "social_proof": {
            "default": "Google'da 4.8/5 puan - 500+ mutlu misafir",
            "promo": "Gecen ay 50+ çift bu teklifi kaçırmadı",
            "event": "Geçen yılki etkinliğimize 200+ kişi katıldı",
        },
        "scarcity": {
            "default": "Bu hafta sonu son 2 oda müsait",
            "promo": "İlk 10 rezervasyona özel %20 indirim",
            "event": "Sınırlı kontenjan - sadece 30 kişilik",
        },
        "fomo": {
            "default": "Geçen hafta sonu tamamen doluydu",
            "promo": "Bu fırsat 3 gün içinde sona eriyor",
            "event": "Geçen etkinlik 1 haftada tükendi",
        },
        "urgency": {
            "default": "Bu hafta sonu için hemen rezervasyon yap",
            "promo": "Son gün! Yarın fiyatlar normale dönüyor",
            "event": "Kayıtlar yarın kapanıyor",
        },
        "authority": {
            "default": "14 yıldır Foça'nın en çok tercih edilen butik oteli",
            "promo": "TripAdvisor Mükemmellik Sertifikası sahibi",
            "event": "Foça'nın en prestijli etkinlik mekanı",
        },
        "reciprocity": {
            "default": "Ücretsiz organik bahçe kahvaltısı her konaklamada dahil",
            "promo": "Hoş geldin ikramımız: Ev yapımı limonata",
            "event": "Katılımcılara özel %10 konaklama indirimi",
        },
    }

    trigger_examples = examples.get(trigger, {})
    return trigger_examples.get(post_type, trigger_examples.get("default", ""))
