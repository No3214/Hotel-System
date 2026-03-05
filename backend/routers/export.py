"""
Kozbeyli Konagi - Data Export & Backup Router
CSV export for reservations, guests, financials + DB backup endpoint.
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from database import db
from helpers import utcnow
import csv
import io
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["export"])


async def _require_admin(request: Request):
    from routers.auth import get_current_user
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(403, "Bu islem icin admin yetkisi gerekli")
    return user


def _make_csv_response(rows: list[dict], filename: str) -> StreamingResponse:
    """Convert a list of dicts to a CSV streaming response."""
    if not rows:
        output = io.StringIO()
        output.write("Veri bulunamadi\n")
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export/reservations")
async def export_reservations(request: Request):
    """Export all reservations as CSV"""
    await _require_admin(request)
    items = await db.reservations.find({}, {"_id": 0}).sort("check_in", -1).to_list(10000)
    logger.info(f"Reservations exported: {len(items)} records")
    return _make_csv_response(items, f"rezervasyonlar_{utcnow()[:10]}.csv")


@router.get("/export/guests")
async def export_guests(request: Request):
    """Export all guests as CSV"""
    await _require_admin(request)
    items = await db.guests.find({}, {"_id": 0}).sort("created_at", -1).to_list(10000)
    logger.info(f"Guests exported: {len(items)} records")
    return _make_csv_response(items, f"misafirler_{utcnow()[:10]}.csv")


@router.get("/export/financials")
async def export_financials(request: Request):
    """Export all financial records as CSV"""
    await _require_admin(request)
    incomes = await db.financials_income.find({}, {"_id": 0}).sort("date", -1).to_list(10000)
    expenses = await db.financials_expense.find({}, {"_id": 0}).sort("date", -1).to_list(10000)
    # Mark type
    for r in incomes:
        r["record_type"] = "income"
    for r in expenses:
        r["record_type"] = "expense"
    all_records = incomes + expenses
    logger.info(f"Financials exported: {len(all_records)} records")
    return _make_csv_response(all_records, f"finans_{utcnow()[:10]}.csv")


@router.get("/export/table-reservations")
async def export_table_reservations(request: Request):
    """Export all table reservations as CSV"""
    await _require_admin(request)
    items = await db.table_reservations.find({}, {"_id": 0}).sort("date", -1).to_list(10000)
    logger.info(f"Table reservations exported: {len(items)} records")
    return _make_csv_response(items, f"masa_rezervasyonlari_{utcnow()[:10]}.csv")


@router.get("/export/backup")
async def export_full_backup(request: Request):
    """Export full database backup as JSON"""
    await _require_admin(request)

    collections = [
        "reservations", "guests", "rooms", "table_reservations",
        "events", "staff", "housekeeping", "tasks", "messages",
        "financials_income", "financials_expense", "reviews",
        "social_media_posts", "organization_inquiries", "settings",
    ]

    backup = {"exported_at": utcnow(), "collections": {}}
    for col_name in collections:
        col = db[col_name]
        items = await col.find({}, {"_id": 0}).to_list(50000)
        backup["collections"][col_name] = items

    total = sum(len(v) for v in backup["collections"].values())
    logger.info(f"Full backup exported: {total} total records across {len(collections)} collections")

    output = io.StringIO()
    json.dump(backup, output, ensure_ascii=False, default=str)
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=backup_{utcnow()[:10]}.json"},
    )
