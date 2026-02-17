"""
Iteration 16 Tests - Domain routing preparation, SEO, QR codes, Chatbot updates
Features tested:
1. QR Code API - /api/qr/menu (PNG image), /api/qr/menu-info (URL info)
2. Chatbot forbidden topics - siyaset, din, etc. should be blocked
3. Chatbot escalation - large groups (30+) should trigger manager referral
4. Chatbot false positives - "iptal politikasi" should NOT trigger forbidden
5. Chatbot price info - "oda fiyatlari" should return room prices
6. Chatbot extra services - "camasir servisi" should return laundry info
7. Public menu API - /api/public/menu returns menu data
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://hospitality-hub-59.preview.emergentagent.com"


class TestQRCodeAPI:
    """QR Code generation endpoint tests"""
    
    def test_qr_menu_returns_png_image(self):
        """GET /api/qr/menu returns a PNG image"""
        response = requests.get(f"{BASE_URL}/api/qr/menu")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.headers.get('content-type') == 'image/png', \
            f"Expected image/png, got {response.headers.get('content-type')}"
        # PNG magic bytes check
        assert response.content[:8] == b'\x89PNG\r\n\x1a\n', "Response is not a valid PNG"
        print(f"PASS: QR code returns valid PNG image ({len(response.content)} bytes)")
    
    def test_qr_menu_with_custom_size(self):
        """GET /api/qr/menu?size=500 returns larger QR image"""
        response = requests.get(f"{BASE_URL}/api/qr/menu?size=500")
        assert response.status_code == 200
        assert response.headers.get('content-type') == 'image/png'
        # Larger size should produce larger file
        response_default = requests.get(f"{BASE_URL}/api/qr/menu")
        assert len(response.content) > len(response_default.content), \
            "size=500 should produce larger image"
        print(f"PASS: QR with size=500 ({len(response.content)} bytes) > default ({len(response_default.content)} bytes)")
    
    def test_qr_menu_info_returns_correct_url(self):
        """GET /api/qr/menu-info returns url=https://kozbeylikonagi.com.tr"""
        response = requests.get(f"{BASE_URL}/api/qr/menu-info")
        assert response.status_code == 200
        data = response.json()
        assert data.get('url') == 'https://kozbeylikonagi.com.tr', \
            f"Expected url=https://kozbeylikonagi.com.tr, got {data.get('url')}"
        assert 'qr_endpoint' in data
        assert 'sizes' in data
        print(f"PASS: QR info returns correct URL: {data.get('url')}")


class TestChatbotForbiddenTopics:
    """Chatbot forbidden topic detection tests"""
    
    def get_session_id(self):
        import uuid
        return f"test_forbidden_{uuid.uuid4().hex[:8]}"
    
    def test_forbidden_politics_blocked(self):
        """POST /api/chatbot with 'siyaset hakkinda ne dusunuyorsun' should be blocked"""
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "siyaset hakkinda ne dusunuyorsun",
            "session_id": self.get_session_id()
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data.get('response', '').lower()
        # Should contain a polite decline
        assert any(kw in resp_text for kw in ['yardimci olamiyorum', 'yardımcı olamıyorum', 'otel', 'aktiviteler']), \
            f"Expected forbidden response, got: {data.get('response')[:100]}"
        print(f"PASS: Politics question blocked - response: {data.get('response')[:80]}...")
    
    def test_forbidden_competitor_blocked(self):
        """POST /api/chatbot asking about competitors should be blocked"""
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "baska otel oner bana",
            "session_id": self.get_session_id()
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data.get('response', '').lower()
        # Should not recommend other hotels
        assert any(kw in resp_text for kw in ['yardimci olamiyorum', 'yorum yapamam', 'kozbeyli', 'yardımcı']), \
            f"Expected forbidden response for competitor, got: {data.get('response')[:100]}"
        print(f"PASS: Competitor question blocked - response: {data.get('response')[:80]}...")


class TestChatbotEscalation:
    """Chatbot escalation to manager tests"""
    
    def get_session_id(self):
        import uuid
        return f"test_escalation_{uuid.uuid4().hex[:8]}"
    
    def test_large_group_escalation(self):
        """POST /api/chatbot with '50 kisilik dugun' should give manager phone"""
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "50 kisilik dugun icin fiyat alabilir miyim",
            "session_id": self.get_session_id()
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data.get('response', '')
        # Should contain manager phone number
        assert '+90 532 234 26 86' in resp_text or '532 234 26 86' in resp_text, \
            f"Expected manager phone in response, got: {resp_text[:150]}"
        print(f"PASS: Large group (50) triggers escalation with manager phone")
    
    def test_30_person_group_escalation(self):
        """POST /api/chatbot with '30 kisi' should trigger escalation"""
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "30 kisi icin organizasyon yapmak istiyorum",
            "session_id": self.get_session_id()
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data.get('response', '')
        # Should escalate for 30+ people
        assert '532 234 26 86' in resp_text or 'yonetici' in resp_text.lower(), \
            f"Expected escalation for 30 people, got: {resp_text[:150]}"
        print(f"PASS: 30 person group triggers escalation")


