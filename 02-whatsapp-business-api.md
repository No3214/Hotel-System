# WhatsApp Business API Entegrasyonu - Teknik Dokümantasyon

## 1. Genel Bakış

WhatsApp Business API, otellerin misafirleriyle doğrudan ve kişiselleştirilmiş iletişim kurmasını sağlayan güçlü bir araçtır.

## 2. Entegrasyon Mimarisi

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KOZBEYLİ KONAĞI SİSTEMİ                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │Rezervasyon   │  │   Misafir    │  │   Otomasyon  │  │   Bildirim   │   │
│  │   Modülü     │  │   Yönetimi   │  │    Botları   │  │   Merkezi    │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │                 │           │
│         └─────────────────┴────────┬────────┴─────────────────┘           │
│                                    │                                       │
│                         ┌──────────▼──────────┐                           │
│                         │  WhatsApp Service   │                           │
│                         │  (Python/FastAPI)   │                           │
│                         └──────────┬──────────┘                           │
│                                    │                                       │
└────────────────────────────────────┼──────────────────────────────────────┘
                                     │
                              HTTPS/Webhook
                                     │
┌────────────────────────────────────┼──────────────────────────────────────┐
│                         ┌──────────▼──────────┐                           │
│                         │  META BUSINESS API  │                           │
│                         │  (WhatsApp Cloud)   │                           │
│                         └──────────┬──────────┘                           │
│                                    │                                       │
│                           ┌────────▼────────┐                             │
│                           │  WhatsApp App   │                             │
│                           │  (Misafir)      │                             │
│                           └─────────────────┘                             │
└───────────────────────────────────────────────────────────────────────────┘
```

## 3. Konfigürasyon

```python
# config/whatsapp.py

import os
from pydantic_settings import BaseSettings

class WhatsAppConfig(BaseSettings):
    # Meta API Credentials
    ACCESS_TOKEN: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    BUSINESS_ACCOUNT_ID: str = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
    APP_SECRET: str = os.getenv("WHATSAPP_APP_SECRET", "")
    VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
    
    # API URL
    API_VERSION: str = "v18.0"
    BASE_URL: str = f"https://graph.facebook.com/{API_VERSION}"
    
    # Mesaj Limitleri
    RATE_LIMIT_PER_SECOND: int = 20
    RATE_LIMIT_PER_MINUTE: int = 1000
    
    # Template Settings
    DEFAULT_LANGUAGE: str = "tr"
    
    class Config:
        env_prefix = "WHATSAPP_"

