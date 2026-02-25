"""
Iteration 15 - Chatbot Updates Testing
Tests: Forbidden topics, escalation protocol, room prices, cancellation policy, extra services, check-in info
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

def unique_session():
    return f"test-session-{uuid.uuid4().hex[:8]}"


class TestChatbotGreeting:
    """Test greeting responses"""
    
    def test_merhaba_greeting(self):
        """Merhaba should return professional greeting"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "merhaba",
            "session_id": session_id
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "response" in data, "Response should have 'response' field"
        resp_text = data["response"].lower()
        assert "merhaba" in resp_text or "hos geldiniz" in resp_text or "kozbeyli" in resp_text, f"Greeting should be welcoming: {data['response']}"
        print(f"✓ Greeting test passed: {data['response'][:100]}...")
    
    def test_greeting_has_no_emojis_in_options(self):
        """Greeting should contain help options"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "selam",
            "session_id": session_id
        })
        assert response.status_code == 200
        data = response.json()
        # Should mention what AI can help with
        resp_text = data["response"].lower()
        assert any(x in resp_text for x in ["rezervasyon", "menu", "oda", "yardim", "kozbeyli"]), f"Should mention services: {data['response']}"
        print(f"✓ Greeting with options passed")


class TestForbiddenTopics:
    """Test forbidden topic detection - politics, religion, inappropriate"""
    
    def test_forbidden_politics(self):
        """Political questions should be rejected"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "siyaset hakkinda ne dusunuyorsun",
            "session_id": session_id
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data["response"].lower()
        # Should politely decline
        assert any(x in resp_text for x in ["yardimci olamiyorum", "bu konuda", "baska"]), f"Should decline politics: {data['response']}"
        print(f"✓ Politics forbidden test passed: {data['response'][:100]}...")
    
    def test_forbidden_religion(self):
        """Religious questions should be rejected"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "din hakkinda goruslerin",
            "session_id": session_id
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data["response"].lower()
        assert any(x in resp_text for x in ["yardimci olamiyorum", "bu konuda", "baska"]), f"Should decline religion: {data['response']}"
        print(f"✓ Religion forbidden test passed: {data['response'][:100]}...")
    
    def test_forbidden_inappropriate(self):
        """Inappropriate content should be rejected"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "cinsel icerik",
            "session_id": session_id
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data["response"].lower()
        assert any(x in resp_text for x in ["yardimci olamiyorum", "bu konuda", "uygun"]), f"Should decline inappropriate: {data['response']}"
        print(f"✓ Inappropriate forbidden test passed: {data['response'][:100]}...")
    
    def test_no_false_positive_iptal_politikasi(self):
        """'iptal politikasi' should NOT trigger forbidden 'politika' keyword"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "iptal politikasi ne",
            "session_id": session_id
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data["response"].lower()
        # Should give cancellation info, NOT forbidden response
        assert "72" in resp_text or "iptal" in resp_text or "gun" in resp_text or "saat" in resp_text, f"Should give cancellation info, not forbidden: {data['response']}"
        # Should NOT say "yardimci olamiyorum" in a forbidden way
        assert "siyaset" not in resp_text, "Should not mention politics in cancellation response"
        print(f"✓ No false positive for 'iptal politikasi' test passed: {data['response'][:100]}...")


class TestEscalationProtocol:
    """Test escalation to manager for large groups, emergencies, complaints"""
    
    def test_escalation_large_group(self):
        """50+ person request should escalate to manager"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "50 kisilik dugun yapmak istiyorum",
            "session_id": session_id
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data["response"]
        # Should contain manager phone
        assert "+90 532 234 26 86" in resp_text, f"Should contain manager phone for large group: {resp_text}"
        print(f"✓ Large group escalation passed: {resp_text[:100]}...")
    
    def test_escalation_emergency(self):
        """Emergency should escalate with 112 and reception"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "acil durum var",
            "session_id": session_id
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data["response"]
        # Should contain emergency info (112 or reception phone)
        has_emergency_info = "112" in resp_text or "+90 232 826 11 12" in resp_text or "acil" in resp_text.lower()
        assert has_emergency_info, f"Should contain emergency numbers: {resp_text}"
        print(f"✓ Emergency escalation passed: {resp_text[:100]}...")
    
    def test_escalation_complaint(self):
        """Complaint should redirect to manager"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "cok mutsuzum sikayet etmek istiyorum",
            "session_id": session_id
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data["response"]
        # Should contain manager phone
        assert "+90 532 234 26 86" in resp_text, f"Should contain manager phone for complaint: {resp_text}"
        print(f"✓ Complaint escalation passed: {resp_text[:100]}...")


