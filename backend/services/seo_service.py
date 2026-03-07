"""
Kozbeyli Konagi - SEO Yonetim Servisi
Meta tag uretimi, Schema.org structured data, sitemap, SEO analizi
"""
import json
import logging
import re
from typing import Dict, Any, List, Optional

from hotel_config import HOTEL_INFO, ROOM_TYPES, RESTAURANT_INFO

logger = logging.getLogger(__name__)


# ==================== SCHEMA.ORG STRUCTURED DATA ====================

def generate_schema_org(schema_type: str = "Hotel") -> Dict[str, Any]:
    """
    JSON-LD structured data uret.
    Desteklenen tipler: Hotel, Restaurant, Event, LocalBusiness
    """
    address = HOTEL_INFO["address"]
    location = HOTEL_INFO["location"]

    base_address = {
        "@type": "PostalAddress",
        "streetAddress": f"{address['village']}, {address['full'].split(',')[1].strip() if ',' in address['full'] else ''}",
        "addressLocality": address["district"],
        "addressRegion": address["city"],
        "postalCode": address["postal_code"],
        "addressCountry": address["country"],
    }

    geo = {
        "@type": "GeoCoordinates",
        "latitude": location["latitude"],
        "longitude": location["longitude"],
    }

    if schema_type == "Hotel":
        schema = {
            "@context": "https://schema.org",
            "@type": "Hotel",
            "name": HOTEL_INFO["name"],
            "description": HOTEL_INFO["tagline"],
            "url": HOTEL_INFO["website"],
            "telephone": HOTEL_INFO["phone"],
            "email": HOTEL_INFO["email"],
            "image": f"{HOTEL_INFO['website']}/images/hotel-main.jpg",
            "address": base_address,
            "geo": geo,
            "starRating": {
                "@type": "Rating",
                "ratingValue": HOTEL_INFO["ratings"].get("google", 4.5),
            },
            "amenityFeature": [
                {"@type": "LocationFeatureSpecification", "name": amenity, "value": True}
                for amenity in HOTEL_INFO["amenities"]
            ],
            "checkinTime": HOTEL_INFO["check_in"],
            "checkoutTime": HOTEL_INFO["check_out"],
            "numberOfRooms": sum(rt["count"] for rt in ROOM_TYPES),
            "priceRange": "$$",
            "sameAs": [
                HOTEL_INFO["social_media"].get("instagram", ""),
                HOTEL_INFO["social_media"].get("facebook", ""),
                HOTEL_INFO["social_media"].get("tripadvisor", ""),
            ],
        }

    elif schema_type == "Restaurant":
        schema = {
            "@context": "https://schema.org",
            "@type": "Restaurant",
            "name": RESTAURANT_INFO["name"],
            "servesCuisine": RESTAURANT_INFO["cuisine"],
            "description": f"{RESTAURANT_INFO['name']} - {RESTAURANT_INFO['cuisine']}",
            "address": base_address,
            "geo": geo,
            "telephone": HOTEL_INFO["phone"],
            "url": HOTEL_INFO["website"],
            "menu": f"{HOTEL_INFO['website']}/menu",
            "openingHours": ["Mo-Su 08:00-23:00"],
            "priceRange": "$$",
            "acceptsReservations": True,
            "sameAs": [
                HOTEL_INFO["social_media"].get("instagram", ""),
                HOTEL_INFO["social_media"].get("tripadvisor", ""),
            ],
        }

    elif schema_type == "Event":
        schema = {
            "@context": "https://schema.org",
            "@type": "Event",
            "name": "Kozbeyli Konagi Etkinlik",
            "description": "Kozbeyli Konagi'nda ozel etkinlikler ve organizasyonlar",
            "location": {
                "@type": "Place",
                "name": HOTEL_INFO["name"],
                "address": base_address,
                "geo": geo,
            },
            "organizer": {
                "@type": "Organization",
                "name": HOTEL_INFO["name"],
                "url": HOTEL_INFO["website"],
            },
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        }

    elif schema_type == "LocalBusiness":
        schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": HOTEL_INFO["name"],
            "description": HOTEL_INFO["tagline"],
            "url": HOTEL_INFO["website"],
            "telephone": HOTEL_INFO["phone"],
            "email": HOTEL_INFO["email"],
            "address": base_address,
            "geo": geo,
            "openingHours": ["Mo-Su 00:00-23:59"],
            "priceRange": "$$",
            "image": f"{HOTEL_INFO['website']}/images/hotel-main.jpg",
            "sameAs": [
                HOTEL_INFO["social_media"].get("instagram", ""),
                HOTEL_INFO["social_media"].get("facebook", ""),
                HOTEL_INFO["social_media"].get("tripadvisor", ""),
                HOTEL_INFO["social_media"].get("booking", ""),
            ],
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": HOTEL_INFO["ratings"].get("google", 4.5),
                "bestRating": 5,
                "reviewCount": 150,
            },
        }

    else:
        schema = {
            "@context": "https://schema.org",
            "@type": "Hotel",
            "name": HOTEL_INFO["name"],
            "url": HOTEL_INFO["website"],
        }

    return schema