settings = WhatsAppConfig()
```

## 4. Mesaj Şablonları (Templates)

### 4.1 Check-out Teşekkür + Yorum İsteği

```json
{
  "name": "checkout_thanks_review",
  "language": {"code": "tr"},
  "category": "UTILITY",
  "components": [
    {
      "type": "HEADER",
      "format": "TEXT",
      "text": "Teşekkürler {{1}}! 🏨"
    },
    {
      "type": "BODY",
      "text": "Kozbeyli Konağı'nda kaldığınız için teşekkür ederiz, {{1}}.\n\nSizin gibi değerli misafirlerimizin görüşleri bizim için çok önemli. Bir dakikanızı ayırarak deneyiminizi değerlendirir misiniz?"
    },
    {
      "type": "FOOTER",
      "text": "Tekrar görüşmek dileğiyle 🌿"
    },
    {
      "type": "BUTTONS",
      "buttons": [
        {
          "type": "URL",
          "text": "Değerlendir",
          "url": "https://g.page/r/XXXX/review"
        }
      ]
    }
  ]
}
```

### 4.2 Rezervasyon Hatırlatma (1 Gün Önce)

```json
{
  "name": "reservation_reminder_1day",
  "language": {"code": "tr"},
  "category": "UTILITY",
  "components": [
    {
      "type": "HEADER",
      "format": "TEXT",
      "text": "Yarın Görüşüyoruz! 🎉"
    },
    {
      "type": "BODY",
      "text": "Merhaba {{1}},\n\nYarın ({{2}}) Kozbeyli Konağı'nda giriş yapacaksınız.\n\n📍 Adres: Kozbeyli Mah. No:1, Fethiye\n⏰ Check-in: 14:00\n📞 İletişim: +90 252 123 4567\n\nWiFi: KozbeyliKonagi2024"
    },
    {
      "type": "FOOTER",
      "text": "Sorularınız için bize ulaşabilirsiniz"
    }
  ]
}
```

### 4.3 Temizlik Ekibi Bildirimi

```json
{
  "name": "cleaning_notification",
  "language": {"code": "tr"},
  "category": "UTILITY",
  "components": [
    {
      "type": "HEADER",
      "format": "TEXT",
      "text": "🧹 Temizlik Bildirimi"
    },
    {
      "type": "BODY",
      "text": "Oda {{1}} boşaldı.\n\nMisafir: {{2}}\nÇıkış: {{3}}\nÖncelik: {{4}}\n\nLütfen odayı hazırlayınız."
    },
    {
      "type": "BUTTONS",
      "buttons": [
        {
          "type": "QUICK_REPLY",
          "text": "Tamamlandı ✅"
        },
        {
          "type": "QUICK_REPLY",
          "text": "Devam Ediyor ⏳"
        }
      ]
    }
  ]
}
```

### 4.4 Oda Hazır Bildirimi

```json
{
  "name": "room_ready_notification",
  "language": {"code": "tr"},
  "category": "UTILITY",
  "components": [
    {
      "type": "HEADER",
      "format": "TEXT",
      "text": "Odanız Hazır! 🏨"
    },
    {
      "type": "BODY",
      "text": "Merhaba {{1}},\n\n{{2}} numaralı odanız hazır.\n\nResepsiyondan anahtarınızı alabilirsiniz.\n\nQR Menü için: https://kozbeyli.com/menu"
    },
    {
      "type": "FOOTER",
      "text": "İyi tatiller! 🌊"
    }
  ]
}
```

### 4.5 Check-in Hoş Geldiniz

```json
{
  "name": "welcome_checkin",
  "language": {"code": "tr"},
  "category": "UTILITY",
  "components": [
    {
      "type": "HEADER",
      "format": "TEXT",
      "text": "Hoş Geldiniz! 🌿"
    },
    {
      "type": "BODY",
      "text": "Merhaba {{1}},\n\nKozbeyli Konağı'na hoş geldiniz! Oda numaranız: {{2}}\n\n🍳 Kahvaltı: 08:00 - 10:30\n🏊 Havuz: 09:00 - 19:00\n🍽️ Restoran: 12:00 - 22:00\n\nSize nasıl yardımcı olabiliriz?"
    },
    {
      "type": "BUTTONS",
      "buttons": [
        {
          "type": "QUICK_REPLY",
          "text": "WiFi Şifresi 📶"
        },
        {
          "type": "QUICK_REPLY",
          "text": "Menü 🍽️"
        },
        {
          "type": "QUICK_REPLY",
          "text": "Yardım ❓"
        }
      ]
    }
  ]
}
```

## 5. WhatsApp Service Sınıfı

```python
# services/whatsapp_service.py

import httpx
from datetime import datetime
from typing import Optional, Dict, List, Any
import logging

from config.whatsapp import settings

logger = logging.getLogger(__name__)

class WhatsAppError(Exception):
    pass

class WhatsAppTemplateError(WhatsAppError):
    pass

class WhatsAppRateLimitError(WhatsAppError):
    pass

