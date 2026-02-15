"""
Test suite for Kozbeyli Hotel - Faz 25 New Features
Tests: Auth (JWT), Dynamic Pricing, Table Reservations, Lifecycle, Automation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://hotel-ops-hub-3.preview.emergentagent.com"


class TestHealthAndSetup:
    """Health check and initial setup tests"""

    def test_health_endpoint(self):
        """GET /api/health - should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print(f"✓ Health check passed: {data}")

    def test_auth_setup_already_exists(self):
        """POST /api/auth/setup - should say system already exists"""
        response = requests.post(f"{BASE_URL}/api/auth/setup")
        assert response.status_code == 200
        data = response.json()
        assert data["has_users"] == True
        assert "kurulmus" in data["message"].lower()
        print(f"✓ Setup check passed: {data}")


class TestAuthJWT:
    """Authentication with JWT tests"""

    def test_login_success(self):
        """POST /api/auth/login - login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "kozbeyli2026"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
        assert data["user"]["permissions"] == ["*"]
        print(f"✓ Login success: user={data['user']['name']}, role={data['user']['role']}")
        return data["token"]

    def test_login_invalid_credentials(self):
        """POST /api/auth/login - should fail with wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid credentials rejected as expected")

    def test_get_me_with_token(self):
        """GET /api/auth/me - returns user info with Bearer token"""
        # First login
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "kozbeyli2026"
        })
        token = login_res.json()["token"]

        # Get user info
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"
        assert "permissions" in data
        print(f"✓ Get me passed: {data['name']} ({data['role']})")

    def test_get_me_without_token(self):
        """GET /api/auth/me - should fail without token"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("✓ Unauthenticated request rejected as expected")

    def test_get_roles(self):
        """GET /api/auth/roles - list available roles"""
        response = requests.get(f"{BASE_URL}/api/auth/roles")
        assert response.status_code == 200
        data = response.json()
        assert "roles" in data
        roles = {r["key"] for r in data["roles"]}
        assert "admin" in roles
        assert "reception" in roles
        assert "kitchen" in roles
        assert "staff" in roles
        print(f"✓ Roles: {roles}")


class TestDynamicPricing:
    """Dynamic pricing calculation tests"""

    def test_calculate_high_season_holiday(self):
        """GET /api/pricing/calculate - high season + holiday pricing"""
        response = requests.get(f"{BASE_URL}/api/pricing/calculate", params={
            "room_id": "double",
            "date": "2026-07-15"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["room_id"] == "double"
        assert data["season"] == "Yuksek Sezon"
        assert data["season_multiplier"] == 1.4
        assert data["is_holiday"] == True
        assert data["holiday_name"] == "Demokrasi ve Milli Birlik Gunu"
        assert data["final_price"] > data["base_price"]
        print(f"✓ High season holiday price: {data['base_price']} -> {data['final_price']} TL ({data['holiday_name']})")

    def test_calculate_low_season(self):
        """GET /api/pricing/calculate - low season pricing"""
        response = requests.get(f"{BASE_URL}/api/pricing/calculate", params={
            "room_id": "single",
            "date": "2026-01-15"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["season"] == "Dusuk Sezon"
        assert data["season_multiplier"] == 0.8
        assert data["final_price"] < data["base_price"]
        assert data["savings"] > 0
        print(f"✓ Low season price: {data['base_price']} -> {data['final_price']} TL (savings: {data['savings']} TL)")

    def test_calculate_price_range(self):
        """GET /api/pricing/range - price for date range"""
        response = requests.get(f"{BASE_URL}/api/pricing/range", params={
            "room_id": "double",
            "start_date": "2026-07-10",
            "end_date": "2026-07-15"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["nights"] == 5
        assert data["total_price"] > 0
        assert "daily_breakdown" in data
        assert len(data["daily_breakdown"]) == 5
        print(f"✓ Range price: {data['nights']} nights = {data['total_price']} TL (avg: {data['average_nightly']} TL/night)")

    def test_get_seasons(self):
        """GET /api/pricing/seasons - list seasons with multipliers"""
        response = requests.get(f"{BASE_URL}/api/pricing/seasons")
        assert response.status_code == 200
        data = response.json()
        assert "seasons" in data
        assert len(data["seasons"]) == 3
        season_keys = {s["key"] for s in data["seasons"]}
        assert season_keys == {"off_season", "mid_season", "high_season"}
        assert data["weekend_multiplier"] == 1.2
        print(f"✓ Seasons: {season_keys}")

    def test_get_holidays(self):
        """GET /api/pricing/holidays - list holidays"""
        response = requests.get(f"{BASE_URL}/api/pricing/holidays")
        assert response.status_code == 200
        data = response.json()
        assert "holidays" in data
        assert len(data["holidays"]) == 14
        print(f"✓ Holidays count: {len(data['holidays'])}")


class TestTableReservations:
    """Restaurant table reservation tests"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test table reservation ID"""
        self.test_res_id = None

    def test_get_availability(self):
        """GET /api/table-reservations/availability - 9 time slots"""
        response = requests.get(f"{BASE_URL}/api/table-reservations/availability", params={
            "date": "2026-03-15"
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["slots"]) == 9
        assert data["config"]["name"] == "Antakya Sofrasi"
        assert data["config"]["total_tables"] == 15
        print(f"✓ Availability: {len(data['slots'])} slots for {data['date']}")

    def test_create_table_reservation(self):
        """POST /api/table-reservations - create restaurant reservation"""
        response = requests.post(f"{BASE_URL}/api/table-reservations", json={
            "guest_name": "TEST_Mehmet Demir",
            "phone": "+905551234568",
            "date": "2026-03-20",
            "time": "20:00",
            "party_size": 6,
            "notes": "Pytest test reservation",
            "occasion": "anniversary",
            "is_hotel_guest": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["guest_name"] == "TEST_Mehmet Demir"
        assert data["status"] == "pending"
        assert data["party_size"] == 6
        assert "id" in data
        print(f"✓ Created table reservation: {data['id']}")
        return data["id"]

    def test_update_reservation_status(self):
        """PATCH /api/table-reservations/{id}/status - confirm reservation"""
        # First create
        create_res = requests.post(f"{BASE_URL}/api/table-reservations", json={
            "guest_name": "TEST_Status Test",
            "phone": "+905559999999",
            "date": "2026-03-21",
            "time": "19:30",
            "party_size": 2
        })
        res_id = create_res.json()["id"]

        # Update status
        response = requests.patch(f"{BASE_URL}/api/table-reservations/{res_id}/status", params={
            "status": "confirmed"
        })
        assert response.status_code == 200
        assert response.json()["success"] == True

        # Verify
        verify_res = requests.get(f"{BASE_URL}/api/table-reservations", params={"date": "2026-03-21"})
        found = [r for r in verify_res.json()["reservations"] if r["id"] == res_id]
        assert len(found) == 1
        assert found[0]["status"] == "confirmed"
        print(f"✓ Status updated to confirmed for {res_id}")

    def test_delete_table_reservation(self):
        """DELETE /api/table-reservations/{id} - delete reservation"""
        # First create
        create_res = requests.post(f"{BASE_URL}/api/table-reservations", json={
            "guest_name": "TEST_Delete Test",
            "phone": "+905558888888",
            "date": "2026-03-22",
            "time": "21:00",
            "party_size": 3
        })
        res_id = create_res.json()["id"]

        # Delete
        response = requests.delete(f"{BASE_URL}/api/table-reservations/{res_id}")
        assert response.status_code == 200
        assert response.json()["success"] == True
        print(f"✓ Deleted reservation {res_id}")


class TestLifecycleMessages:
    """Guest lifecycle messaging tests"""

    def test_get_templates(self):
        """GET /api/lifecycle/templates - list 6 message templates"""
        response = requests.get(f"{BASE_URL}/api/lifecycle/templates")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert len(data["templates"]) == 6
        template_keys = {t["key"] for t in data["templates"]}
        expected = {"booking_confirmation", "pre_arrival", "welcome_checkin", 
                   "during_stay_day2", "checkout_thankyou", "post_stay_followup"}
        assert template_keys == expected
        print(f"✓ Lifecycle templates: {template_keys}")

    def test_preview_message(self):
        """POST /api/lifecycle/preview - preview welcome message"""
        response = requests.post(f"{BASE_URL}/api/lifecycle/preview", params={
            "template_key": "welcome_checkin"
        })
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Hos geldiniz" in data["message"]
        assert "WiFi" in data["message"]
        print(f"✓ Preview message length: {len(data['message'])} chars")

    def test_preview_invalid_template(self):
        """POST /api/lifecycle/preview - invalid template should 404"""
        response = requests.post(f"{BASE_URL}/api/lifecycle/preview", params={
            "template_key": "invalid_template"
        })
        assert response.status_code == 404
        print("✓ Invalid template rejected as expected")


class TestAutomationBots:
    """Automation bots tests"""

    def test_get_summary(self):
        """GET /api/automation/summary - get automation stats"""
        response = requests.get(f"{BASE_URL}/api/automation/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_logs" in data
        assert "payment_reminders" in data
        assert "cancellation_checks" in data
        print(f"✓ Automation summary: {data}")

    def test_payment_reminder_bot(self):
        """POST /api/automation/payment-reminder - run payment reminder bot"""
        response = requests.post(f"{BASE_URL}/api/automation/payment-reminder")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["type"] == "payment_reminder"
        assert "reminders_created" in data
        assert "policy" in data
        print(f"✓ Payment reminder: {data['reminders_created']} reminders created")

    def test_cancellation_check_bot(self):
        """POST /api/automation/cancellation-check - run cancellation check bot"""
        response = requests.post(f"{BASE_URL}/api/automation/cancellation-check")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["type"] == "cancellation_check"
        assert "processed" in data
        print(f"✓ Cancellation check: {data['processed']} processed")

    def test_kitchen_forecast(self):
        """GET /api/automation/kitchen-forecast - 7 day forecast"""
        response = requests.get(f"{BASE_URL}/api/automation/kitchen-forecast", params={
            "days": 7
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["forecast_days"] == 7
        assert len(data["forecast"]) == 7
        # Verify forecast structure
        day = data["forecast"][0]
        assert "date" in day
        assert "day_name" in day
        assert "hotel_guests" in day
        assert "breakfast" in day
        assert "total_meals" in day
        print(f"✓ Kitchen forecast: {len(data['forecast'])} days")


class TestDashboardAndRooms:
    """Dashboard stats and rooms tests"""

    def test_dashboard_stats(self):
        """GET /api/dashboard/stats - get dashboard statistics"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_rooms" in data
        assert "occupancy_rate" in data
        assert data["total_rooms"] == 16
        print(f"✓ Dashboard: {data['total_rooms']} rooms, {data['occupancy_rate']*100}% occupancy")

    def test_get_rooms(self):
        """GET /api/rooms - get room list"""
        response = requests.get(f"{BASE_URL}/api/rooms")
        assert response.status_code == 200
        data = response.json()
        assert "rooms" in data
        assert len(data["rooms"]) > 0
        # Check if prices include Superior (5000 TL) and Family (6000 TL)
        room_prices = {r["room_id"]: r["base_price_try"] for r in data["rooms"]}
        print(f"✓ Rooms: {len(data['rooms'])} room types")
        if "superior" in room_prices:
            print(f"  - Superior: {room_prices['superior']} TL")
        if "family" in room_prices:
            print(f"  - Family: {room_prices['family']} TL")


# Cleanup test data after all tests
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    yield
    # Clean up TEST_ prefixed table reservations
    try:
        res = requests.get(f"{BASE_URL}/api/table-reservations", params={"limit": 100})
        if res.status_code == 200:
            for r in res.json().get("reservations", []):
                if r.get("guest_name", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/table-reservations/{r['id']}")
                    print(f"Cleaned up: {r['id']}")
    except Exception as e:
        print(f"Cleanup error: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
