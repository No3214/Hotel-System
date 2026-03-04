"""
HotelRunner API Service - Kozbeyli Konagi
Live API client with mock fallback.
Set HOTELRUNNER_TOKEN and HOTELRUNNER_HR_ID in .env to enable live mode.
"""
import httpx
import logging
import os
import asyncio
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

HR_BASE = "https://app.hotelrunner.com/api"
HR_TOKEN = os.environ.get("HOTELRUNNER_TOKEN", "")
HR_ID = os.environ.get("HOTELRUNNER_HR_ID", "")


def is_live():
    return bool(HR_TOKEN and HR_ID)


def _auth():
    return {"token": HR_TOKEN, "hr_id": HR_ID}


class HRClient:
    def __init__(self):
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        self._client = None

    def _get_client(self):
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def request(self, method, path, ver="v2", params=None, data=None):
        url = f"{HR_BASE}/{ver}/{path}"
        all_params = {**(params or {}), **_auth()}
        client = self._get_client()
        for attempt in range(3):
            try:
                kw = {"params": all_params}
                if method == "GET":
                    resp = await client.get(url, **kw)
                elif method == "PUT":
                    resp = await client.put(url, data=data, **kw)
                elif method == "POST":
                    resp = await client.post(url, data=data, **kw)
                else:
                    resp = await client.get(url, **kw)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                if attempt < 2 and e.response.status_code in (429, 500, 502, 503):
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
                raise
            except httpx.RequestError:
                if attempt < 2:
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
                raise
        return {}

    async def get(self, path, params=None, ver="v2"):
        return await self.request("GET", path, ver, params=params)

    async def put(self, path, data=None, ver="v2"):
        return await self.request("PUT", path, ver, data=data)


hr = HRClient()


# ===== ROOMS =====

async def get_rooms():
    if not is_live():
        return _mock_rooms()
    try:
        result = await hr.get("apps/rooms")
        return {"rooms": result.get("rooms", []), "live": True}
    except Exception as e:
        logger.error(f"HotelRunner get_rooms error: {e}")
        return {"rooms": [], "live": False, "error": str(e)}


async def update_availability(inv_code, start_date, end_date, availability,
                              channel_codes=None, price=None, min_stay=None,
                              stop_sale=None, days=None):
    if not is_live():
        return {"status": "ok", "transaction_id": "MOCK", "live": False}
    data = {
        "inv_code": inv_code,
        "start_date": start_date,
        "end_date": end_date,
        "availability": str(availability),
    }
    if channel_codes:
        for i, c in enumerate(channel_codes):
            data[f"channel_codes[{i}]"] = c
    if price:
        data["price"] = str(price)
    if min_stay:
        data["min_stay"] = str(min_stay)
    if stop_sale is not None:
        data["stop_sale"] = "1" if stop_sale else "0"
    if days:
        for i, d in enumerate(days):
            data[f"days[{i}]"] = str(d)
    try:
        result = await hr.put("apps/rooms/~", data=data, ver="v1")
        return {
            "status": result.get("status"),
            "transaction_id": result.get("transaction_id"),
            "live": True,
        }
    except Exception as e:
        logger.error(f"HotelRunner update_availability error: {e}")
        return {"status": "error", "message": str(e)}


async def get_transaction_details(transaction_id):
    """Get details of a specific HotelRunner transaction."""
    if not is_live():
        return {"transaction_id": transaction_id, "status": "mock", "live": False}
    try:
        result = await hr.get(f"apps/transactions/{transaction_id}")
        return {**result, "live": True}
    except Exception as e:
        logger.error(f"HotelRunner get_transaction error: {e}")
        return {"transaction_id": transaction_id, "status": "error", "message": str(e)}


# ===== RESERVATIONS =====

async def pull_reservations(page=1, per_page=25):
    if not is_live():
        return _mock_reservations()
    try:
        result = await hr.get("apps/reservations",
                              params={"page": str(page), "per_page": str(per_page)})
        return {"reservations": result.get("reservations", []), "live": True}
    except Exception as e:
        logger.error(f"HotelRunner pull_reservations error: {e}")
        return {"reservations": [], "live": False, "error": str(e)}


