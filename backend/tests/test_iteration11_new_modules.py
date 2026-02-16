"""
Iteration 11 - Test new modules: Revenue Management, Analytics, Audit/Security, HotelRunner Integration
Tests for all P0-P2 features as requested
"""
import pytest
import requests
import os
from datetime import date, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://hotelrunner-sync.preview.emergentagent.com').rstrip('/')

@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


# ==================== REVENUE MANAGEMENT ====================

class TestRevenueManagement:
    """Revenue Management endpoints tests - Dynamic Pricing and KPIs"""
    
    def test_get_room_types(self, api_client):
        """GET /api/revenue/room-types - should return all 5 room types"""
        response = api_client.get(f"{BASE_URL}/api/revenue/room-types")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "room_types" in data
        room_types = data["room_types"]
        assert len(room_types) == 5, f"Expected 5 room types, got {len(room_types)}"
        
        # Check room type keys
        room_keys = [rt["key"] for rt in room_types]
        expected_keys = ["standart_deniz", "standart_kara", "superior", "uc_kisilik", "dort_kisilik"]
        for key in expected_keys:
            assert key in room_keys, f"Missing room type: {key}"
        
        # Each room should have base_price
        for rt in room_types:
            assert "base_price" in rt
            assert rt["base_price"] > 0
        print(f"Room types: {room_keys}")
    
    def test_calculate_dynamic_price(self, api_client):
        """GET /api/revenue/pricing/calculate - should return dynamic price with factors"""
        target_date = (date.today() + timedelta(days=30)).isoformat()
        response = api_client.get(
            f"{BASE_URL}/api/revenue/pricing/calculate",
            params={"room_type": "standart_deniz", "target_date": target_date}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "room_type" in data
        assert data["room_type"] == "standart_deniz"
        assert "date" in data
        assert "base_price" in data
        assert "dynamic_price" in data
        assert "currency" in data
        assert data["currency"] == "TRY"
        assert "total_multiplier" in data
        assert "factors" in data
        
        # Check factors structure
        factors = data["factors"]
        assert "season" in factors
        assert "occupancy" in factors
        assert "demand" in factors
        assert "day" in factors
        assert "special_day" in factors
        
        print(f"Dynamic price for {target_date}: {data['dynamic_price']} TRY (x{data['total_multiplier']})")
    
    def test_pricing_calendar(self, api_client):
        """GET /api/revenue/pricing/calendar - should return price calendar for date range"""
        date_from = date.today().replace(day=1).isoformat()
        date_to = (date.today().replace(day=1) + timedelta(days=27)).isoformat()
        
        response = api_client.get(
            f"{BASE_URL}/api/revenue/pricing/calendar",
            params={"room_type": "standart_deniz", "date_from": date_from, "date_to": date_to}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "room_type" in data
        assert "period" in data
        assert "prices" in data
        assert "summary" in data
        
        prices = data["prices"]
        assert len(prices) > 0, "Expected prices array"
        
        summary = data["summary"]
        assert "min_price" in summary
        assert "max_price" in summary
        assert "avg_price" in summary
        
        print(f"Calendar prices: min={summary['min_price']}, max={summary['max_price']}, avg={summary['avg_price']}")
    
    def test_revenue_kpi(self, api_client):
        """GET /api/revenue/kpi - should return revenue KPIs (ADR, RevPAR, etc.)"""
        response = api_client.get(f"{BASE_URL}/api/revenue/kpi")
        assert response.status_code == 200
        
        data = response.json()
        assert "period" in data
        assert "total_revenue" in data
        assert "adr" in data
        assert "revpar" in data
        assert "occupancy_rate" in data
        assert "base_rates" in data
        
        print(f"KPIs: Revenue={data['total_revenue']} TL, ADR={data['adr']}, RevPAR={data['revpar']}, Occupancy={data['occupancy_rate']}%")
    
    def test_revenue_forecast(self, api_client):
        """GET /api/revenue/forecast - should return 30-day revenue forecast"""
        response = api_client.get(f"{BASE_URL}/api/revenue/forecast")
        assert response.status_code == 200
        
        data = response.json()
        assert "period" in data
        assert "total_predicted_revenue" in data
        assert "average_daily_revenue" in data
        assert "daily_forecasts" in data
        
        forecasts = data["daily_forecasts"]
        assert len(forecasts) >= 30, f"Expected at least 30 forecasts, got {len(forecasts)}"
        
        # Check forecast structure
        if forecasts:
            fc = forecasts[0]
            assert "date" in fc
            assert "predicted_revenue" in fc
            assert "predicted_occupancy" in fc
            assert "avg_rate" in fc
        
        print(f"30-day forecast: Total={data['total_predicted_revenue']} TL, Daily avg={data['average_daily_revenue']} TL")
    
    def test_update_all_prices(self, api_client):
        """POST /api/revenue/pricing/update-all - should update prices for days ahead"""
        response = api_client.post(
            f"{BASE_URL}/api/revenue/pricing/update-all",
            params={"days_ahead": 7}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "updated" in data
        assert data["updated"] > 0
        assert "days_ahead" in data
        assert "room_types" in data
        
        print(f"Updated {data['updated']} prices for {data['days_ahead']} days, {data['room_types']} room types")


# ==================== ANALYTICS ====================

class TestAnalytics:
    """Analytics & Reporting endpoints tests"""
    
    def test_analytics_kpi(self, api_client):
        """GET /api/analytics/dashboard/kpi - should return KPI metrics"""
        response = api_client.get(f"{BASE_URL}/api/analytics/dashboard/kpi")
        assert response.status_code == 200
        
        data = response.json()
        assert "period" in data
        assert "daily_revenue" in data
        assert "occupancy_rate" in data
        assert "adr" in data
        assert "revpar" in data
        
        # Check KPI structure
        for kpi_key in ["daily_revenue", "occupancy_rate", "adr", "revpar"]:
            kpi = data[kpi_key]
            assert "value" in kpi
            assert "trend" in kpi
        
        print(f"Analytics KPIs: Revenue={data['daily_revenue']['value']}, Occupancy={data['occupancy_rate']['value']}%")
    
    def test_revenue_trend(self, api_client):
        """GET /api/analytics/revenue/trend - should return revenue trend data"""
        response = api_client.get(
            f"{BASE_URL}/api/analytics/revenue/trend",
            params={"period": "30d"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "period" in data
        assert "data" in data
        assert "total" in data
        assert "average" in data
        
        trend_data = data["data"]
        assert len(trend_data) >= 30, f"Expected 30 days, got {len(trend_data)}"
        
        if trend_data:
            assert "date" in trend_data[0]
            assert "revenue" in trend_data[0]
        
        print(f"Revenue trend {data['period']}: Total={data['total']}, Avg={data['average']}")
    
    def test_booking_sources(self, api_client):
        """GET /api/analytics/bookings/sources - should return booking source distribution"""
        response = api_client.get(f"{BASE_URL}/api/analytics/bookings/sources")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_bookings" in data
        assert "total_revenue" in data
        assert "sources" in data
        
        sources = data["sources"]
        if sources:
            source = sources[0]
            assert "name" in source
            assert "bookings" in source
            assert "bookings_percent" in source
            assert "revenue" in source
        
        print(f"Booking sources: Total={data['total_bookings']}, Sources={len(sources)}")
    
    def test_occupancy_heatmap(self, api_client):
        """GET /api/analytics/occupancy/heatmap - should return occupancy heatmap data"""
        response = api_client.get(f"{BASE_URL}/api/analytics/occupancy/heatmap")
        assert response.status_code == 200
        
        data = response.json()
        assert "year" in data
        assert "heatmap" in data
        
        heatmap = data["heatmap"]
        assert len(heatmap) == 12, "Expected 12 months"
        
        if heatmap:
            month = heatmap[0]
            assert "month" in month
            assert "month_name" in month
            assert "days" in month
        
        print(f"Heatmap year: {data['year']}, Months: {len(heatmap)}")
    
    def test_room_performance(self, api_client):
        """GET /api/analytics/rooms/performance - should return room performance data"""
        response = api_client.get(f"{BASE_URL}/api/analytics/rooms/performance")
        assert response.status_code == 200
        
        data = response.json()
        assert "period" in data
        assert "rooms" in data
        
        rooms = data["rooms"]
        if rooms:
            room = rooms[0]
            assert "room_id" in room
            assert "bookings_count" in room
            assert "total_revenue" in room
            assert "occupancy_rate" in room
        
        print(f"Room performance: {len(rooms)} rooms analyzed")


# ==================== AUDIT & SECURITY ====================

class TestAuditSecurity:
    """Audit & Security endpoints tests"""
    
    def test_get_audit_logs(self, api_client):
        """GET /api/audit/logs - should return audit logs with pagination"""
        response = api_client.get(
            f"{BASE_URL}/api/audit/logs",
            params={"page": 1, "limit": 10}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        assert "logs" in data
        
        print(f"Audit logs: Total={data['total']}, Page {data['page']}/{data['pages']}")
    
    def test_get_audit_stats(self, api_client):
        """GET /api/audit/stats - should return audit statistics"""
        response = api_client.get(f"{BASE_URL}/api/audit/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "period" in data
        assert "total_logs" in data
        assert "action_counts" in data
        assert "entity_counts" in data
        assert "failed_operations" in data
        assert "success_rate" in data
        
        print(f"Audit stats: Total={data['total_logs']}, Success rate={data['success_rate']}%")
    
    def test_get_security_alerts(self, api_client):
        """GET /api/audit/alerts - should return security alerts"""
        response = api_client.get(f"{BASE_URL}/api/audit/alerts")
        assert response.status_code == 200
        
        data = response.json()
        assert "alerts" in data
        
        print(f"Security alerts: {len(data['alerts'])} alerts found")
    
    def test_run_security_check(self, api_client):
        """POST /api/audit/check-security - should run security check"""
        response = api_client.post(f"{BASE_URL}/api/audit/check-security")
        assert response.status_code == 200
        
        data = response.json()
        assert "alerts_found" in data
        assert "alerts" in data
        
        print(f"Security check: {data['alerts_found']} alerts found")


# ==================== HOTELRUNNER INTEGRATION ====================

class TestHotelRunnerIntegration:
    """HotelRunner integration endpoints tests (mock mode)"""
    
    def test_get_status(self, api_client):
        """GET /api/hotelrunner/status - should return mock_mode=true"""
        response = api_client.get(f"{BASE_URL}/api/hotelrunner/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "connected" in data
        assert "mock_mode" in data
        assert "api_key_set" in data
        assert "hotel_id_set" in data
        assert "total_syncs" in data
        
        # Since no API keys, should be in mock mode
        assert data["mock_mode"] == True, "Expected mock_mode=true without API keys"
        
        print(f"HotelRunner status: mock_mode={data['mock_mode']}, connected={data['connected']}")
    
    def test_get_config(self, api_client):
        """GET /api/hotelrunner/config - should return configuration"""
        response = api_client.get(f"{BASE_URL}/api/hotelrunner/config")
        assert response.status_code == 200
        
        data = response.json()
        assert "mock_mode" in data
        assert "api_key_set" in data
        assert "hotel_id_set" in data
        assert "sync_interval_minutes" in data
        assert "features" in data
        
        features = data["features"]
        assert features["reservation_sync"] == True
        assert features["availability_sync"] == True
        assert features["rate_sync"] == True
        assert features["webhook_handler"] == True
        
        print(f"Config: interval={data['sync_interval_minutes']}min, features={list(features.keys())}")
    
    def test_full_sync_mock(self, api_client):
        """POST /api/hotelrunner/sync/full - should perform full sync in mock mode"""
        response = api_client.post(f"{BASE_URL}/api/hotelrunner/sync/full")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["type"] == "full_sync"
        assert "results" in data
        assert "mock" in data
        assert data["mock"] == True
        
        results = data["results"]
        assert "reservations" in results
        assert "availability" in results
        assert "rates" in results
        
        print(f"Full sync (mock): success={data['success']}, results={list(results.keys())}")
    
    def test_sync_reservations_mock(self, api_client):
        """POST /api/hotelrunner/sync/reservations - mock mode"""
        response = api_client.post(f"{BASE_URL}/api/hotelrunner/sync/reservations")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["type"] == "reservations"
        assert data["mock"] == True
        
        print(f"Reservations sync (mock): success={data['success']}")
    
    def test_sync_availability_mock(self, api_client):
        """POST /api/hotelrunner/sync/availability - mock mode"""
        response = api_client.post(f"{BASE_URL}/api/hotelrunner/sync/availability")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["type"] == "availability"
        assert data["mock"] == True
        
        print(f"Availability sync (mock): success={data['success']}")
    
    def test_sync_rates_mock(self, api_client):
        """POST /api/hotelrunner/sync/rates - mock mode"""
        response = api_client.post(f"{BASE_URL}/api/hotelrunner/sync/rates")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["type"] == "rates"
        assert data["mock"] == True
        
        print(f"Rates sync (mock): success={data['success']}")
    
    def test_get_sync_logs(self, api_client):
        """GET /api/hotelrunner/sync-logs - should return sync log history"""
        response = api_client.get(f"{BASE_URL}/api/hotelrunner/sync-logs")
        assert response.status_code == 200
        
        data = response.json()
        assert "logs" in data
        assert "total" in data
        
        logs = data["logs"]
        if logs:
            log = logs[0]
            assert "sync_type" in log
            assert "status" in log
            assert "mock" in log
        
        print(f"Sync logs: {data['total']} logs found")


# ==================== ADDITIONAL VALIDATION ====================

class TestEndpointAvailability:
    """Test all new endpoints are available and reachable"""
    
    def test_revenue_endpoints_available(self, api_client):
        """All revenue endpoints should be accessible"""
        endpoints = [
            "/api/revenue/room-types",
            "/api/revenue/kpi",
            "/api/revenue/forecast",
            "/api/revenue/pricing/rules",
        ]
        for endpoint in endpoints:
            response = api_client.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"{endpoint} returned {response.status_code}"
            print(f"{endpoint}: OK")
    
    def test_analytics_endpoints_available(self, api_client):
        """All analytics endpoints should be accessible"""
        endpoints = [
            "/api/analytics/dashboard/kpi",
            "/api/analytics/revenue/trend?period=30d",
            "/api/analytics/bookings/sources",
            "/api/analytics/occupancy/heatmap",
            "/api/analytics/rooms/performance",
        ]
        for endpoint in endpoints:
            response = api_client.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"{endpoint} returned {response.status_code}"
            print(f"{endpoint}: OK")
    
    def test_audit_endpoints_available(self, api_client):
        """All audit endpoints should be accessible"""
        endpoints = [
            "/api/audit/logs",
            "/api/audit/stats",
            "/api/audit/alerts",
        ]
        for endpoint in endpoints:
            response = api_client.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"{endpoint} returned {response.status_code}"
            print(f"{endpoint}: OK")
    
    def test_hotelrunner_endpoints_available(self, api_client):
        """All hotelrunner endpoints should be accessible"""
        endpoints = [
            "/api/hotelrunner/status",
            "/api/hotelrunner/config",
            "/api/hotelrunner/sync-logs",
        ]
        for endpoint in endpoints:
            response = api_client.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"{endpoint} returned {response.status_code}"
            print(f"{endpoint}: OK")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
