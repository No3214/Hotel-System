"""
Kozbeyli Konagi - Sentiment Analysis & Guest Memory Service
Jack The Butler'dan ilham: Misafir duygu analizi + hatırlama + akilli escalation

Ozellikler:
- Mesaj sentiment analizi (pozitif/negatif/notral)
- Guest memory: Misafir tercihlerini hatirla
- Akilli escalation: AI belirsiz kaldiginda insana yonlendir
- Conversation quality scoring
"""
import re
import logging
from typing import Optional, Dict, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# ==================== SENTIMENT ANALYSIS ====================

POSITIVE_KEYWORDS_TR = [
    "harika", "mukemmel", "guzel", "super", "muthis", "enfes", "tessekur",
    "tesekkur", "sagol", "memnun", "begendim", "tatli", "lezzetli",
    "temiz", "rahat", "huzurlu", "muhtesem", "kusursuz", "efsane",
    "tavsiye", "yildiz", "bravo", "elinize saglik", "nefis",
    "wonderful", "amazing", "beautiful", "great", "excellent", "perfect",
    "thank", "love", "fantastic", "awesome", "delicious", "comfortable",
]

NEGATIVE_KEYWORDS_TR = [
    "berbat", "kotu", "kirli", "pis", "gurultu", "sikinti", "sorun",
    "problem", "bozuk", "calismiyur", "calismiyor", "mutsuz", "memnuniyetsiz",
    "rezalet", "felaket", "sikayet", "hayal kirikligi", "uzgun",
    "gecikme", "bekledim", "ilgisiz", "kaba", "saygi", "dikkatsiz",
    "bad", "terrible", "dirty", "broken", "disappointed", "angry",
    "worst", "horrible", "awful", "rude", "slow", "cold",
    "pahali", "cok pahali", "ucuz degil", "iade", "geri ver",
]

URGENCY_KEYWORDS = [
    "acil", "hemen", "simdi", "bekleyemem", "ambulans", "yangin",
    "hirsiz", "polis", "tehlike", "urgent", "emergency", "immediately",
    "su basti", "elektrik yok", "sicak su yok", "kapı kilitlendi",
]

UNCERTAINTY_PHRASES = [
    "emin degilim", "bilmiyorum", "anlamadim", "ne demek",
    "nasil yapilir", "mumkun mu", "yapabilir misiniz",
    "ozel istek", "farkli bir sey", "normal disinda",
]


def analyze_sentiment(message: str) -> Dict:
    """
    Mesajin sentiment analizini yap.
    Returns: {score: -1.0 to 1.0, label: positive/negative/neutral, confidence: 0-1}
    """
    lower = message.lower()
    words = lower.split()

    positive_count = sum(1 for kw in POSITIVE_KEYWORDS_TR if kw in lower)
    negative_count = sum(1 for kw in NEGATIVE_KEYWORDS_TR if kw in lower)
    urgency_count = sum(1 for kw in URGENCY_KEYWORDS if kw in lower)

    # Exclamation marks and caps boost intensity
    exclamation_count = message.count("!")
    caps_ratio = sum(1 for c in message if c.isupper()) / max(len(message), 1)

    # Calculate score
    total = positive_count + negative_count
    if total == 0:
        score = 0.0
        label = "neutral"
        confidence = 0.3
    else:
        raw_score = (positive_count - negative_count) / total
        # Intensity boost
        intensity = min(1.0, (exclamation_count * 0.1) + (caps_ratio * 0.5))
        score = raw_score * (1 + intensity * 0.3)
        score = max(-1.0, min(1.0, score))

        if score > 0.2:
            label = "positive"
        elif score < -0.2:
            label = "negative"
        else:
            label = "neutral"

        confidence = min(1.0, total * 0.2 + 0.3)

    # Urgency override
    is_urgent = urgency_count > 0 or (negative_count >= 3)

    return {
        "score": round(score, 2),
        "label": label,
        "confidence": round(confidence, 2),
        "positive_count": positive_count,
        "negative_count": negative_count,
        "is_urgent": is_urgent,
        "urgency_count": urgency_count,
    }


def detect_ai_uncertainty(ai_response: str) -> bool:
    """
    Jack The Butler'dan: AI yanitinin belirsiz olup olmadigini tespit et.
    Belirsizse insana yonlendirilmeli.
    """
    uncertainty_markers = [
        "emin degilim", "bilmiyorum", "kontrol etmem gerekiyor",
        "yoneticiyle gorusmenizi", "resepsiyonu aramanizi",
        "net bilgi veremiyorum", "tahmin ediyorum",
        "maalesef bu konuda", "bu soruyu cevaplayamiyorum",
        "i'm not sure", "i don't know", "let me check",
        "unfortunately", "i cannot answer",
    ]
    lower = ai_response.lower()
    return any(marker in lower for marker in uncertainty_markers)


# ==================== GUEST MEMORY ====================

