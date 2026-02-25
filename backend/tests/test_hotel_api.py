"""
Kozbeyli Konagi Hotel API Tests
Testing all backend endpoints for hotel management system
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndBasics:
    """Basic health and hotel info tests"""
    
    def test_health_endpoint(self):
        """GET /api/health - Health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["hotel"] == "Kozbeyli Konagi"
        print("✓ Health endpoint: healthy")

    def test_hotel_info(self):
        """GET /api/hotel/info - Hotel information"""
        response = requests.get(f"{BASE_URL}/api/hotel/info")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Kozbeyli Konagi"
        assert data["total_rooms"] == 16
        assert "phone" in data
        print("✓ Hotel info: verified")

    def test_hotel_awards(self):
        """GET /api/hotel/awards - Hotel awards list"""
        response = requests.get(f"{BASE_URL}/api/hotel/awards")
        assert response.status_code == 200
        data = response.json()
        assert "awards" in data
        assert len(data["awards"]) > 0
        print(f"✓ Hotel awards: {len(data['awards'])} awards")

    def test_hotel_policies(self):
        """GET /api/hotel/policies - Hotel policies"""
        response = requests.get(f"{BASE_URL}/api/hotel/policies")
        assert response.status_code == 200
        data = response.json()
        assert "cancellation" in data
        assert "no_show" in data
        print("✓ Hotel policies: verified")