class WhatsAppService:
    def __init__(self):
        self.base_url = settings.BASE_URL
        self.phone_number_id = settings.PHONE_NUMBER_ID
        self.access_token = settings.ACCESS_TOKEN
        self.default_language = settings.DEFAULT_LANGUAGE
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=30.0
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _format_phone(self, phone: str) -> str:
        """
        Telefon numarasını uluslararası formata çevirir
        """
        # Sadece rakamları al
        digits = ''.join(filter(str.isdigit, phone))
        
        # Ülke kodu kontrolü
        if not digits.startswith('90') and not digits.startswith('+'):
            digits = '90' + digits
        elif digits.startswith('+'):
            digits = digits[1:]
        
        return digits
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        WhatsApp API'ye istek gönderir
        """
        try:
            response = await self.client.request(
                method=method,
                url=endpoint,
                json=json_data
            )
            
            if response.status_code == 429:
                raise WhatsAppRateLimitError("Rate limit exceeded")
            elif response.status_code == 400:
                error_data = response.json()
                raise WhatsAppTemplateError(
                    f"Template error: {error_data.get('error', {}).get('message')}"
                )
            elif response.status_code != 200:
                raise WhatsAppError(f"API error: {response.status_code} - {response.text}")
            
            return response.json()
            
        except httpx.NetworkError as e:
            logger.error(f"Network error: {e}")
            raise
    
    async def send_template_message(
        self,
        to_phone: str,
        template_name: str,
        language_code: str = None,
        parameters: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Onaylı şablon ile mesaj gönderir
        """
        url = f"/{self.phone_number_id}/messages"
        
        formatted_phone = self._format_phone(to_phone)
        lang_code = language_code or self.default_language
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": lang_code
                }
            }
        }
        
        # Parametreleri ekle
        if parameters:
            payload["template"]["components"] = parameters
        
        result = await self._make_request("POST", url, payload)
        
        # Log kaydet
        await self._log_message(
            to_phone=formatted_phone,
            template_name=template_name,
            message_id=result.get("messages", [{}])[0].get("id"),
            status="sent",
            direction="outgoing"
        )
        
        logger.info(f"Template message sent to {formatted_phone}: {template_name}")
        return result
    
    async def send_text_message(
        self,
        to_phone: str,
        message: str,
        preview_url: bool = False
    ) -> Dict[str, Any]:
        """
        Serbest metin mesajı gönderir (24 saat pencere içinde)
        """
        url = f"/{self.phone_number_id}/messages"
        
        formatted_phone = self._format_phone(to_phone)
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": message
            }
        }
        
        result = await self._make_request("POST", url, payload)
        
        await self._log_message(
            to_phone=formatted_phone,
            message=message,
            message_id=result.get("messages", [{}])[0].get("id"),
            status="sent",
            direction="outgoing"
        )
        
        logger.info(f"Text message sent to {formatted_phone}")
        return result
    
    async def send_interactive_message(
        self,
        to_phone: str,
        header: str,
        body: str,
        buttons: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Butonlu interaktif mesaj gönderir
        """
        url = f"/{self.phone_number_id}/messages"
        
        formatted_phone = self._format_phone(to_phone)
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "text",
                    "text": header
                },
                "body": {
                    "text": body
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": btn["id"],
                                "title": btn["title"]
                            }
                        }
                        for btn in buttons
                    ]
                }
            }
        }
        
        result = await self._make_request("POST", url, payload)
        logger.info(f"Interactive message sent to {formatted_phone}")
        return result
    
    async def send_media_message(
        self,
        to_phone: str,
        media_type: str,  # image, document, video
        media_url: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Medya içeren mesaj gönderir
        """
        url = f"/{self.phone_number_id}/messages"
        
        formatted_phone = self._format_phone(to_phone)
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": media_type,
            media_type: {
                "link": media_url
            }
        }
        
        if caption:
            payload[media_type]["caption"] = caption
        
        result = await self._make_request("POST", url, payload)
        logger.info(f"Media message sent to {formatted_phone}: {media_type}")
        return result
    
    async def _log_message(
        self,
        to_phone: str,
        message_id: Optional[str] = None,
        template_name: Optional[str] = None,
        message: Optional[str] = None,
        status: str = "sent",
        direction: str = "outgoing"
    ):
        """
        Mesaj gönderimini loglar
        """
        from models.whatsapp import WhatsAppMessageLog
        
        await WhatsAppMessageLog.create(
            phone_number=to_phone,
            message_id=message_id,
            template_name=template_name,
            message_content=message[:500] if message else None,  # Limit length
            status=status,
            direction=direction,
            timestamp=datetime.now()
        )
    
    # ==================== ÖZEL MESAJ METODLARI ====================
    
    async def send_checkout_thanks(
        self,
        phone: str,
        guest_name: str,
        review_url: str = "https://g.page/r/XXXX/review"
    ) -> Dict[str, Any]:
        """
        Check-out sonrası teşekkür mesajı gönderir
        """
        parameters = [
            {
                "type": "header",
                "parameters": [
                    {"type": "text", "text": guest_name}
                ]
            },
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": guest_name}
                ]
            }
        ]
        
        return await self.send_template_message(
            to_phone=phone,
            template_name="checkout_thanks_review",
            parameters=parameters
        )
    
    async def send_reservation_reminder(
        self,
        phone: str,
        guest_name: str,
        check_in_date: str
    ) -> Dict[str, Any]:
        """
        Rezervasyon hatırlatması gönderir
        """
        parameters = [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": guest_name},
                    {"type": "text", "text": check_in_date}
                ]
            }
        ]
        
        return await self.send_template_message(
            to_phone=phone,
            template_name="reservation_reminder_1day",
            parameters=parameters
        )
    
    async def notify_cleaning_team(
        self,
        phone: str,
        room_number: str,
        guest_name: str,
        priority: str = "Normal"
    ) -> Dict[str, Any]:
        """
        Temizlik ekibini bilgilendirir
        """
        parameters = [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": room_number},
                    {"type": "text", "text": guest_name},
                    {"type": "text", "text": datetime.now().strftime("%H:%M")},
                    {"type": "text", "text": priority}
                ]
            }
        ]
        
        return await self.send_template_message(
            to_phone=phone,
            template_name="cleaning_notification",
            parameters=parameters
        )
    
    async def send_room_ready(
        self,
        phone: str,
        guest_name: str,
        room_number: str
    ) -> Dict[str, Any]:
        """
        Oda hazır olduğunda misafiri bilgilendirir
        """
        parameters = [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": guest_name},
                    {"type": "text", "text": room_number}
                ]
            }
        ]
        
        return await self.send_template_message(
            to_phone=phone,
            template_name="room_ready_notification",
            parameters=parameters
        )
    
    async def send_welcome_message(
        self,
        phone: str,
        guest_name: str,
        room_number: str
    ) -> Dict[str, Any]:
        """
        Check-in hoş geldiniz mesajı gönderir
        """
        parameters = [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": guest_name},
                    {"type": "text", "text": room_number}
                ]
            }
        ]
        
        return await self.send_template_message(
            to_phone=phone,
            template_name="welcome_checkin",
            parameters=parameters
        )
    
    async def send_reservation_confirmation(
        self, reservation_data: dict) -> Dict[str, Any]:
        """
        Yeni rezervasyon onay mesajı gönderir
        """
        guest = reservation_data.get("guest", {})
        phone = guest.get("phone")
        
        if not phone:
            logger.warning("No phone number for reservation confirmation")
            return None
        
        guest_name = guest.get("first_name", "Misafir")
        check_in = reservation_data.get("check_in", "")
        check_out = reservation_data.get("check_out", "")
        
        message = (
            f"🏨 *Rezervasyon Onayı*\n\n"
            f"Merhaba {guest_name},\n\n"
            f"Rezervasyonunuz başarıyla oluşturuldu.\n\n"
            f"📅 Giriş: {check_in}\n"
            f"📅 Çıkış: {check_out}\n\n"
            f"Sorularınız için bize ulaşabilirsiniz.\n"
            f"📞 +90 252 123 4567"
        )
        
        return await self.send_text_message(phone, message)