# ==================== META TAG GENERATION ====================

# Varsayilan meta tag sablonlari (AI basarisiz olursa kullanilir)
DEFAULT_META_TEMPLATES = {
    "home": {
        "title": "Kozbeyli Konagi | Foca Butik Otel & Restoran",
        "description": "Foca'nin kalbinde, 14. yuzyil Osmanli koyunde dogayla ic ice butik otel deneyimi. Havuz, restoran ve essiz manzara.",
        "keywords": ["kozbeyli konagi", "foca otel", "butik otel izmir", "foca konaklama",
                      "dogayla ic ice otel", "foca restoran", "izmir butik otel", "foca tatil",
                      "kozbeyli koyu", "ege butik otel"],
    },
    "rooms": {
        "title": "Odalarimiz | Kozbeyli Konagi - Foca Butik Otel",
        "description": "Deniz ve dag manzarali 16 butik oda. Superior, standart ve aile odalari ile konforlu konaklama. Online rezervasyon.",
        "keywords": ["foca otel odalari", "butik otel oda", "deniz manzarali oda", "foca konaklama",
                      "aile odasi foca", "superior oda", "foca tatil", "izmir otel oda",
                      "manzarali oda", "kozbeyli konagi oda"],
    },
    "restaurant": {
        "title": "Antakya Sofrasi | Kozbeyli Konagi Restoran",
        "description": "Turk ve Ege mutfaginin en guzel lezzetleri. Serpme kahvalti, kuzu tandir, sac kavurma. Rezervasyon yapin.",
        "keywords": ["foca restoran", "antakya sofrasi", "ege mutfagi", "serpme kahvalti foca",
                      "kuzu tandir", "foca yemek", "izmir restoran", "turk mutfagi foca",
                      "kozbeyli restoran", "foca kahvalti"],
    },
    "events": {
        "title": "Etkinlikler & Organizasyonlar | Kozbeyli Konagi",
        "description": "Dugun, nisan, dogum gunu ve kurumsal etkinlikler icin essiz mekan. Kozbeyli Konagi'nda hayalinizdeki organizasyon.",
        "keywords": ["foca dugun mekan", "kozbeyli organizasyon", "butik otel etkinlik",
                      "nisan mekan izmir", "foca kutlama", "kir dugunu foca", "etkinlik mekan",
                      "organizasyon foca", "ozel gun mekan", "izmir dugun"],
    },
    "contact": {
        "title": "Iletisim | Kozbeyli Konagi - Foca, Izmir",
        "description": "Kozbeyli Konagi iletisim bilgileri, adres ve yol tarifi. Rezervasyon ve bilgi icin bize ulasin.",
        "keywords": ["kozbeyli konagi iletisim", "foca otel telefon", "kozbeyli adres",
                      "foca konaklama iletisim", "kozbeyli konagi yol tarifi", "foca otel rezervasyon",
                      "kozbeyli koyu nerede", "foca butik otel iletisim", "izmir otel iletisim",
                      "kozbeyli konagi ulasim"],
    },
    "blog_post": {
        "title": "Blog | Kozbeyli Konagi - Foca Gezi Rehberi",
        "description": "Foca gezi rehberi, yerel lezzetler, kultur ve dogayla ic ice aktiviteler. Kozbeyli Konagi blog yazilari.",
        "keywords": ["foca gezi rehberi", "foca gezilecek yerler", "kozbeyli blog", "ege tatil",
                      "foca aktiviteler", "foca kultur", "foca dogal guzellikler", "izmir gezi",
                      "foca tarihi yerler", "ege butik otel blog"],
    },
}


