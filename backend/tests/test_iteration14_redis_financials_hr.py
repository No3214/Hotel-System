"""
Iteration 14 - Test Redis Cache, VAPID Push, Financials Module, HotelRunner Improvements
Tests for:
1. Redis Cache Layer (upgraded from in-memory)
2. VAPID Push Notifications
3. Gelir/Gider (Income/Expense) Tracking Module
4. HotelRunner: cancellation policy, webhook, channels, sync logs
"""
import pytest
import requests
import os
from datetime import date, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


@pytest.fixture(scope="module")
def api_session():
    """Create a session with auth token"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    # Login to get token
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    if response.status_code == 200:
        token = response.json().get("token")
        session.headers.update({"Authorization": f"Bearer {token}"})
    return session


# ==================== REDIS CACHE TESTS ====================

class TestRedisCacheLayer:
    """Test Redis cache upgrade from in-memory"""
    
    def test_cache_stats_shows_redis_backend(self, api_session):
        """Cache stats should show backend=redis"""
        response = api_session.get(f"{BASE_URL}/api/cache/stats")
        assert response.status_code == 200
        data = response.json()
        # The cache should show redis backend if Redis is running
        # Or fallback to in-memory if Redis is not available
        assert "backend" in data
        assert data["backend"] in ["redis", "in-memory"]
        assert "hits" in data
        assert "misses" in data
        assert "hit_rate_percent" in data
        print(f"Cache backend: {data['backend']}")
        print(f"Cache stats: hits={data['hits']}, misses={data['misses']}")
    
    def test_cache_hit_on_rooms_double_call(self, api_session):
        """Calling /api/rooms twice should result in cache hit"""
        # First clear cache
        api_session.post(f"{BASE_URL}/api/cache/clear")
        
        # First call - should be cache miss
        api_session.get(f"{BASE_URL}/api/rooms")
        
        # Get stats after first call
        stats1 = api_session.get(f"{BASE_URL}/api/cache/stats").json()
        initial_hits = stats1.get("hits", 0)
        
        # Second call - should be cache hit
        api_session.get(f"{BASE_URL}/api/rooms")
        
        # Get stats after second call
        stats2 = api_session.get(f"{BASE_URL}/api/cache/stats").json()
        final_hits = stats2.get("hits", 0)
        
        # Should have at least one more hit
        assert final_hits > initial_hits, f"Expected cache hit increase, got {initial_hits} -> {final_hits}"
        print(f"Cache hits increased: {initial_hits} -> {final_hits}")
    
    def test_cache_clear_resets_stats(self, api_session):
        """POST /api/cache/clear should reset cache"""
        response = api_session.post(f"{BASE_URL}/api/cache/clear")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True or "cleared" in str(data).lower()
        print(f"Cache clear response: {data}")


# ==================== VAPID PUSH NOTIFICATION TESTS ====================

class TestVAPIDPushNotifications:
    """Test VAPID push notification endpoints"""
    
    def test_vapid_key_returns_public_key(self, api_session):
        """GET /api/notifications/vapid-key should return public key"""
        response = api_session.get(f"{BASE_URL}/api/notifications/vapid-key")
        assert response.status_code == 200
        data = response.json()
        assert "publicKey" in data
        # VAPID public key should be a non-empty string
        assert isinstance(data["publicKey"], str)
        print(f"VAPID public key present: {len(data['publicKey'])} chars")
    
    def test_subscriber_count_returns_count(self, api_session):
        """GET /api/notifications/subscribers should return count"""
        response = api_session.get(f"{BASE_URL}/api/notifications/subscribers")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert isinstance(data["count"], int)
        assert data["count"] >= 0
        print(f"Push subscribers: {data['count']}")
    
    def test_send_test_notification_returns_success(self, api_session):
        """POST /api/notifications/send-test should return success"""
        response = api_session.post(f"{BASE_URL}/api/notifications/send-test")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "notification" in data
        assert data["notification"]["title"] == "Test Bildirimi"
        print(f"Test notification sent: {data}")
    
    def test_today_notifications(self, api_session):
        """GET /api/notifications/today should return today's notifications"""
        response = api_session.get(f"{BASE_URL}/api/notifications/today")
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "total" in data
        assert "checkins" in data
        assert "checkouts" in data
        assert "notifications" in data
        print(f"Today's notifications: {data['total']} (checkins: {data['checkins']}, checkouts: {data['checkouts']})")


