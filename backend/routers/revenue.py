from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import date, datetime, timedelta, timezone
from database import db
from helpers import utcnow, new_id
from hotel_data import ROOMS

router = APIRouter(tags=["revenue"])

# ==================== CONFIGURATION ====================

BASE_RATES = {
    "standart_deniz": 2500,
    "standart_kara": 2200,
    "superior": 3200,
    "uc_kisilik": 3500,
    "dort_kisilik": 4200,
}

SPECIAL_DAYS = {
    (1, 1): {"name": "Yilbasi", "factor": 1.50},
    (2, 14): {"name": "Sevgililer Gunu", "factor": 1.30},
    (4, 23): {"name": "Ulusal Egemenlik", "factor": 1.20},
    (5, 1): {"name": "Isci Bayrami", "factor": 1.20},
    (5, 19): {"name": "Genclik Bayrami", "factor": 1.20},
    (8, 30): {"name": "Zafer Bayrami", "factor": 1.30},
    (10, 29): {"name": "Cumhuriyet Bayrami", "factor": 1.20},
}

TOTAL_ROOMS = 16


# ==================== PRICING ENGINE ====================

def get_season_factor(target_date: date) -> dict:
    month = target_date.month
    if month in [6, 7, 8]:
        return {"season": "peak", "label": "Yuksek Sezon", "factor": 1.50}
    elif month in [5, 9]:
        return {"season": "high", "label": "Omuz Sezon", "factor": 1.25}
    elif month in [11, 12, 1, 2, 3]:
        return {"season": "low", "label": "Dusuk Sezon", "factor": 0.85}
    else:
        return {"season": "shoulder", "label": "Normal Sezon", "factor": 1.0}


def get_day_factor(target_date: date) -> dict:
    weekday = target_date.weekday()
    if weekday in [4, 5]:  # Friday, Saturday
        return {"is_weekend": True, "factor": 1.15}
    elif weekday == 6:
        return {"is_weekend": False, "factor": 1.0}
    else:
        return {"is_weekend": False, "factor": 0.95}


def get_special_day_factor(target_date: date) -> dict:
    key = (target_date.month, target_date.day)
    if key in SPECIAL_DAYS:
        return {"is_special": True, **SPECIAL_DAYS[key]}
    return {"is_special": False, "name": None, "factor": 1.0}


async def get_occupancy_factor(target_date: date) -> dict:
    date_str = target_date.isoformat()
    booked = await db.reservations.count_documents({
        "status": {"$in": ["confirmed", "checked_in"]},
        "check_in": {"$lte": date_str},
        "check_out": {"$gte": date_str},
    })
    occupancy = booked / TOTAL_ROOMS if TOTAL_ROOMS > 0 else 0

    if occupancy >= 0.95:
        factor = 1.50
    elif occupancy >= 0.85:
        factor = 1.30
    elif occupancy >= 0.70:
        factor = 1.15
    elif occupancy >= 0.50:
        factor = 1.0
    elif occupancy >= 0.30:
        factor = 0.85
    else:
        factor = 0.70

    return {"occupancy": round(occupancy * 100, 1), "factor": factor}


async def get_demand_factor(target_date: date) -> dict:
    days_until = (target_date - date.today()).days
    if days_until <= 0:
        return {"demand": "normal", "factor": 1.0}

    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    date_str = target_date.isoformat()
    recent_bookings = await db.reservations.count_documents({
        "check_in": date_str,
        "created_at": {"$gte": week_ago},
    })

    if recent_bookings >= 5:
        return {"demand": "very_high", "factor": 1.20}
    elif recent_bookings >= 3:
        return {"demand": "high", "factor": 1.10}
    elif recent_bookings >= 1:
        return {"demand": "normal", "factor": 1.0}
    else:
        return {"demand": "low", "factor": 0.95}


