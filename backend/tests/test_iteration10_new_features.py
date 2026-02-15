"""
Iteration 10 - Testing 3 NEW Features:
1. 18:00 Evening Room Check automation
2. Dynamic real-time dashboard with live data
3. Multi-language support (TR/EN/DE/FR/RU)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEveningRoomCheckAutomation:
    """Tests for the new 18:00 evening room check feature"""

    def test_evening_room_check_endpoint_exists(self):
        """POST /api/automation/evening-room-check should return notification data"""
        response = requests.post(f"{BASE_URL}/api/automation/evening-room-check")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Expected success=True"
        assert data.get("type") == "evening_room_check", f"Expected type='evening_room_check', got {data.get('type')}"
        # notification can be None if no checkouts today
        assert "notification" in data, "Expected 'notification' key in response"
        
        # Verify notification has expected fields when present
        if data.get("notification"):
            notif = data["notification"]
            assert "message" in notif, "Notification should have 'message'"
            assert "type" in notif, "Notification should have 'type'"
            assert notif["type"] == "evening_room_check"

    def test_scheduled_jobs_includes_evening_check(self):
        """GET /api/automation/scheduled-jobs should show 4 jobs including evening_room_check"""
        response = requests.get(f"{BASE_URL}/api/automation/scheduled-jobs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "jobs" in data, "Expected 'jobs' key in response"
        jobs = data["jobs"]
        
        # Should have 4 jobs now (breakfast_prep, morning_reminders, checkout_cleaning, evening_room_check)
        assert len(jobs) >= 4, f"Expected at least 4 scheduled jobs, got {len(jobs)}"
        
        # Check evening_room_check job exists
        job_ids = [j.get("id") for j in jobs]
        assert "evening_room_check" in job_ids, f"evening_room_check not found in jobs: {job_ids}"
        
        # Verify evening_room_check job properties
        evening_job = next((j for j in jobs if j.get("id") == "evening_room_check"), None)
        assert evening_job is not None, "Evening room check job should exist"
        assert evening_job.get("name") == "Aksam Oda Kontrolu", f"Expected name 'Aksam Oda Kontrolu', got {evening_job.get('name')}"
        assert evening_job.get("status") == "active", f"Evening job should be active, got {evening_job.get('status')}"

    def test_automation_summary_includes_evening_checks(self):
        """GET /api/automation/summary should include evening_checks count"""
        response = requests.get(f"{BASE_URL}/api/automation/summary")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "evening_checks" in data, f"Expected 'evening_checks' in summary. Got keys: {list(data.keys())}"
        assert isinstance(data["evening_checks"], int), "evening_checks should be an integer"

    def test_evening_room_check_creates_log(self):
        """Running evening room check should create an automation log"""
        # Run the evening check
        response = requests.post(f"{BASE_URL}/api/automation/evening-room-check")
        assert response.status_code == 200
        
        # Check logs contain evening_room_check
        logs_response = requests.get(f"{BASE_URL}/api/automation/logs?log_type=evening_room_check&limit=5")
        assert logs_response.status_code == 200
        
        logs_data = logs_response.json()
        assert "logs" in logs_data


class TestDynamicDashboard:
    """Tests for the enhanced dynamic dashboard with live data"""

    def test_dashboard_stats_returns_expected_fields(self):
        """GET /api/dashboard/stats should return all required fields"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Check for original fields
        original_fields = ["total_rooms", "occupied_rooms", "available_rooms", "occupancy_rate",
                         "total_guests", "total_tasks", "pending_tasks", "total_reservations",
                         "active_events", "housekeeping_pending", "ratings", "recent_tasks"]
        
        for field in original_fields:
            assert field in data, f"Missing expected field: {field}"
        
        # Check for NEW dashboard fields
        new_fields = ["weekly_trend", "todays_checkins", "todays_checkouts", 
                     "monthly_revenue", "rooms_list", "room_status_counts", "recent_activity"]
        
        for field in new_fields:
            assert field in data, f"Missing NEW field: {field}"

    def test_weekly_trend_data_structure(self):
        """weekly_trend should have 7 days of data with correct structure"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        
        data = response.json()
        weekly_trend = data.get("weekly_trend", [])
        
        # Should have 7 days
        assert len(weekly_trend) == 7, f"Expected 7 days in weekly_trend, got {len(weekly_trend)}"
        
        # Check structure of each day
        for day in weekly_trend:
            assert "date" in day, "Each day should have 'date'"
            assert "day" in day, "Each day should have 'day' (day name)"
            assert "occupied" in day, "Each day should have 'occupied' count"
            assert "rate" in day, "Each day should have 'rate' (occupancy rate)"
            assert isinstance(day["rate"], int) or isinstance(day["rate"], float), "Rate should be numeric"

    def test_todays_checkins_checkouts_are_integers(self):
        """todays_checkins and todays_checkouts should be integers"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data.get("todays_checkins"), int), "todays_checkins should be int"
        assert isinstance(data.get("todays_checkouts"), int), "todays_checkouts should be int"

    def test_monthly_revenue_is_numeric(self):
        """monthly_revenue should be a number"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        
        data = response.json()
        revenue = data.get("monthly_revenue")
        assert isinstance(revenue, (int, float)), f"monthly_revenue should be numeric, got {type(revenue)}"

    def test_rooms_list_returns_room_data(self):
        """rooms_list should contain room objects with status field"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        
        data = response.json()
        rooms_list = data.get("rooms_list", [])
        
        # Should have rooms
        assert isinstance(rooms_list, list), "rooms_list should be a list"
        
        # If rooms exist, check structure - rooms may have 'id' or 'room_id' or just 'status'
        if len(rooms_list) > 0:
            room = rooms_list[0]
            # At minimum, status should exist
            assert "status" in room, "Room should have 'status'"

    def test_room_status_counts_structure(self):
        """room_status_counts should be a dict with status counts"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        
        data = response.json()
        room_status_counts = data.get("room_status_counts", {})
        
        assert isinstance(room_status_counts, dict), "room_status_counts should be a dict"

    def test_recent_activity_structure(self):
        """recent_activity should contain activity logs"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        
        data = response.json()
        recent_activity = data.get("recent_activity", [])
        
        assert isinstance(recent_activity, list), "recent_activity should be a list"