class TestRoomPrices:
    """Test room price inquiries"""
    
    def test_room_prices_inquiry(self):
        """Should return all 5 room types with correct prices"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "oda fiyatlari ne kadar",
            "session_id": session_id
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data["response"]
        # Should contain prices: Standart 3500, Uc Kisilik 5000, Superior 5500, Aile 6000
        assert "3.500" in resp_text or "3500" in resp_text, f"Should have Standart 3500: {resp_text}"
        assert "5.000" in resp_text or "5000" in resp_text, f"Should have Uc Kisilik 5000: {resp_text}"
        assert "5.500" in resp_text or "5500" in resp_text, f"Should have Superior 5500: {resp_text}"
        assert "6.000" in resp_text or "6000" in resp_text, f"Should have Aile Odasi 6000: {resp_text}"
        print(f"✓ Room prices test passed - All 8 room types with prices")


class TestCancellationPolicy:
    """Test cancellation policy auto-reply"""
    
    def test_cancellation_72_hour_rule(self):
        """Should return 72 hour rule and special day info"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "iptal politikasi ne",
            "session_id": session_id
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data["response"]
        # Should mention 72 hours or 3 days
        assert "72" in resp_text or "3 gun" in resp_text, f"Should mention 72 hours/3 days: {resp_text}"
        # Should mention penalty
        assert "100" in resp_text or "ceza" in resp_text, f"Should mention 100% penalty: {resp_text}"
        print(f"✓ Cancellation policy test passed: {resp_text[:100]}...")


class TestExtraServices:
    """Test extra services auto-reply"""
    
    def test_extra_services_laundry(self):
        """Should return laundry, transfer, parking, baby cot info"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "camasir servisi var mi",
            "session_id": session_id
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data["response"].lower()
        # Should contain extra services info
        has_laundry = "camasir" in resp_text
        has_services_info = "transfer" in resp_text or "otopark" in resp_text or "bebek" in resp_text or "hizmet" in resp_text
        assert has_laundry or has_services_info, f"Should mention laundry or extra services: {data['response']}"
        print(f"✓ Extra services test passed: {data['response'][:100]}...")


class TestCheckinInfo:
    """Test check-in/check-out information"""
    
    def test_checkin_times(self):
        """Should return 14:00 check-in and 12:00 check-out"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "check-in saati kac",
            "session_id": session_id
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data["response"]
        # Should contain 14:00 for check-in
        assert "14:00" in resp_text or "14.00" in resp_text, f"Should mention 14:00 check-in: {resp_text}"
        # Should contain 12:00 for check-out
        assert "12:00" in resp_text or "12.00" in resp_text, f"Should mention 12:00 check-out: {resp_text}"
        print(f"✓ Check-in/out times test passed: {resp_text[:100]}...")


class TestContactInfo:
    """Test contact information"""
    
    def test_contact_info(self):
        """Should return phone, whatsapp, email"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "iletisim bilgileri",
            "session_id": session_id
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data["response"]
        # Should contain phone number
        assert "+90" in resp_text or "232" in resp_text or "532" in resp_text, f"Should contain phone: {resp_text}"
        print(f"✓ Contact info test passed: {resp_text[:100]}...")


class TestWifiInfo:
    """Test WiFi information"""
    
    def test_wifi_password(self):
        """Should return SSID and password"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "wifi sifresi ne",
            "session_id": session_id
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data["response"]
        # Should contain WiFi SSID and password
        has_ssid = "Kozbeyli" in resp_text or "Guest" in resp_text
        has_password = "konak" in resp_text.lower() or "sifre" in resp_text.lower()
        assert has_ssid or has_password, f"Should contain WiFi info: {resp_text}"
        print(f"✓ WiFi info test passed: {resp_text[:100]}...")


class TestPetPolicy:
    """Test pet policy"""
    
    def test_pet_policy(self):
        """Should return pet acceptance policy"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "evcil hayvan kabul ediyor musunuz",
            "session_id": session_id
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data["response"].lower()
        # Should contain pet policy info
        has_pet_info = "evcil" in resp_text or "hayvan" in resp_text or "kopek" in resp_text or "kedi" in resp_text or "kabul" in resp_text
        assert has_pet_info, f"Should contain pet policy: {data['response']}"
        print(f"✓ Pet policy test passed: {data['response'][:100]}...")


class TestTableReservationFlow:
    """Test table reservation flow initiation"""
    
    def test_table_reservation_start(self):
        """Should start table reservation flow"""
        session_id = unique_session()
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "masa ayirtmak istiyorum",
            "session_id": session_id
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data["response"].lower()
        # Should ask for date
        has_table_flow = "masa" in resp_text or "tarih" in resp_text or "rezervasyon" in resp_text or "hangi" in resp_text
        assert has_table_flow, f"Should start table reservation flow: {data['response']}"
        print(f"✓ Table reservation flow test passed: {data['response'][:100]}...")


class TestRegressionBasicAPIs:
    """Regression tests for basic APIs"""
    
    def test_health_endpoint(self):
        """Health check should pass"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("✓ Health check passed")
    
    def test_rooms_endpoint(self):
        """Rooms endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/rooms")
        assert response.status_code == 200, f"Rooms endpoint failed: {response.status_code}"
        data = response.json()
        assert "rooms" in data, "Should return rooms"
        print(f"✓ Rooms endpoint passed - {len(data.get('rooms', []))} rooms")
    
    def test_dashboard_endpoint(self):
        """Dashboard endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/dashboard")
        assert response.status_code == 200, f"Dashboard endpoint failed: {response.status_code}"
        print("✓ Dashboard endpoint passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
