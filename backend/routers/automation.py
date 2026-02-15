from fastapi import APIRouter
from typing import Optional
from database import db
from helpers import utcnow, new_id
from datetime import datetime, timedelta, timezone
from hotel_data import HOTEL_POLICIES
from scheduler import (
    breakfast_prep_job,
    morning_reminders_job,
    checkout_cleaning_job,
    get_scheduled_jobs,
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
    return {
        "total_logs": total_logs,
        "payment_reminders": payment_reminders,
        "cancellation_checks": cancellation_checks,
    }