```

## 6. Webhook Handler (Gelen Mesajlar)

```python
# webhooks/whatsapp_webhook.py

from fastapi import APIRouter, Request, Header, HTTPException
from typing import Optional
import hmac
import hashlib
import logging

from config.whatsapp import settings
from services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks/whatsapp")

@router.get("/")
async def verify_webhook(
    hub_mode: str,
    hub_verify_token: str,
    hub_challenge: str
):
    """
    Webhook doğrulama endpoint'i
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return int(hub_challenge)
    
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/")
async def receive_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    WhatsApp'tan gelen webhook'ları işler
    """
    body = await request.body()
    
    # Signature doğrulama
    if x_hub_signature_256:
        expected = hmac.new(
            settings.APP_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(f"sha256={expected}", x_hub_signature_256):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = await request.json()
    
    # Gelen mesajları işle
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            
            # Gelen mesajlar
            if "messages" in value:
                for message in value["messages"]:
                    await process_incoming_message(message)
            
            # Mesaj durum güncellemeleri
            if "statuses" in value:
                for status in value["statuses"]:
                    await process_message_status(status)
    
    return {"status": "processed"}

async def process_incoming_message(message: dict):
    """
    Gelen mesajı işler
    """
    from_phone = message.get("from")
    message_type = message.get("type")
    message_id = message.get("id")
    
    # Log kaydet
    from models.whatsapp import WhatsAppMessageLog
    await WhatsAppMessageLog.create(
        phone_number=from_phone,
        message_id=message_id,
        message_content=message,
        direction="incoming",
        status="received",
        timestamp=datetime.now()
    )
    
    whatsapp = WhatsAppService()
    
    if message_type == "text":
        text = message.get("text", {}).get("body", "").lower().strip()
        
        # Otomatik yanıtlar
        if any(word in text for word in ["merhaba", "selam", "hello", "hi"]):
            await send_welcome_response(from_phone, whatsapp)
        
        elif any(word in text for word in ["wifi", "internet", "şifre", "password"]):
            await send_wifi_info(from_phone, whatsapp)
        
        elif any(word in text for word in ["kahvaltı", "breakfast", "sabah"]):
            await send_breakfast_info(from_phone, whatsapp)
        
        elif any(word in text for word in ["restoran", "menu", "yemek", "food"]):
            await send_menu_link(from_phone, whatsapp)
        
        elif any(word in text for word in ["havuz", "pool", "plaj", "beach"]):
            await send_facilities_info(from_phone, whatsapp)
        
        elif any(word in text for word in ["yardım", "help", "destek", "support"]):
            await send_help_info(from_phone, whatsapp)
        
        elif any(word in text for word in ["teşekkür", "thanks", "sağol"]):
            await whatsapp.send_text_message(
                from_phone,
                "Rica ederiz! 🌿 İyi tatiller dileriz."
            )
        
        else:
            # AI Asistan'a yönlendir
            await forward_to_ai_assistant(from_phone, text, whatsapp)
    
    elif message_type == "interactive":
        # Buton yanıtı
        button_reply = message.get("interactive", {}).get("button_reply", {})
        button_id = button_reply.get("id")
        
        if button_id == "cleaning_done":
            await mark_cleaning_complete(from_phone)
        elif button_id == "cleaning_progress":
            await acknowledge_cleaning(from_phone)
        elif button_id == "wifi_password":
            await send_wifi_info(from_phone, whatsapp)
        elif button_id == "menu":
            await send_menu_link(from_phone, whatsapp)
        elif button_id == "help":
            await send_help_info(from_phone, whatsapp)

async def process_message_status(status: dict):
    """
    Mesaj durum güncellemelerini işler
    """
    message_id = status.get("id")
    status_type = status.get("status")  # sent, delivered, read, failed
    
    # Log'u güncelle
    from models.whatsapp import WhatsAppMessageLog
    log = await WhatsAppMessageLog.filter(message_id=message_id).first()
    
    if log:
        log.status = status_type
        log.updated_at = datetime.now()
        await log.save()
    
    logger.info(f"Message {message_id} status updated: {status_type}")

# ==================== YARDIMCI FONKSİYONLAR ====================

async def send_welcome_response(phone: str, whatsapp: WhatsAppService):
    """
    Karşılama mesajı gönderir
    """
    message = (
        "🏨 *Kozbeyli Konağı'na Hoş Geldiniz!*\n\n"
        "Size nasıl yardımcı olabilirim?\n\n"
        "📍 *Konum* - Adres bilgisi\n"
        "🍳 *Kahvaltı* - Kahvaltı saatleri\n"
        "📶 *WiFi* - İnternet şifresi\n"
        "🍽️ *Menü* - Restoran menüsü\n"
        "🏊 *Havuz* - Havuz saatleri\n"
        "❓ *Yardım* - Diğer konular"
    )
    
    await whatsapp.send_text_message(phone, message)

async def send_wifi_info(phone: str, whatsapp: WhatsAppService):
    """
    WiFi bilgisi gönderir
    """
    message = (
        "📶 *WiFi Bilgisi*\n\n"
        "Ağ Adı: *KozbeyliKonagi*\n"
        "Şifre: *KozbeyliKonagi2024*\n\n"
        "İyi kullanımlar! 🌐"
    )
    
    await whatsapp.send_text_message(phone, message)

async def send_breakfast_info(phone: str, whatsapp: WhatsAppService):
    """
    Kahvaltı bilgisi gönderir
    """
    message = (
        "🍳 *Kahvaltı Bilgisi*\n\n"
        "⏰ Saat: 08:00 - 10:30\n"
        "📍 Yer: Ana Restoran\n\n"
        "Kahvaltı dahil odalarda ücretsizdir.\n\n"
        "*Menü:*\n"
        "• Serpme kahvaltı\n"
        "• Sıcak içecekler\n"
        "• Taze meyve suyu\n"
        "• Organik reçeller"
    )
    
    await whatsapp.send_text_message(phone, message)

async def send_menu_link(phone: str, whatsapp: WhatsAppService):
    """
    Menü linki gönderir
    """
    message = (
        "🍽️ *Restoran Menümüz*\n\n"
        "QR Menü için tıklayın:\n"
        "https://kozbeyli.com/menu\n\n"
        "📞 Sipariş için: +90 252 123 4567"
    )
    
    await whatsapp.send_text_message(phone, message, preview_url=True)

async def send_facilities_info(phone: str, whatsapp: WhatsAppService):
    """
    Tesis bilgisi gönderir
    """
    message = (
        "🏊 *Tesislerimiz*\n\n"
        "🏊 *Havuz:* 09:00 - 19:00\n"
        "🏖️ *Plaj:* 08:00 - 20:00\n"
        "💆 *Spa:* 10:00 - 22:00\n"
        "🏋️ *Fitness:* 07:00 - 22:00\n\n"
        "Havlu değişimi resepsiyondan yapılmaktadır."
    )
    
    await whatsapp.send_text_message(phone, message)

async def send_help_info(phone: str, whatsapp: WhatsAppService):
    """
    Yardım bilgisi gönderir
    """
    buttons = [
        {"id": "wifi_password", "title": "WiFi Şifresi 📶"},
        {"id": "menu", "title": "Menü 🍽️"},
        {"id": "call_reception", "title": "Resepsiyon 📞"}
    ]
    
    await whatsapp.send_interactive_message(
        phone,
        "Yardım Menüsü",
        "Size nasıl yardımcı olabilirim? Aşağıdaki seçeneklerden birini seçin:",
        buttons
    )

async def forward_to_ai_assistant(
    phone: str,
    message: str,
    whatsapp: WhatsAppService
):
    """
    Mesajı AI asistan'a yönlendirir
    """
    from services.ai_assistant import AIAssistantService
    
    ai = AIAssistantService()
    response = await ai.get_response(message, context="whatsapp_guest")
    
    await whatsapp.send_text_message(phone, response)

async def mark_cleaning_complete(phone: str):
    """
    Temizlik tamamlandı olarak işaretler
    """
    from models.staff import Staff
    
    staff = await Staff.filter(phone=phone).first()
    if staff:
        # Temizlik durumunu güncelle
        logger.info(f"Cleaning marked complete by {staff.name}")
        
        whatsapp = WhatsAppService()
        await whatsapp.send_text_message(
            phone,
            "✅ Temizlik tamamlandı olarak işaretlendi. Teşekkürler!"
        )

async def acknowledge_cleaning(phone: str):
    """
    Temizlik devam ediyor olarak işaretler
    """
    whatsapp = WhatsAppService()
    await whatsapp.send_text_message(
        phone,
        "⏳ Temizlik devam ediyor. Tamamlandığında 'Tamamlandı' butonuna basınız."
    )
```

## 7. Otomatik Mesaj Tetikleyicileri

```python
# services/whatsapp_triggers.py

from datetime import datetime, timedelta
from typing import Optional
import logging

from services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)

