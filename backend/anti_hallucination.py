"""
Kozbeyli Konagi - Anti-Halucinasyon Modulu
AI yanitlarinda otel disi bilgi uretimini engeller.
Fiyat, tarih, politika bilgilerini sadece hotel_data.py verileriyle dogrular.
"""
import re
import logging
from hotel_data import (
    HOTEL_INFO, ROOMS, ROOM_PRICES, SPECIAL_DAY_PRICES,
    HOTEL_POLICIES, RESTAURANT_MENU
)

logger = logging.getLogger(__name__)

# Bilinen fiyatlar (TL)
KNOWN_PRICES = {}
for room_type, price in ROOM_PRICES.items():
    KNOWN_PRICES[price] = room_type
for room_type, price in SPECIAL_DAY_PRICES.items():
    KNOWN_PRICES[price] = f"{room_type}_ozel"
for room in ROOMS:
    KNOWN_PRICES[room["base_price_try"]] = room["room_id"]

# Bilinen menu fiyatlari
for cat, items in RESTAURANT_MENU.items():
    for item in items:
        if isinstance(item, dict) and "price_try" in item:
            KNOWN_PRICES[item["price_try"]] = item.get("name", cat)

# Otel bilgileri referans
HOTEL_FACTS = {
    "phone": HOTEL_INFO["phone"],
    "phone_booking": HOTEL_INFO["phone_booking"],
    "checkin": HOTEL_INFO["checkin_time"],
    "checkout": HOTEL_INFO["checkout_time"],
    "total_rooms": HOTEL_INFO["total_rooms"],
    "address": HOTEL_INFO["location"],
    "wifi": "KozbeyliKonagi2024",
    "iban": "TR86 0001 0003 4454 7464 5450 08",
}

# Potansiyel halucinasyon belirtileri
HALLUCINATION_PATTERNS = [
    r"(?:havuz|pool|spa|sauna|hamam|jakuzi|fitness|gym)",
    r"(?:oda servisi|room service)",
    r"(?:24 saat resepsiyon|24.hour reception)",
    r"(?:minibar ucretsiz|free minibar)",
    r"(?:shuttle|transfer|servis araci)",
    r"(?:toplanti salonu|conference room|meeting room)",
    r"(?:yildiz|star|5\s*yildiz|4\s*yildiz)",
]

# Otelde OLMAYAN hizmetler
NON_EXISTENT_SERVICES = [
    "havuz", "pool", "spa", "sauna", "hamam", "jakuzi",
    "fitness", "gym", "oda servisi", "room service",
    "shuttle", "transfer servisi", "toplanti salonu",
    "conference", "all inclusive", "her sey dahil",
]


def extract_prices_from_text(text: str) -> list:
    """Metinden TL fiyatlarini cikar"""
    patterns = [
        r'(\d{1,3}(?:\.\d{3})*)\s*(?:TL|tl|₺)',
        r'(\d{1,3}(?:,\d{3})*)\s*(?:TL|tl|₺)',
        r'(\d+)\s*(?:TL|tl|₺)',
    ]
    prices = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            cleaned = m.replace(".", "").replace(",", "")
            try:
                prices.append(int(cleaned))
            except ValueError:
                pass
    return prices


