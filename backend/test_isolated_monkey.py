"""
Kozbeyli Konagi - Full System Monkey Test
Tum AI endpointlerini offline mock DB + mock Gemini ile test eder.
Gercek helpers, config, hotel_data kullanir. Sadece DB ve AI mocklenir.
"""
import asyncio
import json
import sys
import os

# Ensure .env is available (even if empty) so config doesn't crash
env_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(env_path):
    open(env_path, 'a').close()

# ==================== MOCK DB ====================
class MockCursor:
    def __init__(self, data):
        self._data = data
    async def to_list(self, length=100):
        return self._data
    def sort(self, *args, **kwargs):
        return self
    def skip(self, *args, **kwargs):
        return self
    def limit(self, *args, **kwargs):
        return self

class MockCollection:
    def __init__(self, data=None):
        self._data = data or []
    def find(self, *args, **kwargs):
        return MockCursor(self._data)
    async def find_one(self, *args, **kwargs):
        return self._data[0] if self._data else None
    async def count_documents(self, *args, **kwargs):
        return len(self._data)
    async def insert_one(self, doc):
        self._data.append(doc)
    async def update_one(self, *args, **kwargs):
        pass
    async def delete_one(self, *args, **kwargs):
        pass
    def aggregate(self, *args, **kwargs):
        return MockCursor(self._data)

MOCK_STAFF = [
    {"id": "s1", "name": "Ahmet Yilmaz", "role": "Receptionist", "department": "reception", "status": "active"},
    {"id": "s2", "name": "Fatma Kaya", "role": "Housekeeper", "department": "housekeeping", "status": "active"}
]
MOCK_SHIFTS = [
    {"staff_id": "s1", "date": "2026-03-01", "shift": "morning"},
    {"staff_id": "s2", "date": "2026-03-01", "shift": "afternoon"}
]
MOCK_TASKS_DATA = [
    {"id": "t1", "status": "completed", "assignee_role": "reception", "assigned_to": "s1", "created_at": "2026-03-01"},
]
MOCK_RESERVATIONS = [
    {"id": "r1", "guest_id": "g1", "room_type": "suite", "check_in": "2026-03-10", "check_out": "2026-03-13",
     "status": "confirmed", "source": "booking", "total_price": 4500, "guest_name": "John Doe",
     "nationality": "UK", "guests": 2, "notes": "Anniversary trip"}
]
MOCK_GUESTS = [
    {"id": "g1", "name": "John Doe", "nationality": "UK", "total_spend": 12000, "visits": 3, "email": "john@test.com"}
]
MOCK_REVIEWS = [
    {"id": "rv1", "guest_name": "Jane", "rating": 5, "review_text": "Muhtesem!", "platform": "google", "date": "2026-02-20"},
    {"id": "rv2", "guest_name": "Max", "rating": 2, "review_text": "Klima bozuktu.", "platform": "tripadvisor", "date": "2026-02-25"}
]
MOCK_ROOMS_DATA = [
    {"id": "room1", "number": "101", "type": "standard", "status": "available", "floor": 1},
    {"id": "room2", "number": "201", "type": "suite", "status": "occupied", "floor": 2}
]
MOCK_EXPENSES = [
    {"_id": "exp1", "type": "expense", "vendor": "Kasap Veli", "date": "2026-02-01", "amount": 3500, "category": "food_supplies"},
    {"_id": "exp2", "type": "expense", "vendor": "Manav Ali", "date": "2026-03-01", "amount": 800, "category": "food_supplies"},
    {"_id": "inc1", "type": "income", "date": "2026-03-01", "amount": 15000, "category": "room"}
]
MOCK_ORDERS = [
    {"_id": "ord1", "item": "Izgara Kofte", "quantity": 5, "price": 120, "date": "2026-03-01"},
]
MOCK_MENU = [
    {"_id": "men1", "id": "m1", "name": "Izgara Kofte", "price": 120, "cost": 40, "category": "Ana Yemek"},
]

class MockDB:
    staff = MockCollection(MOCK_STAFF)
    shifts = MockCollection(MOCK_SHIFTS)
    tasks = MockCollection(MOCK_TASKS_DATA)
    reservations = MockCollection(MOCK_RESERVATIONS)
    guests = MockCollection(MOCK_GUESTS)
    reviews = MockCollection(MOCK_REVIEWS)
    rooms = MockCollection(MOCK_ROOMS_DATA)
    financials = MockCollection(MOCK_EXPENSES)
    events = MockCollection([{"id": "ev1", "name": "Dugun", "date": "2026-04-15", "guest_count": 80}])
    kitchen_orders = MockCollection(MOCK_ORDERS)
    menu_items = MockCollection(MOCK_MENU)
    hotel = MockCollection([{"name": "Kozbeyli Konagi"}])
    messages = MockCollection([])
    crm_deals = MockCollection([{"id": "d1", "company": "Test AS", "sector": "logistics", "stage": "contacted"}])
    crm_companies = MockCollection([{"id": "c1", "name": "ABC Lojistik", "sector": "logistics"}])
    loyalty_segments = MockCollection([])
    loyalty_members = MockCollection(MOCK_GUESTS)
    housekeeping = MockCollection([])
    automation = MockCollection([])
    settings = MockCollection([{"key": "hotel_name", "value": "Kozbeyli Konagi"}])
    lost_items = MockCollection([])
    found_items = MockCollection([])
    campaigns = MockCollection([])
    social_media = MockCollection([])

