"""
Test suite for Google Reviews API endpoints - Kozbeyli Konagi hotel
Tests CRUD operations for reviews and AI response generation
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestReviewsAPI:
    """Review CRUD and AI response generation tests"""
    
    created_review_id = None
    
    def test_health_check(self):
        """Verify API is healthy before running tests"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print(f"✓ Health check passed: {data['hotel']}")
    
    def test_get_reviews_list(self):
        """GET /api/reviews - list all reviews"""
        response = requests.get(f"{BASE_URL}/api/reviews")
        assert response.status_code == 200
        data = response.json()
        assert "reviews" in data
        assert "total" in data
        assert isinstance(data["reviews"], list)
        print(f"✓ GET /api/reviews - Found {data['total']} reviews")
    
    def test_get_review_stats(self):
        """GET /api/reviews/stats - review statistics"""
        response = requests.get(f"{BASE_URL}/api/reviews/stats")
        assert response.status_code == 200
        data = response.json()
        # Verify all expected fields exist
        assert "total" in data
        assert "responded" in data
        assert "pending" in data
        assert "avg_rating" in data
        assert "by_rating" in data
        # Verify pending calculation
        assert data["pending"] == data["total"] - data["responded"]
        # Verify by_rating has all 5 star ratings
        for i in range(1, 6):
            assert str(i) in data["by_rating"]
        print(f"✓ GET /api/reviews/stats - Total: {data['total']}, Avg: {data['avg_rating']}, Responded: {data['responded']}, Pending: {data['pending']}")
    
    def test_create_review(self):
        """POST /api/reviews - create a new review"""
        payload = {
            "reviewer_name": "TEST_ReviewUser",
            "rating": 4,
            "review_text": "This is a test review. The hotel was nice, the location beautiful, and breakfast was excellent.",
            "platform": "google",
            "review_date": "2026-01-15"
        }
        response = requests.post(f"{BASE_URL}/api/reviews", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Verify response structure
        assert "id" in data
        assert data["reviewer_name"] == payload["reviewer_name"]
        assert data["rating"] == payload["rating"]
        assert data["review_text"] == payload["review_text"]
        assert data["platform"] == payload["platform"]
        assert data["review_date"] == payload["review_date"]
        # Verify default fields
        assert data["ai_response"] is None
        assert data["response_tone"] is None
        assert data["responded_at"] is None
        assert "created_at" in data
        assert "updated_at" in data
        TestReviewsAPI.created_review_id = data["id"]
        print(f"✓ POST /api/reviews - Created review with ID: {data['id']}")
    
    def test_verify_review_created_in_list(self):
        """Verify created review appears in GET /api/reviews"""
        assert TestReviewsAPI.created_review_id is not None, "Review was not created"
        response = requests.get(f"{BASE_URL}/api/reviews")
        assert response.status_code == 200
        data = response.json()
        # Find our test review in the list
        review_ids = [r["id"] for r in data["reviews"]]
        assert TestReviewsAPI.created_review_id in review_ids
        print(f"✓ Verified review {TestReviewsAPI.created_review_id} exists in reviews list")
    
    def test_generate_ai_response_professional(self):
        """POST /api/reviews/{id}/generate-response?tone=professional - generate AI response"""
        assert TestReviewsAPI.created_review_id is not None, "Review was not created"
        # AI response generation may take 5-10 seconds
        response = requests.post(
            f"{BASE_URL}/api/reviews/{TestReviewsAPI.created_review_id}/generate-response?tone=professional",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "response" in data
        assert data["tone"] == "professional"
        assert len(data["response"]) > 10, "AI response should be non-empty"
        print(f"✓ POST /api/reviews/{{id}}/generate-response - Generated professional response ({len(data['response'])} chars)")
        print(f"  Response preview: {data['response'][:100]}...")
    
    def test_verify_ai_response_persisted(self):
        """Verify AI response was saved to review via GET /api/reviews"""
        assert TestReviewsAPI.created_review_id is not None, "Review was not created"
        response = requests.get(f"{BASE_URL}/api/reviews")
        assert response.status_code == 200
        data = response.json()
        # Find our test review
        test_review = next((r for r in data["reviews"] if r["id"] == TestReviewsAPI.created_review_id), None)
        assert test_review is not None
        # Verify AI response was persisted
        assert test_review["ai_response"] is not None
        assert test_review["response_tone"] == "professional"
        assert test_review["responded_at"] is not None
        print(f"✓ Verified AI response was persisted to review")
    
    def test_update_review(self):
        """PATCH /api/reviews/{id} - update review fields"""
        assert TestReviewsAPI.created_review_id is not None, "Review was not created"
        updated_response = "This is a manually edited AI response for testing."
        payload = {
            "ai_response": updated_response
        }
        response = requests.patch(
            f"{BASE_URL}/api/reviews/{TestReviewsAPI.created_review_id}",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify update persisted
        get_response = requests.get(f"{BASE_URL}/api/reviews")
        assert get_response.status_code == 200
        reviews = get_response.json()["reviews"]
        test_review = next((r for r in reviews if r["id"] == TestReviewsAPI.created_review_id), None)
        assert test_review is not None
        assert test_review["ai_response"] == updated_response
        print(f"✓ PATCH /api/reviews/{{id}} - Updated review successfully")
    
    def test_generate_ai_response_friendly(self):
        """Test AI response generation with friendly tone"""
        assert TestReviewsAPI.created_review_id is not None, "Review was not created"
        response = requests.post(
            f"{BASE_URL}/api/reviews/{TestReviewsAPI.created_review_id}/generate-response?tone=friendly",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["tone"] == "friendly"
        assert len(data["response"]) > 10
        print(f"✓ Generated friendly tone response ({len(data['response'])} chars)")
    
    def test_generate_ai_response_formal(self):
        """Test AI response generation with formal tone"""
        assert TestReviewsAPI.created_review_id is not None, "Review was not created"
        response = requests.post(
            f"{BASE_URL}/api/reviews/{TestReviewsAPI.created_review_id}/generate-response?tone=formal",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["tone"] == "formal"
        assert len(data["response"]) > 10
        print(f"✓ Generated formal tone response ({len(data['response'])} chars)")
    
    def test_generate_response_invalid_review_id(self):
        """Test AI response generation with invalid review ID returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/reviews/invalid-id-12345/generate-response?tone=professional",
            timeout=10
        )
        assert response.status_code == 404
        print(f"✓ Invalid review ID correctly returns 404")
    
    def test_delete_review(self):
        """DELETE /api/reviews/{id} - delete review"""
        assert TestReviewsAPI.created_review_id is not None, "Review was not created"
        response = requests.delete(f"{BASE_URL}/api/reviews/{TestReviewsAPI.created_review_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        print(f"✓ DELETE /api/reviews/{{id}} - Deleted review {TestReviewsAPI.created_review_id}")
    
    def test_verify_review_deleted(self):
        """Verify deleted review no longer in GET /api/reviews"""
        assert TestReviewsAPI.created_review_id is not None, "Review was not created"
        response = requests.get(f"{BASE_URL}/api/reviews")
        assert response.status_code == 200
        data = response.json()
        review_ids = [r["id"] for r in data["reviews"]]
        assert TestReviewsAPI.created_review_id not in review_ids
        print(f"✓ Verified review {TestReviewsAPI.created_review_id} was deleted from database")
    
    def test_delete_nonexistent_review(self):
        """DELETE non-existent review should return 404"""
        response = requests.delete(f"{BASE_URL}/api/reviews/nonexistent-id-99999")
        assert response.status_code == 404
        print(f"✓ Delete non-existent review correctly returns 404")
    
    def test_update_nonexistent_review(self):
        """PATCH non-existent review should return 404"""
        response = requests.patch(
            f"{BASE_URL}/api/reviews/nonexistent-id-99999",
            json={"ai_response": "test"}
        )
        assert response.status_code == 404
        print(f"✓ Update non-existent review correctly returns 404")
    
    def test_create_review_with_rating_validation(self):
        """Test review creation with different ratings"""
        # Test rating 1 (negative review)
        payload_negative = {
            "reviewer_name": "TEST_NegativeReviewer",
            "rating": 1,
            "review_text": "Very disappointed with the experience.",
            "platform": "google"
        }
        response = requests.post(f"{BASE_URL}/api/reviews", json=payload_negative)
        assert response.status_code == 200
        neg_id = response.json()["id"]
        
        # Test rating 5 (positive review)
        payload_positive = {
            "reviewer_name": "TEST_PositiveReviewer",
            "rating": 5,
            "review_text": "Amazing experience, highly recommended!",
            "platform": "google"
        }
        response = requests.post(f"{BASE_URL}/api/reviews", json=payload_positive)
        assert response.status_code == 200
        pos_id = response.json()["id"]
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/reviews/{neg_id}")
        requests.delete(f"{BASE_URL}/api/reviews/{pos_id}")
        print(f"✓ Created and cleaned up reviews with ratings 1 and 5")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
