"""
Iteration 13 Test Suite - P2 Features: Caching Layer + Push Notifications
Tests:
- Cache API endpoints: /api/cache/stats, /api/cache/clear
- Verify caching working on /api/rooms, /api/analytics/dashboard/kpi, /api/revenue/kpi
- Notification API endpoints: /api/notifications/today, /api/notifications/subscribe, /api/notifications/send-test
- PWA assets: manifest.json, service-worker.js with push handler
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCacheAPI:
    """Tests for Cache API endpoints"""
    
    def test_cache_clear(self):
        """POST /api/cache/clear should clear all caches"""
        response = requests.post(f"{BASE_URL}/api/cache/clear")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        print(f"Cache clear response: {data}")
    
    def test_cache_stats_initial(self):
        """GET /api/cache/stats should return cache statistics"""
        # First clear cache to reset stats
        requests.post(f"{BASE_URL}/api/cache/clear")
        
        response = requests.get(f"{BASE_URL}/api/cache/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "hits" in data
        assert "misses" in data
        assert "hit_rate_percent" in data
        assert "cache_sizes" in data
        
        print(f"Cache stats after clear: {data}")
    
    def test_rooms_caching(self):
        """Call GET /api/rooms twice, check cache stats shows 1 hit"""
        # Clear cache first
        requests.post(f"{BASE_URL}/api/cache/clear")
        
        # First call - should miss
        response1 = requests.get(f"{BASE_URL}/api/rooms")
        assert response1.status_code == 200
        
        # Second call - should hit cache
        response2 = requests.get(f"{BASE_URL}/api/rooms")
        assert response2.status_code == 200
        
        # Verify same data returned
        data1 = response1.json()
        data2 = response2.json()
        assert data1 == data2, "Cached response should match original"
        
        # Check cache stats - should have 1 hit
        stats_response = requests.get(f"{BASE_URL}/api/cache/stats")
        stats = stats_response.json()
        
        print(f"Cache stats after 2 rooms calls: {stats}")
        assert stats["hits"] >= 1, f"Expected at least 1 cache hit, got {stats['hits']}"
    
    def test_analytics_kpi_caching(self):
        """Call GET /api/analytics/dashboard/kpi twice, second should be cached"""
        # Clear cache first
        requests.post(f"{BASE_URL}/api/cache/clear")
        
        # First call - should miss
        response1 = requests.get(f"{BASE_URL}/api/analytics/dashboard/kpi")
        assert response1.status_code == 200
        
        # Second call - should hit cache
        response2 = requests.get(f"{BASE_URL}/api/analytics/dashboard/kpi")
        assert response2.status_code == 200
        
        # Verify same data returned
        data1 = response1.json()
        data2 = response2.json()
        assert data1 == data2, "Cached response should match original"
        
        # Check cache stats - should have hit
        stats_response = requests.get(f"{BASE_URL}/api/cache/stats")
        stats = stats_response.json()
        
        print(f"Cache stats after analytics KPI calls: {stats}")
        assert stats["hits"] >= 1, f"Expected at least 1 cache hit, got {stats['hits']}"
    
    def test_revenue_kpi_caching(self):
        """Call GET /api/revenue/kpi twice, second should be cached"""
        # Clear cache first
        requests.post(f"{BASE_URL}/api/cache/clear")
        
        # First call - should miss
        response1 = requests.get(f"{BASE_URL}/api/revenue/kpi")
        assert response1.status_code == 200
        
        # Second call - should hit cache
        response2 = requests.get(f"{BASE_URL}/api/revenue/kpi")
        assert response2.status_code == 200
        
        # Verify same data returned
        data1 = response1.json()
        data2 = response2.json()
        assert data1 == data2, "Cached response should match original"
        
        # Check cache stats - should have hit
        stats_response = requests.get(f"{BASE_URL}/api/cache/stats")
        stats = stats_response.json()
        
        print(f"Cache stats after revenue KPI calls: {stats}")
        assert stats["hits"] >= 1, f"Expected at least 1 cache hit, got {stats['hits']}"
    
    def test_cache_stats_structure(self):
        """Verify cache stats returns all expected fields"""
        response = requests.get(f"{BASE_URL}/api/cache/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Required fields
        assert isinstance(data.get("hits"), int)
        assert isinstance(data.get("misses"), int)
        assert isinstance(data.get("hit_rate_percent"), (int, float))
        assert isinstance(data.get("cache_sizes"), dict)
        
        # Cache sizes should have short, medium, long
        sizes = data["cache_sizes"]
        assert "short" in sizes
        assert "medium" in sizes
        assert "long" in sizes
        
        print(f"Cache stats structure verified: {data}")


class TestNotificationsAPI:
    """Tests for Notifications API endpoints"""
    
    def test_notifications_today(self):
        """GET /api/notifications/today should return today's notifications"""
        response = requests.get(f"{BASE_URL}/api/notifications/today")
        assert response.status_code == 200
        data = response.json()
        
        # Required fields
        assert "date" in data
        assert "total" in data
        assert "checkins" in data
        assert "checkouts" in data
        assert "notifications" in data
        assert isinstance(data["notifications"], list)
        
        print(f"Today's notifications: date={data['date']}, total={data['total']}, checkins={data['checkins']}, checkouts={data['checkouts']}")
    
    def test_notifications_subscribe(self):
        """POST /api/notifications/subscribe should accept subscription data"""
        subscription = {
            "subscription": {
                "endpoint": "https://test-endpoint.example.com/push/12345",
                "keys": {
                    "p256dh": "test_p256dh_key",
                    "auth": "test_auth_key"
                }
            },
            "user_id": "test_user_123"
        }
        
        response = requests.post(f"{BASE_URL}/api/notifications/subscribe", json=subscription)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        
        print(f"Subscribe response: {data}")
    
    def test_notifications_unsubscribe(self):
        """POST /api/notifications/unsubscribe should accept endpoint"""
        response = requests.post(f"{BASE_URL}/api/notifications/unsubscribe", json={
            "endpoint": "https://test-endpoint.example.com/push/12345"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        
        print(f"Unsubscribe response: {data}")
    
    def test_notifications_send_test(self):
        """POST /api/notifications/send-test should return success with notification object"""
        response = requests.post(f"{BASE_URL}/api/notifications/send-test")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") is True
        assert "notification" in data
        assert "title" in data["notification"]
        assert "body" in data["notification"]
        
        print(f"Test notification: {data['notification']}")


class TestPWAAssets:
    """Tests for PWA assets: manifest.json, service-worker.js"""
    
    def test_manifest_json_accessible(self):
        """manifest.json should be accessible and contain PWA metadata"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        assert response.status_code == 200
        
        data = response.json()
        
        # Required PWA fields
        assert "name" in data
        assert "short_name" in data
        assert "icons" in data
        assert "start_url" in data
        assert "display" in data
        assert "theme_color" in data
        assert "background_color" in data
        
        print(f"Manifest: name={data['name']}, short_name={data['short_name']}, display={data['display']}")
    
    def test_service_worker_accessible(self):
        """service-worker.js should be accessible"""
        response = requests.get(f"{BASE_URL}/service-worker.js")
        assert response.status_code == 200
        
        content = response.text
        assert len(content) > 0
        
        # Verify it's JavaScript
        assert "self.addEventListener" in content or "addEventListener" in content
        
        print(f"Service worker content length: {len(content)} bytes")
    
    def test_service_worker_has_push_handler(self):
        """service-worker.js should contain push event handler"""
        response = requests.get(f"{BASE_URL}/service-worker.js")
        assert response.status_code == 200
        
        content = response.text
        
        # Check for push event handler
        assert "push" in content, "Service worker should handle push events"
        assert "self.addEventListener('push'" in content or "addEventListener('push'" in content, \
            "Service worker should have push event listener"
        
        print("Service worker push handler verified")
    
    def test_service_worker_has_notification_click(self):
        """service-worker.js should handle notification clicks"""
        response = requests.get(f"{BASE_URL}/service-worker.js")
        assert response.status_code == 200
        
        content = response.text
        
        # Check for notificationclick handler
        assert "notificationclick" in content, "Service worker should handle notification clicks"
        
        print("Service worker notification click handler verified")


class TestRegressionAuth:
    """Regression tests for authentication"""
    
    def test_login_admin(self):
        """Login with admin/admin123 should work"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        
        print(f"Login successful: user={data['user'].get('name')}, role={data['user'].get('role')}")
        return data["token"]
    
    def test_health_check(self):
        """Health check should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        
        print(f"Health check: {data}")


class TestRegressionNavigation:
    """Regression tests for API endpoints that power navigation pages"""
    
    def test_rooms_api(self):
        """GET /api/rooms should return rooms"""
        response = requests.get(f"{BASE_URL}/api/rooms")
        assert response.status_code == 200
        data = response.json()
        assert "rooms" in data
        
        print(f"Rooms count: {len(data['rooms'])}")
    
    def test_guests_api(self):
        """GET /api/guests should return guests"""
        response = requests.get(f"{BASE_URL}/api/guests")
        assert response.status_code == 200
        
        print("Guests API working")
    
    def test_reservations_api(self):
        """GET /api/reservations should return reservations"""
        response = requests.get(f"{BASE_URL}/api/reservations")
        assert response.status_code == 200
        
        print("Reservations API working")
    
    def test_analytics_kpi_api(self):
        """GET /api/analytics/dashboard/kpi should return KPI data"""
        response = requests.get(f"{BASE_URL}/api/analytics/dashboard/kpi")
        assert response.status_code == 200
        data = response.json()
        assert "period" in data
        assert "daily_revenue" in data
        assert "occupancy_rate" in data
        
        print(f"Analytics KPI: period={data['period']}")
    
    def test_revenue_kpi_api(self):
        """GET /api/revenue/kpi should return revenue KPI data"""
        response = requests.get(f"{BASE_URL}/api/revenue/kpi")
        assert response.status_code == 200
        data = response.json()
        assert "period" in data
        assert "total_revenue" in data
        assert "adr" in data
        assert "revpar" in data
        
        print(f"Revenue KPI: total_revenue={data['total_revenue']}, adr={data['adr']}")
    
    def test_audit_logs_api(self):
        """GET /api/audit/logs should return audit logs"""
        response = requests.get(f"{BASE_URL}/api/audit/logs")
        assert response.status_code == 200
        
        print("Audit logs API working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
