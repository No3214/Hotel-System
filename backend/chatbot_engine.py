"""
Kozbeyli Konagi - Akilli Chatbot Engine
Multi-Agent Router, Auto-Reply, Conversation Flow
Master Project Dump'tan adapte edildi
"""
from typing import Optional, Dict, List, Any
from enum import Enum
from datetime import datetime, timedelta
from database import db
from helpers import utcnow, new_id

# ==============================================
# AGENT TİPLERİ
# ==============================================

class AgentType(str, Enum):
    RESERVATION = "reservation"      # Oda rezervasyonu
    TABLE = "table"                  # Masa rezervasyonu
    RESTAURANT = "restaurant"        # Menu, yemek
    CONCIERGE = "concierge"          # Yerel rehber, Foca
    HOUSEKEEPING = "housekeeping"    # Oda servisi
    EVENTS = "events"                # Etkinlikler, organizasyon
    GENERAL = "general"              # Genel bilgi


class ConversationState(str, Enum):
    IDLE = "idle"
    TABLE_ASK_DATE = "table_ask_date"
    TABLE_ASK_TIME = "table_ask_time"
    TABLE_ASK_PARTY_SIZE = "table_ask_party_size"
    TABLE_ASK_NAME = "table_ask_name"
    TABLE_ASK_PHONE = "table_ask_phone"
    TABLE_CONFIRM = "table_confirm"
    ROOM_ASK_DATES = "room_ask_dates"
    ROOM_ASK_GUESTS = "room_ask_guests"
    ROOM_CONFIRM = "room_confirm"


# ==============================================
# GELİŞMİŞ INTENT KEYWORDS (Master Dump'tan)
# ==============================================

INTENT_KEYWORDS = {
    # Masa rezervasyonu
    "table_reservation": [
        "masa", "masam", "masa ayirt", "masa rezervasyon", "restoran rezervasyon",
        "yer ayirt", "aksam yemegi", "ogle yemegi", "kahvalti", "yemek yemek",
        "table", "dinner", "lunch", "breakfast", "reservation"
    ],
    # Oda rezervasyonu
    "room_reservation": [
        "oda", "konaklama", "gecelik", "rezervasyon", "fiyat", "yer var mi",
        "musait", "booking", "price", "available", "room", "ucret", "kac para",
        "kalmak", "kalmak istiyorum", "oda ayirt"
    ],
    # İptal
    "cancellation": [
        "iptal", "iade", "vazgec", "cancel", "refund", "degisiklik"
    ],
    # Menu
    "menu": [
        "menu", "yemek", "ne yenir", "tavsiye", "lezzet", "food",
        "antakya", "kunefe", "kebap", "meze", "tatli", "icecek"
    ],
    # Konum
    "location": [
        "nerede", "konum", "adres", "nasil gelinir", "yol tarifi",
        "location", "address", "directions", "harita", "map", "ulasim"
    ],
    # WiFi
    "wifi": [
        "wifi", "internet", "sifre", "password", "baglanti", "ag"
    ],
    # Etkinlikler
    "events": [
        "etkinlik", "dugun", "nisan", "toplanti", "organizasyon",
        "event", "wedding", "meeting", "parti", "kutlama", "dogum gunu"
    ],
    # Check-in/out
    "checkin": [
        "giris", "cikis", "check-in", "check-out", "erken giris",
        "gec cikis", "saat kacta"
    ],
    # Evcil hayvan
    "pets": [
        "evcil hayvan", "kopek", "kedi", "pet", "dog", "cat", "hayvan"
    ],
    # İletişim
    "contact": [
        "telefon", "numara", "iletisim", "arayin", "phone", "contact",
        "whatsapp", "mesaj"
    ],
    # Fiyat
    "price": [
        "fiyat", "ucret", "kac lira", "kac tl", "ne kadar", "price",
        "cost", "rate"
    ],
    # Selamlama
    "greeting": [
        "merhaba", "selam", "gunayin", "iyi gunler", "iyi aksamlar",
        "hello", "hi", "hey", "good morning", "good evening"
    ],
    # Teşekkür
    "thanks": [
        "tesekkur", "sagol", "eyv", "thanks", "thank you", "mersi"
    ],
}

