"""
Iteration 18 - Test Removed Features (Kitchen, Financials, Pricing/Revenue) and Celery Task Queue
Tests:
- Removed features should return 404
- Celery scheduled jobs endpoint
- Celery task execution endpoints
- Group notifications with celery source
- WhatsApp/Instagram webhook status
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndRemovedFeatures:
    """Test health endpoint and verify removed features return 404"""
    
    def test_health_endpoint(self):
        """GET /api/health should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print("✅ Health endpoint: healthy")
    
    def test_kitchen_orders_removed(self):
        """GET /api/kitchen/orders should return 404 (removed feature)"""
        response = requests.get(f"{BASE_URL}/api/kitchen/orders", timeout=10)
        assert response.status_code == 404
        print("✅ Kitchen orders endpoint returns 404 (removed)")
    
    def test_kitchen_notifications_removed(self):
        """GET /api/kitchen/notifications should return 404 (removed feature)"""
        response = requests.get(f"{BASE_URL}/api/kitchen/notifications", timeout=10)
        assert response.status_code == 404
        print("✅ Kitchen notifications endpoint returns 404 (removed)")
    
    def test_financials_income_removed(self):
        """GET /api/financials/income should return 404 (removed feature)"""
        response = requests.get(f"{BASE_URL}/api/financials/income", timeout=10)
        assert response.status_code == 404
        print("✅ Financials income endpoint returns 404 (removed)")
    
    def test_financials_expense_removed(self):
        """GET /api/financials/expense should return 404 (removed feature)"""
        response = requests.get(f"{BASE_URL}/api/financials/expense", timeout=10)
        assert response.status_code == 404
        print("✅ Financials expense endpoint returns 404 (removed)")
    
    def test_financials_monthly_removed(self):
        """GET /api/financials/monthly should return 404 (removed feature)"""
        response = requests.get(f"{BASE_URL}/api/financials/monthly", timeout=10)
        assert response.status_code == 404
        print("✅ Financials monthly endpoint returns 404 (removed)")
    
    def test_revenue_pricing_calculate_removed(self):
        """GET /api/revenue/pricing/calculate should return 404 (removed feature)"""
        response = requests.get(f"{BASE_URL}/api/revenue/pricing/calculate", timeout=10)
        assert response.status_code == 404
        print("✅ Revenue pricing calculate endpoint returns 404 (removed)")
    
    def test_revenue_forecast_removed(self):
        """GET /api/revenue/forecast should return 404 (removed feature)"""
        response = requests.get(f"{BASE_URL}/api/revenue/forecast", timeout=10)
        assert response.status_code == 404
        print("✅ Revenue forecast endpoint returns 404 (removed)")


class TestCeleryScheduledJobs:
    """Test Celery beat scheduled jobs endpoint"""
    
    def test_scheduled_jobs_returns_6_jobs(self):
        """GET /api/automation/scheduled-jobs should return 6 Celery beat jobs"""
        response = requests.get(f"{BASE_URL}/api/automation/scheduled-jobs", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert data["total"] == 6
        
        job_names = [job["name"] for job in data["jobs"]]
        expected_jobs = [
            "breakfast-prep",
            "morning-reminders", 
            "checkout-cleaning",
            "evening-room-check",
            "whatsapp-reservation-reminders",
            "whatsapp-checkout-thanks"
        ]
        for expected in expected_jobs:
            assert expected in job_names, f"Missing job: {expected}"
        
        # Verify all jobs are active
        for job in data["jobs"]:
            assert job["status"] == "active"
        
        print(f"✅ Scheduled jobs: {data['total']} jobs active")


class TestCeleryTaskExecution:
    """Test Celery task execution via POST endpoints"""
    
    def test_breakfast_notification_task(self):
        """POST /api/automation/breakfast-notification should queue task"""
        response = requests.post(f"{BASE_URL}/api/automation/breakfast-notification", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["type"] == "breakfast_prep"
        assert "Gorev kuyruga eklendi" in data["message"]
        print("✅ Breakfast notification task queued")
    
    def test_morning_reminders_task(self):
        """POST /api/automation/morning-reminders should queue task"""
        response = requests.post(f"{BASE_URL}/api/automation/morning-reminders", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["type"] == "morning_reminders"
        assert "Gorev kuyruga eklendi" in data["message"]
        print("✅ Morning reminders task queued")
    
    def test_cleaning_notification_task(self):
        """POST /api/automation/cleaning-notification should queue task"""
        response = requests.post(f"{BASE_URL}/api/automation/cleaning-notification", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["type"] == "checkout_cleaning"
        assert "Gorev kuyruga eklendi" in data["message"]
        print("✅ Cleaning notification task queued")
    
    def test_evening_room_check_task(self):
        """POST /api/automation/evening-room-check should queue task"""
        response = requests.post(f"{BASE_URL}/api/automation/evening-room-check", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["type"] == "evening_room_check"
        assert "Gorev kuyruga eklendi" in data["message"]
        print("✅ Evening room check task queued")


class TestCeleryGroupNotifications:
    """Test group notifications from Celery tasks"""
    
    def test_group_notifications_have_celery_source(self):
        """GET /api/automation/group-notifications should return notifications from celery"""
        # Wait a bit for queued tasks to execute
        time.sleep(2)
        
        response = requests.get(f"{BASE_URL}/api/automation/group-notifications", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        
        # Check there are notifications with celery source
        celery_notifications = [n for n in data["notifications"] if n.get("source") == "celery"]
        assert len(celery_notifications) > 0, "No celery-sourced notifications found"
        
        # Verify notification structure
        sample = celery_notifications[0]
        assert "id" in sample
        assert "type" in sample
        assert "message" in sample
        assert "status" in sample
        assert sample["source"] == "celery"
        
        print(f"✅ Group notifications: {len(celery_notifications)} from celery source")


class TestWhatsAppInstagramStatus:
    """Test WhatsApp and Instagram webhook status"""
    
    def test_webhooks_status_both_platforms(self):
        """GET /api/webhooks/status should return both WhatsApp and Instagram statuses"""
        response = requests.get(f"{BASE_URL}/api/webhooks/status", timeout=10)
        assert response.status_code == 200
        data = response.json()
        
        # Check WhatsApp status
        assert "whatsapp" in data
        assert "verify_token" in data["whatsapp"]
        assert "total_messages" in data["whatsapp"]
        
        # Check Instagram status
        assert "instagram" in data
        assert "verify_token" in data["instagram"]
        assert "total_messages" in data["instagram"]
        
        print(f"✅ Webhooks status: WhatsApp msgs={data['whatsapp']['total_messages']}, Instagram msgs={data['instagram']['total_messages']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