async def calculate_dynamic_price(room_type: str, target_date: date, base_price: float = None):
    if base_price is None:
        base_price = BASE_RATES.get(room_type, 2500)

    season = get_season_factor(target_date)
    day = get_day_factor(target_date)
    special = get_special_day_factor(target_date)
    occupancy = await get_occupancy_factor(target_date)
    demand = await get_demand_factor(target_date)

    total_multiplier = (
        season["factor"] * occupancy["factor"] * demand["factor"] * day["factor"] * special["factor"]
    )

    min_mult, max_mult = 0.7, 2.0
    raw_price = base_price * total_multiplier
    min_price = base_price * min_mult
    max_price = base_price * max_mult
    dynamic_price = max(min_price, min(raw_price, max_price))
    dynamic_price = round(dynamic_price / 50) * 50

    return {
        "room_type": room_type,
        "date": target_date.isoformat(),
        "base_price": base_price,
        "dynamic_price": dynamic_price,
        "currency": "TRY",
        "total_multiplier": round(total_multiplier, 3),
        "factors": {
            "season": {"label": season["label"], "value": season["factor"]},
            "occupancy": {"percent": occupancy["occupancy"], "value": occupancy["factor"]},
            "demand": {"level": demand["demand"], "value": demand["factor"]},
            "day": {"is_weekend": day["is_weekend"], "value": day["factor"]},
            "special_day": {"is_special": special["is_special"], "name": special["name"], "value": special["factor"]},
        },
        "limits": {"min": min_price, "max": max_price},
    }


# ==================== API ENDPOINTS ====================

@router.get("/revenue/pricing/calculate")
async def api_calculate_price(
    room_type: str = Query(...),
    target_date: date = Query(...),
    base_price: Optional[float] = Query(default=None),
):
    result = await calculate_dynamic_price(room_type, target_date, base_price)
    return result


@router.get("/revenue/pricing/calendar")
async def get_pricing_calendar(
    room_type: str = Query(...),
    date_from: date = Query(...),
    date_to: date = Query(...),
):
    prices = []
    current = date_from
    while current <= date_to:
        price_data = await calculate_dynamic_price(room_type, current)
        prices.append(price_data)
        current += timedelta(days=1)

    return {
        "room_type": room_type,
        "period": {"from": date_from.isoformat(), "to": date_to.isoformat()},
        "prices": prices,
        "summary": {
            "min_price": min(p["dynamic_price"] for p in prices) if prices else 0,
            "max_price": max(p["dynamic_price"] for p in prices) if prices else 0,
            "avg_price": round(sum(p["dynamic_price"] for p in prices) / len(prices)) if prices else 0,
        },
    }


@router.post("/revenue/pricing/update-all")
async def update_all_prices(days_ahead: int = Query(default=90)):
    updated = 0
    for i in range(days_ahead):
        target = date.today() + timedelta(days=i)
        for room_type, base in BASE_RATES.items():
            price_data = await calculate_dynamic_price(room_type, target, base)
            await db.dynamic_prices.update_one(
                {"room_type": room_type, "date": target.isoformat()},
                {"$set": {
                    "base_price": price_data["base_price"],
                    "dynamic_price": price_data["dynamic_price"],
                    "factors": price_data["factors"],
                    "total_multiplier": price_data["total_multiplier"],
                    "updated_at": utcnow(),
                }},
                upsert=True,
            )
            updated += 1
    return {"success": True, "updated": updated, "days_ahead": days_ahead, "room_types": len(BASE_RATES)}


@router.get("/revenue/pricing/rules")
async def get_pricing_rules():
    rules = await db.pricing_rules.find({}, {"_id": 0}).sort("priority", -1).to_list(100)
    return {"rules": rules}


@router.post("/revenue/pricing/rules")
async def create_pricing_rule(
    name: str = Query(...),
    room_type: Optional[str] = Query(default=None),
    adjustment_type: str = Query(...),
    adjustment_value: float = Query(...),
    priority: int = Query(default=0),
):
    rule = {
        "id": new_id(),
        "name": name,
        "room_type": room_type,
        "adjustment_type": adjustment_type,
        "adjustment_value": adjustment_value,
        "priority": priority,
        "is_active": True,
        "created_at": utcnow(),
    }
    await db.pricing_rules.insert_one(rule)
    del rule["_id"]
    return rule