# Agent routing keywords
AGENT_KEYWORDS = {
    AgentType.TABLE: ["masa", "restoran", "yemek", "aksam", "ogle", "kahvalti", "rezervasyon"],
    AgentType.RESERVATION: ["oda", "konaklama", "gecelik", "kalmak", "fiyat", "booking"],
    AgentType.RESTAURANT: ["menu", "yemek", "antakya", "kunefe", "kebap", "meze", "lezzet"],
    AgentType.CONCIERGE: ["foca", "gezi", "plaj", "ulasim", "taksi", "cevre", "yakin"],
    AgentType.HOUSEKEEPING: ["temizlik", "havlu", "klima", "sicak su", "sabun", "oda servisi"],
    AgentType.EVENTS: ["dugun", "nisan", "toplanti", "dogum gunu", "organizasyon", "etkinlik"],
    AgentType.GENERAL: ["merhaba", "selam", "wifi", "otopark", "tesekkur", "bilgi"],
}


# ==============================================
# CONVERSATION FLOW MANAGER
# ==============================================

class ConversationFlow:
    """Konuşma akışı yöneticisi - Masa rezervasyonu için"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = ConversationState.IDLE
        self.data: Dict[str, Any] = {}
    
    @classmethod
    async def load(cls, session_id: str) -> "ConversationFlow":
        """Session'dan mevcut flow'u yükle"""
        flow = cls(session_id)
        session = await db.chat_sessions.find_one({"session_id": session_id}, {"_id": 0})
        if session:
            flow.state = ConversationState(session.get("flow_state", "idle"))
            flow.data = session.get("flow_data", {})
        return flow
    
    async def save(self):
        """Flow state'i kaydet"""
        await db.chat_sessions.update_one(
            {"session_id": self.session_id},
            {
                "$set": {
                    "flow_state": self.state.value,
                    "flow_data": self.data,
                    "updated_at": utcnow()
                },
                "$setOnInsert": {
                    "session_id": self.session_id,
                    "created_at": utcnow()
                }
            },
            upsert=True
        )
    
    async def reset(self):
        """Flow'u sıfırla"""
        self.state = ConversationState.IDLE
        self.data = {}
        await self.save()


# ==============================================
# INTENT DETECTION
# ==============================================

def detect_intent(message: str) -> str:
    """Mesajdan intent tespit et"""
    lower = message.lower()
    
    # Öncelik sırasına göre kontrol
    priority_order = [
        "table_reservation", "room_reservation", "cancellation", 
        "menu", "location", "wifi", "events", "checkin", 
        "pets", "contact", "price", "greeting", "thanks"
    ]
    
    for intent in priority_order:
        keywords = INTENT_KEYWORDS.get(intent, [])
        if any(kw in lower for kw in keywords):
            return intent
    
    return "general"


def route_to_agent(message: str) -> AgentType:
    """Mesajı en uygun agent'a yönlendir"""
    lower = message.lower()
    
    best_agent = AgentType.GENERAL
    max_score = 0
    
    for agent, keywords in AGENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in lower)
        if score > max_score:
            max_score = score
            best_agent = agent
    
    return best_agent


# ==============================================
# AUTO-REPLY ENGINE
# ==============================================

