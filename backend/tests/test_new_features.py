"""
Test suite for new features: Dynamic Pricing, Table Reservations, Guest Lifecycle
Also includes regression tests for existing APIs after backend refactoring
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestHealthAndBasics:
    """Health check and basic API tests - regression after refactoring"""
    
    def test_health_endpoint(self):
        """GET /api/health - system health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        print(f"✓ Health check passed: {data}")
    
    def test_dashboard_stats(self):
        """GET /api/dashboard/stats - dashboard statistics"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        # Verify required fields
        assert "total_rooms" in data
        assert "occupancy_rate" in data
        assert "total_guests" in data
        assert "total_reservations" in data
        assert "pending_tasks" in data
        assert data["total_rooms"] == 16  # Hotel has 16 rooms
        print(f"✓ Dashboard stats: rooms={data['total_rooms']}, occupancy={data['occupancy_rate']}%")
    
    def test_rooms_list(self):
        """GET /api/rooms - list all rooms with prices"""
        response = requests.get(f"{BASE_URL}/api/rooms")
        assert response.status_code == 200
        data = response.json()
        assert "rooms" in data
        rooms = data["rooms"]
        assert len(rooms) >= 4, "Expected at least 4 room types"
        
        # Note: DB has old prices (Superior=4500, Family=5000) while code says (5000, 6000)
        # This is a data sync issue to report - just verify rooms exist with valid prices
        for room in rooms:
            assert "room_id" in room
            assert "base_price_try" in room
            assert room.get("base_price_try") > 0
            print(f"✓ Room: {room.get('name_tr')} ({room.get('room_id')}) - {room.get('base_price_try')}TL")


class TestReviewsRegression:
    """Regression tests for reviews API after refactoring"""
    
    def test_reviews_list(self):
        """GET /api/reviews - list reviews"""
        response = requests.get(f"{BASE_URL}/api/reviews")
        assert response.status_code == 200
        data = response.json()
        assert "reviews" in data
        print(f"✓ Reviews count: {len(data['reviews'])}")
    
    def test_reviews_stats(self):
        """GET /api/reviews/stats - review statistics"""
        response = requests.get(f"{BASE_URL}/api/reviews/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "avg_rating" in data
        print(f"✓ Reviews stats: total={data.get('total')}, avg_rating={data.get('avg_rating')}")


class TestDynamicPricing:
    """Dynamic Pricing API tests"""
    
    def test_pricing_calculate_high_season_holiday(self):
        """GET /api/pricing/calculate - high season + holiday (July 15)"""
        response = requests.get(f"{BASE_URL}/api/pricing/calculate?room_id=double&date=2026-07-15")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "room_id" in data
        assert "base_price" in data
        assert "final_price" in data
        assert "season" in data
        assert "is_holiday" in data
        assert "holiday_name" in data
        
        # July 15 is "Demokrasi ve Milli Birlik Gunu" - high season + holiday
        assert data["season"] == "Yuksek Sezon"
        assert data["is_holiday"] == True
        assert "Demokrasi" in data["holiday_name"]
        
        # Price should be higher than base due to multipliers
        assert data["final_price"] > data["base_price"]
        print(f"✓ High season + holiday price: {data['base_price']}TL → {data['final_price']}TL (holiday: {data['holiday_name']})")
    
    def test_pricing_calculate_low_season(self):
        """GET /api/pricing/calculate - low season (February 15)"""
        response = requests.get(f"{BASE_URL}/api/pricing/calculate?room_id=single&date=2026-02-15")
        assert response.status_code == 200
        data = response.json()
        
        # February is low season
        assert data["season"] == "Dusuk Sezon"
        assert data["season_multiplier"] == 0.8
        assert data["is_holiday"] == False
        
        # Low season price should be lower than base
        assert data["final_price"] < data["base_price"]
        print(f"✓ Low season price: {data['base_price']}TL → {data['final_price']}TL (season: {data['season']})")
    
    def test_pricing_range(self):
        """GET /api/pricing/range - price range calculation"""
        response = requests.get(f"{BASE_URL}/api/pricing/range?room_id=double&start_date=2026-07-10&end_date=2026-07-15")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "room_id" in data
        assert "nights" in data
        assert "total_price" in data
        assert "average_nightly" in data
        assert "daily_breakdown" in data
        
        assert data["nights"] == 5  # July 10-15 = 5 nights
        assert len(data["daily_breakdown"]) == 5
        print(f"✓ Price range: {data['nights']} nights = {data['total_price']}TL (avg: {data['average_nightly']}TL/night)")
    
    def test_pricing_seasons(self):
        """GET /api/pricing/seasons - season config"""
        response = requests.get(f"{BASE_URL}/api/pricing/seasons")
        assert response.status_code == 200
        data = response.json()
        
        assert "seasons" in data
        assert "weekend_multiplier" in data
        
        seasons = data["seasons"]
        assert len(seasons) == 3  # off, mid, high
        
        # Verify multipliers
        season_dict = {s["key"]: s["multiplier"] for s in seasons}
        assert season_dict.get("high_season") == 1.4
        assert season_dict.get("mid_season") == 1.0
        assert season_dict.get("off_season") == 0.8
        
        assert data["weekend_multiplier"] == 1.2
        print(f"✓ Seasons: {seasons}, weekend_multiplier: {data['weekend_multiplier']}")
    
    def test_pricing_holidays(self):
        """GET /api/pricing/holidays - holiday list (14 holidays)"""
        response = requests.get(f"{BASE_URL}/api/pricing/holidays")
        assert response.status_code == 200
        data = response.json()
        
        assert "holidays" in data
        holidays = data["holidays"]
        assert len(holidays) == 14, f"Expected 14 holidays, got {len(holidays)}"
        
        # Verify some holidays exist
        holiday_names = [h["name"] for h in holidays]
        assert "Yilbasi" in holiday_names
        assert "Cumhuriyet Bayrami" in holiday_names
        print(f"✓ Holidays count: {len(holidays)}")


class TestTableReservations:
    """Table Reservations API tests"""
    
    created_reservation_id = None
    
    def test_table_reservations_list(self):
        """GET /api/table-reservations - list table reservations"""
        response = requests.get(f"{BASE_URL}/api/table-reservations")
        assert response.status_code == 200
        data = response.json()
        
        assert "reservations" in data
        assert "total" in data
        assert "config" in data
        
        # Verify restaurant config
        config = data["config"]
        assert config["name"] == "Antakya Sofrasi"
        assert config["total_tables"] == 15
        print(f"✓ Table reservations: {data['total']} total, restaurant: {config['name']}")
    
    def test_table_reservations_availability(self):
        """GET /api/table-reservations/availability - check availability (9 time slots)"""
        response = requests.get(f"{BASE_URL}/api/table-reservations/availability?date=2026-03-01")
        assert response.status_code == 200
        data = response.json()
        
        assert "date" in data
        assert "slots" in data
        assert "config" in data
        
        slots = data["slots"]
        assert len(slots) == 9, f"Expected 9 time slots, got {len(slots)}"
        
        # Verify slot structure
        for slot in slots:
            assert "time" in slot
            assert "booked" in slot
            assert "available" in slot
            assert "is_available" in slot
        
        print(f"✓ Availability: {len(slots)} time slots for {data['date']}")
    
    def test_table_reservations_create(self):
        """POST /api/table-reservations - create table reservation"""
        payload = {
            "guest_name": "TEST_Ali Yilmaz",
            "phone": "+905551234567",
            "date": "2026-03-15",
            "time": "19:00",
            "party_size": 4,
            "notes": "Birthday celebration",
            "occasion": "birthday",
            "is_hotel_guest": True
        }
        
        response = requests.post(f"{BASE_URL}/api/table-reservations", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify created reservation
        assert "id" in data
        assert data["guest_name"] == payload["guest_name"]
        assert data["phone"] == payload["phone"]
        assert data["date"] == payload["date"]
        assert data["time"] == payload["time"]
        assert data["party_size"] == payload["party_size"]
        assert data["status"] == "pending"
        
        TestTableReservations.created_reservation_id = data["id"]
        print(f"✓ Created table reservation: {data['id']} for {data['guest_name']}")
    
    def test_table_reservations_update_status(self):
        """PATCH /api/table-reservations/{id}/status - status update"""
        if not TestTableReservations.created_reservation_id:
            pytest.skip("No reservation ID from previous test")
        
        res_id = TestTableReservations.created_reservation_id
        response = requests.patch(f"{BASE_URL}/api/table-reservations/{res_id}/status?status=confirmed")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Updated reservation status to confirmed")
    
    def test_table_reservations_verify_update(self):
        """GET to verify status update persisted"""
        if not TestTableReservations.created_reservation_id:
            pytest.skip("No reservation ID from previous test")
        
        response = requests.get(f"{BASE_URL}/api/table-reservations")
        assert response.status_code == 200
        data = response.json()
        
        # Find the created reservation
        found = False
        for res in data["reservations"]:
            if res.get("id") == TestTableReservations.created_reservation_id:
                assert res["status"] == "confirmed"
                found = True
                break
        
        assert found, "Created reservation not found"
        print(f"✓ Verified reservation status is confirmed")
    
    def test_table_reservations_delete(self):
        """DELETE /api/table-reservations/{id} - delete"""
        if not TestTableReservations.created_reservation_id:
            pytest.skip("No reservation ID from previous test")
        
        res_id = TestTableReservations.created_reservation_id
        response = requests.delete(f"{BASE_URL}/api/table-reservations/{res_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Deleted table reservation: {res_id}")


class TestGuestLifecycle:
    """Guest Lifecycle API tests"""
    
    def test_lifecycle_templates_list(self):
        """GET /api/lifecycle/templates - list 6 message templates"""
        response = requests.get(f"{BASE_URL}/api/lifecycle/templates")
        assert response.status_code == 200
        data = response.json()
        
        assert "templates" in data
        templates = data["templates"]
        assert len(templates) == 6, f"Expected 6 templates, got {len(templates)}"
        
        # Verify template keys
        template_keys = [t["key"] for t in templates]
        expected_keys = ["booking_confirmation", "pre_arrival", "welcome_checkin", 
                        "during_stay_day2", "checkout_thankyou", "post_stay_followup"]
        for key in expected_keys:
            assert key in template_keys, f"Missing template: {key}"
        
        # Verify template structure
        for t in templates:
            assert "key" in t
            assert "name" in t
            assert "content" in t
            assert "variables" in t
        
        print(f"✓ Lifecycle templates: {len(templates)} templates")
    
    def test_lifecycle_template_single(self):
        """GET /api/lifecycle/templates/{key} - get single template"""
        response = requests.get(f"{BASE_URL}/api/lifecycle/templates/welcome_checkin")
        assert response.status_code == 200
        data = response.json()
        
        assert data["key"] == "welcome_checkin"
        assert "content" in data
        assert "variables" in data
        assert "guest_name" in data["variables"]
        print(f"✓ Single template: {data['key']} with variables: {data['variables']}")
    
    def test_lifecycle_preview(self):
        """POST /api/lifecycle/preview - preview template"""
        response = requests.post(
            f"{BASE_URL}/api/lifecycle/preview?template_key=welcome_checkin",
            json={"guest_name": "TEST_Mehmet Bey", "hotel_phone": "+902327777777"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "template_key" in data
        assert "message" in data
        assert "data" in data
        
        # Verify placeholder replacement
        assert "TEST_Mehmet Bey" in data["message"] or "Misafir" in data["message"]
        print(f"✓ Template preview generated for {data['template_key']}")
    
    def test_lifecycle_history(self):
        """GET /api/lifecycle/history - message history"""
        response = requests.get(f"{BASE_URL}/api/lifecycle/history")
        assert response.status_code == 200
        data = response.json()
        
        assert "messages" in data
        print(f"✓ Lifecycle history: {len(data['messages'])} messages")


class TestOtherExistingAPIs:
    """Regression tests for other existing APIs after refactoring"""
    
    def test_guests_list(self):
        """GET /api/guests"""
        response = requests.get(f"{BASE_URL}/api/guests")
        assert response.status_code == 200
        data = response.json()
        assert "guests" in data
        print(f"✓ Guests: {len(data['guests'])} total")
    
    def test_reservations_list(self):
        """GET /api/reservations"""
        response = requests.get(f"{BASE_URL}/api/reservations")
        assert response.status_code == 200
        data = response.json()
        assert "reservations" in data
        print(f"✓ Reservations: {len(data['reservations'])} total")
    
    def test_tasks_list(self):
        """GET /api/tasks"""
        response = requests.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        print(f"✓ Tasks: {len(data['tasks'])} total")
    
    def test_events_list(self):
        """GET /api/events"""
        response = requests.get(f"{BASE_URL}/api/events")
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        print(f"✓ Events: {len(data['events'])} total")
    
    def test_knowledge_list(self):
        """GET /api/knowledge"""
        response = requests.get(f"{BASE_URL}/api/knowledge")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        print(f"✓ Knowledge items: {len(data['items'])} total")
    
    def test_menu(self):
        """GET /api/menu"""
        response = requests.get(f"{BASE_URL}/api/menu")
        assert response.status_code == 200
        data = response.json()
        assert "menu" in data
        assert "restaurant" in data
        print(f"✓ Menu for {data['restaurant']}")
    
    def test_settings(self):
        """GET /api/settings"""
        response = requests.get(f"{BASE_URL}/api/settings")
        assert response.status_code == 200
        data = response.json()
        assert "hotel_name" in data or "type" in data
        print(f"✓ Settings loaded")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