async def generate_meta_tags(page_type: str, content: str = "") -> Dict[str, Any]:
    """
    AI destekli meta tag uretimi.
    AI basarisiz olursa varsayilan sablonlar kullanilir.
    """
    # Oncelikle varsayilanlari hazirla
    defaults = DEFAULT_META_TEMPLATES.get(page_type, DEFAULT_META_TEMPLATES["home"])

    try:
        from services.ai_provider_service import ai_request, build_system_prompt

        system_prompt = build_system_prompt(
            role="Sen deneyimli bir SEO uzmanisin. Turkiye'deki butik oteller ve restoranlar konusunda uzmanlastin.",
            task="Verilen sayfa turu ve icerik icin SEO uyumlu meta taglar uret.",
            context=f"""<hotel_info>
Otel: {HOTEL_INFO['name']}
Konum: {HOTEL_INFO['address']['full']}
Tur: {HOTEL_INFO['type']}
Slogan: {HOTEL_INFO['tagline']}
</hotel_info>

<page_info>
Sayfa Turu: {page_type}
Ek Icerik: {content or 'Yok'}
</page_info>""",
            output_format="""{
    "title": "50-60 karakter arasi sayfa basligi",
    "description": "150-160 karakter arasi meta aciklamasi",
    "keywords": ["10 adet ilgili anahtar kelime"]
}"""
        )

        result = await ai_request(
            message=f"'{page_type}' sayfasi icin SEO meta taglari uret. Icerik: {content or 'Genel sayfa'}",
            system_prompt=system_prompt,
            task_type="marketing_copy",
        )

        response_text = result.get("response", "")

        # JSON parse etmeyi dene
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            ai_tags = json.loads(json_match.group())
            title = ai_tags.get("title", defaults["title"])
            description = ai_tags.get("description", defaults["description"])
            keywords = ai_tags.get("keywords", defaults["keywords"])
        else:
            title = defaults["title"]
            description = defaults["description"]
            keywords = defaults["keywords"]

    except Exception as e:
        logger.warning(f"AI meta tag uretimi basarisiz, varsayilanlar kullaniliyor: {e}")
        title = defaults["title"]
        description = defaults["description"]
        keywords = defaults["keywords"]

    return {
        "title": title[:60],
        "description": description[:160],
        "keywords": keywords[:10] if isinstance(keywords, list) else keywords,
        "og_title": title[:60],
        "og_description": description[:160],
        "og_image": f"{HOTEL_INFO['website']}/images/og-{page_type}.jpg",
        "og_url": HOTEL_INFO["website"],
        "og_type": "website",
        "page_type": page_type,
    }


# ==================== SITEMAP GENERATION ====================

