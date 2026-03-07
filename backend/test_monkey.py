import pytest
from fastapi.testclient import TestClient
from server import app
import random

# Bypass Gemini calls during testing to run quickly and without cost/rate limits
# We'll monkeypatch get_chat_response to return dummy JSON strings based on prompts.
@pytest.fixture(autouse=True)
def mock_gemini(monkeypatch):
    async def mock_get_chat_response(message, session_id=None, system_prompt=None, temp=None):
        prompt_lower = (system_prompt or message).lower()
        if "market intelligence" in prompt_lower:
            return '''```json
            {
                "market_position": "Test Position",
                "competitor_analysis": "Test Analysis",
                "recommended_strategy": "Test Strategy",
                "rate_adjustment_suggestion": "0%",
                "actionable_insights": ["Test Insight 1"]
            }
            ```'''
        if "vendor" in prompt_lower or "cfo" in prompt_lower or "finansal uzman" in prompt_lower:
            return '''```json
            {
                "financial_score": 85,
                "overall_summary": "Good",
                "red_flags": [],
                "savings_recommendations": [],
                "top_vendors_analysis": []
            }
            ```'''
        if "ik uzmani" in prompt_lower or "performans" in prompt_lower or "burnout" in prompt_lower:
            return '''```json
            {
                "burnout_risk": "Düşük",
                "workload_analysis": "Normal",
                "manager_recommendation": "Keep up",
                "efficiency_score": 90
            }
            ```'''
        if "welcome" in prompt_lower or "konsiyerj" in prompt_lower:
            return '''```json
            {
                "guest_segment": "Test Segment",
                "whatsapp_welcome_message": "Welcome!",
                "upsell_suggestions": []
            }
            ```'''
        return "{}"

    import gemini_service
    monkeypatch.setattr(gemini_service, "get_chat_response", mock_get_chat_response)

    # Mock DB collections to prevent hangs
    class MockCursor:
        async def to_list(self, length): return []
    class MockCollection:
        def find(self, *args, **kwargs): return MockCursor()
        def find_one(self, *args, **kwargs): return None
        def count_documents(self, *args, **kwargs): return 0
    class MockDB:
        financials = MockCollection()
        staff = MockCollection()
        tasks = MockCollection()
        reviews = MockCollection()
        reservations = MockCollection()
        guests = MockCollection()
        revenue = MockCollection()
    import database
    monkeypatch.setattr(database, "db", MockDB())

client = TestClient(app)

def test_ai_vendor_roi():
    response = client.get("/api/financials/ai-vendor-roi")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "report" in data

def test_ai_burnout_radar():
    response = client.get("/api/staff/ai-burnout-radar")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "radar" in data
    assert isinstance(data["radar"], list)

def test_ai_guest_journey():
    response = client.get("/api/reservations/ai-guest-journey")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "journey_data" in data

def test_ai_market_intel():
    response = client.get("/api/revenue/ai-market-intel")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "intelligence" in data