def check_hallucination_indicators(text: str) -> list:
    """Halucinasyon belirtilerini kontrol et"""
    issues = []
    text_lower = text.lower()

    # 1. Olmayan hizmet kontrol
    for service in NON_EXISTENT_SERVICES:
        if service in text_lower:
            # "yok" veya "mevcut degil" ile birlikte kullanilmissa ok
            context_window = 50
            idx = text_lower.find(service)
            surrounding = text_lower[max(0, idx - context_window):idx + len(service) + context_window]
            negatives = ["yok", "mevcut degil", "bulunmuyor", "sunmuyor", "sunmuyoruz", "not available"]
            if not any(neg in surrounding for neg in negatives):
                issues.append({
                    "type": "non_existent_service",
                    "detail": f"Otelde bulunmayan hizmet: '{service}'",
                    "severity": "high",
                })

    # 2. Yanlis telefon numarasi
    phone_patterns = re.findall(r'(?:\+90|0)[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}', text)
    for phone in phone_patterns:
        cleaned = re.sub(r'\s|-', '', phone)
        known_phones = [
            re.sub(r'\s|-', '', HOTEL_FACTS["phone"]),
            re.sub(r'\s|-', '', HOTEL_FACTS["phone_booking"]),
        ]
        if cleaned not in known_phones and cleaned.replace("+90", "0") not in [p.replace("+90", "0") for p in known_phones]:
            issues.append({
                "type": "wrong_phone",
                "detail": f"Bilinmeyen telefon numarasi: {phone}",
                "severity": "high",
            })

    # 3. Yanlis IBAN
    iban_match = re.findall(r'TR\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{2}', text)
    for iban in iban_match:
        cleaned = iban.replace(" ", "")
        known_iban = HOTEL_FACTS["iban"].replace(" ", "")
        if cleaned != known_iban:
            issues.append({
                "type": "wrong_iban",
                "detail": "Yanlis IBAN numarasi",
                "severity": "critical",
            })

    # 4. Yanlis oda sayisi
    room_count_match = re.findall(r'(\d+)\s*(?:oda|room)', text_lower)
    for count_str in room_count_match:
        count = int(count_str)
        if count != HOTEL_FACTS["total_rooms"] and count > 5:
            issues.append({
                "type": "wrong_room_count",
                "detail": f"Yanlis oda sayisi: {count} (dogru: {HOTEL_FACTS['total_rooms']})",
                "severity": "medium",
            })

    return issues


def calculate_confidence(text: str, intent: str = "general") -> dict:
    """Yanit guven skoru hesapla"""
    issues = check_hallucination_indicators(text)
    prices_in_text = extract_prices_from_text(text)

    # Fiyat dogrulama
    price_issues = 0
    for price in prices_in_text:
        if price not in KNOWN_PRICES and price > 100:
            # Tolerans: %10
            found_close = False
            for known_price in KNOWN_PRICES:
                if abs(price - known_price) / known_price < 0.10:
                    found_close = True
                    break
            if not found_close:
                price_issues += 1
                issues.append({
                    "type": "unverified_price",
                    "detail": f"Dogrulanamayan fiyat: {price} TL",
                    "severity": "medium",
                })

    # Skor hesapla
    score = 1.0
    for issue in issues:
        if issue["severity"] == "critical":
            score -= 0.4
        elif issue["severity"] == "high":
            score -= 0.25
        elif issue["severity"] == "medium":
            score -= 0.15

    score = max(0.0, min(1.0, score))

    return {
        "confidence": round(score, 2),
        "issues": issues,
        "issue_count": len(issues),
        "verified_prices": len(prices_in_text) - price_issues,
        "unverified_prices": price_issues,
        "is_safe": score >= 0.6,
    }


def sanitize_response(text: str, intent: str = "general") -> dict:
    """AI yanitini kontrol et ve gerekirse duzelt"""
    confidence = calculate_confidence(text, intent)

    if confidence["is_safe"]:
        return {
            "text": text,
            "modified": False,
            "confidence": confidence,
        }

    # Guven dusukse - uyari ekle
    critical_issues = [i for i in confidence["issues"] if i["severity"] in ("critical", "high")]

    if critical_issues:
        # Kritik sorunlarda uyari mesaji ekle
        warning = "\n\n_Not: Bu bilgiler genel niteliktedir. Guncel fiyat ve detaylar icin bizi arayin: " + HOTEL_FACTS["phone_booking"] + "_"
        return {
            "text": text + warning,
            "modified": True,
            "confidence": confidence,
        }

    return {
        "text": text,
        "modified": False,
        "confidence": confidence,
    }
