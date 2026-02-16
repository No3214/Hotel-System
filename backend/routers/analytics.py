from fastapi import APIRouter, Query
from typing import Optional
from datetime import date, datetime, timedelta, timezone
from database import db
from helpers import utcnow
from services.cache_service import cache_get, cache_set

router = APIRouter(tags=["analytics"])

TOTAL_ROOMS = 16
MONTH_NAMES_TR = ["", "Oca", "Sub", "Mar", "Nis", "May", "Haz", "Tem", "Agu", "Eyl", "Eki", "Kas", "Ara"]


async def calc_revenue(date_from: str, date_to: str) -> float:
    reservations = await db.reservations.find({
        "check_in": {"$gte": date_from, "$lte": date_to},
        "status": {"$in": ["confirmed", "checked_in", "checked_out"]},
    }, {"_id": 0, "total_price": 1}).to_list(5000)
    return sum(r.get("total_price", 0) or 0 for r in reservations)


async def calc_occupancy(date_from: str, date_to: str) -> float:
    try:
        d_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        d_to = datetime.strptime(date_to, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return 0

    total_days = (d_to - d_from).days + 1
    total_room_nights = TOTAL_ROOMS * total_days
    if total_room_nights <= 0:
        return 0

    reservations = await db.reservations.find({
        "check_in": {"$lte": date_to},
        "check_out": {"$gte": date_from},
        "status": {"$in": ["confirmed", "checked_in", "checked_out"]},
    }, {"_id": 0, "check_in": 1, "check_out": 1}).to_list(5000)

    occupied_nights = 0
    for r in reservations:
        try:
            ci = max(datetime.strptime(r["check_in"], "%Y-%m-%d").date(), d_from)
            co = min(datetime.strptime(r["check_out"], "%Y-%m-%d").date(), d_to)
            nights = (co - ci).days
            if nights > 0:
                occupied_nights += nights
        except (ValueError, TypeError, KeyError):
            pass

    return occupied_nights / total_room_nights


async def calc_sold_nights(date_from: str, date_to: str) -> int:
    reservations = await db.reservations.find({
        "check_in": {"$gte": date_from, "$lte": date_to},
        "status": {"$in": ["confirmed", "checked_in", "checked_out"]},
    }, {"_id": 0, "check_in": 1, "check_out": 1}).to_list(5000)

    total = 0
    for r in reservations:
        try:
            ci = datetime.strptime(r["check_in"], "%Y-%m-%d")
            co = datetime.strptime(r["check_out"], "%Y-%m-%d")
            total += (co - ci).days
        except (ValueError, TypeError, KeyError):
            pass
    return total


# ==================== KPI DASHBOARD ====================

@router.get("/analytics/dashboard/kpi")
async def get_kpi_metrics(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
):
    if not date_from:
        date_from = date.today()
    if not date_to:
        date_to = date.today()

    df_str = date_from.isoformat()
    dt_str = date_to.isoformat()

    daily_revenue = await calc_revenue(df_str, dt_str)
    occupancy_rate = await calc_occupancy(df_str, dt_str)
    sold_nights = await calc_sold_nights(df_str, dt_str)
    adr = round(daily_revenue / sold_nights) if sold_nights > 0 else 0

    total_days = (date_to - date_from).days + 1
    total_room_nights = TOTAL_ROOMS * total_days
    revpar = round(daily_revenue / total_room_nights) if total_room_nights > 0 else 0

    # Previous period
    prev_days = total_days
    prev_from = (date_from - timedelta(days=prev_days)).isoformat()
    prev_to = (date_from - timedelta(days=1)).isoformat()
    prev_revenue = await calc_revenue(prev_from, prev_to)
    revenue_change = round((daily_revenue - prev_revenue) / prev_revenue * 100, 1) if prev_revenue > 0 else 0

    prev_occupancy = await calc_occupancy(prev_from, prev_to)
    occ_change = round((occupancy_rate - prev_occupancy) * 100, 1)

    return {
        "period": {"from": df_str, "to": dt_str},
        "daily_revenue": {
            "value": round(daily_revenue, 2),
            "currency": "TRY",
            "change_percent": revenue_change,
            "trend": "up" if revenue_change >= 0 else "down",
        },
        "occupancy_rate": {
            "value": round(occupancy_rate * 100, 1),
            "change_percent": occ_change,
            "trend": "up" if occ_change >= 0 else "down",
        },
        "adr": {
            "value": adr,
            "currency": "TRY",
            "change_percent": 0,
            "trend": "up",
        },
        "revpar": {
            "value": revpar,
            "currency": "TRY",
            "change_percent": 0,
            "trend": "up",
        },
    }


# ==================== REVENUE TREND ====================

@router.get("/analytics/revenue/trend")
async def get_revenue_trend(period: str = Query(default="30d")):
    days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = days_map.get(period, 30)

    data = []
    for i in range(days):
        day = date.today() - timedelta(days=days - i - 1)
        day_str = day.isoformat()
        revenue = await calc_revenue(day_str, day_str)
        data.append({"date": day_str, "revenue": round(revenue, 2)})

    total = sum(d["revenue"] for d in data)
    return {
        "period": period,
        "data": data,
        "total": round(total, 2),
        "average": round(total / len(data), 2) if data else 0,
    }


# ==================== BOOKING SOURCES ====================

@router.get("/analytics/bookings/sources")
async def get_booking_sources(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
):
    if not date_from:
        date_from = date.today() - timedelta(days=30)
    if not date_to:
        date_to = date.today()

    reservations = await db.reservations.find({
        "created_at": {"$gte": date_from.isoformat(), "$lte": date_to.isoformat() + "T23:59:59"},
    }, {"_id": 0, "source": 1, "total_price": 1}).to_list(5000)

    sources_data = {}
    for r in reservations:
        source = r.get("source", "direct") or "direct"
        if source not in sources_data:
            sources_data[source] = {"count": 0, "revenue": 0}
        sources_data[source]["count"] += 1
        sources_data[source]["revenue"] += r.get("total_price", 0) or 0

    # Add default sources if empty
    if not sources_data:
        sources_data = {
            "direct": {"count": 0, "revenue": 0},
            "booking.com": {"count": 0, "revenue": 0},
            "hotelrunner": {"count": 0, "revenue": 0},
            "walk-in": {"count": 0, "revenue": 0},
        }

    total_bookings = max(sum(s["count"] for s in sources_data.values()), 1)
    total_revenue = max(sum(s["revenue"] for s in sources_data.values()), 1)

    sources = []
    for name, data in sources_data.items():
        sources.append({
            "name": name,
            "bookings": data["count"],
            "bookings_percent": round(data["count"] / total_bookings * 100, 1),
            "revenue": round(data["revenue"], 2),
            "revenue_percent": round(data["revenue"] / total_revenue * 100, 1),
        })

    sources.sort(key=lambda x: x["revenue"], reverse=True)
    return {"total_bookings": total_bookings, "total_revenue": round(total_revenue, 2), "sources": sources}


# ==================== OCCUPANCY HEATMAP ====================

@router.get("/analytics/occupancy/heatmap")
async def get_occupancy_heatmap(year: Optional[int] = Query(default=None)):
    if not year:
        year = date.today().year

    heatmap = []
    for month in range(1, 13):
        month_data = []
        for day in range(1, 32):
            try:
                current_date = date(year, month, day)
            except ValueError:
                break

            date_str = current_date.isoformat()
            booked = await db.reservations.count_documents({
                "check_in": {"$lte": date_str},
                "check_out": {"$gte": date_str},
                "status": {"$in": ["confirmed", "checked_in", "checked_out"]},
            })
            occupancy = round(booked / TOTAL_ROOMS * 100, 1)
            if occupancy >= 80:
                level = "high"
            elif occupancy >= 60:
                level = "medium"
            elif occupancy >= 40:
                level = "low"
            else:
                level = "critical"

            month_data.append({"day": day, "occupancy": occupancy, "level": level})

        heatmap.append({
            "month": month,
            "month_name": MONTH_NAMES_TR[month],
            "days": month_data,
        })

    return {"year": year, "heatmap": heatmap}


# ==================== ROOM PERFORMANCE ====================

@router.get("/analytics/rooms/performance")
async def get_room_performance(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
):
    if not date_from:
        date_from = date.today() - timedelta(days=30)
    if not date_to:
        date_to = date.today()

    rooms = await db.rooms.find({}, {"_id": 0}).to_list(100)
    performance = []

    for room in rooms:
        room_id = room.get("room_id") or room.get("id")
        bookings = await db.reservations.find({
            "room_id": room_id,
            "check_in": {"$gte": date_from.isoformat()},
            "check_out": {"$lte": date_to.isoformat()},
        }, {"_id": 0}).to_list(500)

        total_nights = 0
        total_revenue = 0
        for b in bookings:
            try:
                ci = datetime.strptime(b["check_in"], "%Y-%m-%d")
                co = datetime.strptime(b["check_out"], "%Y-%m-%d")
                total_nights += (co - ci).days
            except (ValueError, TypeError, KeyError):
                pass
            total_revenue += b.get("total_price", 0) or 0

        available_nights = (date_to - date_from).days + 1
        occupancy = round(total_nights / available_nights * 100, 1) if available_nights > 0 else 0

        performance.append({
            "room_id": room_id,
            "room_name": room.get("name_tr", room.get("name", "")),
            "room_type": room.get("type", ""),
            "bookings_count": len(bookings),
            "total_nights": total_nights,
            "occupancy_rate": occupancy,
            "total_revenue": round(total_revenue, 2),
            "adr": round(total_revenue / total_nights) if total_nights > 0 else 0,
        })

    performance.sort(key=lambda x: x["total_revenue"], reverse=True)
    return {
        "period": {"from": date_from.isoformat(), "to": date_to.isoformat()},
        "rooms": performance,
    }


# ==================== GUEST SATISFACTION ====================

@router.get("/analytics/guests/satisfaction")
async def get_guest_satisfaction(period: str = Query(default="30d")):
    days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = days_map.get(period, 30)
    cutoff = (date.today() - timedelta(days=days)).isoformat()

    reviews = await db.reviews.find({
        "created_at": {"$gte": cutoff},
    }, {"_id": 0}).to_list(1000)

    if not reviews:
        return {
            "overall_rating": 0,
            "total_reviews": 0,
            "rating_distribution": {5: 0, 4: 0, 3: 0, 2: 0, 1: 0},
            "monthly_trend": [],
        }

    avg_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews)
    distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews:
        rating = r.get("rating", 0)
        if rating in distribution:
            distribution[rating] += 1

    return {
        "overall_rating": round(avg_rating, 2),
        "total_reviews": len(reviews),
        "rating_distribution": distribution,
        "monthly_trend": [],
    }
