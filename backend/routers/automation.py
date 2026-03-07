from fastapi import APIRouter, HTTPException
from typing import Optional
from database import db
from helpers import utcnow, new_id
import json
from datetime import datetime, timedelta, timezone
from hotel_data import HOTEL_POLICIES
from celery_tasks import (
    breakfast_prep_task,
    morning_reminders_task,
    checkout_cleaning_task,
    evening_room_check_task,
)

router = APIRouter(tags=["automation"])


# ==================== ODEME HATIRLATMA BOTU ====================

@router.post("/automation/payment-reminder")
async def run_payment_reminder():
    """Cumartesi check-in olan ve odemesi tamamlanmayan rezervasyonlari hatirlatir"""
    now = datetime.now(timezone.utc)

    # Find upcoming Saturday reservations without full payment
    upcoming = await db.reservations.find({
        "status": {"$in": ["pending", "confirmed"]},
        "payment_status": {"$ne": "paid"},
    }, {"_id": 0}).to_list(100)

    reminders = []
    for res in upcoming:
        try:
            check_in = datetime.strptime(res.get("check_in", ""), "%Y-%m-%d")
        except (ValueError, TypeError):
            continue

        # Saturday = 5
        if check_in.weekday() == 5:
            days_until = (check_in - now.replace(tzinfo=None)).days
            if 0 <= days_until <= 7:
                reminder = {
                    "id": new_id(),
                    "type": "payment_reminder",
                    "reservation_id": res["id"],
                    "guest_id": res.get("guest_id"),
                    "check_in": res.get("check_in"),
                    "room_type": res.get("room_type"),
                    "total_price": res.get("total_price"),
                    "days_until": days_until,
                    "message": f"Cumartesi check-in. Tam on odeme gerekli. {days_until} gun kaldi.",
                    "status": "pending",
                    "created_at": utcnow(),
                }
                await db.automation_logs.insert_one(reminder)
                reminders.append({k: v for k, v in reminder.items() if k != "_id"})

    return {
        "success": True,
        "type": "payment_reminder",
        "reminders_created": len(reminders),
        "reminders": reminders,
        "policy": HOTEL_POLICIES["saturday_payment"]["tr"],
    }


# ==================== IPTAL POLITIKASI DENETCISI ====================

@router.post("/automation/cancellation-check")
async def run_cancellation_check():
    """Iptal taleplerini kontrol eder ve ceza hesaplar"""
    now = datetime.now(timezone.utc)

    cancelled = await db.reservations.find({
        "status": "cancelled",
        "cancellation_processed": {"$ne": True},
    }, {"_id": 0}).to_list(100)

    results = []
    for res in cancelled:
        try:
            check_in = datetime.strptime(res.get("check_in", ""), "%Y-%m-%d")
        except (ValueError, TypeError):
            continue

        cancelled_at = res.get("cancelled_at") or res.get("updated_at") or utcnow()
        try:
            cancel_date = datetime.fromisoformat(cancelled_at.replace("Z", "+00:00")).replace(tzinfo=None)
        except (ValueError, TypeError):
            cancel_date = now.replace(tzinfo=None)

        days_before = (check_in - cancel_date).days
        total_price = res.get("total_price", 0) or 0

        if days_before >= 3:
            penalty_rate = 0
            penalty_type = "ucretsiz_iptal"
            policy_text = "3+ gun once: Ucretsiz iptal"
        elif days_before >= 1:
            penalty_rate = 0.5
            penalty_type = "gec_iptal"
            policy_text = "1-2 gun once: %50 ceza"
        else:
            penalty_rate = 1.0
            penalty_type = "son_gun_iptal"
            policy_text = "Ayni gun / no-show: %100 ceza"

        penalty_amount = round(total_price * penalty_rate)

        result = {
            "id": new_id(),
            "type": "cancellation_penalty",
            "reservation_id": res["id"],
            "guest_id": res.get("guest_id"),
            "check_in": res.get("check_in"),
            "total_price": total_price,
            "days_before_checkin": days_before,
            "penalty_type": penalty_type,
            "penalty_rate": penalty_rate,
            "penalty_amount": penalty_amount,
            "policy": policy_text,
            "status": "calculated",
            "created_at": utcnow(),
        }
        await db.automation_logs.insert_one(result)

        # Mark as processed
        await db.reservations.update_one(
            {"id": res["id"]},
            {"$set": {"cancellation_processed": True, "penalty_amount": penalty_amount, "penalty_type": penalty_type}}
        )

        results.append({k: v for k, v in result.items() if k != "_id"})

    return {
        "success": True,
        "type": "cancellation_check",
        "processed": len(results),
        "results": results,
    }