class WhatsAppTriggers:
    def __init__(self):
        self.whatsapp = WhatsAppService()
    
    async def send_checkout_thanks(self, reservation_id: str):
        """
        Check-out sonrası teşekkür mesajı gönderir
        """
        from models.reservation import Reservation
        
        reservation = await Reservation.get(id=reservation_id)
        
        if not reservation.guest_phone:
            logger.warning(f"No phone for reservation {reservation_id}")
            return
        
        try:
            await self.whatsapp.send_checkout_thanks(
                phone=reservation.guest_phone,
                guest_name=reservation.guest_name
            )
            
            # İşaretle
            reservation.thanks_sent = True
            await reservation.save()
            
            logger.info(f"Checkout thanks sent to {reservation.guest_phone}")
            
        except Exception as e:
            logger.error(f"Failed to send checkout thanks: {e}")
    
    async def send_reservation_reminder(self, reservation_id: str):
        """
        Rezervasyon hatırlatması gönderir
        """
        from models.reservation import Reservation
        
        reservation = await Reservation.get(id=reservation_id)
        
        if not reservation.guest_phone:
            return
        
        try:
            await self.whatsapp.send_reservation_reminder(
                phone=reservation.guest_phone,
                guest_name=reservation.guest_name,
                check_in_date=reservation.check_in.strftime("%d.%m.%Y")
            )
            
            reservation.reminder_sent = True
            await reservation.save()
            
            logger.info(f"Reminder sent to {reservation.guest_phone}")
            
        except Exception as e:
            logger.error(f"Failed to send reminder: {e}")
    
    async def notify_cleaning_team(self, room_id: str, reservation_id: str):
        """
        Temizlik ekibini bilgilendirir
        """
        from models.reservation import Reservation
        from models.room import Room
        from models.staff import Staff
        
        reservation = await Reservation.get(id=reservation_id)
        room = await Room.get(id=room_id)
        
        # Temizlik ekibi telefon numaraları
        cleaning_team = await Staff.filter(department="cleaning").all()
        
        priority = "VIP" if reservation.is_vip else "Normal"
        
        for staff in cleaning_team:
            if staff.phone:
                try:
                    await self.whatsapp.notify_cleaning_team(
                        phone=staff.phone,
                        room_number=room.number,
                        guest_name=reservation.guest_name,
                        priority=priority
                    )
                except Exception as e:
                    logger.error(f"Failed to notify {staff.name}: {e}")
    
    async def send_room_ready_notification(self, reservation_id: str):
        """
        Oda hazır olduğunda misafiri bilgilendirir
        """
        from models.reservation import Reservation
        
        reservation = await Reservation.get(id=reservation_id)
        
        if not reservation.guest_phone:
            return
        
        try:
            await self.whatsapp.send_room_ready(
                phone=reservation.guest_phone,
                guest_name=reservation.guest_name,
                room_number=reservation.room_number
            )
            
            logger.info(f"Room ready notification sent to {reservation.guest_phone}")
            
        except Exception as e:
            logger.error(f"Failed to send room ready notification: {e}")
    
    async def send_welcome_message(self, reservation_id: str):
        """
        Check-in hoş geldiniz mesajı gönderir
        """
        from models.reservation import Reservation
        
        reservation = await Reservation.get(id=reservation_id)
        
        if not reservation.guest_phone:
            return
        
        try:
            await self.whatsapp.send_welcome_message(
                phone=reservation.guest_phone,
                guest_name=reservation.guest_name,
                room_number=reservation.room_number
            )
            
            logger.info(f"Welcome message sent to {reservation.guest_phone}")
            
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")
```

## 8. Scheduler Entegrasyonu

```python
# scheduler/whatsapp_jobs.py

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import logging

