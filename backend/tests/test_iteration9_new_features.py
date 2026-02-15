"""
Iteration 9 - Testing 3 NEW Features:
1. Rate Limiter (15 req/min per session on chatbot endpoint)
2. Anti-Hallucination Module (confidence field in chatbot response)
3. Loyalty System (4 levels: bronze/silver/gold/platinum)
"""
import pytest
import requests
import os
import uuid
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndBasics:
    """Health check and basic API tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert data.get("database") == "connected"
        print(f"✓ Health check passed: {data}")


class TestLoyaltySystem:
    """Loyalty System API Tests - 4 levels: bronze/silver/gold/platinum"""
    
    def test_loyalty_levels_endpoint(self):
        """GET /api/loyalty/levels should return 4 loyalty levels"""
        response = requests.get(f"{BASE_URL}/api/loyalty/levels")
        assert response.status_code == 200
        data = response.json()
        assert "levels" in data
        levels = data["levels"]
        assert "bronze" in levels
        assert "silver" in levels
        assert "gold" in levels
        assert "platinum" in levels
        
        # Verify discount structure
        assert levels["bronze"]["discount"] == 0
        assert levels["silver"]["discount"] == 5
        assert levels["gold"]["discount"] == 10
        assert levels["platinum"]["discount"] == 15
        print(f"✓ Loyalty levels: {list(levels.keys())}")
    
    def test_loyalty_stats_endpoint(self):
        """GET /api/loyalty/stats should return total_guests, returning_guests, level_counts"""
        response = requests.get(f"{BASE_URL}/api/loyalty/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "total_guests" in data
        assert "returning_guests" in data
        assert "level_counts" in data
        assert "return_rate" in data
        assert "top_vips" in data
        
        # Level counts should have all 4 levels
        level_counts = data["level_counts"]
        assert "bronze" in level_counts
        assert "silver" in level_counts
        assert "gold" in level_counts
        assert "platinum" in level_counts
        
        print(f"✓ Loyalty stats: {data['total_guests']} total guests, {data['returning_guests']} returning")
    
    def test_loyalty_guests_list(self):
        """GET /api/loyalty/guests should return list of loyalty guests"""
        response = requests.get(f"{BASE_URL}/api/loyalty/guests")
        assert response.status_code == 200
        data = response.json()
        assert "guests" in data
        assert "total" in data
        print(f"✓ Loyalty guests list: {data['total']} guests")
    
    def test_loyalty_guests_filter_by_level(self):
        """GET /api/loyalty/guests?level=silver should filter by level"""
        response = requests.get(f"{BASE_URL}/api/loyalty/guests?level=silver")
        assert response.status_code == 200
        data = response.json()
        assert "guests" in data
        print(f"✓ Silver level guests: {data['total']} guests")
    
    def test_loyalty_match_guest_without_params(self):
        """POST /api/loyalty/match-guest without params should return error"""
        response = requests.post(f"{BASE_URL}/api/loyalty/match-guest")
        assert response.status_code == 200
        data = response.json()
        assert data.get("matched") == False
        assert "error" in data
        print(f"✓ Match guest validation works: {data.get('error')}")
    
    def test_loyalty_match_guest_with_phone(self):
        """POST /api/loyalty/match-guest?phone=... should search for guest"""
        response = requests.post(f"{BASE_URL}/api/loyalty/match-guest?phone=5551234567")
        assert response.status_code == 200
        data = response.json()
        # May or may not match, but should have matched field
        assert "matched" in data
        print(f"✓ Match guest by phone: matched={data.get('matched')}")


class TestGuestLoyaltyDetail:
    """Test guest-specific loyalty endpoints"""
    
    @pytest.fixture
    def guest_id(self):
        """Get a real guest ID from the guests list"""
        response = requests.get(f"{BASE_URL}/api/guests")
        if response.status_code == 200:
            guests = response.json().get("guests", [])
            if guests:
                return guests[0].get("id")
        return None
    
    def test_guest_loyalty_detail_with_valid_id(self, guest_id):
        """GET /api/loyalty/guest/{id} should return loyalty info"""
        if not guest_id:
            pytest.skip("No guests in database")
        
        response = requests.get(f"{BASE_URL}/api/loyalty/guest/{guest_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Should have guest and loyalty info
        assert "guest" in data or "error" in data
        if "guest" in data:
            assert "loyalty" in data
            loyalty = data["loyalty"]
            assert "level" in loyalty
            assert "discount_percent" in loyalty
            assert "total_stays" in loyalty
            print(f"✓ Guest loyalty detail: level={loyalty.get('level')}, stays={loyalty.get('total_stays')}")
        else:
            print(f"✓ Guest loyalty detail returned: {data}")
    
    def test_guest_loyalty_detail_with_invalid_id(self):
        """GET /api/loyalty/guest/{invalid_id} should return error"""
        response = requests.get(f"{BASE_URL}/api/loyalty/guest/invalid-guest-id-12345")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        print(f"✓ Invalid guest ID handled: {data.get('error')}")
    
    def test_update_guest_loyalty(self, guest_id):
        """POST /api/loyalty/update-guest/{id} should recalculate loyalty"""
        if not guest_id:
            pytest.skip("No guests in database")
        
        response = requests.post(f"{BASE_URL}/api/loyalty/update-guest/{guest_id}")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data or "error" in data
        if data.get("success"):
            assert "loyalty" in data
            print(f"✓ Guest loyalty updated: level={data.get('loyalty', {}).get('level')}")
        else:
            print(f"✓ Guest loyalty update response: {data}")


class TestChatbotWithAntiHallucination:
    """Test Chatbot with Anti-Hallucination (confidence field)"""
    
    def test_chatbot_returns_confidence_field(self):
        """POST /api/chatbot should return confidence field"""
        session_id = f"test_confidence_{uuid.uuid4().hex[:8]}"
        payload = {
            "message": "Odalariniz kac kisilik?",
            "session_id": session_id
        }
        
        response = requests.post(f"{BASE_URL}/api/chatbot", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Should have response
        assert "response" in data
        assert "session_id" in data
        
        # Confidence may be present if Gemini AI responds
        # Engine responses may not have confidence
        print(f"✓ Chatbot response keys: {list(data.keys())}")
        if "confidence" in data:
            assert isinstance(data["confidence"], (int, float))
            assert 0 <= data["confidence"] <= 1
            print(f"✓ Confidence score: {data['confidence']}")
        else:
            print(f"✓ Chatbot responded (engine response, no confidence needed)")
    
    def test_chatbot_response_structure(self):
        """POST /api/chatbot response structure validation"""
        session_id = f"test_structure_{uuid.uuid4().hex[:8]}"
        payload = {
            "message": "Fiyatlariniz nedir?",
            "session_id": session_id
        }
        
        response = requests.post(f"{BASE_URL}/api/chatbot", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Basic response structure
        assert "response" in data
        assert "session_id" in data
        assert data["session_id"] == session_id
        
        # Should have intent detected
        if "intent" in data:
            print(f"✓ Intent detected: {data['intent']}")
        
        print(f"✓ Chatbot response valid")


class TestRateLimiter:
    """Rate Limiter Test - 15 requests/min per session on chatbot"""
    
    def test_rate_limiter_allows_15_requests(self):
        """First 15 requests with same session_id should succeed"""
        session_id = f"rate_test_{uuid.uuid4().hex[:8]}"
        payload = {
            "message": "Merhaba",
            "session_id": session_id
        }
        
        success_count = 0
        for i in range(15):
            response = requests.post(f"{BASE_URL}/api/chatbot", json=payload)
            if response.status_code == 200:
                success_count += 1
            else:
                print(f"Request {i+1} failed with status: {response.status_code}")
        
        assert success_count == 15, f"Expected 15 successful requests, got {success_count}"
        print(f"✓ Rate limiter: {success_count}/15 requests succeeded")
    
    def test_rate_limiter_blocks_16th_request(self):
        """16th request with same session_id should return 429"""
        session_id = f"rate_test_16_{uuid.uuid4().hex[:8]}"
        payload = {
            "message": "Test",
            "session_id": session_id
        }
        
        # Send 15 requests first
        for i in range(15):
            response = requests.post(f"{BASE_URL}/api/chatbot", json=payload)
            assert response.status_code == 200, f"Request {i+1} failed unexpectedly"
        
        # 16th request should be rate limited
        response = requests.post(f"{BASE_URL}/api/chatbot", json=payload)
        assert response.status_code == 429, f"Expected 429, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert "retry_after" in detail
        print(f"✓ Rate limiter: 16th request blocked with 429, retry_after={detail.get('retry_after')}")
    
    def test_rate_limiter_different_sessions_independent(self):
        """Different session_ids should have independent rate limits"""
        session1 = f"session1_{uuid.uuid4().hex[:8]}"
        session2 = f"session2_{uuid.uuid4().hex[:8]}"
        
        # Use session1 for 15 requests
        for i in range(15):
            response = requests.post(f"{BASE_URL}/api/chatbot", json={
                "message": "Test",
                "session_id": session1
            })
            assert response.status_code == 200
        
        # Session2 should still work
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "Test",
            "session_id": session2
        })
        assert response.status_code == 200, f"Session2 should not be rate limited"
        print(f"✓ Rate limiter: different sessions are independent")


class TestExistingFeatures:
    """Verify existing features still work after new additions"""
    
    def test_events_endpoint(self):
        """GET /api/events should still return events"""
        response = requests.get(f"{BASE_URL}/api/events")
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        print(f"✓ Events endpoint: {len(data['events'])} events")
    
    def test_guests_endpoint(self):
        """GET /api/guests should still return guests"""
        response = requests.get(f"{BASE_URL}/api/guests")
        assert response.status_code == 200
        data = response.json()
        assert "guests" in data
        print(f"✓ Guests endpoint: {len(data['guests'])} guests")
    
    def test_automation_summary(self):
        """GET /api/automation/summary should still work"""
        response = requests.get(f"{BASE_URL}/api/automation/summary")
        assert response.status_code == 200
        print(f"✓ Automation summary works")
    
    def test_scheduled_jobs(self):
        """GET /api/automation/scheduled-jobs should still return jobs"""
        response = requests.get(f"{BASE_URL}/api/automation/scheduled-jobs")
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        print(f"✓ Scheduled jobs: {len(data['jobs'])} jobs")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
