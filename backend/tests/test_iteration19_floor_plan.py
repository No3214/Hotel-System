"""
Iteration 19 - Table Reservations Floor Plan Testing
Tests the new real floor plan with 20 tables from Kozbeyli Konagi's actual layout PDF.
Tables: M1-M3 + A/B/C (Somine), M5-M8 (Sahne), M10-M13 (Manzara), S1-S4 (Ara), BAR1-BAR2 (Bar)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestFloorPlanEndpoints:
    """Test floor plan, zones, and tables endpoints"""
    
    def test_floor_plan_returns_5_zones(self):
        """GET /api/table-reservations/floor-plan returns 5 zones"""
        response = requests.get(f"{BASE_URL}/api/table-reservations/floor-plan")
        assert response.status_code == 200
        data = response.json()
        
        # Verify 5 zones exist
        assert "zones" in data
        assert len(data["zones"]) == 5
        
        zone_ids = [z["id"] for z in data["zones"]]
        expected_zones = ["somine", "sahne", "manzara", "ara", "bar"]
        for zone in expected_zones:
            assert zone in zone_ids, f"Zone '{zone}' not found in floor plan"
    
    def test_floor_plan_returns_20_tables(self):
        """GET /api/table-reservations/floor-plan returns 20 total tables"""
        response = requests.get(f"{BASE_URL}/api/table-reservations/floor-plan")
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_tables"] == 20
        
        # Count tables across all zones
        total_counted = sum(z["total_count"] for z in data["zones"])
        assert total_counted == 20
    
    def test_floor_plan_zone_counts(self):
        """Verify correct table counts per zone"""
        response = requests.get(f"{BASE_URL}/api/table-reservations/floor-plan")
        assert response.status_code == 200
        data = response.json()
        
        zone_counts = {z["id"]: z["total_count"] for z in data["zones"]}
        
        # Somine: M1, M2, M3, A, B, C = 6 tables
        assert zone_counts["somine"] == 6
        # Sahne: M5, M6, M7, M8 = 4 tables
        assert zone_counts["sahne"] == 4
        # Manzara: M10, M11, M12, M13 = 4 tables
        assert zone_counts["manzara"] == 4
        # Ara: S1, S2, S3, S4 = 4 tables
        assert zone_counts["ara"] == 4
        # Bar: BAR1, BAR2 = 2 tables
        assert zone_counts["bar"] == 2
    
    def test_tables_endpoint_returns_20_tables(self):
        """GET /api/table-reservations/tables returns 20 tables with config"""
        response = requests.get(f"{BASE_URL}/api/table-reservations/tables")
        assert response.status_code == 200
        data = response.json()
        
        assert "tables" in data
        assert len(data["tables"]) == 20
        
        # Verify config data
        assert "config" in data
        assert data["config"]["total_tables"] == 20
        assert data["config"]["total_capacity"] == 106
    
    def test_tables_capacity_total_106(self):
        """Verify total capacity is 106 seats"""
        response = requests.get(f"{BASE_URL}/api/table-reservations/tables")
        assert response.status_code == 200
        data = response.json()
        
        total_capacity = sum(t["capacity"] for t in data["tables"])
        assert total_capacity == 106
    
    def test_tables_types_count(self):
        """Verify table type counts"""
        response = requests.get(f"{BASE_URL}/api/table-reservations/tables")
        assert response.status_code == 200
        data = response.json()
        
        config = data["config"]
        # M1, M2, M3 (3) + M5, M6, M7, M8 (4) + M10, M11, M12, M13 (4) = 11 rectangular
        assert config["rectangular_tables"] == 11
        assert config["round_tables"] == 3         # A, B, C
        assert config["small_tables"] == 4         # S1-S4
        assert config["bar_tables"] == 2           # BAR1, BAR2
    
    def test_zones_endpoint_returns_5_zones(self):
        """GET /api/table-reservations/zones returns 5 zones"""
        response = requests.get(f"{BASE_URL}/api/table-reservations/zones")
        assert response.status_code == 200
        data = response.json()
        
        assert "zones" in data
        assert len(data["zones"]) == 5
        
        expected_ids = ["somine", "sahne", "manzara", "ara", "bar"]
        zone_ids = [z["id"] for z in data["zones"]]
        assert set(zone_ids) == set(expected_ids)


class TestTableReservationCRUD:
    """Test reservation creation and floor plan updates"""
    
    def test_create_reservation_m10_dinner(self):
        """POST /api/table-reservations - create reservation for M10 (dinner, 19:00, 6 people)"""
        test_data = {
            "guest_name": f"TEST_FloorPlan_{uuid.uuid4().hex[:6]}",
            "phone": "05551234567",
            "date": "2026-03-10",
            "time": "19:00",
            "party_size": 6,
            "meal_type": "dinner",
            "preferred_table_id": "M10",
            "notes": "Test reservation for M10"
        }
        
        response = requests.post(f"{BASE_URL}/api/table-reservations", json=test_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["table_id"] == "M10"
        assert data["party_size"] == 6
        assert data["meal_type"] == "dinner"
        assert data["time"] == "19:00"
        assert "id" in data
        
        # Cleanup
        res_id = data["id"]
        requests.delete(f"{BASE_URL}/api/table-reservations/{res_id}")
    
    def test_floor_plan_shows_occupied_after_reservation(self):
        """Verify floor plan shows M10 as occupied after reservation"""
        test_data = {
            "guest_name": f"TEST_Occupied_{uuid.uuid4().hex[:6]}",
            "phone": "05559876543",
            "date": "2026-03-11",
            "time": "19:00",
            "party_size": 4,
            "meal_type": "dinner",
            "preferred_table_id": "M10"
        }
        
        # Create reservation
        create_res = requests.post(f"{BASE_URL}/api/table-reservations", json=test_data)
        assert create_res.status_code == 200
        res_id = create_res.json()["id"]
        
        try:
            # Check floor plan for that date
            floor_res = requests.get(f"{BASE_URL}/api/table-reservations/floor-plan?date=2026-03-11")
            assert floor_res.status_code == 200
            floor_data = floor_res.json()
            
            # Find Manzara zone and M10 table
            manzara_zone = next((z for z in floor_data["zones"] if z["id"] == "manzara"), None)
            assert manzara_zone is not None
            
            m10_table = next((t for t in manzara_zone["tables"] if t["id"] == "M10"), None)
            assert m10_table is not None
            assert m10_table["is_occupied"] == True
            assert m10_table["reservation"] is not None
        finally:
            # Cleanup
            requests.delete(f"{BASE_URL}/api/table-reservations/{res_id}")
    
    def test_create_reservation_round_table_a_8_people(self):
        """POST /api/table-reservations - create reservation for round table A (8 people)"""
        test_data = {
            "guest_name": f"TEST_RoundA_{uuid.uuid4().hex[:6]}",
            "phone": "05551112233",
            "date": "2026-03-12",
            "time": "20:00",
            "party_size": 8,
            "meal_type": "dinner",
            "preferred_table_id": "A",
            "notes": "Group dinner at round table"
        }
        
        response = requests.post(f"{BASE_URL}/api/table-reservations", json=test_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["table_id"] == "A"
        assert data["table_name"] == "Yuvarlak A"
        assert data["party_size"] == 8
        
        # Verify round table A is in Somine zone
        table_res = requests.get(f"{BASE_URL}/api/table-reservations/tables")
        table_a = next((t for t in table_res.json()["tables"] if t["id"] == "A"), None)
        assert table_a["zone"] == "somine"
        assert table_a["type"] == "round"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/table-reservations/{data['id']}")
    
    def test_availability_dinner_endpoint(self):
        """GET /api/table-reservations/availability - check dinner availability"""
        response = requests.get(
            f"{BASE_URL}/api/table-reservations/availability",
            params={"date": "2026-03-15", "meal_type": "dinner", "party_size": 4}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "availability" in data
        assert "dinner" in data["availability"]
        
        # Should have 6 dinner time slots
        dinner_slots = data["availability"]["dinner"]
        assert len(dinner_slots) == 6
        
        # Check time slots
        expected_times = ["18:00", "18:30", "19:00", "19:30", "20:00", "20:30"]
        actual_times = [s["time"] for s in dinner_slots]
        assert actual_times == expected_times


class TestTableReservationStats:
    """Test stats endpoint returns correct configuration"""
    
    def test_stats_returns_config(self):
        """GET /api/table-reservations/stats - returns config with 20 tables, 106 capacity"""
        response = requests.get(f"{BASE_URL}/api/table-reservations/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "config" in data
        config = data["config"]
        
        assert config["total_tables"] == 20
        assert config["total_capacity"] == 106
        # M1, M2, M3 (3) + M5, M6, M7, M8 (4) + M10, M11, M12, M13 (4) = 11
        assert config["rectangular_tables"] == 11
        assert config["round_tables"] == 3
        assert config["small_tables"] == 4
        assert config["bar_tables"] == 2
    
    def test_stats_meal_breakdown(self):
        """Verify stats has meal breakdown"""
        response = requests.get(f"{BASE_URL}/api/table-reservations/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "by_meal" in data
        assert "breakfast" in data["by_meal"]
        assert "lunch" in data["by_meal"]
        assert "dinner" in data["by_meal"]


class TestSpecificTableIds:
    """Verify all 20 specific table IDs exist"""
    
    def test_all_table_ids_present(self):
        """Verify all 20 expected table IDs are present"""
        response = requests.get(f"{BASE_URL}/api/table-reservations/tables")
        assert response.status_code == 200
        data = response.json()
        
        table_ids = set(t["id"] for t in data["tables"])
        
        # Expected table IDs
        expected = {
            # Somine: M1, M2, M3, A, B, C
            "M1", "M2", "M3", "A", "B", "C",
            # Sahne: M5, M6, M7, M8
            "M5", "M6", "M7", "M8",
            # Manzara: M10, M11, M12, M13
            "M10", "M11", "M12", "M13",
            # Ara: S1, S2, S3, S4
            "S1", "S2", "S3", "S4",
            # Bar: BAR1, BAR2
            "BAR1", "BAR2"
        }
        
        assert table_ids == expected
    
    def test_round_tables_capacity(self):
        """Round tables A, B, C should each have 8 person capacity"""
        response = requests.get(f"{BASE_URL}/api/table-reservations/tables")
        data = response.json()
        
        round_tables = [t for t in data["tables"] if t["type"] == "round"]
        assert len(round_tables) == 3
        
        for table in round_tables:
            assert table["capacity"] == 8
            assert table["id"] in ["A", "B", "C"]
    
    def test_small_tables_capacity(self):
        """Small tables S1-S4 should each have 2 person capacity"""
        response = requests.get(f"{BASE_URL}/api/table-reservations/tables")
        data = response.json()
        
        small_tables = [t for t in data["tables"] if t["type"] == "small"]
        assert len(small_tables) == 4
        
        for table in small_tables:
            assert table["capacity"] == 2
            assert table["id"].startswith("S")
    
    def test_bar_tables_capacity(self):
        """Bar tables should each have 4 person capacity"""
        response = requests.get(f"{BASE_URL}/api/table-reservations/tables")
        data = response.json()
        
        bar_tables = [t for t in data["tables"] if t["type"] == "bar"]
        assert len(bar_tables) == 2
        
        for table in bar_tables:
            assert table["capacity"] == 4
            assert table["id"].startswith("BAR")


@pytest.fixture(autouse=True)
def cleanup_test_reservations():
    """Cleanup TEST_ prefixed reservations after tests"""
    yield
    # Cleanup any leftover test reservations
    try:
        response = requests.get(f"{BASE_URL}/api/table-reservations")
        if response.status_code == 200:
            reservations = response.json().get("reservations", [])
            for res in reservations:
                if res.get("guest_name", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/table-reservations/{res['id']}")
    except Exception:
        pass