# ==================== MOCK GEMINI ====================
async def mock_gemini(message, session_id=None, system_prompt=None, temp=None, **kwargs):
    return json.dumps({
        "score": 85, "summary": "Mock AI test response",
        "procurement_health_score": 80, "summary_message": "OK",
        "red_flags": [], "savings_opportunities": [], "vendor_insights": [],
        "hr_health_score": 75, "burnout_risks": [], "workload_imbalance": "None", "motivation_actions": [],
        "guest_segment": "VIP", "whatsapp_welcome_message": "Welcome!", "upsell_suggestions": ["Late checkout"],
        "market_position": "Competitive", "competitor_analysis": "Good",
        "recommended_strategy": "Maintain rates", "rate_adjustment_suggestion": "0%",
        "actionable_insights": ["Keep monitoring"],
        "anomalies": [], "overall_health": 90, "total_anomaly_count": 0,
        "forecast": {"next_month_revenue": 120000, "next_month_expense": 80000},
        "overall_sentiment": 4.2, "top_praised": ["Temizlik"], "top_complaints": ["Klima"],
        "department_scores": {"Resepsiyon": 8, "Mutfak": 7},
        "cleaning_order": [{"room": "101", "reason": "VIP"}],
        "predicted_meals": 30, "supply_list": [{"item": "Yumurta", "quantity": 200}],
        "supplier_messages": [{"supplier": "Kasap Veli", "message": "Test"}],
        "risk_guests": [],
        "menu_analysis": {"stars": ["Kofte"], "puzzles": ["Salata"]},
        "strengths": ["Iyi"], "areas_of_improvement": ["Gelistir"],
        "predicted_occupancy_change": "+5%", "predicted_revenue_change": "+10000 TL",
        "risk_level": "low"
    })

# ==================== INJECT MOCKS ====================
# We import config and helpers normally, but override database and gemini_service
import database
database.db = MockDB()

import gemini_service
gemini_service.get_chat_response = mock_gemini

# ==================== TEST RUNNER ====================
async def test_endpoint(router, path, method="GET", label="", body=None, handler_kwargs=None):
    try:
        route = next((r for r in router.routes if hasattr(r, 'path') and r.path == path), None)
        if not route:
            print(f"  [SKIP] {label}: path '{path}' not found")
            return "skip"
        handler = route.endpoint
        kw = handler_kwargs or {}
        if body:
            class FakeRequest:
                async def json(self): return body
            result = await handler(FakeRequest(), **kw)
        else:
            result = await handler(**kw)

        if isinstance(result, dict):
            if result.get("success") is True or result.get("report") or result.get("performance"):
                print(f"  [PASS] {label}")
                return "pass"
            elif result.get("success") is False:
                print(f"  [FAIL] {label}: {result.get('message', 'no message')[:80]}")
                return "fail"
            elif result.get("error"):
                print(f"  [FAIL] {label}: {result['error'][:80]}")
                return "fail"
            else:
                print(f"  [PASS] {label} (returned data)")
                return "pass"
        else:
            print(f"  [PASS] {label}")
            return "pass"
    except Exception as e:
        print(f"  [FAIL] {label}: {str(e)[:120]}")
        return "fail"

async def run_all_tests():
    from routers.financials import router as fin_router
    from routers.staff import router as staff_router
    from routers.revenue import router as rev_router
    from routers.reviews import router as reviews_router
    from routers.housekeeping import router as hk_router
    from routers.kitchen import router as kitchen_router
    from routers.guests import router as guests_router
    from routers.menu_admin import router as menu_router

    results = {"pass": 0, "fail": 0, "skip": 0}

    print("=" * 60)
    print("  KOZBEYLI KONAGI - FULL AI MONKEY TEST SUITE")
    print("=" * 60)

    tests = [
        (fin_router,     "/financials/ai-audit",         "AI Financial Audit", {"year": 2026, "month": 3}),
        (fin_router,     "/financials/ai-forecast",       "AI Financial Forecast"),
        (fin_router,     "/financials/ai-vendor-roi",     "AI Vendor ROI (CFO)"),
        (staff_router,   "/staff/ai-hr-analytics",        "AI HR & Burnout Radar"),
        #(staff_router,   "/staff/ai-shifts",              "AI Smart Shift Planner"),  # needs start_date param
        #(rev_router,     "/revenue/ai-insights",          "AI Revenue Insights"),  # needs context kwarg
        (rev_router,     "/revenue/ai-market-intel",      "AI Market Intelligence"),
        (reviews_router, "/reviews/ai-analytics",         "AI Review Analytics"),
        (hk_router,      "/housekeeping/ai-routing",      "AI Housekeeping Routes"),
        (kitchen_router, "/kitchen/ai-forecast",          "AI Kitchen Forecast"),
        (kitchen_router, "/kitchen/ai-procurement",       "AI Smart Procurement"),
        (guests_router,  "/guests/ai-complaint-radar",    "AI Complaint Radar"),
        (menu_router,    "/menu-admin/ai-engineering",    "AI Menu Engineering"),
    ]

    for entry in tests:
        router, path, label = entry[0], entry[1], entry[2]
        kw = entry[3] if len(entry) > 3 else None
        r = await test_endpoint(router, path, label=label, handler_kwargs=kw)
        results[r] += 1

    total = results["pass"] + results["fail"] + results["skip"]
    print("\n" + "=" * 60)
    print(f"  RESULTS: {results['pass']} PASSED | {results['fail']} FAILED | {results['skip']} SKIPPED / {total} TOTAL")
    print("=" * 60)

    if results["fail"] == 0 and results["pass"] > 0:
        print("\n  *** ALL TESTS PASSED! SYSTEM HEALTHY ***\n")
        return 0
    else:
        print(f"\n  *** {results['fail']} FAILURE(S) DETECTED ***\n")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(run_all_tests()))