from services.whatsapp_triggers import WhatsAppTriggers

logger = logging.getLogger(__name__)

class WhatsAppScheduler:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.triggers = WhatsAppTriggers()
    
    def schedule_all(self):
        """
        Tüm WhatsApp job'larını schedule eder
        """
        # Rezervasyon hatırlatma - Her gün 10:00'da
        self.scheduler.add_job(
            self.send_daily_reminders,
            CronTrigger(hour=10, minute=0),
            id="whatsapp_daily_reminders",
            replace_existing=True
        )
        
        # Check-out teşekkür - Her saat başı
        self.scheduler.add_job(
            self.send_checkout_thanks_batch,
            CronTrigger(minute=0),
            id="whatsapp_checkout_thanks",
            replace_existing=True
        )
        
        logger.info("WhatsApp scheduler jobs registered")
    
    async def send_daily_reminders(self):
        """
        Yarın için giriş yapacak misafirlere hatırlatma gönderir
        """
        from models.reservation import Reservation
        
        tomorrow = datetime.now().date() + timedelta(days=1)
        
        reservations = await Reservation.filter(
            check_in=tomorrow,
            status="confirmed",
            reminder_sent=False
        ).all()
        
        logger.info(f"Sending reminders to {len(reservations)} guests")
        
        for res in reservations:
            try:
                await self.triggers.send_reservation_reminder(res.id)
            except Exception as e:
                logger.error(f"Failed to send reminder to {res.guest_phone}: {e}")
    
    async def send_checkout_thanks_batch(self):
        """
        Son 1 saat içinde çıkış yapmış misafirlere teşekkür gönderir
        """
        from models.reservation import Reservation
        
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        reservations = await Reservation.filter(
            check_out__lte=datetime.now(),
            check_out__gte=one_hour_ago,
            status="checked_out",
            thanks_sent=False
        ).all()
        
        logger.info(f"Sending thanks to {len(reservations)} guests")
        
        for res in reservations:
            try:
                await self.triggers.send_checkout_thanks(res.id)
            except Exception as e:
                logger.error(f"Failed to send thanks to {res.guest_phone}: {e}")
    
    def schedule_room_ready(self, reservation_id: str, send_at: datetime):
        """
        Oda hazır bildirimini schedule eder
        """
        self.scheduler.add_job(
            self.triggers.send_room_ready_notification,
            DateTrigger(run_date=send_at),
            args=[reservation_id],
            id=f"room_ready_{reservation_id}",
            replace_existing=True
        )
    
    def schedule_welcome_message(self, reservation_id: str, send_at: datetime):
        """
        Hoş geldiniz mesajını schedule eder
        """
        self.scheduler.add_job(
            self.triggers.send_welcome_message,
            DateTrigger(run_date=send_at),
            args=[reservation_id],
            id=f"welcome_{reservation_id}",
            replace_existing=True
        )
