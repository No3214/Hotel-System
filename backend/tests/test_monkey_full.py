"""
Monkey Test - Kozbeyli Konagi Hotel System
Tests all critical API endpoints using mongomock (no real MongoDB needed).
"""
import os
os.environ["USE_MONGOMOCK"] = "true"
os.environ["ENVIRONMENT"] = "development"
os.environ["JWT_SECRET"] = "test-secret-key"
os.environ["RATE_LIMIT_ENABLED"] = "false"

import asyncio
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from httpx import AsyncClient, ASGITransport

PASS = 0
FAIL = 0
ERRORS = []


def result(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        ERRORS.append(f"{name}: {detail}")
        print(f"  [FAIL] {name} — {detail}")


async def run_tests():
    # Import after env vars set
    from server import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:

        # ==================== AUTH ====================
        print("\n=== AUTH ===")

        # Setup admin
        r = await c.post("/api/auth/setup")
        result("POST /auth/setup", r.status_code in (200, 409),
               f"status={r.status_code}")
        setup_data = r.json() if r.status_code == 200 else {}
        admin_password = setup_data.get("password", "")

        # Login with generated password
        r = await c.post("/api/auth/login", json={
            "username": "admin", "password": admin_password
        })
        result("POST /auth/login", r.status_code == 200, f"status={r.status_code}")
        token = r.json().get("token", "") if r.status_code == 200 else ""
        headers = {"Authorization": f"Bearer {token}"}

        # Get roles
        r = await c.get("/api/auth/roles")
        result("GET /auth/roles", r.status_code == 200, f"status={r.status_code}")

        # ==================== HEALTH & SEED ====================
        print("\n=== HEALTH & SEED ===")

        r = await c.get("/api/health")
        result("GET /health", r.status_code == 200, f"status={r.status_code}")
        if r.status_code == 200:
            data = r.json()
            result("  health.status", data.get("status") in ("healthy", "degraded"),
                   f"status={data.get('status')}")

        r = await c.post("/api/seed", headers=headers)
        result("POST /seed", r.status_code == 200, f"status={r.status_code}")

        # ==================== ROOMS ====================
        print("\n=== ROOMS ===")

        r = await c.get("/api/rooms", headers=headers)
        result("GET /rooms", r.status_code == 200, f"status={r.status_code}")
        if r.status_code == 200:
            rooms = r.json()
            room_list = rooms if isinstance(rooms, list) else rooms.get("rooms", [])
            result("  rooms.count == 8", len(room_list) == 8,
                   f"got {len(room_list)}")
            # Check room names
            names = [rm.get("name_tr", "") for rm in room_list]
            result("  has 'Superior 2 Kisilik Oda'",
                   any("Superior 2" in n for n in names), f"names={names}")
            result("  no old 'Superior Oda'",
                   not any(n == "Superior Oda" for n in names), f"names={names}")

        # ==================== HOTEL INFO ====================
        print("\n=== HOTEL ===")

        r = await c.get("/api/hotel/info")
        result("GET /hotel/info", r.status_code == 200, f"status={r.status_code}")
        if r.status_code == 200:
            info = r.json()
            result("  hotel.name", "Kozbeyli" in str(info.get("name", "")),
                   f"name={info.get('name')}")
            result("  total_rooms == 16", info.get("total_rooms") == 16,
                   f"got {info.get('total_rooms')}")

        # ==================== GUESTS ====================
        print("\n=== GUESTS ===")

        r = await c.post("/api/guests", headers=headers, json={
            "name": "Test Misafir", "email": "test@test.com",
            "phone": "+905001112233", "nationality": "TR"
        })
        result("POST /guests", r.status_code in (200, 201), f"status={r.status_code}")
        guest_id = r.json().get("id", "") if r.status_code in (200, 201) else ""

        r = await c.get("/api/guests", headers=headers)
        result("GET /guests", r.status_code == 200, f"status={r.status_code}")

        # ==================== RESERVATIONS ====================
        print("\n=== RESERVATIONS ===")

        r = await c.post("/api/reservations", headers=headers, json={
            "guest_name": "Test Misafir", "guest_id": guest_id or "test-guest",
            "room_id": "standart", "room_type": "standart",
            "check_in": "2026-04-01", "check_out": "2026-04-03",
            "adults": 2, "children": 0, "total_price": 7000,
            "status": "confirmed", "source": "direct"
        })
        result("POST /reservations", r.status_code in (200, 201),
               f"status={r.status_code}")
        res_id = r.json().get("id", "") if r.status_code in (200, 201) else ""

        r = await c.get("/api/reservations", headers=headers)
        result("GET /reservations", r.status_code == 200, f"status={r.status_code}")

        # ==================== TASKS ====================
        print("\n=== TASKS ===")

        r = await c.post("/api/tasks", headers=headers, json={
            "title": "Test Gorev", "description": "Test aciklama",
            "priority": "normal", "source": "manual"
        })
        result("POST /tasks", r.status_code in (200, 201), f"status={r.status_code}")

        r = await c.get("/api/tasks", headers=headers)
        result("GET /tasks", r.status_code == 200, f"status={r.status_code}")

        # ==================== EVENTS ====================
        print("\n=== EVENTS ===")

        r = await c.get("/api/events", headers=headers)
        result("GET /events", r.status_code == 200, f"status={r.status_code}")

        # ==================== HOUSEKEEPING ====================
        print("\n=== HOUSEKEEPING ===")

        r = await c.get("/api/housekeeping", headers=headers)
        result("GET /housekeeping", r.status_code == 200, f"status={r.status_code}")

        # ==================== STAFF ====================
        print("\n=== STAFF ===")

        r = await c.get("/api/staff", headers=headers)
        result("GET /staff", r.status_code == 200, f"status={r.status_code}")

        # ==================== KNOWLEDGE ====================
        print("\n=== KNOWLEDGE ===")

        r = await c.get("/api/knowledge", headers=headers)
        result("GET /knowledge", r.status_code == 200, f"status={r.status_code}")

        # ==================== MESSAGES ====================
        print("\n=== MESSAGES ===")

        r = await c.get("/api/messages", headers=headers)
        result("GET /messages", r.status_code == 200, f"status={r.status_code}")

        # ==================== REVIEWS ====================
        print("\n=== REVIEWS ===")

        r = await c.get("/api/reviews", headers=headers)
        result("GET /reviews", r.status_code == 200, f"status={r.status_code}")

        # ==================== PRICING ====================
        print("\n=== PRICING ===")

        r = await c.get("/api/pricing/seasons", headers=headers)
        result("GET /pricing/seasons", r.status_code == 200, f"status={r.status_code}")

        # ==================== HOTELRUNNER ====================
        print("\n=== HOTELRUNNER ===")

        r = await c.get("/api/hotelrunner/status", headers=headers)
        result("GET /hotelrunner/status", r.status_code == 200,
               f"status={r.status_code}")
        if r.status_code == 200:
            hr = r.json()
            result("  mode == mock", hr.get("mode") == "mock", f"mode={hr.get('mode')}")
            result("  mock_mode == True", hr.get("mock_mode") is True,
                   f"mock_mode={hr.get('mock_mode')}")

        r = await c.get("/api/hotelrunner/rooms", headers=headers)
        result("GET /hotelrunner/rooms", r.status_code == 200,
               f"status={r.status_code}")
        if r.status_code == 200:
            hr_rooms = r.json()
            result("  mock rooms == 8", len(hr_rooms.get("rooms", [])) == 8,
                   f"got {len(hr_rooms.get('rooms', []))}")

        r = await c.get("/api/hotelrunner/channels", headers=headers)
        result("GET /hotelrunner/channels", r.status_code == 200,
               f"status={r.status_code}")

        r = await c.get("/api/hotelrunner/config", headers=headers)
        result("GET /hotelrunner/config", r.status_code == 200,
               f"status={r.status_code}")

        r = await c.get("/api/hotelrunner/sync-logs", headers=headers)
        result("GET /hotelrunner/sync-logs", r.status_code == 200,
               f"status={r.status_code}")

        r = await c.post("/api/hotelrunner/sync/reservations", headers=headers)
        result("POST /hotelrunner/sync/reservations", r.status_code == 200,
               f"status={r.status_code}")

        r = await c.post("/api/hotelrunner/sync/availability", headers=headers)
        result("POST /hotelrunner/sync/availability", r.status_code == 200,
               f"status={r.status_code}")

        r = await c.post("/api/hotelrunner/sync/rates", headers=headers)
        result("POST /hotelrunner/sync/rates", r.status_code == 200,
               f"status={r.status_code}")

        r = await c.post("/api/hotelrunner/sync/full", headers=headers)
        result("POST /hotelrunner/sync/full", r.status_code == 200,
               f"status={r.status_code}")

        r = await c.get("/api/hotelrunner/reservations", headers=headers)
        result("GET /hotelrunner/reservations", r.status_code == 200,
               f"status={r.status_code}")

        r = await c.get("/api/hotelrunner/transactions/MOCK-TX-1", headers=headers)
        result("GET /hotelrunner/transactions/{tid}", r.status_code == 200,
               f"status={r.status_code}")

        r = await c.put("/api/hotelrunner/rooms/availability", headers=headers,
                        json={"inv_code": "HR:1", "start_date": "2026-04-01",
                              "end_date": "2026-04-02", "availability": 2})
        result("PUT /hotelrunner/rooms/availability", r.status_code == 200,
               f"status={r.status_code}")

        r = await c.put("/api/hotelrunner/reservations/MOCK-001/confirm",
                        headers=headers)
        result("PUT /hotelrunner/reservations/{rid}/confirm",
               r.status_code == 200, f"status={r.status_code}")

        # Cancellation penalty
        r = await c.post("/api/hotelrunner/cancellation-penalty", headers=headers,
                         json={"check_in": "2026-04-01", "total_price": 7000})
        result("POST /hotelrunner/cancellation-penalty", r.status_code == 200,
               f"status={r.status_code}")

        # Webhook (public - no auth)
        r = await c.post("/api/hotelrunner/webhook", json={
            "event_type": "reservation.created",
            "data": {"reservation": {
                "id": "HR-TEST-1", "guest_name": "Webhook Test",
                "checkin_date": "2026-05-01", "checkout_date": "2026-05-03",
                "total_price": 5000, "status": "new"
            }}
        })
        result("POST /hotelrunner/webhook", r.status_code == 200,
               f"status={r.status_code}")

        # ==================== DASHBOARD ====================
        print("\n=== DASHBOARD ===")

        r = await c.get("/api/dashboard/stats", headers=headers)
        result("GET /dashboard/stats", r.status_code == 200,
               f"status={r.status_code}")
        if r.status_code == 200:
            stats = r.json()
            result("  total_rooms == 16", stats.get("total_rooms") == 16,
                   f"got {stats.get('total_rooms')}")
            result("  has rooms_list", isinstance(stats.get("rooms_list"), list),
                   f"type={type(stats.get('rooms_list'))}")
            room_names = [r.get("name_tr", "") for r in stats.get("rooms_list", [])]
            result("  rooms_list has 8 types",
                   len(stats.get("rooms_list", [])) == 8,
                   f"got {len(stats.get('rooms_list', []))}")
            result("  no old 'Superior Oda' in dashboard",
                   "Superior Oda" not in room_names,
                   f"names={room_names}")

        # ==================== SETTINGS ====================
        print("\n=== SETTINGS ===")

        r = await c.get("/api/i18n?lang=tr")
        result("GET /i18n?lang=tr", r.status_code == 200, f"status={r.status_code}")

        # ==================== ANALYTICS ====================
        print("\n=== ANALYTICS ===")

        r = await c.get("/api/analytics/dashboard/kpi", headers=headers)
        result("GET /analytics/dashboard/kpi", r.status_code == 200,
               f"status={r.status_code}")

        # ==================== FINANCIALS ====================
        print("\n=== FINANCIALS ===")

        r = await c.get("/api/financials/monthly", headers=headers)
        result("GET /financials/monthly", r.status_code == 200,
               f"status={r.status_code}")

        # ==================== AUTOMATION ====================
        print("\n=== AUTOMATION ===")

        r = await c.get("/api/automation/summary", headers=headers)
        result("GET /automation/summary", r.status_code == 200,
               f"status={r.status_code}")

        # ==================== LOYALTY ====================
        print("\n=== LOYALTY ===")

        r = await c.get("/api/loyalty/levels", headers=headers)
        result("GET /loyalty/levels", r.status_code == 200,
               f"status={r.status_code}")

        # ==================== CAMPAIGNS ====================
        print("\n=== CAMPAIGNS ===")

        r = await c.get("/api/campaigns", headers=headers)
        result("GET /campaigns", r.status_code == 200, f"status={r.status_code}")

        # ==================== NOTIFICATIONS ====================
        print("\n=== NOTIFICATIONS ===")

        r = await c.get("/api/notifications/today", headers=headers)
        result("GET /notifications/today", r.status_code == 200,
               f"status={r.status_code}")

        # ==================== AUDIT ====================
        print("\n=== AUDIT ===")

        r = await c.get("/api/audit/stats", headers=headers)
        result("GET /audit/stats", r.status_code == 200, f"status={r.status_code}")

        # ==================== EDGE CASES ====================
        print("\n=== EDGE CASES ===")

        # Invalid auth
        r = await c.get("/api/rooms", headers={"Authorization": "Bearer INVALID"})
        result("Invalid token → 401", r.status_code == 401,
               f"status={r.status_code}")

        # Missing auth
        r = await c.get("/api/rooms")
        result("No auth → 401", r.status_code == 401, f"status={r.status_code}")

        # 404 endpoint
        r = await c.get("/api/nonexistent", headers=headers)
        result("Nonexistent → 404", r.status_code == 404,
               f"status={r.status_code}")

        # Invalid reservation data
        r = await c.post("/api/reservations", headers=headers, json={})
        result("Empty reservation → error", r.status_code in (400, 422, 500),
               f"status={r.status_code}")

    # ==================== SUMMARY ====================
    print(f"\n{'='*50}")
    print(f"MONKEY TEST RESULTS: {PASS} passed, {FAIL} failed")
    print(f"{'='*50}")
    if ERRORS:
        print("\nFailed tests:")
        for e in ERRORS:
            print(f"  - {e}")
    return FAIL


if __name__ == "__main__":
    exit_code = asyncio.run(run_tests())
    sys.exit(1 if exit_code > 0 else 0)