async def get_auto_reply(message: str, language: str = "tr") -> Optional[Dict[str, Any]]:
    """Kural tabanlı otomatik yanıt"""
    intent = detect_intent(message)
    
    if intent == "greeting":
        return {
            "matched": True,
            "intent": intent,
            "message": "Merhaba! 🏨 Kozbeyli Konağı'na hoş geldiniz. Size nasıl yardımcı olabilirim?\n\n• Masa rezervasyonu\n• Oda rezervasyonu\n• Menü bilgisi\n• Konum ve ulaşım" if language == "tr" else 
                      "Hello! 🏨 Welcome to Kozbeyli Konağı. How can I help you?\n\n• Table reservation\n• Room reservation\n• Menu information\n• Location and directions"
        }
    
    if intent == "thanks":
        return {
            "matched": True,
            "intent": intent,
            "message": "Rica ederim! Başka bir konuda yardımcı olabilir miyim? 😊" if language == "tr" else
                      "You're welcome! Is there anything else I can help you with? 😊"
        }
    
    if intent == "wifi":
        return {
            "matched": True,
            "intent": intent,
            "message": "📶 WiFi Bilgileri:\n\nAğ Adı: Kozbeyli_Konagi_Guest\nŞifre: konak1234\n\nTesis genelinde ücretsiz internet erişimi mevcuttur."
        }
    
    if intent == "location":
        return {
            "matched": True,
            "intent": intent,
            "message": "📍 Kozbeyli Konağı\n\nAdres: Kozbeyli Köyü Küme Evleri No:188, Foça, İzmir\n\n🗺️ Konum: https://maps.app.goo.gl/kozbeyli\n\n🚗 Foça merkezden 10 dakika\n✈️ İzmir Havalimanı'ndan 60 dakika"
        }
    
    if intent == "contact":
        return {
            "matched": True,
            "intent": intent,
            "message": "📞 İletişim Bilgileri:\n\nTelefon: +90 232 826 11 12\nWhatsApp: +90 532 234 26 86\nE-posta: info@kozbeylikonagi.com\n\n🌐 www.kozbeylikonagi.com\n📸 @kozbeylikonagi"
        }
    
    if intent == "checkin":
        return {
            "matched": True,
            "intent": intent,
            "message": "🕐 Giriş/Çıkış Saatleri:\n\n✅ Giriş (Check-in): 14:00\n✅ Çıkış (Check-out): 12:00\n\n⏰ Erken giriş ve geç çıkış müsaitliğe bağlı olarak ek ücret karşılığında mümkündür.\n\n🚪 Otel kapısı güvenlik nedeniyle 23:00'da kapanır."
        }
    
    if intent == "pets":
        return {
            "matched": True,
            "intent": intent,
            "message": "🐾 Evcil Hayvan Politikası:\n\n✅ Küçük ırk evcil hayvanlar ücretsiz kabul edilir\n✅ Büyük ırklar için balkonlu oda ayarlanabilir\n⚠️ Restoran kapalı alanına evcil hayvan giremez\n\nLütfen rezervasyon sırasında bilgi veriniz."
        }
    
    # Masa rezervasyonu intent'i - Flow başlat
    if intent == "table_reservation":
        return {
            "matched": True,
            "intent": intent,
            "start_flow": "table",
            "message": "🍽️ Masa rezervasyonu için memnuniyetle yardımcı olacağım!\n\n📅 Hangi tarih için rezervasyon yapmak istiyorsunuz?\n\n(Örnek: 15 Şubat, yarın, bu cumartesi)"
        }
    
    return None


# ==============================================
# MASA REZERVASYONU AKIŞI
# ==============================================