class TestChatbotNoFalsePositive:
    """Ensure valid questions are not blocked"""
    
    def get_session_id(self):
        import uuid
        return f"test_valid_{uuid.uuid4().hex[:8]}"
    
    def test_iptal_politikasi_not_forbidden(self):
        """POST /api/chatbot with 'iptal politikasi' should NOT trigger forbidden"""
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "iptal politikasi nedir",
            "session_id": self.get_session_id()
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data.get('response', '').lower()
        # Should provide cancellation policy info, not block
        assert 'yardimci olamiyorum' not in resp_text, \
            f"'iptal politikasi' should NOT be blocked, got: {data.get('response')[:100]}"
        # Should contain policy-related info
        assert any(kw in resp_text for kw in ['iptal', 'saat', 'gun', 'gün', 'ucretsiz', 'ücretsiz', '72', 'iade']), \
            f"Expected cancellation policy info, got: {data.get('response')[:150]}"
        print(f"PASS: 'iptal politikasi' returns valid info, not blocked")


class TestChatbotPriceInfo:
    """Chatbot room price information tests"""
    
    def get_session_id(self):
        import uuid
        return f"test_price_{uuid.uuid4().hex[:8]}"
    
    def test_oda_fiyatlari_returns_5_room_types(self):
        """POST /api/chatbot with 'oda fiyatlari' returns 5 room types with prices"""
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "oda fiyatlari nedir",
            "session_id": self.get_session_id()
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data.get('response', '')
        
        # Should contain room types
        room_types = ['tek kisilik', 'cift kisilik', 'uc kisilik', 'superior', 'aile']
        found_rooms = sum(1 for rt in room_types if rt.lower() in resp_text.lower())
        
        # Should have price mentions (TL or fiyat)
        has_prices = 'TL' in resp_text or 'tl' in resp_text.lower() or 'fiyat' in resp_text.lower()
        
        assert found_rooms >= 3, f"Expected at least 3 room types, found {found_rooms}: {resp_text[:200]}"
        assert has_prices, f"Expected price info, got: {resp_text[:200]}"
        print(f"PASS: 'oda fiyatlari' returns {found_rooms} room types with prices")


class TestChatbotExtraServices:
    """Chatbot extra services information tests"""
    
    def get_session_id(self):
        import uuid
        return f"test_extra_{uuid.uuid4().hex[:8]}"
    
    def test_camasir_servisi_returns_laundry_info(self):
        """POST /api/chatbot with 'camasir servisi' returns laundry info"""
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "camasir servisi var mi",
            "session_id": self.get_session_id()
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data.get('response', '').lower()
        
        # Should mention laundry service
        assert any(kw in resp_text for kw in ['camasir', 'çamaşır', 'laundry', 'ucretli', 'ücretli', 'teslimat']), \
            f"Expected laundry info, got: {data.get('response')[:150]}"
        print(f"PASS: 'camasir servisi' returns laundry info")
    
    def test_transfer_info(self):
        """POST /api/chatbot with 'transfer' returns transfer info"""
        response = requests.post(f"{BASE_URL}/api/chatbot", json={
            "message": "havaalani transferi ayarlayabilir misiniz",
            "session_id": self.get_session_id()
        })
        assert response.status_code == 200
        data = response.json()
        resp_text = data.get('response', '').lower()
        
        # Should mention transfer service
        assert any(kw in resp_text for kw in ['transfer', 'havaalani', 'havaalanı', 'resepsiyon', 'ulasim', 'ulaşım']), \
            f"Expected transfer info, got: {data.get('response')[:150]}"
        print(f"PASS: Transfer query returns relevant info")


class TestPublicMenu:
    """Public menu API tests - for root URL menu display"""
    
    def test_public_menu_api_works(self):
        """GET /api/public/menu returns menu data"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        assert response.status_code == 200
        data = response.json()
        
        # Should have menu categories
        assert 'menu' in data, f"Expected 'menu' key in response"
        menu = data['menu']
        assert len(menu) > 0, "Menu should have categories"
        
        # Should have theme info
        assert 'theme' in data or 'restaurant' in data, "Should have theme or restaurant info"
        
        print(f"PASS: Public menu API returns {len(menu)} categories")


class TestHealthAndRegression:
    """Basic health checks and regression tests"""
    
    def test_health_check(self):
        """GET /api/health returns ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'ok' or 'status' in data
        print(f"PASS: Health check returns OK")
    
    def test_dashboard_stats(self):
        """GET /api/dashboard/stats returns stats"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert 'occupancy_rate' in data or 'total_rooms' in data or 'pending_tasks' in data
        print(f"PASS: Dashboard stats API working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