async def generate_sitemap() -> str:
    """XML sitemap uret. Statik + dinamik sayfalar."""
    from helpers import utcnow

    today = utcnow()[:10]  # YYYY-MM-DD

    # Statik sayfalar
    static_pages = [
        {"loc": "/", "priority": "1.0", "changefreq": "weekly"},
        {"loc": "/menu", "priority": "0.8", "changefreq": "weekly"},
        {"loc": "/admin", "priority": "0.3", "changefreq": "monthly"},
    ]

    # Dinamik sayfalar - odalar
    room_pages = []
    for room_type in ROOM_TYPES:
        room_pages.append({
            "loc": f"/rooms/{room_type['id']}",
            "priority": "0.7",
            "changefreq": "monthly",
        })

    # Dinamik sayfalar - etkinlikler (DB'den)
    event_pages = []
    try:
        from database import db
        events = await db.events.find(
            {"status": {"$in": ["active", "upcoming"]}},
            {"_id": 0, "id": 1, "updated_at": 1}
        ).to_list(100)
        for event in events:
            event_pages.append({
                "loc": f"/events/{event.get('id', '')}",
                "priority": "0.6",
                "changefreq": "weekly",
                "lastmod": event.get("updated_at", today)[:10],
            })
    except Exception as e:
        logger.warning(f"Etkinlikler sitemap icin alinamadi: {e}")

    # XML olustur
    base_url = HOTEL_INFO["website"].rstrip("/")
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    all_pages = static_pages + room_pages + event_pages
    for page in all_pages:
        lastmod = page.get("lastmod", today)
        xml_parts.append(f"""  <url>
    <loc>{base_url}{page['loc']}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{page['changefreq']}</changefreq>
    <priority>{page['priority']}</priority>
  </url>""")

    xml_parts.append("</urlset>")
    return "\n".join(xml_parts)


# ==================== SEO ANALYSIS ====================

