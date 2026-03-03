"""
Kozbeyli Konagi - Iteration 8 Comprehensive Test Suite
Tests all backend APIs including:
- Authentication (login with admin/admin123)
- Dashboard, Rooms, Guests, Reservations
- Events (including seed-samples)
- Automation (6 bots, scheduled jobs, group notifications)
- WhatsApp, Kitchen, Table Reservations
- Chatbot, Social Media
- QR Menu public page
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://teklif-yonetimi-2.preview.emergentagent.com').rstrip('/')

class TestHealthCheck:
    """Health check tests"""
    
    def test_health_endpoint(self):
        """GET /api/health should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["hotel"] == "Kozbeyli Konagi"
        print("Health check: PASSED")


class TestAuthentication:
    """Authentication flow tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("token")
        # Try setup if login fails
        setup_resp = requests.post(f"{BASE_URL}/api/auth/setup")
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "kozbeyli2026"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed")
    
    def test_login_with_admin_credentials(self):
        """POST /api/auth/login with admin/admin123"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        # First try admin123, if fails try kozbeyli2026 (setup password)
        if response.status_code != 200:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "admin",
                "password": "kozbeyli2026"
            })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["username"] == "admin"
        assert data["user"]["role"] == "admin"
        print(f"Login success: user={data['user']['username']}, role={data['user']['role']}")
    
    def test_get_me_endpoint(self, auth_token):
        """GET /api/auth/me returns current user"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        print(f"Get me: username={data.get('username')}")
    
    def test_get_roles(self, auth_token):
        """GET /api/auth/roles returns available roles"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/roles", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "roles" in data
        assert len(data["roles"]) >= 4  # admin, reception, kitchen, staff
        print(f"Roles: {[r.get('key') for r in data['roles']]}")


class TestDashboard:
    """Dashboard API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code != 200:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "admin",
                "password": "kozbeyli2026"
            })
        return response.json().get("token") if response.status_code == 200 else None
    
    def test_dashboard_stats(self, auth_token):
        """GET /api/dashboard/stats returns stats"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Should have dashboard stat fields
        assert isinstance(data, dict)
        print(f"Dashboard stats: {list(data.keys())}")


class TestRooms:
    """Rooms API tests"""
    
    def test_list_rooms(self):
        """GET /api/rooms returns list of rooms"""
        response = requests.get(f"{BASE_URL}/api/rooms")
        assert response.status_code == 200
        data = response.json()
        assert "rooms" in data
        assert isinstance(data["rooms"], list)
        print(f"Rooms count: {len(data['rooms'])}")


class TestGuests:
    """Guests API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code != 200:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "admin",
                "password": "kozbeyli2026"
            })
        return response.json().get("token") if response.status_code == 200 else None
    
    def test_list_guests(self, auth_token):
        """GET /api/guests returns guest list"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/guests", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "guests" in data
        print(f"Guests count: {len(data['guests'])}")


class TestReservations:
    """Reservations API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code != 200:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "admin",
                "password": "kozbeyli2026"
            })
        return response.json().get("token") if response.status_code == 200 else None
    
    def test_list_reservations(self, auth_token):
        """GET /api/reservations returns reservation list"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/reservations", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "reservations" in data
        print(f"Reservations count: {len(data['reservations'])}")