class TestMultiLanguageSupport:
    """Tests for i18n multi-language support (TR/EN/DE/FR/RU)"""

    def test_languages_list_returns_5_languages(self):
        """GET /api/i18n should return 5 languages"""
        response = requests.get(f"{BASE_URL}/api/i18n")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "languages" in data, "Expected 'languages' key"
        
        languages = data["languages"]
        assert len(languages) == 5, f"Expected 5 languages, got {len(languages)}"
        
        # Check language codes
        codes = [lang["code"] for lang in languages]
        expected_codes = ["tr", "en", "de", "fr", "ru"]
        for code in expected_codes:
            assert code in codes, f"Language code '{code}' not found in {codes}"

    def test_english_translations(self):
        """GET /api/i18n/en should return English translations"""
        response = requests.get(f"{BASE_URL}/api/i18n/en")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("language") == "en", f"Expected language='en', got {data.get('language')}"
        assert "translations" in data, "Expected 'translations' key"
        
        translations = data["translations"]
        
        # Check some key translations exist
        key_translations = ["dashboard", "rooms", "guests", "reservations", "settings",
                          "occupancy_rate", "todays_checkins", "weekly_trend", "live"]
        
        for key in key_translations:
            assert key in translations, f"Missing translation key: {key}"
        
        # Verify English values
        assert translations.get("dashboard") == "Dashboard"
        assert translations.get("rooms") == "Rooms"
        assert translations.get("guests") == "Guests"
        assert translations.get("live") == "Live"

    def test_turkish_translations(self):
        """GET /api/i18n/tr should return Turkish translations"""
        response = requests.get(f"{BASE_URL}/api/i18n/tr")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("language") == "tr", f"Expected language='tr', got {data.get('language')}"
        
        translations = data["translations"]
        
        # Verify Turkish values
        assert translations.get("rooms") == "Odalar"
        assert translations.get("guests") == "Misafirler"
        assert translations.get("live") == "Canli"
        assert translations.get("reservations") == "Rezervasyonlar"

    def test_german_translations(self):
        """GET /api/i18n/de should return German translations"""
        response = requests.get(f"{BASE_URL}/api/i18n/de")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("language") == "de"
        
        translations = data["translations"]
        assert translations.get("rooms") == "Zimmer"
        assert translations.get("guests") == "Gaste"
        assert translations.get("dashboard") == "Dashboard"

    def test_french_translations(self):
        """GET /api/i18n/fr should return French translations"""
        response = requests.get(f"{BASE_URL}/api/i18n/fr")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("language") == "fr"
        
        translations = data["translations"]
        assert translations.get("rooms") == "Chambres"
        assert translations.get("guests") == "Clients"
        assert translations.get("dashboard") == "Tableau de Bord"

    def test_russian_translations(self):
        """GET /api/i18n/ru should return Russian translations"""
        response = requests.get(f"{BASE_URL}/api/i18n/ru")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("language") == "ru"
        
        translations = data["translations"]
        assert translations.get("rooms") == "Nomera"
        assert translations.get("guests") == "Gosti"

    def test_invalid_language_falls_back_to_turkish(self):
        """GET /api/i18n/invalid should fall back to Turkish"""
        response = requests.get(f"{BASE_URL}/api/i18n/xyz")
        assert response.status_code == 200
        
        data = response.json()
        # Should fall back to Turkish
        assert data.get("language") == "tr", "Invalid language should fall back to 'tr'"

    def test_language_list_structure(self):
        """Each language in the list should have code, name, and flag"""
        response = requests.get(f"{BASE_URL}/api/i18n")
        assert response.status_code == 200
        
        data = response.json()
        for lang in data["languages"]:
            assert "code" in lang, "Language should have 'code'"
            assert "name" in lang, "Language should have 'name'"
            assert "flag" in lang, "Language should have 'flag'"


class TestScheduledJobsComplete:
    """Verify all 4 scheduled jobs are present and active"""

    def test_all_four_jobs_exist(self):
        """Should have exactly 4 scheduled jobs"""
        response = requests.get(f"{BASE_URL}/api/automation/scheduled-jobs")
        assert response.status_code == 200
        
        data = response.json()
        jobs = data.get("jobs", [])
        
        expected_jobs = {
            "breakfast_prep": "Kahvalti Hazirligi",
            "morning_reminders": "Sabah Hatirlama",
            "checkout_cleaning": "Check-out Temizlik",
            "evening_room_check": "Aksam Oda Kontrolu"
        }
        
        job_ids = [j.get("id") for j in jobs]
        
        for job_id, job_name in expected_jobs.items():
            assert job_id in job_ids, f"Job '{job_id}' not found. Found: {job_ids}"
            
            job = next((j for j in jobs if j.get("id") == job_id), None)
            assert job.get("status") == "active", f"Job '{job_id}' should be active"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