def analyze_seo_score(content: str, page_type: str = "general") -> Dict[str, Any]:
    """
    Icerik icin SEO skoru hesapla (0-100).
    Kategoriler: baslik, aciklama, anahtar kelime, baslik yapisi, resim alt, ic linkler.
    """
    score = 0
    max_score = 100
    categories = {}
    suggestions = []

    # 1. Baslik kontrolu (20 puan)
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    title_score = 0
    if title_match:
        title = title_match.group(1)
        title_len = len(title)
        if 50 <= title_len <= 60:
            title_score = 20
        elif 30 <= title_len < 50:
            title_score = 15
            suggestions.append(f"Baslik cok kisa ({title_len} karakter). 50-60 karakter oneriliyor.")
        elif 60 < title_len <= 80:
            title_score = 12
            suggestions.append(f"Baslik cok uzun ({title_len} karakter). 50-60 karakter oneriliyor.")
        else:
            title_score = 5
            suggestions.append(f"Baslik uzunlugu uygun degil ({title_len} karakter). 50-60 karakter oneriliyor.")
    else:
        suggestions.append("Sayfada <title> etiketi bulunamadi. SEO icin baslik etiketi ekleyin.")
    categories["title"] = {"score": title_score, "max": 20}
    score += title_score

    # 2. Meta description kontrolu (20 puan)
    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
    desc_score = 0
    if desc_match:
        desc = desc_match.group(1)
        desc_len = len(desc)
        if 150 <= desc_len <= 160:
            desc_score = 20
        elif 100 <= desc_len < 150:
            desc_score = 14
            suggestions.append(f"Meta aciklama biraz kisa ({desc_len} karakter). 150-160 karakter oneriliyor.")
        elif 160 < desc_len <= 200:
            desc_score = 12
            suggestions.append(f"Meta aciklama biraz uzun ({desc_len} karakter). 150-160 karakter oneriliyor.")
        else:
            desc_score = 5
            suggestions.append(f"Meta aciklama uzunlugu uygun degil ({desc_len} karakter). 150-160 karakter oneriliyor.")
    else:
        suggestions.append("Meta description etiketi bulunamadi. Arama sonuclarinda gorunen aciklama ekleyin.")
    categories["description"] = {"score": desc_score, "max": 20}
    score += desc_score

    # 3. Anahtar kelime kontrolu (15 puan)
    keyword_score = 0
    hotel_keywords = [
        "kozbeyli", "konagi", "foca", "otel", "butik", "restoran",
        "izmir", "konaklama", "tatil", "rezervasyon",
    ]
    content_lower = content.lower()
    found_keywords = [kw for kw in hotel_keywords if kw in content_lower]
    keyword_ratio = len(found_keywords) / len(hotel_keywords)
    if keyword_ratio >= 0.6:
        keyword_score = 15
    elif keyword_ratio >= 0.4:
        keyword_score = 10
    elif keyword_ratio >= 0.2:
        keyword_score = 5
        suggestions.append("Icerikde daha fazla ilgili anahtar kelime kullanin.")
    else:
        keyword_score = 0
        suggestions.append("Icerikde otel, konum ve hizmetlerle ilgili anahtar kelimeler eksik.")
    categories["keywords"] = {"score": keyword_score, "max": 15, "found": found_keywords}
    score += keyword_score

    # 4. Baslik yapisi (h1-h6) (15 puan)
    heading_score = 0
    h1_count = len(re.findall(r'<h1[^>]*>', content, re.IGNORECASE))
    h2_count = len(re.findall(r'<h2[^>]*>', content, re.IGNORECASE))
    h3_count = len(re.findall(r'<h3[^>]*>', content, re.IGNORECASE))

    if h1_count == 1:
        heading_score += 7
    elif h1_count == 0:
        suggestions.append("Sayfada h1 basligi bulunamadi. Her sayfada bir adet h1 olmali.")
    else:
        heading_score += 3
        suggestions.append(f"Sayfada {h1_count} adet h1 var. Tek bir h1 kullanmak SEO icin daha iyidir.")

    if h2_count >= 2:
        heading_score += 5
    elif h2_count == 1:
        heading_score += 3
        suggestions.append("Daha fazla h2 alt basligi ekleyerek icerigi bolumleyin.")
    else:
        suggestions.append("h2 alt basliklari ekleyin. Icerik hiyerarsisi SEO icin onemlidir.")

    if h3_count >= 1:
        heading_score += 3
    categories["headings"] = {"score": heading_score, "max": 15, "h1": h1_count, "h2": h2_count, "h3": h3_count}
    score += heading_score

    # 5. Resim alt etiketleri (15 puan)
    img_score = 0
    images = re.findall(r'<img[^>]*>', content, re.IGNORECASE)
    images_with_alt = re.findall(r'<img[^>]*alt=["\'][^"\']+["\'][^>]*>', content, re.IGNORECASE)
    total_images = len(images)
    total_with_alt = len(images_with_alt)

    if total_images == 0:
        img_score = 10
        suggestions.append("Sayfada resim bulunamadi. SEO icin optimize edilmis gorseller ekleyin.")
    elif total_with_alt == total_images:
        img_score = 15
    elif total_with_alt > 0:
        img_score = int(15 * (total_with_alt / total_images))
        missing = total_images - total_with_alt
        suggestions.append(f"{missing} resimde alt etiketi eksik. Tum resimlere aciklayici alt etiketi ekleyin.")
    else:
        suggestions.append("Hicbir resimde alt etiketi yok. Tum resimlere aciklayici alt etiketi ekleyin.")
    categories["images"] = {"score": img_score, "max": 15, "total": total_images, "with_alt": total_with_alt}
    score += img_score

    # 6. Ic linkler (15 puan)
    link_score = 0
    internal_links = re.findall(r'<a[^>]*href=["\'](?!/|http)', content, re.IGNORECASE)
    internal_links += re.findall(r'<a[^>]*href=["\']/', content, re.IGNORECASE)
    external_links = re.findall(r'<a[^>]*href=["\']https?://', content, re.IGNORECASE)
    total_internal = len(internal_links)

    if total_internal >= 5:
        link_score = 15
    elif total_internal >= 3:
        link_score = 10
    elif total_internal >= 1:
        link_score = 5
        suggestions.append("Daha fazla ic link ekleyerek sayfa otoritesini artirin.")
    else:
        suggestions.append("Icerikde ic link bulunamadi. Diger sayfalara linkler ekleyin.")
    categories["internal_links"] = {"score": link_score, "max": 15, "count": total_internal}
    score += link_score

    # Genel degerlendirme
    if score >= 80:
        grade = "A"
        summary = "Mukemmel! SEO uyumlulugu cok iyi."
    elif score >= 60:
        grade = "B"
        summary = "Iyi. Birka iyilestirme ile daha da iyi olabilir."
    elif score >= 40:
        grade = "C"
        summary = "Orta. Onemli SEO iyilestirmeleri gerekli."
    elif score >= 20:
        grade = "D"
        summary = "Zayif. Ciddi SEO calismasi gerekli."
    else:
        grade = "F"
        summary = "Cok zayif. Temel SEO gereksinimleri karsilanmiyor."

    return {
        "score": min(score, max_score),
        "max_score": max_score,
        "grade": grade,
        "summary": summary,
        "categories": categories,
        "suggestions": suggestions,
        "page_type": page_type,
    }