```

## 9. Veri Modelleri

```python
# models/whatsapp.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class WhatsAppMessageLog(BaseModel):
    id: str
    phone_number: str
    message_id: Optional[str]  # WhatsApp message ID
    template_name: Optional[str]
    message_content: Optional[str]
    status: str  # sent, delivered, read, failed, received
    direction: str  # incoming, outgoing
    timestamp: datetime
    updated_at: Optional[datetime] = None
    error_message: Optional[str] = None

class WhatsAppTemplate(BaseModel):
    id: str
    name: str
    language: str
    category: str  # UTILITY, MARKETING, AUTHENTICATION
    status: str  # PENDING, APPROVED, REJECTED
    components: dict
    created_at: datetime

class WhatsAppConfig(BaseModel):
    id: str
    phone_number_id: str
    business_account_id: str
    default_language: str = "tr"
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
```

## 10. API Endpoint'leri

```python
# api/whatsapp_routes.py

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List

from services.whatsapp_service import WhatsAppService

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])

@router.post("/send/template")
async def send_template_message(
    phone: str,
    template_name: str,
    language_code: Optional[str] = Query(default="tr"),
    parameters: Optional[List[dict]] = Query(default=None)
):
    """
    Şablon mesaj gönderir
    """
    async with WhatsAppService() as service:
        result = await service.send_template_message(
            to_phone=phone,
            template_name=template_name,
            language_code=language_code,
            parameters=parameters
        )
    
    return result

@router.post("/send/text")
async def send_text_message(
    phone: str,
    message: str,
    preview_url: bool = Query(default=False)
):
    """
    Metin mesajı gönderir
    """
    async with WhatsAppService() as service:
        result = await service.send_text_message(
            to_phone=phone,
            message=message,
            preview_url=preview_url
        )
    
    return result

@router.get("/logs")
async def get_message_logs(
    phone: Optional[str] = Query(default=None),
    direction: Optional[str] = Query(default=None),
    limit: int = Query(default=50)
):
    """
    Mesaj loglarını listeler
    """
    from models.whatsapp import WhatsAppMessageLog
    
    query = WhatsAppMessageLog.all().order_by("-timestamp")
    
    if phone:
        query = query.filter(phone_number=phone)
    if direction:
        query = query.filter(direction=direction)
    
    logs = await query.limit(limit).all()
    
    return {
        "logs": [
            {
                "id": log.id,
                "phone": log.phone_number,
                "template": log.template_name,
                "status": log.status,
                "direction": log.direction,
                "timestamp": log.timestamp.isoformat()
            }
            for log in logs
        ]
    }

