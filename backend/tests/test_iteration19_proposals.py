"""
Iteration 19 - Proposals (Teklif Yonetimi) API Tests
Tests for CRUD operations on proposals: list, create, update status, duplicate, delete
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestProposalsAPI:
    """Proposal Management API Tests"""
    
    # Test data to cleanup
    created_proposal_ids = []
    
    @classmethod
    def setup_class(cls):
        """Setup for test class"""
        cls.session = requests.Session()
        cls.session.headers.update({"Content-Type": "application/json"})
    
    @classmethod
    def teardown_class(cls):
        """Cleanup created test proposals"""
        for proposal_id in cls.created_proposal_ids:
            try:
                cls.session.delete(f"{BASE_URL}/api/proposals/{proposal_id}")
            except:
                pass
    
    def test_01_list_proposals(self):
        """GET /api/proposals - List all proposals"""
        response = self.session.get(f"{BASE_URL}/api/proposals")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "proposals" in data, "Response should contain 'proposals' key"
        assert "total" in data, "Response should contain 'total' key"
        assert isinstance(data["proposals"], list), "Proposals should be a list"
        print(f"PASS: Listed {data['total']} proposals")
    
    def test_02_proposal_stats_summary(self):
        """GET /api/proposals/stats/summary - Get proposal statistics"""
        response = self.session.get(f"{BASE_URL}/api/proposals/stats/summary")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        expected_keys = ["total", "draft", "sent", "accepted", "rejected", "expired", "total_value", "accepted_value", "conversion_rate"]
        for key in expected_keys:
            assert key in data, f"Stats should contain '{key}' key"
        
        print(f"PASS: Stats - Total: {data['total']}, Draft: {data['draft']}, Conversion: {data['conversion_rate']}%")
    
    def test_03_create_proposal(self):
        """POST /api/proposals - Create a new proposal"""
        payload = {
            "customer_name": "TEST_Mehmet Test",
            "customer_phone": "0555 123 4567",
            "customer_email": "test@example.com",
            "event_type": "dugun",
            "event_date": "2026-06-15",
            "guest_count": 80,
            "accommodation_items": [
                {"room_type": "Double Oda (2 Kisilik)", "room_count": 5, "nights": 1, "per_room_price": 3500, "total": 17500, "note": ""}
            ],
            "accommodation_total": 17500,
            "meal_options": [
                {"description": "Kredi Karti ile", "per_person_price": 2500, "guest_count": 80, "payment_method": "kredi_karti", "total": 200000}
            ],
            "meal_total": 200000,
            "extra_services": [
                {"name": "Dekorasyon", "description": "Dugun dekorasyonu", "price": 40000}
            ],
            "extras_total": 40000,
            "grand_total": 257500,
            "discount_amount": 7500,
            "discount_note": "Erken rezervasyon indirimi",
            "validity_days": 15,
            "notes": "Test teklifisi",
            "internal_notes": "Testing icin olusturuldu"
        }
        
        response = self.session.post(f"{BASE_URL}/api/proposals", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "id" in data, "Response should contain 'id'"
        assert "proposal_number" in data, "Response should contain 'proposal_number'"
        assert data["customer_name"] == payload["customer_name"], "Customer name should match"
        assert data["status"] == "draft", "New proposal should have 'draft' status"
        assert data["event_type"] == "dugun", "Event type should match"
        assert data["guest_count"] == 80, "Guest count should match"
        
        # Store for cleanup and further tests
        self.__class__.created_proposal_ids.append(data["id"])
        self.__class__.test_proposal_id = data["id"]
        
        print(f"PASS: Created proposal {data['proposal_number']} with ID {data['id']}")
    
    def test_04_get_proposal_detail(self):
        """GET /api/proposals/{id} - Get single proposal detail"""
        proposal_id = self.__class__.test_proposal_id
        response = self.session.get(f"{BASE_URL}/api/proposals/{proposal_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["id"] == proposal_id, "Proposal ID should match"
        assert data["customer_name"] == "TEST_Mehmet Test", "Customer name should match"
        assert len(data["accommodation_items"]) > 0, "Should have accommodation items"
        assert len(data["meal_options"]) > 0, "Should have meal options"
        
        print(f"PASS: Retrieved proposal {data['proposal_number']} details")
    
    def test_05_update_proposal_status_to_sent(self):
        """PATCH /api/proposals/{id} - Update status to 'sent'"""
        proposal_id = self.__class__.test_proposal_id
        response = self.session.patch(f"{BASE_URL}/api/proposals/{proposal_id}", json={"status": "sent"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "sent", f"Status should be 'sent', got {data['status']}"
        assert data["sent_at"], "sent_at should be populated"
        
        print(f"PASS: Updated proposal status to 'sent'")
    
    def test_06_update_proposal_status_to_accepted(self):
        """PATCH /api/proposals/{id} - Update status to 'accepted'"""
        proposal_id = self.__class__.test_proposal_id
        response = self.session.patch(f"{BASE_URL}/api/proposals/{proposal_id}", json={"status": "accepted"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["status"] == "accepted", f"Status should be 'accepted', got {data['status']}"
        assert data["responded_at"], "responded_at should be populated"
        
        print(f"PASS: Updated proposal status to 'accepted'")
    
    def test_07_stats_after_acceptance(self):
        """GET /api/proposals/stats/summary - Verify stats updated after acceptance"""
        response = self.session.get(f"{BASE_URL}/api/proposals/stats/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert data["accepted"] >= 1, "Accepted count should be at least 1"
        
        print(f"PASS: Stats show {data['accepted']} accepted, total value: {data['total_value']}")
    
    def test_08_duplicate_proposal(self):
        """POST /api/proposals/{id}/duplicate - Duplicate a proposal"""
        proposal_id = self.__class__.test_proposal_id
        response = self.session.post(f"{BASE_URL}/api/proposals/{proposal_id}/duplicate")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["id"] != proposal_id, "Duplicated proposal should have new ID"
        assert data["proposal_number"] != "", "Duplicated proposal should have new number"
        assert data["status"] == "draft", "Duplicated proposal should have 'draft' status"
        assert "(Kopya)" in data["customer_name"], "Customer name should contain '(Kopya)'"
        
        # Store for cleanup
        self.__class__.created_proposal_ids.append(data["id"])
        self.__class__.duplicated_id = data["id"]
        
        print(f"PASS: Duplicated proposal to {data['proposal_number']} with ID {data['id']}")
    
    def test_09_delete_duplicated_proposal(self):
        """DELETE /api/proposals/{id} - Delete the duplicated proposal"""
        duplicated_id = self.__class__.duplicated_id
        response = self.session.delete(f"{BASE_URL}/api/proposals/{duplicated_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("deleted") == True, "Response should confirm deletion"
        
        # Verify it's gone
        verify_response = self.session.get(f"{BASE_URL}/api/proposals/{duplicated_id}")
        assert verify_response.status_code == 404, "Deleted proposal should return 404"
        
        # Remove from cleanup list since already deleted
        if duplicated_id in self.__class__.created_proposal_ids:
            self.__class__.created_proposal_ids.remove(duplicated_id)
        
        print(f"PASS: Deleted duplicated proposal {duplicated_id}")
    
    def test_10_filter_proposals_by_status(self):
        """GET /api/proposals?status=draft - Filter proposals by status"""
        response = self.session.get(f"{BASE_URL}/api/proposals?status=draft")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # All returned proposals should be draft
        for proposal in data["proposals"]:
            assert proposal["status"] == "draft", f"All proposals should be 'draft', got {proposal['status']}"
        
        print(f"PASS: Filtered {data['total']} draft proposals")
    
    def test_11_update_proposal_status_to_rejected(self):
        """PATCH /api/proposals/{id} - Create another proposal and reject it"""
        # Create a new proposal for rejection test
        payload = {
            "customer_name": "TEST_Reddedilecek",
            "customer_phone": "0555 111 2222",
            "event_type": "kurumsal",
            "event_date": "2026-07-01",
            "guest_count": 30,
            "grand_total": 50000
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/proposals", json=payload)
        assert create_response.status_code == 200
        proposal_id = create_response.json()["id"]
        self.__class__.created_proposal_ids.append(proposal_id)
        
        # First send it
        self.session.patch(f"{BASE_URL}/api/proposals/{proposal_id}", json={"status": "sent"})
        
        # Then reject it
        response = self.session.patch(f"{BASE_URL}/api/proposals/{proposal_id}", json={"status": "rejected"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "rejected", f"Status should be 'rejected', got {data['status']}"
        assert data["responded_at"], "responded_at should be populated for rejected"
        
        print(f"PASS: Proposal {proposal_id} rejected successfully")
    
    def test_12_proposal_404_for_nonexistent(self):
        """GET /api/proposals/{id} - Should return 404 for nonexistent proposal"""
        response = self.session.get(f"{BASE_URL}/api/proposals/nonexistent-id-12345")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        
        print(f"PASS: Returns 404 for nonexistent proposal")
    
    def test_13_check_existing_proposals(self):
        """Verify existing seed proposals are present"""
        response = self.session.get(f"{BASE_URL}/api/proposals")
        assert response.status_code == 200
        
        data = response.json()
        proposal_numbers = [p["proposal_number"] for p in data["proposals"]]
        
        # Check at least original seed proposals exist or some proposals exist
        assert len(data["proposals"]) >= 2, "Should have at least 2 proposals (seed + test)"
        
        print(f"PASS: Found {data['total']} total proposals in system")
    
    def test_14_cleanup_test_proposals(self):
        """Clean up all TEST_ prefixed proposals"""
        # Delete remaining test proposals
        for proposal_id in list(self.__class__.created_proposal_ids):
            try:
                self.session.delete(f"{BASE_URL}/api/proposals/{proposal_id}")
                self.__class__.created_proposal_ids.remove(proposal_id)
            except:
                pass
        
        print(f"PASS: Cleaned up test proposals")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