async def process_table_flow(
    flow: ConversationFlow, 
    message: str
) -> Dict[str, Any]:
    """Masa rezervasyonu konuşma akışını işle"""
    
    lower = message.lower().strip()
    
    # Tarih soruluyor
    if flow.state == ConversationState.TABLE_ASK_DATE:
        # Tarih parse etmeye çalış
        date = parse_date(message)
        if date:
            flow.data["date"] = date
            flow.data["date_display"] = format_date_turkish(date)
            flow.state = ConversationState.TABLE_ASK_TIME
            await flow.save()
            return {
                "message": f"📅 {flow.data['date_display']} için not aldım.\n\n⏰ Saat kaçta gelmek istersiniz?\n\n🌅 Kahvaltı: 08:30-11:00\n☀️ Öğle: 12:00-14:00\n🌙 Akşam: 18:00-22:00\n\n(Örnek: 20:00, akşam 8)"
            }
        else:
            return {
                "message": "📅 Tarihi anlayamadım. Lütfen şu formatta yazın:\n\n• 15 Şubat\n• 15.02.2026\n• Yarın\n• Bu cumartesi"
            }
    
    # Saat soruluyor
    if flow.state == ConversationState.TABLE_ASK_TIME:
        time, meal_type = parse_time(message)
        if time:
            flow.data["time"] = time
            flow.data["meal_type"] = meal_type
            flow.state = ConversationState.TABLE_ASK_PARTY_SIZE
            await flow.save()
            
            meal_name = {"breakfast": "Kahvaltı", "lunch": "Öğle", "dinner": "Akşam"}.get(meal_type, "")
            return {
                "message": f"⏰ {time} ({meal_name}) için not aldım.\n\n👥 Kaç kişi olacaksınız?"
            }
        else:
            return {
                "message": "⏰ Saati anlayamadım. Lütfen şu formatta yazın:\n\n• 20:00\n• Akşam 8\n• 19.30"
            }
    
    # Kişi sayısı soruluyor
    if flow.state == ConversationState.TABLE_ASK_PARTY_SIZE:
        party_size = parse_number(message)
        if party_size and 1 <= party_size <= 12:
            flow.data["party_size"] = party_size
            flow.state = ConversationState.TABLE_ASK_NAME
            await flow.save()
            return {
                "message": f"👥 {party_size} kişi için not aldım.\n\n📝 Rezervasyon hangi isim üzerine olacak?"
            }
        else:
            return {
                "message": "👥 Lütfen 1-12 arası kişi sayısı belirtin.\n\n12 kişiden fazla gruplar için lütfen bizi arayın: +90 532 234 26 86"
            }
    
    # İsim soruluyor
    if flow.state == ConversationState.TABLE_ASK_NAME:
        if len(message.strip()) >= 2:
            flow.data["guest_name"] = message.strip().title()
            flow.state = ConversationState.TABLE_ASK_PHONE
            await flow.save()
            return {
                "message": f"📝 {flow.data['guest_name']} olarak kaydediyorum.\n\n📱 İletişim için telefon numaranızı alabilir miyim?\n\n(Örnek: 0532 234 26 86)"
            }
        else:
            return {
                "message": "📝 Lütfen geçerli bir isim giriniz."
            }
    
    # Telefon soruluyor
    if flow.state == ConversationState.TABLE_ASK_PHONE:
        phone = parse_phone(message)
        if phone:
            flow.data["phone"] = phone
            flow.state = ConversationState.TABLE_CONFIRM
            await flow.save()
            
            # Onay mesajı
            summary = f"""✅ *Rezervasyon Özeti*

📅 Tarih: {flow.data['date_display']}
⏰ Saat: {flow.data['time']}
👥 Kişi Sayısı: {flow.data['party_size']} kişi
📝 İsim: {flow.data['guest_name']}
📱 Telefon: {flow.data['phone']}

Bu bilgiler doğru mu? Onaylıyor musunuz?

*Evet* yazarak onaylayabilir veya *Hayır* yazarak iptal edebilirsiniz."""
            
            return {"message": summary}
        else:
            return {
                "message": "📱 Telefon numarasını anlayamadım. Lütfen şu formatta yazın:\n\n• 0532 234 26 86\n• 5322342686"
            }
    
    # Onay bekleniyor
    if flow.state == ConversationState.TABLE_CONFIRM:
        if any(word in lower for word in ["evet", "onay", "tamam", "ok", "yes", "dogru", "doğru"]):
            # Flow verisini önce kaydet
            flow_data = flow.data.copy()
            
            # Rezervasyonu kaydet
            reservation = await create_table_reservation_from_flow(flow_data)
            
            # Grup bildirimi için kaydet
            await save_notification_for_group(reservation)
            
            # Flow'u sıfırla
            await flow.reset()
            
            return {
                "message": f"""🎉 *Rezervasyonunuz Alındı!*

Rezervasyon No: #{reservation['id'][:8].upper()}

📅 {flow_data.get('date_display', reservation.get('date', ''))}
⏰ {flow_data.get('time', reservation.get('time', ''))}
👥 {flow_data.get('party_size', reservation.get('party_size', ''))} kişi

Sizi bekliyoruz! 🏨

📞 Değişiklik için: +90 532 234 26 86

_Kozbeyli Konağı - Antakya Sofrası_""",
                "reservation_created": True,
                "reservation": reservation
            }
        
        elif any(word in lower for word in ["hayir", "hayır", "iptal", "vazgec", "no", "cancel"]):
            await flow.reset()
            return {
                "message": "❌ Rezervasyon iptal edildi.\n\nBaşka bir konuda yardımcı olabilir miyim?"
            }
        
        else:
            return {
                "message": "Lütfen *Evet* veya *Hayır* yazarak yanıtlayın."
            }
    
    return None


# ==============================================
# YARDIMCI FONKSİYONLAR
# ==============================================