# ==================== MUTFAK TAHMIN BOTU ====================

@router.get("/automation/kitchen-forecast")
async def kitchen_forecast(days: int = 7):
    """Doluluk oranina gore mutfak malzeme tahmini"""
    now = datetime.now(timezone.utc)
    forecast = []

    for i in range(days):
        date = (now + timedelta(days=i)).strftime("%Y-%m-%d")

        # Count reservations for that date
        guest_count = await db.reservations.count_documents({
            "status": {"$in": ["confirmed", "checked_in"]},
            "check_in": {"$lte": date},
            "check_out": {"$gte": date},
        })

        # Average 2 guests per reservation if no specific count
        estimated_guests = guest_count * 2

        # Basic meal estimates (breakfast is included for hotel guests)
        breakfast_servings = estimated_guests
        lunch_estimate = round(estimated_guests * 0.3)  # 30% of guests eat lunch
        dinner_estimate = round(estimated_guests * 0.7)  # 70% of guests eat dinner

        # Table reservation guests
        table_res = await db.table_reservations.count_documents({
            "date": date,
            "status": {"$in": ["pending", "confirmed"]},
        })

        forecast.append({
            "date": date,
            "day_name": ["Pzt", "Sal", "Car", "Per", "Cum", "Cmt", "Paz"][(now + timedelta(days=i)).weekday()],
            "hotel_guests": estimated_guests,
            "table_reservations": table_res,
            "breakfast": breakfast_servings,
            "lunch": lunch_estimate + table_res,
            "dinner": dinner_estimate + table_res,
            "total_meals": breakfast_servings + lunch_estimate + dinner_estimate + (table_res * 2),
        })

    return {
        "success": True,
        "forecast_days": days,
        "forecast": forecast,
    }


# ==================== OTOMASYON LOGLARI ====================

@router.get("/automation/logs")
async def get_automation_logs(log_type: Optional[str] = None, limit: int = 50):
    query = {"type": log_type} if log_type else {}
    logs = await db.automation_logs.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return {"logs": logs, "total": len(logs)}


@router.get("/automation/summary")
async def automation_summary():
    total_logs = await db.automation_logs.count_documents({})
    payment_reminders = await db.automation_logs.count_documents({"type": "payment_reminder"})
    cancellation_checks = await db.automation_logs.count_documents({"type": "cancellation_penalty"})
    breakfast_preps = await db.automation_logs.count_documents({"type": "breakfast_prep"})
    cleaning_notifications = await db.automation_logs.count_documents({"type": "checkout_cleaning"})
    morning_reminders = await db.automation_logs.count_documents({"type": {"$in": ["morning_toilet_reminder", "morning_checkin_reminder"]}})
    evening_checks = await db.automation_logs.count_documents({"type": "evening_room_check"})
    return {
        "total_logs": total_logs,
        "payment_reminders": payment_reminders,
        "cancellation_checks": cancellation_checks,
        "breakfast_preps": breakfast_preps,
        "cleaning_notifications": cleaning_notifications,
        "morning_reminders": morning_reminders,
        "evening_checks": evening_checks,
    }


# ==================== OPERASYONEL OTOMASYON ====================

@router.post("/automation/breakfast-notification")
async def run_breakfast_notification():
    """Kahvalti hazirligi bildirimini Celery ile tetikle"""
    breakfast_prep_task.delay()
    return {"success": True, "type": "breakfast_prep", "message": "Gorev kuyruga eklendi"}


@router.post("/automation/morning-reminders")
async def run_morning_reminders():
    """Sabah hatirlama mesajlarini Celery ile tetikle"""
    morning_reminders_task.delay()
    return {"success": True, "type": "morning_reminders", "message": "Gorev kuyruga eklendi"}


@router.post("/automation/cleaning-notification")
async def run_cleaning_notification():
    """Temizlik listesi bildirimini Celery ile tetikle"""
    checkout_cleaning_task.delay()
    return {"success": True, "type": "checkout_cleaning", "message": "Gorev kuyruga eklendi"}


@router.post("/automation/evening-room-check")
async def run_evening_room_check():
    """Aksam oda kontrolu bildirimini Celery ile tetikle"""
    evening_room_check_task.delay()
    return {"success": True, "type": "evening_room_check", "message": "Gorev kuyruga eklendi"}


