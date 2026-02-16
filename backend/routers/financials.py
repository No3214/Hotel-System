"""
Gelir/Gider Takip Modulu - Kozbeyli Konagi
Income/Expense CRUD, daily/monthly reports, KPI, commission reports.
"""
from fastapi import APIRouter, Query, Request
from typing import Optional
from datetime import date, datetime, timedelta, timezone
from database import db
from helpers import utcnow, new_id
import calendar

router = APIRouter(tags=["financials"])

TOTAL_ROOMS = 16

INCOME_CATEGORIES = [
    {"key": "room", "label": "Oda Geliri"},
    {"key": "restaurant", "label": "Restoran"},
    {"key": "bar", "label": "Bar"},
    {"key": "event", "label": "Etkinlik"},
    {"key": "minibar", "label": "Minibar"},
    {"key": "extra_service", "label": "Ekstra Hizmet"},
    {"key": "other", "label": "Diger"},
]

EXPENSE_CATEGORIES = [
    {"key": "food_supplies", "label": "Gida Malzemesi"},
    {"key": "beverages", "label": "Icecek"},
    {"key": "cleaning", "label": "Temizlik Malzemesi"},
    {"key": "energy", "label": "Elektrik/Su/Dogalgaz"},
    {"key": "salary", "label": "Maas"},
    {"key": "insurance", "label": "Sigorta"},
    {"key": "maintenance", "label": "Bakim/Onarim"},
    {"key": "marketing", "label": "Pazarlama"},
    {"key": "commission", "label": "OTA Komisyon"},
    {"key": "tax", "label": "Vergi"},
    {"key": "rent", "label": "Kira"},
    {"key": "equipment", "label": "Ekipman"},
    {"key": "laundry", "label": "Camasir"},
    {"key": "garden", "label": "Bahce Bakimi"},
    {"key": "entertainment", "label": "Eglence/Sanatci"},
    {"key": "software", "label": "Yazilim/Teknoloji"},
    {"key": "other", "label": "Diger"},
]


# ==================== CATEGORIES ====================

@router.get("/financials/categories")
async def get_categories():
    return {
        "income_categories": INCOME_CATEGORIES,
        "expense_categories": EXPENSE_CATEGORIES,
    }


# ==================== INCOME CRUD ====================

@router.post("/financials/income")
async def add_income(request: Request):
    body = await request.json()
    record = {
        "id": new_id(),
        "type": "income",
        "date": body.get("date", date.today().isoformat()),
        "category": body.get("category", "other"),
        "description": body.get("description", ""),
        "amount": float(body.get("amount", 0)),
        "source": body.get("source", "direct"),
        "reservation_id": body.get("reservation_id"),
        "commission_rate": float(body.get("commission_rate", 0)),
        "created_at": utcnow(),
    }

    # Calculate net amount after commission
    if record["commission_rate"] > 0:
        record["commission_amount"] = round(record["amount"] * record["commission_rate"] / 100, 2)
        record["net_amount"] = round(record["amount"] - record["commission_amount"], 2)
    else:
        record["commission_amount"] = 0
        record["net_amount"] = record["amount"]

    await db.financials.insert_one(record)
    return {"success": True, "id": record["id"], "message": "Gelir kaydedildi"}


@router.get("/financials/income")
async def list_income(
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=100),
):
    query = {"type": "income"}
    if date_from:
        query["date"] = {"$gte": date_from}
    if date_to:
        query.setdefault("date", {})["$lte"] = date_to
    if category:
        query["category"] = category

    records = await db.financials.find(query, {"_id": 0}).sort("date", -1).limit(limit).to_list(limit)
    return {"records": records, "total": len(records)}


# ==================== EXPENSE CRUD ====================

@router.post("/financials/expense")
async def add_expense(request: Request):
    body = await request.json()
    record = {
        "id": new_id(),
        "type": "expense",
        "date": body.get("date", date.today().isoformat()),
        "category": body.get("category", "other"),
        "description": body.get("description", ""),
        "amount": float(body.get("amount", 0)),
        "is_paid": body.get("is_paid", True),
        "vendor": body.get("vendor", ""),
        "created_at": utcnow(),
    }
    await db.financials.insert_one(record)
    return {"success": True, "id": record["id"], "message": "Gider kaydedildi"}


@router.get("/financials/expense")
async def list_expenses(
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=100),
):
    query = {"type": "expense"}
    if date_from:
        query["date"] = {"$gte": date_from}
    if date_to:
        query.setdefault("date", {})["$lte"] = date_to
    if category:
        query["category"] = category

    records = await db.financials.find(query, {"_id": 0}).sort("date", -1).limit(limit).to_list(limit)
    return {"records": records, "total": len(records)}


# ==================== DELETE ====================

@router.delete("/financials/{record_id}")
async def delete_financial_record(record_id: str):
    result = await db.financials.delete_one({"id": record_id})
    if result.deleted_count == 0:
        return {"success": False, "error": "Kayit bulunamadi"}
    return {"success": True, "message": "Kayit silindi"}


# ==================== DAILY SUMMARY ====================