async def get_guest_memory(session_id: str, phone: str = None) -> Dict:
    """
    Misafirin gecmis konusmalarindan tercihlerini ve bilgilerini getir.
    Jack The Butler'dan: "Remembers preferences across conversations"
    """
    from database import db

    memory = {
        "name": None,
        "phone": phone,
        "language": "tr",
        "preferences": [],
        "past_visits": 0,
        "sentiment_history": [],
        "last_topics": [],
        "is_returning": False,
    }

    # Session'dan gecmis mesajlari kontrol et
    past_messages = await db.chat_messages.find(
        {"session_id": session_id},
        {"_id": 0, "intent": 1, "created_at": 1}
    ).sort("created_at", -1).limit(20).to_list(20)

    if past_messages:
        memory["last_topics"] = list(set(
            m.get("intent", "") for m in past_messages if m.get("intent")
        ))[:5]

    # Telefon numarasindan misafir bul
    if phone:
        guest = await db.guests.find_one(
            {"$or": [{"phone": phone}, {"phone": {"$regex": phone[-10:]}}]},
            {"_id": 0}
        )
        if guest:
            memory["name"] = guest.get("name")
            memory["is_returning"] = True
            memory["preferences"] = guest.get("preferences", [])

        # Gecmis rezervasyonlari say
        past_res = await db.reservations.count_documents(
            {"$or": [{"phone": phone}, {"guest_phone": phone}]}
        )
        memory["past_visits"] = past_res

    # Dil tespiti - son mesajlardan
    if past_messages:
        for msg in past_messages:
            text = msg.get("user_message", "")
            if text and any(c in text.lower() for c in ["hello", "hi", "how", "please", "thank"]):
                memory["language"] = "en"
                break

    return memory


async def update_guest_memory(session_id: str, key: str, value, phone: str = None):
    """Misafir hafizasini guncelle"""
    from database import db
    from helpers import utcnow

    update = {"$set": {f"memory.{key}": value, "updated_at": utcnow()}}
    await db.chat_sessions.update_one(
        {"session_id": session_id},
        update,
        upsert=True
    )

    # Eger telefon varsa guest tablosunda da guncelle
    if phone and key == "preferences":
        await db.guests.update_one(
            {"$or": [{"phone": phone}, {"phone": {"$regex": phone[-10:]}}]},
            {"$addToSet": {"preferences": {"$each": value if isinstance(value, list) else [value]}}},
        )


# ==================== SMART ESCALATION ====================

async def smart_escalation_check(
    message: str,
    ai_response: str,
    session_id: str,
    platform: str = "web"
) -> Optional[Dict]:
    """
    Jack The Butler'dan: Akilli escalation - AI belirsiz kaldigi %20'yi insana yonlendir.

    Escalation kosullari:
    1. Mesaj sentiment'i cok negatif (< -0.5)
    2. AI yaniti belirsiz
    3. Tekrarli soru (ayni intent 3+ kez)
    4. Acil durum tespiti
    """
    from database import db
    from helpers import utcnow, new_id

    sentiment = analyze_sentiment(message)
    ai_uncertain = detect_ai_uncertainty(ai_response)

    # Tekrarli soru kontrolu
    repeated = False
    recent_intents = await db.chat_messages.find(
        {"session_id": session_id},
        {"_id": 0, "intent": 1}
    ).sort("created_at", -1).limit(5).to_list(5)

    if len(recent_intents) >= 3:
        last_3_intents = [m.get("intent") for m in recent_intents[:3]]
        if len(set(last_3_intents)) == 1 and last_3_intents[0] not in ("greeting", "thanks", "general"):
            repeated = True

    # Escalation karar
    should_escalate = False
    escalation_reason = None
    severity = "LOW"

    if sentiment["is_urgent"]:
        should_escalate = True
        escalation_reason = "urgent_situation"
        severity = "HIGH"
    elif sentiment["score"] < -0.5:
        should_escalate = True
        escalation_reason = "very_negative_sentiment"
        severity = "MEDIUM"
    elif ai_uncertain:
        should_escalate = True
        escalation_reason = "ai_uncertainty"
        severity = "LOW"
    elif repeated:
        should_escalate = True
        escalation_reason = "repeated_question"
        severity = "MEDIUM"

    if not should_escalate:
        return None

    # Escalation kaydi
    escalation = {
        "id": new_id(),
        "session_id": session_id,
        "platform": platform,
        "message": message,
        "ai_response": ai_response[:200],
        "reason": escalation_reason,
        "severity": severity,
        "sentiment": sentiment,
        "status": "open",
        "created_at": utcnow(),
    }
    await db.escalation_log.insert_one(escalation)

    # Staff bildirimi
    if severity in ("MEDIUM", "HIGH"):
        await db.group_notifications.insert_one({
            "id": new_id(),
            "type": f"smart_escalation_{severity.lower()}",
            "message": (
                f"{'ACIL' if severity == 'HIGH' else 'Dikkat'}: "
                f"Misafir yardim bekliyor ({escalation_reason}). "
                f"Platform: {platform}. Mesaj: {message[:100]}"
            ),
            "status": "sent",
            "source": "sentiment_service",
            "escalation_id": escalation["id"],
            "created_at": utcnow(),
        })

    # Escalation yanitlari
    responses = {
        "urgent_situation": "Durumunuzu anladim. Yoneticimiz hemen bilgilendirildi ve en kisa surede sizinle iletisime gececek. Acil durumlarda: +90 232 826 11 12",
        "very_negative_sentiment": "Yasadiginiz durumdan dolayi cok uzgunuz. Durumu yoneticimize ilettim, en kisa surede sizinle ilgilenecek: +90 532 234 26 86",
        "ai_uncertainty": None,  # Don't interrupt, just log
        "repeated_question": "Bu konuda size daha detayli yardimci olabilmemiz icin sizi yoneticimizle gorusturmek istiyorum: +90 532 234 26 86",
    }

    return {
        "should_escalate": True,
        "reason": escalation_reason,
        "severity": severity,
        "response": responses.get(escalation_reason),
        "escalation_id": escalation["id"],
    }