@router.get("/automation/scheduled-jobs")
async def list_scheduled_jobs():
    """Celery beat zamanli gorevlerini getir"""
    from celery_app import celery_app as capp
    beat_schedule = capp.conf.beat_schedule or {}
    jobs = []
    for name, config in beat_schedule.items():
        schedule = config.get("schedule", {})
        if hasattr(schedule, 'hour') and hasattr(schedule, 'minute'):
            schedule_str = f"{schedule.hour}:{str(schedule.minute).zfill(2)}"
        else:
            schedule_str = str(schedule)
        jobs.append({
            "id": name,
            "name": name,
            "task": config.get("task", ""),
            "schedule": schedule_str,
            "status": "active",
        })
    return {"jobs": jobs, "total": len(jobs)}


    return {"notifications": notifications, "total": len(notifications)}


# ==================== PHASE 10: AI SÜRDÜRÜLEBİLİRLİK (GREEN HOTEL AI) ====================

@router.get("/automation/energy-ai")
async def get_energy_ai_report():
    """
    Otel dolulugunu ve kat bazli bos odalari analiz ederek 
    enerji tasarruf (klima kapatma, koridor isiklari) onerileri sunar.
    """
    try:
        from gemini_service import get_chat_response
        import random
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # 1. Tum odalari ve aktif rezervasyonlari cek
        rooms = await db.rooms.find({}, {"_id": 0, "id": 1, "floor": 1, "status": 1}).to_list(100)
        
        active_res = await db.reservations.find({
            "status": "checked_in",
            "check_in": {"$lte": now},
            "check_out": {"$gt": now}
        }, {"_id": 0, "room_id": 1}).to_list(100)
        occupied_room_ids = [r.get("room_id") for r in active_res if r.get("room_id")]

        # Kat bazli analiz
        floor_data = {}
        for r in rooms:
            floor = r.get("floor", "Zemin")
            if floor not in floor_data:
                floor_data[floor] = {"total": 0, "occupied": 0, "empty": 0}
            floor_data[floor]["total"] += 1
            if r.get("id") in occupied_room_ids:
                floor_data[floor]["occupied"] += 1
            else:
                floor_data[floor]["empty"] += 1

        # Ornek hava durumu verisi (Normalde dis API'den alinmali, simdilik mock)
        weather_conditions = ["Gunesli, 25C", "Bulutlu, 15C", "Hafif Yagmurlu, 12C", "Sicak, 32C"]
        current_weather = random.choice(weather_conditions)

        prompt = f"""
        Sen 'Green Hotel AI' adlı bir sürdürülebilirlik ve enerji tasarruf uzmanısın.
        Bugünün tarihi: {now} | Hava Durumu (Foça): {current_weather}
        
        Kat bazlı güncel doluluk oranları (Sadece 'occupied' olan odalarda misafir var):
        {json.dumps(floor_data, indent=2, ensure_ascii=False)}
        
        Görevlerin:
        1. Doluluk verilerini ve hava durumunu analiz et.
        2. Tamamen veya büyük oranda boş olan katlar için (örneğin X. kattaki koridor aydınlatmalarını 1/3 oranına düşürün, ortak alan klimalarını kapatın gibi) "Enerji Tasarruf Aksiyonları" belirle.
        3. Hava durumuna göre genel bina iklimlendirme (havuz ısıtması, genel lobi kliması vb.) tavsiyesi ver.
        
        Lutfen aşağıdaki JSON formatında don:
        {{
            "weather_context": "Disarisi 25C Gunesli oldugu icin...",
            "carbon_saving_estimate_kg": 15.5,
            "actions": [
                {{"title": "2. Kat Ortak Alanlar", "description": "2. Katta hic misafir yok, koridor ve lobi klimalarini tamamen kapatin.", "department": "teknik"}}
            ]
        }}
        """

        ai_resp = await get_chat_response("automation", new_id(), prompt)
        
        import re
        json_match = re.search(r'```(?:json)?(.*?)```', ai_resp, re.DOTALL)
        res_str = json_match.group(1).strip() if json_match else ai_resp
        report_data = json.loads(res_str)
        
        return {
            "success": True,
            "date": now,
            "weather": current_weather,
            "floor_occupancy": floor_data,
            "report": report_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Green AI Raporu olusturulamadi: {str(e)}")