@router.get("/financials/daily/{date_str}")
async def daily_summary(date_str: str):
    incomes = await db.financials.find(
        {"type": "income", "date": date_str}, {"_id": 0}
    ).to_list(500)
    expenses = await db.financials.find(
        {"type": "expense", "date": date_str}, {"_id": 0}
    ).to_list(500)

    total_income = sum(r.get("net_amount", r.get("amount", 0)) for r in incomes)
    total_expense = sum(r.get("amount", 0) for r in expenses)

    # Group by category
    income_by_cat = {}
    for r in incomes:
        cat = r.get("category", "other")
        income_by_cat[cat] = income_by_cat.get(cat, 0) + r.get("net_amount", r.get("amount", 0))

    expense_by_cat = {}
    for r in expenses:
        cat = r.get("category", "other")
        expense_by_cat[cat] = expense_by_cat.get(cat, 0) + r.get("amount", 0)

    return {
        "date": date_str,
        "income": {"total": round(total_income, 2), "by_category": income_by_cat, "count": len(incomes)},
        "expense": {"total": round(total_expense, 2), "by_category": expense_by_cat, "count": len(expenses)},
        "profit": round(total_income - total_expense, 2),
    }


# ==================== MONTHLY SUMMARY ====================

@router.get("/financials/monthly")
async def monthly_summary(
    year: int = Query(default=None),
    month: int = Query(default=None),
):
    if not year:
        year = date.today().year
    if not month:
        month = date.today().month

    days_in_month = calendar.monthrange(year, month)[1]
    date_from = f"{year}-{month:02d}-01"
    date_to = f"{year}-{month:02d}-{days_in_month}"

    incomes = await db.financials.find(
        {"type": "income", "date": {"$gte": date_from, "$lte": date_to}}, {"_id": 0}
    ).to_list(5000)
    expenses = await db.financials.find(
        {"type": "expense", "date": {"$gte": date_from, "$lte": date_to}}, {"_id": 0}
    ).to_list(5000)

    total_income = sum(r.get("net_amount", r.get("amount", 0)) for r in incomes)
    total_expense = sum(r.get("amount", 0) for r in expenses)
    gross_income = sum(r.get("amount", 0) for r in incomes)
    total_commission = sum(r.get("commission_amount", 0) for r in incomes)

    # Group by category
    income_by_cat = {}
    for r in incomes:
        cat = r.get("category", "other")
        income_by_cat[cat] = income_by_cat.get(cat, 0) + r.get("net_amount", r.get("amount", 0))

    expense_by_cat = {}
    for r in expenses:
        cat = r.get("category", "other")
        expense_by_cat[cat] = expense_by_cat.get(cat, 0) + r.get("amount", 0)

    # Source breakdown
    income_by_source = {}
    for r in incomes:
        src = r.get("source", "direct")
        if src not in income_by_source:
            income_by_source[src] = {"gross": 0, "commission": 0, "net": 0, "count": 0}
        income_by_source[src]["gross"] += r.get("amount", 0)
        income_by_source[src]["commission"] += r.get("commission_amount", 0)
        income_by_source[src]["net"] += r.get("net_amount", r.get("amount", 0))
        income_by_source[src]["count"] += 1

    # Daily trend
    daily_trend = []
    for day in range(1, days_in_month + 1):
        d = f"{year}-{month:02d}-{day:02d}"
        day_income = sum(r.get("net_amount", r.get("amount", 0)) for r in incomes if r.get("date") == d)
        day_expense = sum(r.get("amount", 0) for r in expenses if r.get("date") == d)
        daily_trend.append({"date": d, "income": round(day_income, 2), "expense": round(day_expense, 2)})

    # KPI
    reservations = await db.reservations.find({
        "check_in": {"$gte": date_from, "$lte": date_to},
        "status": {"$in": ["confirmed", "checked_in", "checked_out"]},
    }, {"_id": 0, "total_price": 1, "check_in": 1, "check_out": 1}).to_list(5000)

    occupied_nights = 0
    for r in reservations:
        try:
            ci = datetime.strptime(r.get("check_in", ""), "%Y-%m-%d")
            co = datetime.strptime(r.get("check_out", ""), "%Y-%m-%d")
            occupied_nights += max(0, (co - ci).days)
        except (ValueError, TypeError):
            pass

    total_room_nights = TOTAL_ROOMS * days_in_month
    occupancy = round(occupied_nights / total_room_nights * 100, 1) if total_room_nights > 0 else 0
    adr = round(total_income / occupied_nights) if occupied_nights > 0 else 0
    revpar = round(total_income / total_room_nights) if total_room_nights > 0 else 0
    profit_margin = round((total_income - total_expense) / total_income * 100, 1) if total_income > 0 else 0

    return {
        "period": f"{year}-{month:02d}",
        "income": {
            "gross": round(gross_income, 2),
            "net": round(total_income, 2),
            "commission": round(total_commission, 2),
            "by_category": income_by_cat,
            "by_source": income_by_source,
            "count": len(incomes),
        },
        "expense": {
            "total": round(total_expense, 2),
            "by_category": expense_by_cat,
            "count": len(expenses),
        },
        "profit": round(total_income - total_expense, 2),
        "profit_margin": profit_margin,
        "daily_trend": daily_trend,
        "kpis": {
            "occupancy_rate": occupancy,
            "adr": adr,
            "revpar": revpar,
            "total_reservations": len(reservations),
            "occupied_nights": occupied_nights,
            "total_room_nights": total_room_nights,
        },
    }