def parse_date(text: str) -> Optional[str]:
    """Metinden tarih parse et"""
    import re
    from datetime import datetime, timedelta
    
    lower = text.lower().strip()
    today = datetime.now()
    
    # Bugün, yarın, vs
    if "bugun" in lower or "bugün" in lower:
        return today.strftime("%Y-%m-%d")
    if "yarin" in lower or "yarın" in lower:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    if "cumartesi" in lower:
        days_until = (5 - today.weekday()) % 7
        if days_until == 0:
            days_until = 7
        return (today + timedelta(days=days_until)).strftime("%Y-%m-%d")
    if "pazar" in lower:
        days_until = (6 - today.weekday()) % 7
        if days_until == 0:
            days_until = 7
        return (today + timedelta(days=days_until)).strftime("%Y-%m-%d")
    
    # Ay isimleri
    months = {
        "ocak": 1, "subat": 2, "şubat": 2, "mart": 3, "nisan": 4,
        "mayis": 5, "mayıs": 5, "haziran": 6, "temmuz": 7, "agustos": 8,
        "ağustos": 8, "eylul": 9, "eylül": 9, "ekim": 10, "kasim": 11,
        "kasım": 11, "aralik": 12, "aralık": 12
    }
    
    # "15 Şubat" formatı
    for month_name, month_num in months.items():
        if month_name in lower:
            day_match = re.search(r'(\d{1,2})', lower)
            if day_match:
                day = int(day_match.group(1))
                year = today.year
                if month_num < today.month or (month_num == today.month and day < today.day):
                    year += 1
                try:
                    date = datetime(year, month_num, day)
                    return date.strftime("%Y-%m-%d")
                except ValueError:
                    pass
    
    # DD.MM.YYYY veya DD/MM/YYYY formatı
    date_match = re.search(r'(\d{1,2})[./](\d{1,2})(?:[./](\d{2,4}))?', text)
    if date_match:
        day = int(date_match.group(1))
        month = int(date_match.group(2))
        year = int(date_match.group(3)) if date_match.group(3) else today.year
        if year < 100:
            year += 2000
        try:
            date = datetime(year, month, day)
            return date.strftime("%Y-%m-%d")
        except ValueError:
            pass
    
    return None


def format_date_turkish(date_str: str) -> str:
    """Tarihi Türkçe formata çevir"""
    from datetime import datetime
    
    months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
              "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = days[date.weekday()]
        return f"{date.day} {months[date.month-1]} {day_name}"
    except:
        return date_str


