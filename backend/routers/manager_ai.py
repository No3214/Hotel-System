from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timezone, timedelta
from database import db
from gemini_service import get_chat_response
from helpers import new_id

router = APIRouter(prefix="/manager-ai", tags=["Manager AI"])
logger = logging.getLogger(__name__)

class ManagerChatRequest(BaseModel):
    message: str
    session_id: str = Field(default_factory=new_id)

MANAGER_SYSTEM_PROMPT = """Sen Kozbeyli Konağı Otel ve Restoranı'nın 'Yönetici Asistanı' yapay zekasısın (Manager AI).
Sadece otel yöneticilerine, personeline ve sahiplerine hizmet veriyorsun.
Amacın: Yöneticilere canlı veriler doğrultusunda otelin durumu, finansal istatistikleri, restoran siparişleri ve personel görevleri hakkında hızlı ve net bilgiler vermek.

Seninle konuşan kişi bir otel yöneticisi. Resmi ama pratik ve analitik bir dil kullan. 
Sana sağlanan 'Canlı Veri Özeti'ni kullanarak yöneticinin sorularını asistan gibi yanıtla.
Eğer verilerde bulunmayan tahmine dayalı bir soru sorulursa, genel bir öngörüde bulunabilirsin ama elindeki verilere sadık kal.
Eğer yönetici "Bugün durum nasıl?", "Gelirler ne alemde?", "Önümüzdeki hafta yoğun mu?" gibi sorular sorarsa canlı veriyi yorumlayarak kısa bir yönetici özeti sun.
"""

@router.post("/chat")
async def manager_ai_chat(request: ManagerChatRequest):
    try:
        # Canlı verileri topla
        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d")
        tomorrow = today + timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")

        # 1. Günlük Rezervasyonlar
        reservations_today = await db.reservations.count_documents({
            "check_in": {"$lte": today_str},
            "check_out": {"$gt": today_str},
            "status": {"$in": ["confirmed", "checked_in"]}
        })
        
        check_ins_today = await db.reservations.count_documents({
            "check_in": today_str,
            "status": {"$in": ["pending", "confirmed"]}
        })
        
        check_outs_today = await db.reservations.count_documents({
            "check_out": today_str,
            "status": {"$in": ["confirmed", "checked_in"]}
        })

        # 2. Bekleyen Görevler
        pending_tasks = await db.tasks.count_documents({"status": {"$in": ["pending", "in_progress"]}})
        
        # 3. Restoran Siparişleri (Bugün aktif olanlar veya tamamlananlar)
        today_orders = await db.orders.count_documents({"date": today_str}) if "orders" in await db.list_collection_names() else 0

        # 4. Gelir verileri (Basit bir hesaplama, reservations koleksiyonundan)
        recent_reservations = await db.reservations.find({
            "created_at": {"$gte": (today - timedelta(days=7)).isoformat()}
        }).to_list(100)
        
        weekly_revenue = sum(res.get("total_price", 0) for res in recent_reservations if res.get("total_price"))

        # 5. HotelRunner Durumu (FAZ 4 - Hedef 2)
        try:
            from routers.hotelrunner import get_status
            hr_status_data = await get_status()
            hr_state = "Aktif (Bagli)" if hr_status_data.get("connected") else "Pasif (Mock/Test Modu)"
            last_sync_doc = hr_status_data.get("last_sync")
            last_sync_time = last_sync_doc.get("timestamp") if last_sync_doc else "Hic yapilmadi"
            hr_failed = hr_status_data.get("failed_syncs", 0)
        except Exception:
            hr_state = "Bilinmiyor"
            last_sync_time = "Bilinmiyor"
            hr_failed = "?"
            
        # 6. FAZ 4 - Hedef 3: VCC ve OTA Finans Uyarıları
        ota_today_finances = []
        try:
            # Bugun islem goren (giris/cikis yapan) HotelRunner kaynakli rezervasyonlari bulalim
            ota_query = {
                "hotelrunner_id": {"$exists": True, "$ne": ""},
                "$or": [
                    {"check_in": today_str},
                    {"check_out": today_str}
                ]
            }
            ota_res = await db.reservations.find(ota_query).to_list(20)
            
            for r in ota_res:
                source = r.get("source", "OTA")
                t_price = r.get("total_price", 0)
                g_name = r.get("guest_name", "Misafir")
                # Basit kural: Booking genelde VCC (Sanal Kart) ile, Expedia ise 'Otel Tahsilatli' (Hotel Collect) yollar.
                # (Gelecekte payment_type alani API'den cekilebilir, simdilik simulasyon)
                if "booking" in source.lower():
                    ota_today_finances.append(f"[{source.upper()}] {g_name} - {t_price} TL: Sanal Kredi Karti (VCC) tahsilati yapilmasi gerekiyor.")
                elif "expedia" in source.lower():
                    ota_today_finances.append(f"[{source.upper()}] {g_name} - {t_price} TL: Otel Tahsilatli (Misafirden nakit/kart alinacak).")
                else:
                    ota_today_finances.append(f"[{source.upper()}] {g_name} - {t_price} TL: Gelen OTA rezervasyonu, odeme durumunu kontrol et.")
                    
        except Exception as e:
            logger.error(f"OTA Finans verisi cekilemedi: {e}")
            
        ota_finance_str = "\n  - ".join(ota_today_finances) if ota_today_finances else "Bugun icin acil OTA tahsilat islemi gorunmuyor."

        # Context build
        context = f"""
Canlı Veri Özeti ({today_str}):
- Otelde konaklayan (dolu oda): {reservations_today} (Toplam Kapasite: 16 oda)
- Bugün Giriş Yapacak (Check-in): {check_ins_today}
- Bugün Çıkış Yapacak (Check-out): {check_outs_today}
- Bekleyen Personel Görevleri: {pending_tasks}
- Bugüne Ait Restoran Siparişi Sayısı: {today_orders}
- Son 7 Günlük Rezerve Edilen Toplam Oda Geliri: {weekly_revenue} TL
- HotelRunner Kanal Yöneticisi Durumu: {hr_state}
- Son OTA Senkronizasyonu: {last_sync_time} (Hata Sayisi: {hr_failed})

OTA Finans & Tahsilat Uyarilari (VCC / Otel Tahsilatli):
  - {ota_finance_str}
"""

        # Gemini'ye gönder
        response_text = await get_chat_response(
            message=request.message,
            session_id=request.session_id,
            system_prompt=MANAGER_SYSTEM_PROMPT,
            context=context
        )

        return {
            "response": response_text,
            "session_id": request.session_id,
            "data_context": context # Debug & display amacli
        }

    except Exception as e:
        logger.error(f"Manager AI Chat err: {e}")
        raise HTTPException(status_code=500, detail=str(e))