@router.get("/stats")
async def get_message_stats(
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None)
):
    """
    Mesaj istatistiklerini döndürür
    """
    from models.whatsapp import WhatsAppMessageLog
    
    if not date_from:
        date_from = datetime.now().replace(hour=0, minute=0, second=0)
    if not date_to:
        date_to = datetime.now()
    
    logs = await WhatsAppMessageLog.filter(
        timestamp__gte=date_from,
        timestamp__lte=date_to
    ).all()
    
    total_sent = len([l for l in logs if l.direction == "outgoing"])
    total_received = len([l for l in logs if l.direction == "incoming"])
    delivered = len([l for l in logs if l.status == "delivered"])
    read = len([l for l in logs if l.status == "read"])
    failed = len([l for l in logs if l.status == "failed"])
    
    return {
        "period": {
            "from": date_from.isoformat(),
            "to": date_to.isoformat()
        },
        "total_sent": total_sent,
        "total_received": total_received,
        "delivered": delivered,
        "read": read,
        "failed": failed,
        "delivery_rate": round(delivered / total_sent * 100, 1) if total_sent > 0 else 0,
        "read_rate": round(read / total_sent * 100, 1) if total_sent > 0 else 0
    }
```

## 11. Maliyet Analizi

```
Meta WhatsApp Business API Fiyatlandırması (Türkiye):

┌─────────────────────────────────────────────────────────────┐
│  Mesaj Tipi              │  Fiyat (USD)   │  Fiyat (TRY)   │
├─────────────────────────────────────────────────────────────┤
│  Marketing (Şablon)      │  $0.0500      │  ~1.75 TL      │
│  Utility (Şablon)        │  $0.0300      │  ~1.05 TL      │
│  Authentication          │  $0.0300      │  ~1.05 TL      │
│  Service (24h pencere)   │  $0.0050      │  ~0.18 TL      │
└─────────────────────────────────────────────────────────────┘

Aylık Tahmini Kullanım (Kozbeyli Konağı):

┌─────────────────────────────────────────────────────────────┐
│  Senaryo                    │  Adet │  Birim   │  Toplam   │
├─────────────────────────────────────────────────────────────┤
│  Check-out teşekkür         │  450  │  $0.03   │  $13.50   │
│  Rezervasyon hatırlatma     │  450  │  $0.03   │  $13.50   │
│  Temizlik bildirimi         │  900  │  $0.03   │  $27.00   │
│  Oda hazır bildirimi        │  450  │  $0.03   │  $13.50   │
│  Hoş geldiniz mesajı        │  450  │  $0.03   │  $13.50   │
│  Gelen mesaj yanıtları      │  200  │  $0.005  │  $1.00    │
├─────────────────────────────────────────────────────────────┤
│  TOPLAM AYLIK               │ 2900  │          │  $82.00   │
│  Yıllık Tahmini             │       │          │  ~$984    │
│  Yıllık TRY (28 TL/$)       │       │          │  ~27,500₺ │
└─────────────────────────────────────────────────────────────┘
```

## 12. Meta Business Hesap Kurulumu

```
1. business.facebook.com adresine gidin
2. "Hesap Oluştur" > "İşletme Hesabı" seçin
3. İşletme bilgilerini doldurun:
   - İşletme adı: Kozbeyli Konağı
   - Adres: Kozbeyli Mah. Fethiye/Muğla
   - Web sitesi: www.kozbeylikonagi.com
   - Sektör: Konaklama

4. İşletme Doğrulama (1-3 gün):
   - Vergi levhası
   - İmza sirküleri
   - Fatura veya banka ekstresi

5. WhatsApp Business API Başvurusu:
   - "WhatsApp" > "Başlayın" seçin
   - Telefon numarası ekle (sabit hat önerilir)
   - Display name: Kozbeyli Konağı

6. Mesaj Şablonları Oluşturma:
   - "Hesap Araçları" > "Mesaj Şablonları"
   - Yukarıdaki JSON şablonlarını yükle
   - Meta onayı bekle (1-24 saat)

7. API Erişimi:
   - Sistem kullanıcısı oluştur
   - Access token oluştur
   - Phone Number ID ve Business Account ID not al
```

## 13. Çevre Değişkenleri

```bash
# .env
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id_here
WHATSAPP_APP_SECRET=your_app_secret_here
WHATSAPP_VERIFY_TOKEN=your_verify_token_here
```

---

**Not:** Bu dokümantasyon Meta WhatsApp Business API v18.0 için hazırlanmıştır. API versiyonu değişiklik gösterebilir, güncel dokümantasyon için Meta developer portalını kontrol edin.