async def confirm_reservation(reservation_id):
    if not is_live():
        return {"status": "confirmed", "live": False}
    try:
        await hr.put(f"apps/reservations/{reservation_id}/confirm_delivery")
        return {"status": "confirmed", "live": True}
    except Exception as e:
        logger.error(f"HotelRunner confirm_reservation error: {e}")
        return {"status": "error", "message": str(e)}


# ===== CHANNELS =====

async def get_hr_channels():
    if not is_live():
        return {
            "channels": [
                {"code": "bookingcom", "name": "Booking.com"},
                {"code": "expedia", "name": "Expedia"},
                {"code": "online", "name": "HotelRunner Online"},
            ],
            "live": False,
        }
    try:
        result = await hr.get("apps/channels")
        return {"channels": result.get("channels", []), "live": True}
    except Exception as e:
        logger.error(f"HotelRunner get_channels error: {e}")
        return {"channels": [], "live": False}


# ===== SYNC =====

async def full_hr_sync():
    results = {"timestamp": datetime.now(timezone.utc).isoformat()}
    try:
        results["rooms"] = await get_rooms()
    except Exception as e:
        logger.error(f"full_hr_sync rooms failed: {e}")
        results["rooms"] = {"error": "failed"}
    try:
        results["reservations"] = await pull_reservations(per_page=50)
    except Exception as e:
        logger.error(f"full_hr_sync reservations failed: {e}")
        results["reservations"] = {"error": "failed"}
    return results


# ===== MOCK DATA =====

def _mock_rooms():
    return {
        "rooms": [
            {
                "rate_code": "HR:1", "inv_code": "HR:1",
                "name": "Standart 2 Kisilik Oda",
                "room_capacity": 2,
                "channel_codes": ["bookingcom", "online", "expedia"],
            },
            {
                "rate_code": "HR:2", "inv_code": "HR:2",
                "name": "Standart Bahce Manzarali Oda",
                "room_capacity": 2,
                "channel_codes": ["bookingcom", "online"],
            },
            {
                "rate_code": "HR:3", "inv_code": "HR:3",
                "name": "Standart Deniz Manzarali Oda",
                "room_capacity": 2,
                "channel_codes": ["bookingcom", "online", "expedia"],
            },
            {
                "rate_code": "HR:4", "inv_code": "HR:4",
                "name": "Uc Kisilik Oda",
                "room_capacity": 3,
                "channel_codes": ["bookingcom", "online"],
            },
            {
                "rate_code": "HR:5", "inv_code": "HR:5",
                "name": "4 Kisilik Aile Odasi",
                "room_capacity": 4,
                "channel_codes": ["bookingcom", "online", "expedia"],
            },
            {
                "rate_code": "HR:6", "inv_code": "HR:6",
                "name": "4 Kisilik Aile Odasi Balkonlu",
                "room_capacity": 4,
                "channel_codes": ["bookingcom", "online"],
            },
            {
                "rate_code": "HR:7", "inv_code": "HR:7",
                "name": "Superior 2 Kisilik Oda",
                "room_capacity": 2,
                "channel_codes": ["bookingcom", "online", "expedia"],
            },
            {
                "rate_code": "HR:8", "inv_code": "HR:8",
                "name": "Superior 3 Kisilik Oda",
                "room_capacity": 3,
                "channel_codes": ["bookingcom", "online"],
            },
        ],
        "total": 8,
        "live": False,
        "mock": True,
    }


def _mock_reservations():
    return {
        "reservations": [
            {
                "id": "MOCK-001",
                "guest_name": "Test Misafir",
                "channel_code": "bookingcom",
                "inv_code": "HR:1",
                "checkin": "2025-07-15",
                "checkout": "2025-07-18",
                "total_price": 7500.0,
                "status": "confirmed",
            },
        ],
        "total": 1,
        "live": False,
        "mock": True,
    }