def parse_time(text: str) -> tuple:
    """Metinden saat parse et, meal type döndür"""
    import re
    
    lower = text.lower().strip()
    
    # Öğün isimlerinden tahmin
    if "kahvalti" in lower or "kahvaltı" in lower:
        return ("09:00", "breakfast")
    if "ogle" in lower or "öğle" in lower:
        return ("12:30", "lunch")
    if "aksam" in lower or "akşam" in lower:
        time_match = re.search(r'(\d{1,2})', lower)
        if time_match:
            hour = int(time_match.group(1))
            if hour < 12:
                hour += 12
            return (f"{hour:02d}:00", "dinner")
        return ("20:00", "dinner")
    
    # HH:MM veya HH.MM formatı
    time_match = re.search(r'(\d{1,2})[:.:]?(\d{2})?', text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        
        # 12 saat formatını 24 saate çevir
        if hour < 12 and ("aksam" in lower or "akşam" in lower):
            hour += 12
        
        time_str = f"{hour:02d}:{minute:02d}"
        
        # Meal type belirle
        if 8 <= hour < 12:
            meal_type = "breakfast"
        elif 12 <= hour < 17:
            meal_type = "lunch"
        else:
            meal_type = "dinner"
        
        return (time_str, meal_type)
    
    return (None, None)


def parse_number(text: str) -> Optional[int]:
    """Metinden sayı parse et"""
    import re
    
    lower = text.lower().strip()
    
    # Yazılı sayılar
    numbers = {
        "bir": 1, "iki": 2, "uc": 3, "üç": 3, "dort": 4, "dört": 4,
        "bes": 5, "beş": 5, "alti": 6, "altı": 6, "yedi": 7, "sekiz": 8,
        "dokuz": 9, "on": 10, "onbir": 11, "oniki": 12
    }
    
    for word, num in numbers.items():
        if word in lower:
            return num
    
    # Rakam
    match = re.search(r'(\d+)', text)
    if match:
        return int(match.group(1))
    
    return None


def parse_phone(text: str) -> Optional[str]:
    """Telefon numarası parse et"""
    import re
    
    # Sadece rakamları al
    digits = re.sub(r'\D', '', text)
    
    # Türkiye formatı kontrolü
    if len(digits) >= 10:
        if digits.startswith("90"):
            digits = digits[2:]
        elif digits.startswith("0"):
            digits = digits[1:]
        
        if len(digits) == 10:
            return f"+90 {digits[:3]} {digits[3:6]} {digits[6:]}"
    
    return None


async def create_table_reservation_from_flow(data: Dict) -> Dict:
    """Flow verisinden masa rezervasyonu oluştur"""
    from routers.table_reservations import find_available_tables, MealType, MEAL_DURATIONS
    
    meal_type = MealType(data["meal_type"])
    
    # Uygun masa bul
    available_tables = await find_available_tables(
        data["date"], data["time"], meal_type, data["party_size"]
    )
    
    selected_table = available_tables[0] if available_tables else None
    
    # Rezervasyon oluştur
    duration = MEAL_DURATIONS[meal_type]
    start_mins = int(data["time"].replace(":", "")[:2]) * 60 + int(data["time"].replace(":", "")[2:] if len(data["time"]) > 2 else 0)
    end_mins = start_mins + duration
    end_time = f"{end_mins // 60:02d}:{end_mins % 60:02d}"
    
    reservation = {
        "id": new_id(),
        "guest_name": data["guest_name"],
        "phone": data["phone"],
        "date": data["date"],
        "time": data["time"],
        "party_size": data["party_size"],
        "meal_type": data["meal_type"],
        "table_id": selected_table["id"] if selected_table else None,
        "table_name": selected_table["name"] if selected_table else "Atanacak",
        "end_time": end_time,
        "duration_minutes": duration,
        "status": "confirmed",
        "source": "whatsapp_bot",
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    
    await db.table_reservations.insert_one(reservation)
    return reservation


async def save_notification_for_group(reservation: Dict):
    """Rezervasyon grubuna gönderilecek bildirimi kaydet"""
    notification = {
        "id": new_id(),
        "type": "table_reservation",
        "reservation_id": reservation["id"],
        "message": f"""🍽️ *Yeni Masa Rezervasyonu*

📅 {format_date_turkish(reservation['date'])}
⏰ {reservation['time']}
👥 {reservation['party_size']} kişi
📝 {reservation['guest_name']}
📱 {reservation['phone']}
🪑 {reservation.get('table_name', 'Atanacak')}

_WhatsApp Bot ile alındı_""",
        "status": "pending",
        "created_at": utcnow(),
    }
    
    await db.group_notifications.insert_one(notification)


# ==============================================
# ANA CHATBOT İŞLEM FONKSİYONU
# ==============================================

async def process_chatbot_message(
    message: str,
    session_id: str,
    platform: str = "web",
    language: str = "tr"
) -> Dict[str, Any]:
    """Ana chatbot mesaj işleme fonksiyonu"""
    
    # 1. Conversation flow kontrol et
    flow = await ConversationFlow.load(session_id)
    
    # 2. Aktif flow varsa işle
    if flow.state != ConversationState.IDLE:
        result = await process_table_flow(flow, message)
        if result:
            # message -> response olarak dönüştür
            return {
                "response": result.get("message", ""),
                "intent": "table_flow",
                "reservation_created": result.get("reservation_created", False),
                "reservation": result.get("reservation"),
            }
    
    # 3. Auto-reply kontrol et
    auto_reply = await get_auto_reply(message, language)
    if auto_reply:
        # Masa rezervasyonu flow başlat
        if auto_reply.get("start_flow") == "table":
            flow.state = ConversationState.TABLE_ASK_DATE
            await flow.save()
        
        return {
            "response": auto_reply["message"],
            "intent": auto_reply["intent"],
            "matched": True
        }
    
    # 4. AI'ya yönlendir
    return None  # Chatbot router tarafından AI'ya gönderilecek