# ==================== KEYWORD SUGGESTIONS ====================

async def suggest_keywords(topic: str) -> Dict[str, Any]:
    """
    AI destekli anahtar kelime onerileri.
    Otel, restoran, turizm odakli Turkce anahtar kelimeler.
    """
    # Varsayilan anahtar kelimeler (AI basarisiz olursa)
    default_keywords = {
        "primary": [
            f"{topic} foca", f"{topic} izmir", f"kozbeyli konagi {topic}",
            f"butik otel {topic}", f"foca {topic}",
        ],
        "secondary": [
            f"en iyi {topic} foca", f"{topic} otel", f"{topic} restoran",
            f"ege {topic}", f"{topic} tatil",
        ],
        "long_tail": [
            f"foca'da en iyi {topic} nerede", f"kozbeyli konagi {topic} fiyatlari",
            f"izmir foca {topic} onerileri", f"butik otel {topic} deneyimi",
            f"foca {topic} yorumlari",
        ],
    }

    try:
        from services.ai_provider_service import ai_request, build_system_prompt

        system_prompt = build_system_prompt(
            role="Sen Turkiye turizm sektoru icin uzmanlasmis bir SEO ve anahtar kelime arastirma uzmanisin.",
            task="Verilen konu icin otel, restoran ve turizm odakli Turkce anahtar kelime onerileri uret.",
            context=f"""<hotel_info>
Otel: {HOTEL_INFO['name']}
Konum: {HOTEL_INFO['address']['district']}, {HOTEL_INFO['address']['city']}
Tur: {HOTEL_INFO['type']}
</hotel_info>

<topic>{topic}</topic>""",
            output_format="""{
    "primary": ["5 adet ana anahtar kelime - yuksek arama hacimli"],
    "secondary": ["5 adet ikincil anahtar kelime - orta arama hacimli"],
    "long_tail": ["5 adet uzun kuyruk anahtar kelime - dusuk rekabet"]
}"""
        )

        result = await ai_request(
            message=f"'{topic}' konusu icin Turkce SEO anahtar kelime onerileri uret. Otel ve turizm odakli olsun.",
            system_prompt=system_prompt,
            task_type="data_analysis",
        )

        response_text = result.get("response", "")
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            ai_keywords = json.loads(json_match.group())
            return {
                "primary": ai_keywords.get("primary", default_keywords["primary"])[:5],
                "secondary": ai_keywords.get("secondary", default_keywords["secondary"])[:5],
                "long_tail": ai_keywords.get("long_tail", default_keywords["long_tail"])[:5],
                "topic": topic,
                "source": "ai",
            }

    except Exception as e:
        logger.warning(f"AI anahtar kelime onerisi basarisiz: {e}")

    return {
        **default_keywords,
        "topic": topic,
        "source": "default",
    }


# ==================== LOCAL SEO REPORT ====================