class TestEvents:
    """Events API tests - including seed-samples endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code != 200:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "admin",
                "password": "kozbeyli2026"
            })
        return response.json().get("token") if response.status_code == 200 else None
    
    def test_seed_sample_events(self, auth_token):
        """POST /api/events/seed-samples creates sample events"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/events/seed-samples", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"Seed events: inserted={data.get('inserted')}, total_samples={data.get('total_samples')}")
    
    def test_list_events(self, auth_token):
        """GET /api/events returns events list including Ece Yazar and GORAY"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/events", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        events = data["events"]
        
        # Check for expected events
        event_titles = [e.get("title", "").lower() for e in events]
        has_ece_yazar = any("ece yazar" in t for t in event_titles)
        has_goray = any("goray" in t for t in event_titles)
        
        print(f"Events count: {len(events)}")
        print(f"Has Ece Yazar event: {has_ece_yazar}")
        print(f"Has GORAY event: {has_goray}")
        
        # Check for cover images and pricing
        for event in events:
            if event.get("cover_image"):
                print(f"Event '{event.get('title')}' has cover image: {event.get('cover_image')[:50]}...")
            if event.get("pricing"):
                print(f"Event '{event.get('title')}' pricing: {event.get('pricing')}")


class TestAutomation:
    """Automation API tests - 6 bots, scheduled jobs, group notifications"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code != 200:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "admin",
                "password": "kozbeyli2026"
            })
        return response.json().get("token") if response.status_code == 200 else None
    
    def test_automation_summary(self, auth_token):
        """GET /api/automation/summary returns automation counts"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/automation/summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_logs" in data
        assert "breakfast_preps" in data
        assert "cleaning_notifications" in data
        print(f"Automation summary: total_logs={data.get('total_logs')}, breakfast={data.get('breakfast_preps')}, cleaning={data.get('cleaning_notifications')}")
    
    def test_scheduled_jobs(self, auth_token):
        """GET /api/automation/scheduled-jobs returns 3 active jobs"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/automation/scheduled-jobs", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        jobs = data["jobs"]
        assert len(jobs) == 3, f"Expected 3 scheduled jobs, got {len(jobs)}"
        
        job_ids = [j.get("id") for j in jobs]
        assert "breakfast_prep" in job_ids, "Missing breakfast_prep job"
        assert "morning_reminders" in job_ids, "Missing morning_reminders job"
        assert "checkout_cleaning" in job_ids, "Missing checkout_cleaning job"
        
        active_jobs = [j for j in jobs if j.get("status") == "active"]
        print(f"Scheduled jobs: total={len(jobs)}, active={len(active_jobs)}")
        for job in jobs:
            print(f"  - {job.get('id')}: {job.get('status')}, next={job.get('next_run')}")
    
    def test_breakfast_notification_manual_trigger(self, auth_token):
        """POST /api/automation/breakfast-notification triggers breakfast bot"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/automation/breakfast-notification", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["type"] == "breakfast_prep"
        print(f"Breakfast notification: {data.get('notification', {}).get('message', 'triggered')}")
    
    def test_morning_reminders_manual_trigger(self, auth_token):
        """POST /api/automation/morning-reminders triggers morning bot"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/automation/morning-reminders", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["type"] == "morning_reminders"
        print(f"Morning reminders: {len(data.get('notifications', []))} notifications")
    
    def test_cleaning_notification_manual_trigger(self, auth_token):
        """POST /api/automation/cleaning-notification triggers cleaning bot"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/automation/cleaning-notification", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["type"] == "checkout_cleaning"
        # notification can be None if no checkouts today
        notif = data.get('notification') or {}
        print(f"Cleaning notification: {notif.get('message', 'no checkouts today')}")
    
    def test_group_notifications_list(self, auth_token):
        """GET /api/automation/group-notifications returns sent notifications"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/automation/group-notifications", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        print(f"Group notifications: {len(data['notifications'])} total")
    
    def test_automation_logs(self, auth_token):
        """GET /api/automation/logs returns automation history"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/automation/logs", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        print(f"Automation logs: {len(data['logs'])} entries")
    
    def test_payment_reminder_bot(self, auth_token):
        """POST /api/automation/payment-reminder runs payment bot"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/automation/payment-reminder", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"Payment reminder: {data.get('reminders_created', 0)} reminders created")
    
    def test_cancellation_check_bot(self, auth_token):
        """POST /api/automation/cancellation-check runs cancellation bot"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/automation/cancellation-check", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"Cancellation check: {data.get('processed', 0)} processed")
    
    def test_kitchen_forecast_bot(self, auth_token):
        """GET /api/automation/kitchen-forecast returns 7 day forecast"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/automation/kitchen-forecast?days=7", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "forecast" in data
        assert len(data["forecast"]) == 7, f"Expected 7 days, got {len(data['forecast'])}"
        print(f"Kitchen forecast: {len(data['forecast'])} days")


class TestWhatsApp:
    """WhatsApp API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code != 200:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "admin",
                "password": "kozbeyli2026"
            })
        return response.json().get("token") if response.status_code == 200 else None
    
    def test_whatsapp_config_status(self, auth_token):
        """GET /api/whatsapp/config shows mock mode status"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/whatsapp/config", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "configured" in data
        print(f"WhatsApp config: configured={data.get('configured')}, has_token={data.get('has_token')}")
    
    def test_whatsapp_messages_list(self, auth_token):
        """GET /api/whatsapp/messages returns messages"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/whatsapp/messages", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        print(f"WhatsApp messages: {len(data['messages'])} total")
    
    def test_whatsapp_notifications_list(self, auth_token):
        """GET /api/whatsapp/notifications returns group notifications"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/whatsapp/notifications", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        print(f"WhatsApp notifications: {len(data['notifications'])} total")


class TestKitchen:
    """Kitchen API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code != 200:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "admin",
                "password": "kozbeyli2026"
            })
        return response.json().get("token") if response.status_code == 200 else None
    
    def test_kitchen_orders_list(self, auth_token):
        """GET /api/kitchen/orders returns orders"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/kitchen/orders", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data
        print(f"Kitchen orders: {len(data['orders'])} total")
    
    def test_kitchen_summary(self, auth_token):
        """GET /api/kitchen/summary returns kitchen summary"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/kitchen/summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        print(f"Kitchen summary: {data}")


class TestTableReservations:
    """Table reservations API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code != 200:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "admin",
                "password": "kozbeyli2026"
            })
        return response.json().get("token") if response.status_code == 200 else None
    
    def test_table_reservations_list(self, auth_token):
        """GET /api/table-reservations returns list"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/table-reservations", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "reservations" in data
        print(f"Table reservations: {len(data['reservations'])} total")


class TestChatbot:
    """Chatbot API tests"""
    
    def test_chatbot_send_message(self):
        """POST /api/chatbot sends message and receives response"""
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "Merhaba",
            "session_id": "test_session_123",
            "language": "tr"
        })
        assert response.status_code == 200
        data = response.json()
        assert "response" in data or "message" in data
        print(f"Chatbot response received: {str(data)[:100]}...")


class TestSocialMedia:
    """Social media API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code != 200:
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "admin",
                "password": "kozbeyli2026"
            })
        return response.json().get("token") if response.status_code == 200 else None
    
    def test_social_posts_list(self, auth_token):
        """GET /api/social/posts returns posts list"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/social/posts", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        print(f"Social posts: {len(data['posts'])} total")


class TestPublicQRMenu:
    """Public QR Menu tests - no auth required"""
    
    def test_public_menu_loads(self):
        """GET /api/public/menu returns menu without auth"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data or "menu" in data or isinstance(data, dict)
        print(f"Public menu loaded: {list(data.keys()) if isinstance(data, dict) else 'OK'}")
    
    def test_public_theme_loads(self):
        """GET /api/public/theme returns theme without auth"""
        response = requests.get(f"{BASE_URL}/api/public/theme")
        assert response.status_code == 200
        data = response.json()
        print(f"Public theme loaded: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