@router.delete("/revenue/pricing/rules/{rule_id}")
async def delete_pricing_rule(rule_id: str):
    result = await db.pricing_rules.delete_one({"id": rule_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Kural bulunamadi")
    return {"success": True}


# ==================== FORECAST ====================

@router.get("/revenue/forecast")
async def get_revenue_forecast(
    date_from: date = Query(default=None),
    date_to: date = Query(default=None),
    room_type: Optional[str] = Query(default=None),
):
    if not date_from:
        date_from = date.today()
    if not date_to:
        date_to = date.today() + timedelta(days=30)

    forecasts = []
    total_revenue = 0

    current = date_from
    while current <= date_to:
        date_str = current.isoformat()
        booked = await db.reservations.count_documents({
            "status": {"$in": ["confirmed", "checked_in"]},
            "check_in": {"$lte": date_str},
            "check_out": {"$gte": date_str},
        })
        occupied = booked
        available = TOTAL_ROOMS - occupied

        # Get average dynamic price
        if room_type:
            pd = await calculate_dynamic_price(room_type, current)
            avg_rate = pd["dynamic_price"]
        else:
            rates = []
            for rt, base in BASE_RATES.items():
                pd = await calculate_dynamic_price(rt, current, base)
                rates.append(pd["dynamic_price"])
            avg_rate = round(sum(rates) / len(rates)) if rates else 2500

        confirmed_revenue = occupied * avg_rate
        potential_revenue = round(available * 0.4 * avg_rate)
        predicted_revenue = confirmed_revenue + potential_revenue
        predicted_occupancy = round((occupied + available * 0.4) / TOTAL_ROOMS * 100, 1)

        forecasts.append({
            "date": date_str,
            "occupied_rooms": occupied,
            "available_rooms": available,
            "predicted_occupancy": predicted_occupancy,
            "avg_rate": avg_rate,
            "confirmed_revenue": confirmed_revenue,
            "potential_revenue": potential_revenue,
            "predicted_revenue": predicted_revenue,
            "predicted_revpar": round(predicted_revenue / TOTAL_ROOMS),
        })
        total_revenue += predicted_revenue
        current += timedelta(days=1)

    days = len(forecasts)
    return {
        "period": {"from": date_from.isoformat(), "to": date_to.isoformat()},
        "total_predicted_revenue": total_revenue,
        "average_daily_revenue": round(total_revenue / days) if days else 0,
        "daily_forecasts": forecasts,
    }


# ==================== KPI ====================

@router.get("/revenue/kpi")
async def get_revenue_kpi(
    date_from: date = Query(default=None),
    date_to: date = Query(default=None),
):
    if not date_from:
        date_from = date.today() - timedelta(days=30)
    if not date_to:
        date_to = date.today()

    date_from_str = date_from.isoformat()
    date_to_str = date_to.isoformat()

    reservations = await db.reservations.find({
        "check_in": {"$gte": date_from_str, "$lte": date_to_str},
        "status": {"$in": ["confirmed", "checked_in", "checked_out"]},
    }, {"_id": 0}).to_list(1000)

    total_revenue = sum(r.get("total_price", 0) or 0 for r in reservations)
    total_nights = 0
    for r in reservations:
        try:
            ci = datetime.strptime(r.get("check_in", ""), "%Y-%m-%d")
            co = datetime.strptime(r.get("check_out", ""), "%Y-%m-%d")
            total_nights += (co - ci).days
        except (ValueError, TypeError):
            pass

    total_days = (date_to - date_from).days + 1
    total_room_nights = TOTAL_ROOMS * total_days

    adr = round(total_revenue / total_nights) if total_nights > 0 else 0
    revpar = round(total_revenue / total_room_nights) if total_room_nights > 0 else 0
    occupancy = round(total_nights / total_room_nights * 100, 1) if total_room_nights > 0 else 0

    # Previous period comparison
    prev_days = total_days
    prev_from = (date_from - timedelta(days=prev_days)).isoformat()
    prev_to = (date_from - timedelta(days=1)).isoformat()

    prev_reservations = await db.reservations.find({
        "check_in": {"$gte": prev_from, "$lte": prev_to},
        "status": {"$in": ["confirmed", "checked_in", "checked_out"]},
    }, {"_id": 0}).to_list(1000)
    prev_revenue = sum(r.get("total_price", 0) or 0 for r in prev_reservations)
    revenue_change = round((total_revenue - prev_revenue) / prev_revenue * 100, 1) if prev_revenue > 0 else 0

    return {
        "period": {"from": date_from_str, "to": date_to_str},
        "total_revenue": total_revenue,
        "total_nights": total_nights,
        "reservation_count": len(reservations),
        "adr": adr,
        "revpar": revpar,
        "occupancy_rate": occupancy,
        "revenue_change_percent": revenue_change,
        "base_rates": BASE_RATES,
    }


@router.get("/revenue/room-types")
async def get_room_types():
    return {"room_types": [{"key": k, "base_price": v} for k, v in BASE_RATES.items()]}