def generate_local_seo_report() -> Dict[str, Any]:
    """
    Yerel SEO kontrol listesi ve raporu.
    Google Business, NAP tutarliligi, yerel anahtar kelimeler, yorum hedefleri.
    """
    checklist = []

    # 1. Google Business Profile
    has_google_reviews = bool(HOTEL_INFO["social_media"].get("google_reviews"))
    checklist.append({
        "item": "Google Business Profile",
        "description": "Google Isletme Profili kaydi ve optimizasyonu",
        "status": "done" if has_google_reviews else "todo",
        "priority": "high",
    })

    # 2. NAP Tutarliligi (Name, Address, Phone)
    has_full_address = all([
        HOTEL_INFO.get("name"),
        HOTEL_INFO.get("address", {}).get("full"),
        HOTEL_INFO.get("phone"),
    ])
    checklist.append({
        "item": "NAP Tutarliligi",
        "description": "Isim, Adres, Telefon bilgilerinin tum platformlarda tutarli olmasi",
        "status": "done" if has_full_address else "warning",
        "priority": "high",
        "details": {
            "name": HOTEL_INFO.get("name", ""),
            "address": HOTEL_INFO.get("address", {}).get("full", ""),
            "phone": HOTEL_INFO.get("phone", ""),
        },
    })

    # 3. Sosyal medya profilleri
    social_platforms = HOTEL_INFO.get("social_media", {})
    active_platforms = [k for k, v in social_platforms.items() if v]
    total_platforms = len(social_platforms)
    checklist.append({
        "item": "Sosyal Medya Profilleri",
        "description": f"{len(active_platforms)}/{total_platforms} platform aktif",
        "status": "done" if len(active_platforms) >= 4 else "warning",
        "priority": "medium",
        "details": {"active": active_platforms},
    })

    # 4. Yerel anahtar kelimeler
    local_keywords = [
        "foca otel", "foca butik otel", "izmir butik otel",
        "foca konaklama", "kozbeyli konagi", "foca restoran",
    ]
    checklist.append({
        "item": "Yerel Anahtar Kelimeler",
        "description": "Web sitesinde yerel anahtar kelimelerin kullanimi",
        "status": "warning",
        "priority": "high",
        "details": {"target_keywords": local_keywords},
    })

    # 5. Online yorum hedefleri
    google_rating = HOTEL_INFO.get("ratings", {}).get("google", 0)
    tripadvisor_rating = HOTEL_INFO.get("ratings", {}).get("tripadvisor", 0)
    checklist.append({
        "item": "Online Yorum Hedefleri",
        "description": "Google ve TripAdvisor yorum sayisi ve puani",
        "status": "warning" if google_rating < 4.5 else "done",
        "priority": "high",
        "details": {
            "google_rating": google_rating,
            "tripadvisor_rating": tripadvisor_rating,
            "target_google_rating": 4.7,
            "target_review_count": 200,
        },
    })

    # 6. Schema.org structured data
    checklist.append({
        "item": "Schema.org Structured Data",
        "description": "Hotel, Restaurant ve LocalBusiness JSON-LD verisi",
        "status": "todo",
        "priority": "high",
    })

    # 7. Booking platformlari
    has_booking = bool(social_platforms.get("booking"))
    has_tripadvisor = bool(social_platforms.get("tripadvisor"))
    checklist.append({
        "item": "Rezervasyon Platformlari",
        "description": "Booking.com ve TripAdvisor listelemeleri",
        "status": "done" if (has_booking and has_tripadvisor) else "warning",
        "priority": "medium",
    })

    # 8. Mobil uyumluluk
    checklist.append({
        "item": "Mobil Uyumluluk",
        "description": "Web sitesinin mobil cihazlarda duzgun goruntulenmesi",
        "status": "warning",
        "priority": "high",
    })

    # 9. Sayfa hizi
    checklist.append({
        "item": "Sayfa Hizi Optimizasyonu",
        "description": "Web sitesi yukleme suresi (hedef: < 3 saniye)",
        "status": "todo",
        "priority": "medium",
    })

    # 10. SSL sertifikasi
    has_https = HOTEL_INFO.get("website", "").startswith("https")
    checklist.append({
        "item": "SSL Sertifikasi",
        "description": "HTTPS ile guvenli baglanti",
        "status": "done" if has_https else "todo",
        "priority": "high",
    })

    # Toplam skor hesapla
    done_count = sum(1 for item in checklist if item["status"] == "done")
    warning_count = sum(1 for item in checklist if item["status"] == "warning")
    todo_count = sum(1 for item in checklist if item["status"] == "todo")
    total = len(checklist)
    local_seo_score = int(((done_count * 1.0 + warning_count * 0.5) / total) * 100)

    return {
        "score": local_seo_score,
        "total_items": total,
        "done": done_count,
        "warning": warning_count,
        "todo": todo_count,
        "checklist": checklist,
    }