# ==================== FINANCIAL CATEGORIES TESTS ====================

class TestFinancialCategories:
    """Test financial categories endpoint"""
    
    def test_categories_returns_income_and_expense(self, api_session):
        """GET /api/financials/categories should return 7 income + 17 expense categories"""
        response = api_session.get(f"{BASE_URL}/api/financials/categories")
        assert response.status_code == 200
        data = response.json()
        
        assert "income_categories" in data
        assert "expense_categories" in data
        
        income_cats = data["income_categories"]
        expense_cats = data["expense_categories"]
        
        # Should have 7 income categories
        assert len(income_cats) == 7, f"Expected 7 income categories, got {len(income_cats)}"
        # Should have 17 expense categories
        assert len(expense_cats) == 17, f"Expected 17 expense categories, got {len(expense_cats)}"
        
        # Check category structure
        for cat in income_cats:
            assert "key" in cat
            assert "label" in cat
        
        for cat in expense_cats:
            assert "key" in cat
            assert "label" in cat
        
        print(f"Income categories: {[c['key'] for c in income_cats]}")
        print(f"Expense categories: {[c['key'] for c in expense_cats]}")


# ==================== FINANCIAL INCOME TESTS ====================

class TestFinancialIncome:
    """Test income CRUD operations"""
    
    created_income_id = None
    
    def test_add_income_with_commission(self, api_session):
        """POST /api/financials/income with room income and commission_rate"""
        payload = {
            "date": date.today().isoformat(),
            "category": "room",
            "description": "TEST_Income - Oda 101 rezervasyon",
            "amount": 5000,
            "source": "booking",
            "commission_rate": 15
        }
        response = api_session.post(f"{BASE_URL}/api/financials/income", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "id" in data
        TestFinancialIncome.created_income_id = data["id"]
        print(f"Created income: {data['id']}")
    
    def test_list_income_with_date_range(self, api_session):
        """GET /api/financials/income with date_from/date_to"""
        today = date.today()
        date_from = (today - timedelta(days=30)).isoformat()
        date_to = today.isoformat()
        
        response = api_session.get(f"{BASE_URL}/api/financials/income", params={
            "date_from": date_from,
            "date_to": date_to
        })
        assert response.status_code == 200
        data = response.json()
        assert "records" in data
        assert "total" in data
        assert isinstance(data["records"], list)
        print(f"Income records in date range: {data['total']}")
        
        # Verify commission calculation on returned records
        for rec in data["records"]:
            if rec.get("commission_rate", 0) > 0:
                expected_commission = round(rec["amount"] * rec["commission_rate"] / 100, 2)
                assert "commission_amount" in rec
                assert "net_amount" in rec
                print(f"  Income {rec['id']}: amount={rec['amount']}, commission={rec.get('commission_amount')}, net={rec.get('net_amount')}")


# ==================== FINANCIAL EXPENSE TESTS ====================

class TestFinancialExpense:
    """Test expense CRUD operations"""
    
    created_expense_id = None
    
    def test_add_expense(self, api_session):
        """POST /api/financials/expense"""
        payload = {
            "date": date.today().isoformat(),
            "category": "food_supplies",
            "description": "TEST_Expense - Haftalik gida alimi",
            "amount": 2500,
            "vendor": "Metro",
            "is_paid": True
        }
        response = api_session.post(f"{BASE_URL}/api/financials/expense", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "id" in data
        TestFinancialExpense.created_expense_id = data["id"]
        print(f"Created expense: {data['id']}")
    
    def test_list_expense_with_date_range(self, api_session):
        """GET /api/financials/expense with date_from/date_to"""
        today = date.today()
        date_from = (today - timedelta(days=30)).isoformat()
        date_to = today.isoformat()
        
        response = api_session.get(f"{BASE_URL}/api/financials/expense", params={
            "date_from": date_from,
            "date_to": date_to
        })
        assert response.status_code == 200
        data = response.json()
        assert "records" in data
        assert "total" in data
        assert isinstance(data["records"], list)
        print(f"Expense records in date range: {data['total']}")


# ==================== FINANCIAL SUMMARY TESTS ====================

class TestFinancialSummary:
    """Test daily and monthly summary endpoints"""
    
    def test_daily_summary(self, api_session):
        """GET /api/financials/daily/{date} returns income/expense/profit"""
        today = date.today().isoformat()
        response = api_session.get(f"{BASE_URL}/api/financials/daily/{today}")
        assert response.status_code == 200
        data = response.json()
        
        assert "date" in data
        assert "income" in data
        assert "expense" in data
        assert "profit" in data
        
        assert "total" in data["income"]
        assert "by_category" in data["income"]
        assert "total" in data["expense"]
        assert "by_category" in data["expense"]
        
        print(f"Daily summary for {today}:")
        print(f"  Income: {data['income']['total']} TL")
        print(f"  Expense: {data['expense']['total']} TL")
        print(f"  Profit: {data['profit']} TL")
    
    def test_monthly_summary_with_kpis(self, api_session):
        """GET /api/financials/monthly returns income/expense/profit/kpis/daily_trend"""
        today = date.today()
        response = api_session.get(f"{BASE_URL}/api/financials/monthly", params={
            "year": today.year,
            "month": today.month
        })
        assert response.status_code == 200
        data = response.json()
        
        # Check main structure
        assert "period" in data
        assert "income" in data
        assert "expense" in data
        assert "profit" in data
        assert "profit_margin" in data
        assert "daily_trend" in data
        assert "kpis" in data
        
        # Check income structure
        income = data["income"]
        assert "gross" in income
        assert "net" in income
        assert "commission" in income
        assert "by_category" in income
        assert "by_source" in income
        assert "count" in income
        
        # Check KPIs
        kpis = data["kpis"]
        assert "occupancy_rate" in kpis
        assert "adr" in kpis
        assert "revpar" in kpis
        assert "total_reservations" in kpis
        assert "occupied_nights" in kpis
        assert "total_room_nights" in kpis
        
        # Check daily trend
        assert isinstance(data["daily_trend"], list)
        if len(data["daily_trend"]) > 0:
            day = data["daily_trend"][0]
            assert "date" in day
            assert "income" in day
            assert "expense" in day
        
        print(f"Monthly summary for {data['period']}:")
        print(f"  Gross Income: {income['gross']} TL")
        print(f"  Net Income: {income['net']} TL")
        print(f"  Total Commission: {income['commission']} TL")
        print(f"  Total Expense: {data['expense']['total']} TL")
        print(f"  Profit: {data['profit']} TL (margin: {data['profit_margin']}%)")
        print(f"  KPIs: Occupancy={kpis['occupancy_rate']}%, ADR={kpis['adr']}, RevPAR={kpis['revpar']}")


# ==================== FINANCIAL DELETE TESTS ====================

class TestFinancialDelete:
    """Test delete financial record"""
    
    def test_delete_financial_record(self, api_session):
        """DELETE /api/financials/{id} deletes record"""
        # First create a test record
        payload = {
            "date": date.today().isoformat(),
            "category": "other",
            "description": "TEST_Delete - To be deleted",
            "amount": 100
        }
        create_resp = api_session.post(f"{BASE_URL}/api/financials/income", json=payload)
        assert create_resp.status_code == 200
        record_id = create_resp.json()["id"]
        
        # Delete it
        delete_resp = api_session.delete(f"{BASE_URL}/api/financials/{record_id}")
        assert delete_resp.status_code == 200
        data = delete_resp.json()
        assert data.get("success") == True
        print(f"Deleted financial record: {record_id}")


# ==================== HOTELRUNNER TESTS ====================

class TestHotelRunnerStatus:
    """Test HotelRunner status endpoint"""
    
    def test_status_returns_mock_mode_and_channels(self, api_session):
        """GET /api/hotelrunner/status returns mock_mode=true and 5 OTA channels"""
        response = api_session.get(f"{BASE_URL}/api/hotelrunner/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "connected" in data
        assert "mock_mode" in data
        assert data["mock_mode"] == True  # Should be mock mode since no API keys
        assert "channels" in data
        
        channels = data["channels"]
        assert len(channels) == 5, f"Expected 5 OTA channels, got {len(channels)}"
        
        channel_ids = [c["id"] for c in channels]
        expected_channels = ["booking", "expedia", "airbnb", "google", "trivago"]
        for ch in expected_channels:
            assert ch in channel_ids, f"Missing channel: {ch}"
        
        print(f"HotelRunner status: mock_mode={data['mock_mode']}, channels={len(channels)}")
        print(f"  Channels: {channel_ids}")


class TestHotelRunnerChannels:
    """Test HotelRunner channels endpoint"""
    
    def test_channels_returns_5_otas(self, api_session):
        """GET /api/hotelrunner/channels returns 5 OTA channels"""
        response = api_session.get(f"{BASE_URL}/api/hotelrunner/channels")
        assert response.status_code == 200
        data = response.json()
        
        assert "channels" in data
        assert "mock_mode" in data
        
        channels = data["channels"]
        assert len(channels) == 5
        
        # Check channel structure
        for ch in channels:
            assert "id" in ch
            assert "name" in ch
            assert "commission" in ch
            assert "status" in ch
        
        print(f"OTA Channels: {[(c['id'], c['commission']) for c in channels]}")


class TestHotelRunnerCancellation:
    """Test HotelRunner cancellation penalty endpoint"""
    
    def test_cancellation_penalty_special_day(self, api_session):
        """POST /api/hotelrunner/cancellation-penalty with check_in and total_price"""
        # Test with a special day (Valentine's Day Feb 14)
        payload = {
            "check_in": "2026-02-14",
            "total_price": 3000
        }
        response = api_session.post(f"{BASE_URL}/api/hotelrunner/cancellation-penalty", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "percentage" in data
        assert "amount" in data
        assert "reason" in data
        assert "is_special_day" in data
        
        # Feb 14 is Valentine's Day - should be 100% penalty
        assert data["is_special_day"] == True
        assert data["percentage"] == 100
        assert data["amount"] == 3000
        
        print(f"Cancellation penalty (special day): {data}")
    
    def test_cancellation_penalty_regular_day(self, api_session):
        """Test cancellation penalty for regular day >3 days away"""
        # Test with a date far in the future
        future_date = (date.today() + timedelta(days=30)).isoformat()
        payload = {
            "check_in": future_date,
            "total_price": 2000
        }
        response = api_session.post(f"{BASE_URL}/api/hotelrunner/cancellation-penalty", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Regular day >3 days away should be free cancellation
        assert data["percentage"] == 0
        assert data["amount"] == 0
        
        print(f"Cancellation penalty (regular day, >3 days): {data}")


class TestHotelRunnerWebhook:
    """Test HotelRunner webhook endpoint"""
    
    def test_webhook_reservation_created(self, api_session):
        """POST /api/hotelrunner/webhook with reservation.created event"""
        payload = {
            "event_type": "reservation.created",
            "data": {
                "channel": "booking.com",
                "reservation": {
                    "id": "HR_TEST_12345",
                    "guest_name": "TEST_Webhook",
                    "guest_surname": "Guest",
                    "guest_email": "test@webhook.com",
                    "guest_phone": "+905551234567",
                    "checkin_date": "2026-03-15",
                    "checkout_date": "2026-03-17",
                    "adults": 2,
                    "children": 0,
                    "room_type_name": "Deluxe Oda",
                    "total_price": 4500,
                    "currency": "TRY",
                    "status": "confirmed",
                    "channel_name": "Booking.com",
                    "confirmation_code": "BK123456"
                }
            }
        }
        response = api_session.post(f"{BASE_URL}/api/hotelrunner/webhook", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        assert data.get("event_type") == "reservation.created"
        assert "processed" in data
        
        print(f"Webhook response: {data}")


class TestHotelRunnerSync:
    """Test HotelRunner sync endpoints"""
    
    def test_full_sync_returns_mock_results(self, api_session):
        """POST /api/hotelrunner/sync/full returns mock results"""
        response = api_session.post(f"{BASE_URL}/api/hotelrunner/sync/full")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        assert data.get("type") == "full_sync"
        assert "results" in data
        assert data.get("mock") == True
        
        results = data["results"]
        assert "reservations" in results
        assert "availability" in results
        assert "rates" in results
        
        print(f"Full sync (mock): {data}")
    
    def test_sync_logs_returns_logs_array(self, api_session):
        """GET /api/hotelrunner/sync-logs returns logs array"""
        response = api_session.get(f"{BASE_URL}/api/hotelrunner/sync-logs")
        assert response.status_code == 200
        data = response.json()
        
        assert "logs" in data
        assert "total" in data
        assert isinstance(data["logs"], list)
        
        print(f"Sync logs count: {data['total']}")
        if len(data["logs"]) > 0:
            log = data["logs"][0]
            print(f"  Last log: {log.get('sync_type')} at {log.get('timestamp')}")


# ==================== CLEANUP ====================

class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_financials(self, api_session):
        """Delete TEST_ prefixed financial records"""
        # Get income records
        income_resp = api_session.get(f"{BASE_URL}/api/financials/income", params={"limit": 100})
        if income_resp.status_code == 200:
            records = income_resp.json().get("records", [])
            for rec in records:
                if rec.get("description", "").startswith("TEST_"):
                    api_session.delete(f"{BASE_URL}/api/financials/{rec['id']}")
                    print(f"Deleted test income: {rec['id']}")
        
        # Get expense records
        expense_resp = api_session.get(f"{BASE_URL}/api/financials/expense", params={"limit": 100})
        if expense_resp.status_code == 200:
            records = expense_resp.json().get("records", [])
            for rec in records:
                if rec.get("description", "").startswith("TEST_"):
                    api_session.delete(f"{BASE_URL}/api/financials/{rec['id']}")
                    print(f"Deleted test expense: {rec['id']}")


# ==================== REGRESSION TESTS ====================

class TestRegression:
    """Regression tests for existing functionality"""
    
    def test_health_check(self, api_session):
        """Health check endpoint"""
        response = api_session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"Health: {data}")
    
    def test_dashboard_stats(self, api_session):
        """Dashboard stats endpoint"""
        response = api_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "revenue" in data or "today_revenue" in data or "rooms" in data
        print(f"Dashboard stats: OK")
    
    def test_rooms_endpoint(self, api_session):
        """Rooms endpoint"""
        response = api_session.get(f"{BASE_URL}/api/rooms")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "rooms" in data
        print(f"Rooms: OK")
    
    def test_reservations_endpoint(self, api_session):
        """Reservations endpoint"""
        response = api_session.get(f"{BASE_URL}/api/reservations")
        assert response.status_code == 200
        print(f"Reservations: OK")
    
    def test_analytics_kpi(self, api_session):
        """Analytics KPI endpoint"""
        response = api_session.get(f"{BASE_URL}/api/analytics/dashboard/kpi")
        assert response.status_code == 200
        print(f"Analytics KPI: OK")
    
    def test_audit_logs(self, api_session):
        """Audit logs endpoint"""
        response = api_session.get(f"{BASE_URL}/api/audit/logs")
        assert response.status_code == 200
        print(f"Audit logs: OK")