class TestDashboard:
    """Dashboard stats tests"""
    
    def test_dashboard_stats(self):
        """GET /api/dashboard/stats - Dashboard statistics"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_rooms"] == 16
        assert "occupancy_rate" in data
        assert "ratings" in data
        assert "booking_com" in data["ratings"]
        assert "tripadvisor" in data["ratings"]
        print(f"✓ Dashboard stats: {data['total_rooms']} rooms, {data['occupancy_rate']}% occupancy")


class TestRooms:
    """Rooms endpoint tests"""
    
    def test_list_rooms(self):
        """GET /api/rooms - List all room types"""
        response = requests.get(f"{BASE_URL}/api/rooms")
        assert response.status_code == 200
        data = response.json()
        assert "rooms" in data
        rooms = data["rooms"]
        assert len(rooms) == 8, f"Expected 8 room types, got {len(rooms)}"

        # Verify room types
        room_ids = [r["room_id"] for r in rooms]
        assert "standart" in room_ids, "Expected room types not found"
        
        # Check prices
        for room in rooms:
            assert "base_price_try" in room
            assert "base_price_eur" in room
            assert room["base_price_try"] > 0
        print(f"✓ Rooms: {len(rooms)} room types with TL and EUR prices")

    def test_get_single_room(self):
        """GET /api/rooms/{room_id} - Get single room"""
        response = requests.get(f"{BASE_URL}/api/rooms/standart")
        assert response.status_code == 200
        data = response.json()
        assert data["room_id"] == "standart"
        assert "name_tr" in data
        print("✓ Single room retrieval works")


class TestMenu:
    """Restaurant menu tests"""
    
    def test_get_menu(self):
        """GET /api/menu - Get restaurant menu"""
        response = requests.get(f"{BASE_URL}/api/menu")
        assert response.status_code == 200
        data = response.json()
        assert "menu" in data
        assert "restaurant" in data
        menu = data["menu"]
        
        # Verify menu categories
        expected_categories = ["kahvalti", "ana_yemek", "meze", "tatli"]
        for cat in expected_categories:
            assert cat in menu, f"Missing category: {cat}"
        
        # Check items have prices
        for cat, items in menu.items():
            for item in items:
                assert "name" in item
                assert "price_try" in item
        print(f"✓ Menu: {len(menu)} categories")

    def test_menu_category(self):
        """GET /api/menu/{category} - Get menu category"""
        response = requests.get(f"{BASE_URL}/api/menu/kahvalti")
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "kahvalti"
        assert "items" in data
        print("✓ Menu category endpoint works")


class TestGuests:
    """Guest CRUD tests"""
    
    def test_create_guest_and_verify(self):
        """POST /api/guests - Create guest and verify with GET"""
        # Create guest
        guest_data = {
            "name": f"TEST_Misafir_{uuid.uuid4().hex[:6]}",
            "email": "test@kozbeylikonagi.com",
            "phone": "+905321234567",
            "nationality": "TR",
            "notes": "Test misafir"
        }
        response = requests.post(f"{BASE_URL}/api/guests", json=guest_data)
        assert response.status_code == 200
        created = response.json()
        assert created["name"] == guest_data["name"]
        assert created["email"] == guest_data["email"]
        assert "id" in created
        
        guest_id = created["id"]
        
        # Verify with GET
        get_response = requests.get(f"{BASE_URL}/api/guests/{guest_id}")
        assert get_response.status_code == 200
        fetched = get_response.json()
        assert fetched["name"] == guest_data["name"]
        print(f"✓ Guest created and verified: {guest_id}")
        
        return guest_id

    def test_list_guests(self):
        """GET /api/guests - List guests"""
        response = requests.get(f"{BASE_URL}/api/guests")
        assert response.status_code == 200
        data = response.json()
        assert "guests" in data
        assert "total" in data
        print(f"✓ Guests list: {data['total']} total")


class TestTasks:
    """Task CRUD tests"""
    
    def test_create_task_and_update(self):
        """POST /api/tasks - Create task, PATCH update status"""
        # Create task
        task_data = {
            "title": f"TEST_Gorev_{uuid.uuid4().hex[:6]}",
            "description": "Test gorev aciklamasi",
            "priority": "high",
            "assignee_role": "resepsiyon"
        }
        response = requests.post(f"{BASE_URL}/api/tasks", json=task_data)
        assert response.status_code == 200
        created = response.json()
        assert created["title"] == task_data["title"]
        assert created["status"] == "pending"
        assert "id" in created
        
        task_id = created["id"]
        
        # Update task status
        update_response = requests.patch(
            f"{BASE_URL}/api/tasks/{task_id}",
            json={"status": "completed"}
        )
        assert update_response.status_code == 200
        
        # Verify via list
        list_response = requests.get(f"{BASE_URL}/api/tasks")
        tasks = list_response.json()["tasks"]
        task = next((t for t in tasks if t["id"] == task_id), None)
        assert task is not None
        assert task["status"] == "completed"
        print(f"✓ Task created and updated: {task_id}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/tasks/{task_id}")
        return task_id

    def test_list_tasks(self):
        """GET /api/tasks - List tasks"""
        response = requests.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        print(f"✓ Tasks list: {data['total']} total")

    def test_delete_task(self):
        """DELETE /api/tasks/{id} - Delete task"""
        # Create task first
        task_data = {"title": f"TEST_Delete_{uuid.uuid4().hex[:6]}", "priority": "low"}
        create_response = requests.post(f"{BASE_URL}/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Delete task
        delete_response = requests.delete(f"{BASE_URL}/api/tasks/{task_id}")
        assert delete_response.status_code == 200
        
        # Verify deletion - should not find in list
        list_response = requests.get(f"{BASE_URL}/api/tasks")
        tasks = list_response.json()["tasks"]
        task = next((t for t in tasks if t["id"] == task_id), None)
        assert task is None
        print(f"✓ Task deleted: {task_id}")


class TestEvents:
    """Event CRUD tests"""
    
    def test_create_event_and_delete(self):
        """POST /api/events - Create event, DELETE after"""
        event_data = {
            "title": f"TEST_Etkinlik_{uuid.uuid4().hex[:6]}",
            "description": "Test etkinlik aciklamasi",
            "event_type": "special_dinner",
            "event_date": "2026-03-15",
            "start_time": "19:00",
            "capacity": 50,
            "price_per_person": 350.0,
            "is_active": True
        }
        response = requests.post(f"{BASE_URL}/api/events", json=event_data)
        assert response.status_code == 200
        created = response.json()
        assert created["title"] == event_data["title"]
        assert created["event_date"] == event_data["event_date"]
        assert "id" in created
        
        event_id = created["id"]
        
        # Delete event
        delete_response = requests.delete(f"{BASE_URL}/api/events/{event_id}")
        assert delete_response.status_code == 200
        print(f"✓ Event created and deleted: {event_id}")

    def test_list_events(self):
        """GET /api/events - List events"""
        response = requests.get(f"{BASE_URL}/api/events")
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        print(f"✓ Events list: {len(data['events'])} events")


class TestHousekeeping:
    """Housekeeping tests"""
    
    def test_create_housekeeping(self):
        """POST /api/housekeeping - Create housekeeping log"""
        hk_data = {
            "room_number": "101",
            "task_type": "standard_clean",
            "priority": "normal",
            "notes": "Test kat hizmeti"
        }
        response = requests.post(f"{BASE_URL}/api/housekeeping", json=hk_data)
        assert response.status_code == 200
        created = response.json()
        assert created["room_number"] == "101"
        assert created["status"] == "pending"
        print(f"✓ Housekeeping log created: {created['id']}")

    def test_list_housekeeping(self):
        """GET /api/housekeeping - List housekeeping logs"""
        response = requests.get(f"{BASE_URL}/api/housekeeping")
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        print(f"✓ Housekeeping list: {len(data['logs'])} logs")


class TestKnowledge:
    """Knowledge base tests"""
    
    def test_create_knowledge(self):
        """POST /api/knowledge - Create knowledge base item"""
        kb_data = {
            "title": f"TEST_Bilgi_{uuid.uuid4().hex[:6]}",
            "content": "Test bilgi bankasi icerigi",
            "category": "policy",
            "tags": ["test", "policy"]
        }
        response = requests.post(f"{BASE_URL}/api/knowledge", json=kb_data)
        assert response.status_code == 200
        created = response.json()
        assert created["title"] == kb_data["title"]
        assert "id" in created
        
        kb_id = created["id"]
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/knowledge/{kb_id}")
        print(f"✓ Knowledge item created and cleaned up: {kb_id}")

    def test_list_knowledge(self):
        """GET /api/knowledge - List knowledge base"""
        response = requests.get(f"{BASE_URL}/api/knowledge")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        print(f"✓ Knowledge base: {data['total']} items")


class TestChatbot:
    """AI Chatbot tests"""
    
    def test_chatbot_message(self):
        """POST /api/chatbot - Send message to Gemini AI"""
        session_id = f"test-session-{uuid.uuid4().hex[:6]}"
        chat_data = {
            "message": "Odalariniz hakkinda bilgi verir misiniz?",
            "session_id": session_id
        }
        response = requests.post(f"{BASE_URL}/api/chatbot", json=chat_data, timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["session_id"] == session_id
        assert "intent" in data
        assert len(data["response"]) > 0
        print(f"✓ Chatbot response: {data['intent']} intent, {len(data['response'])} chars")
        
        # Clear session
        requests.delete(f"{BASE_URL}/api/chatbot/session/{session_id}")


class TestWhatsApp:
    """WhatsApp webhook tests"""
    
    def test_whatsapp_webhook(self):
        """POST /api/whatsapp/webhook - WhatsApp message webhook"""
        wa_data = {
            "from_number": "+905321234567",
            "message": "Merhaba, rezervasyon yapmak istiyorum",
            "sender_name": "Test Misafir"
        }
        response = requests.post(f"{BASE_URL}/api/whatsapp/webhook", json=wa_data, timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "intent" in data
        assert len(data["reply"]) > 0
        print(f"✓ WhatsApp webhook: {data['intent']} intent")

    def test_list_whatsapp_messages(self):
        """GET /api/whatsapp/messages - List WhatsApp messages"""
        response = requests.get(f"{BASE_URL}/api/whatsapp/messages")
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        print(f"✓ WhatsApp messages: {len(data['messages'])} messages")


class TestMessages:
    """All messages endpoint tests"""
    
    def test_list_all_messages(self):
        """GET /api/messages - List all platform messages"""
        response = requests.get(f"{BASE_URL}/api/messages")
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        print(f"✓ All messages: {len(data['messages'])} messages")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
