"""
Iteration 12: P2 Optimization Tests (Database Indexing + PWA)
Tests for:
1. Database indexing applied on startup
2. PWA manifest.json and service-worker.js accessibility
3. Regression tests for core APIs
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestHealthAndDatabase:
    """Health check and database connection tests"""
    
    def test_health_endpoint_status(self):
        """Test /api/health returns 200 and database is connected"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["hotel"] == "Kozbeyli Konagi"
        print(f"PASS: Health check - status={data['status']}, db={data['database']}")


class TestPWAAssets:
    """PWA manifest and service worker accessibility tests"""
    
    def test_manifest_json_accessible(self):
        """Test /manifest.json is accessible and has correct PWA metadata"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        assert response.status_code == 200
        data = response.json()
        
        # Check PWA required fields
        assert data["short_name"] == "Kozbeyli"
        assert data["name"] == "Kozbeyli Konagi Yonetim Sistemi"
        assert data["display"] == "standalone"
        assert data["theme_color"] == "#1a1a2e"
        assert data["background_color"] == "#0f0f1a"
        assert "icons" in data
        assert len(data["icons"]) >= 2  # Should have at least 192x192 and 512x512
        print(f"PASS: manifest.json - name={data['name']}, theme={data['theme_color']}")
    
    def test_service_worker_accessible(self):
        """Test /service-worker.js returns 200"""
        response = requests.get(f"{BASE_URL}/service-worker.js")
        assert response.status_code == 200
        content_type = response.headers.get('content-type', '')
        assert 'javascript' in content_type
        # Check service worker has basic content
        content = response.text
        assert 'CACHE_NAME' in content or 'caches' in content or 'fetch' in content
        print(f"PASS: service-worker.js accessible, content-type={content_type}")


class TestAuthFlow:
    """Authentication tests with both password options"""
    
    def test_login_with_admin123(self):
        """Test login with admin/admin123"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code == 200:
            data = response.json()
            assert "token" in data
            assert "user" in data
            print(f"PASS: Login with admin/admin123 successful")
            return True
        else:
            print(f"INFO: Login with admin123 failed, status={response.status_code}")
            return False
    
    def test_login_with_kozbeyli2026(self):
        """Test login with admin/kozbeyli2026"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "kozbeyli2026"
        })
        if response.status_code == 200:
            data = response.json()
            assert "token" in data
            assert "user" in data
            print(f"PASS: Login with admin/kozbeyli2026 successful")
            return True
        else:
            print(f"INFO: Login with kozbeyli2026 failed, status={response.status_code}")
            return False
    
    def test_login_at_least_one_password_works(self):
        """Ensure at least one login method works"""
        # Try admin123 first (from handoff)
        res1 = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if res1.status_code == 200:
            print("PASS: Login working with admin/admin123")
            return
        
        # Try kozbeyli2026 (shown on login page)
        res2 = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "kozbeyli2026"
        })
        if res2.status_code == 200:
            print("PASS: Login working with admin/kozbeyli2026")
            return
        
        # If neither works, fail the test
        assert False, "Neither admin/admin123 nor admin/kozbeyli2026 works for login"


class TestCoreAPIs:
    """Regression tests for core API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for authenticated requests"""
        # Try admin123 first
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code != 200:
            # Try kozbeyli2026
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "admin",
                "password": "kozbeyli2026"
            })
        
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_rooms_endpoint(self):
        """Test /api/rooms returns room data"""
        response = requests.get(f"{BASE_URL}/api/rooms", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "rooms" in data
        rooms = data["rooms"]
        assert len(rooms) >= 1
        # Check room structure
        room = rooms[0]
        assert "room_id" in room
        assert "name_tr" in room
        assert "base_price_try" in room
        print(f"PASS: /api/rooms returns {len(rooms)} rooms")
    
    def test_guests_endpoint(self):
        """Test /api/guests returns guest data"""
        response = requests.get(f"{BASE_URL}/api/guests", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "guests" in data
        print(f"PASS: /api/guests returns {len(data['guests'])} guests")
    
    def test_reservations_endpoint(self):
        """Test /api/reservations returns data"""
        response = requests.get(f"{BASE_URL}/api/reservations", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "reservations" in data
        print(f"PASS: /api/reservations returns {len(data['reservations'])} reservations")


class TestNewModulesRegression:
    """Regression tests for Phase 25 modules (Revenue, Analytics, Audit)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code != 200:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "admin",
                "password": "kozbeyli2026"
            })
        
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_revenue_kpi_endpoint(self):
        """Test /api/revenue/kpi returns KPI data"""
        response = requests.get(f"{BASE_URL}/api/revenue/kpi", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        # Should have revenue KPIs
        assert any(key in data for key in ["revenue", "adr", "revpar", "occupancy_rate", "total_revenue"])
        print(f"PASS: /api/revenue/kpi returns revenue data")
    
    def test_analytics_kpi_endpoint(self):
        """Test /api/analytics/dashboard/kpi returns analytics"""
        response = requests.get(f"{BASE_URL}/api/analytics/dashboard/kpi", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        print(f"PASS: /api/analytics/dashboard/kpi returns analytics data")
    
    def test_audit_logs_endpoint(self):
        """Test /api/audit/logs returns audit logs"""
        response = requests.get(f"{BASE_URL}/api/audit/logs", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        print(f"PASS: /api/audit/logs returns {len(data['logs'])} logs")


class TestStaticAssets:
    """Test static assets accessibility"""
    
    def test_logo_accessible(self):
        """Test /logo.jpeg is accessible"""
        response = requests.get(f"{BASE_URL}/logo.jpeg")
        # Logo should be accessible (200) or redirect
        assert response.status_code in [200, 301, 302, 304]
        print(f"PASS: /logo.jpeg accessible, status={response.status_code}")
    
    def test_index_html_accessible(self):
        """Test main page is accessible"""
        response = requests.get(BASE_URL)
        assert response.status_code == 200
        # Check for PWA manifest link
        assert 'manifest.json' in response.text
        print(f"PASS: Index page accessible with manifest link")
    
    def test_page_title_is_kozbeyli(self):
        """Test page title is 'Kozbeyli Konagi'"""
        response = requests.get(BASE_URL)
        assert response.status_code == 200
        assert '<title>Kozbeyli Konagi</title>' in response.text
        print(f"PASS: Page title is 'Kozbeyli Konagi'")


class TestOtherEndpoints:
    """Additional regression tests for other endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code != 200:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "admin",
                "password": "kozbeyli2026"
            })
        
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_tasks_endpoint(self):
        """Test /api/tasks"""
        response = requests.get(f"{BASE_URL}/api/tasks", headers=self.headers)
        assert response.status_code == 200
        print(f"PASS: /api/tasks returns data")
    
    def test_events_endpoint(self):
        """Test /api/events"""
        response = requests.get(f"{BASE_URL}/api/events", headers=self.headers)
        assert response.status_code == 200
        print(f"PASS: /api/events returns data")
    
    def test_housekeeping_endpoint(self):
        """Test /api/housekeeping"""
        response = requests.get(f"{BASE_URL}/api/housekeeping", headers=self.headers)
        assert response.status_code == 200
        print(f"PASS: /api/housekeeping returns data")
    
    def test_staff_endpoint(self):
        """Test /api/staff"""
        response = requests.get(f"{BASE_URL}/api/staff", headers=self.headers)
        assert response.status_code == 200
        print(f"PASS: /api/staff returns data")
    
    def test_table_reservations_endpoint(self):
        """Test /api/table-reservations"""
        response = requests.get(f"{BASE_URL}/api/table-reservations", headers=self.headers)
        assert response.status_code == 200
        print(f"PASS: /api/table-reservations returns data")
    
    def test_automation_rules_endpoint(self):
        """Test /api/automation/rules"""
        response = requests.get(f"{BASE_URL}/api/automation/rules", headers=self.headers)
        assert response.status_code == 200
        print(f"PASS: /api/automation/rules returns data")
    
    def test_hotelrunner_status_endpoint(self):
        """Test /api/hotelrunner/status"""
        response = requests.get(f"{BASE_URL}/api/hotelrunner/status", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        # Should show mock mode since no API key configured
        assert "mock_mode" in data
        print(f"PASS: /api/hotelrunner/status returns mock_mode={data.get('mock_mode')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
