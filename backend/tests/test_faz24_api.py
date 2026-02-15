"""
Kozbeyli Konagi Hotel API Tests - Faz 2-4 Features
Testing new endpoints: Campaigns, Staff/Shifts, Reservations CRUD, Settings, KVKK, i18n, Foca Guide
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ==================== CAMPAIGNS (Faz 2) ====================
class TestCampaigns:
    """Email campaign CRUD tests"""
    
    def test_create_campaign(self):
        """POST /api/campaigns - Create email campaign"""
        campaign_data = {
            "title": f"TEST_Kampanya_{uuid.uuid4().hex[:6]}",
            "subject": "Ozel Yaz Firsatlari",
            "content": "Kozbeyli Konagi'nda bu yaz ozel fiyatlar!",
            "target_segment": "all",
            "channel": "email"
        }
        response = requests.post(f"{BASE_URL}/api/campaigns", json=campaign_data)
        assert response.status_code == 200
        created = response.json()
        assert created["title"] == campaign_data["title"]
        assert created["status"] == "draft"
        assert "id" in created
        print(f"✓ Campaign created: {created['id']}")
        return created["id"]

    def test_send_campaign_and_verify_recipients(self):
        """PATCH /api/campaigns/{id}/status?status=sent - Send campaign and verify recipients count"""
        # Create campaign
        campaign_data = {
            "title": f"TEST_Send_{uuid.uuid4().hex[:6]}",
            "subject": "Test Gonderim",
            "content": "Bu bir test kampanyasidir.",
            "target_segment": "all",
            "channel": "email"
        }
        create_response = requests.post(f"{BASE_URL}/api/campaigns", json=campaign_data)
        assert create_response.status_code == 200
        campaign_id = create_response.json()["id"]
        
        # Send campaign
        send_response = requests.patch(f"{BASE_URL}/api/campaigns/{campaign_id}/status?status=sent")
        assert send_response.status_code == 200
        data = send_response.json()
        assert data["success"] == True
        assert "recipients" in data
        print(f"✓ Campaign sent to {data['recipients']} recipients")
        
        # Verify via list
        list_response = requests.get(f"{BASE_URL}/api/campaigns")
        campaigns = list_response.json()["campaigns"]
        campaign = next((c for c in campaigns if c["id"] == campaign_id), None)
        assert campaign is not None
        assert campaign["status"] == "sent"
        assert "recipients_count" in campaign
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/campaigns/{campaign_id}")
        return campaign_id
    
    def test_delete_campaign(self):
        """DELETE /api/campaigns/{id} - Delete campaign"""
        # Create campaign first
        campaign_data = {"title": f"TEST_Del_{uuid.uuid4().hex[:6]}", "subject": "Del", "content": "Delete me"}
        create_response = requests.post(f"{BASE_URL}/api/campaigns", json=campaign_data)
        campaign_id = create_response.json()["id"]
        
        # Delete
        delete_response = requests.delete(f"{BASE_URL}/api/campaigns/{campaign_id}")
        assert delete_response.status_code == 200
        
        # Verify deletion
        list_response = requests.get(f"{BASE_URL}/api/campaigns")
        campaigns = list_response.json()["campaigns"]
        campaign = next((c for c in campaigns if c["id"] == campaign_id), None)
        assert campaign is None
        print(f"✓ Campaign deleted: {campaign_id}")


# ==================== STAFF & SHIFTS (Faz 3) ====================
class TestStaff:
    """Staff CRUD tests"""
    
    def test_create_staff(self):
        """POST /api/staff - Create staff member"""
        staff_data = {
            "name": f"TEST_Personel_{uuid.uuid4().hex[:6]}",
            "role": "Resepsiyon Gorevlisi",
            "phone": "+905321111111",
            "email": "test@kozbeyli.com",
            "department": "resepsiyon",
            "is_active": True
        }
        response = requests.post(f"{BASE_URL}/api/staff", json=staff_data)
        assert response.status_code == 200
        created = response.json()
        assert created["name"] == staff_data["name"]
        assert created["role"] == staff_data["role"]
        assert created["department"] == "resepsiyon"
        assert "id" in created
        print(f"✓ Staff created: {created['id']}")
        return created["id"]

    def test_delete_staff(self):
        """DELETE /api/staff/{id} - Delete staff member"""
        # Create staff first
        staff_data = {"name": f"TEST_Del_{uuid.uuid4().hex[:6]}", "role": "Temizlik"}
        create_response = requests.post(f"{BASE_URL}/api/staff", json=staff_data)
        staff_id = create_response.json()["id"]
        
        # Delete
        delete_response = requests.delete(f"{BASE_URL}/api/staff/{staff_id}")
        assert delete_response.status_code == 200
        
        # Verify deletion
        list_response = requests.get(f"{BASE_URL}/api/staff")
        staff_list = list_response.json()["staff"]
        staff = next((s for s in staff_list if s["id"] == staff_id), None)
        assert staff is None
        print(f"✓ Staff deleted: {staff_id}")


class TestShifts:
    """Shift CRUD tests"""
    
    @pytest.fixture(scope="class")
    def test_staff_id(self):
        """Create a staff member for shift tests"""
        staff_data = {"name": f"TEST_ShiftStaff_{uuid.uuid4().hex[:6]}", "role": "Vardiya Test"}
        response = requests.post(f"{BASE_URL}/api/staff", json=staff_data)
        return response.json()["id"], response.json()["name"]

    def test_create_shift(self, test_staff_id):
        """POST /api/shifts - Create shift for staff member"""
        staff_id, staff_name = test_staff_id
        shift_data = {
            "staff_id": staff_id,
            "staff_name": staff_name,
            "date": "2026-02-15",
            "start_time": "08:00",
            "end_time": "17:00",
            "department": "resepsiyon",
            "notes": "Sabah vardiyasi"
        }
        response = requests.post(f"{BASE_URL}/api/shifts", json=shift_data)
        assert response.status_code == 200
        created = response.json()
        assert created["staff_id"] == staff_id
        assert created["date"] == "2026-02-15"
        assert created["start_time"] == "08:00"
        assert "id" in created
        print(f"✓ Shift created: {created['id']}")
        return created["id"]

    def test_delete_shift(self, test_staff_id):
        """DELETE /api/shifts/{id} - Delete shift"""
        staff_id, staff_name = test_staff_id
        # Create shift first
        shift_data = {"staff_id": staff_id, "staff_name": staff_name, "date": "2026-02-16", "start_time": "08:00", "end_time": "17:00"}
        create_response = requests.post(f"{BASE_URL}/api/shifts", json=shift_data)
        shift_id = create_response.json()["id"]
        
        # Delete
        delete_response = requests.delete(f"{BASE_URL}/api/shifts/{shift_id}")
        assert delete_response.status_code == 200
        
        # Verify deletion
        list_response = requests.get(f"{BASE_URL}/api/shifts")
        shifts = list_response.json()["shifts"]
        shift = next((s for s in shifts if s["id"] == shift_id), None)
        assert shift is None
        print(f"✓ Shift deleted: {shift_id}")


# ==================== RESERVATIONS EXTENDED (Faz 2-3) ====================
class TestReservationsExtended:
    """Extended reservation CRUD with status workflow and auto-housekeeping"""
    
    @pytest.fixture(scope="class")
    def test_guest_id(self):
        """Create a guest for reservation tests"""
        guest_data = {"name": f"TEST_ResGuest_{uuid.uuid4().hex[:6]}", "phone": "+905320000000"}
        response = requests.post(f"{BASE_URL}/api/guests", json=guest_data)
        return response.json()["id"]

    def test_create_reservation(self, test_guest_id):
        """POST /api/reservations - Create reservation"""
        res_data = {
            "guest_id": test_guest_id,
            "room_type": "double",
            "check_in": "2026-03-01",
            "check_out": "2026-03-05",
            "guests_count": 2,
            "notes": "Test rezervasyon",
            "total_price": 12000.0
        }
        response = requests.post(f"{BASE_URL}/api/reservations", json=res_data)
        assert response.status_code == 200
        created = response.json()
        assert created["guest_id"] == test_guest_id
        assert created["room_type"] == "double"
        assert created["status"] == "pending"
        assert created["total_price"] == 12000.0
        assert "id" in created
        print(f"✓ Reservation created: {created['id']}")
        return created["id"]

    def test_update_reservation_status_flow(self, test_guest_id):
        """PATCH /api/reservations/{id} - Update reservation with status flow (pending->confirmed->checked_in->checked_out)"""
        # Create reservation
        res_data = {"guest_id": test_guest_id, "room_type": "suite", "check_in": "2026-03-10", "check_out": "2026-03-12"}
        create_response = requests.post(f"{BASE_URL}/api/reservations", json=res_data)
        res_id = create_response.json()["id"]
        
        # Confirm
        confirm_response = requests.patch(f"{BASE_URL}/api/reservations/{res_id}", json={"status": "confirmed"})
        assert confirm_response.status_code == 200
        
        # Check-in
        checkin_response = requests.patch(f"{BASE_URL}/api/reservations/{res_id}", json={"status": "checked_in"})
        assert checkin_response.status_code == 200
        
        # Check-out (should auto-create housekeeping)
        checkout_response = requests.patch(f"{BASE_URL}/api/reservations/{res_id}", json={"status": "checked_out"})
        assert checkout_response.status_code == 200
        
        # Verify final status
        get_response = requests.get(f"{BASE_URL}/api/reservations/{res_id}")
        assert get_response.status_code == 200
        res = get_response.json()
        assert res["status"] == "checked_out"
        print(f"✓ Reservation status flow completed: {res_id}")
        
        # Verify housekeeping was auto-created
        hk_response = requests.get(f"{BASE_URL}/api/housekeeping")
        hk_logs = hk_response.json()["logs"]
        auto_hk = [h for h in hk_logs if h.get("reservation_id") == res_id]
        assert len(auto_hk) > 0, "Auto-housekeeping not created on checkout"
        print(f"✓ Auto-housekeeping created on checkout")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/reservations/{res_id}")
        return res_id

    def test_delete_reservation(self, test_guest_id):
        """DELETE /api/reservations/{id} - Delete reservation"""
        # Create reservation
        res_data = {"guest_id": test_guest_id, "room_type": "single", "check_in": "2026-04-01", "check_out": "2026-04-03"}
        create_response = requests.post(f"{BASE_URL}/api/reservations", json=res_data)
        res_id = create_response.json()["id"]
        
        # Delete
        delete_response = requests.delete(f"{BASE_URL}/api/reservations/{res_id}")
        assert delete_response.status_code == 200
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/reservations/{res_id}")
        assert get_response.status_code == 404
        print(f"✓ Reservation deleted: {res_id}")


# ==================== SETTINGS (Faz 3) ====================
class TestSettings:
    """Settings endpoint tests"""
    
    def test_get_settings(self):
        """GET /api/settings - Get settings object"""
        response = requests.get(f"{BASE_URL}/api/settings")
        assert response.status_code == 200
        data = response.json()
        assert "hotel_name" in data
        assert "phone" in data
        assert "email" in data
        assert "whatsapp_enabled" in data
        assert "auto_housekeeping" in data
        print(f"✓ Settings retrieved: {data.get('hotel_name')}")

    def test_update_settings(self):
        """PATCH /api/settings - Update settings"""
        update_data = {"auto_housekeeping": True, "auto_reply_enabled": True}
        response = requests.patch(f"{BASE_URL}/api/settings", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Settings updated")


# ==================== KVKK (Faz 3) ====================
class TestKVKK:
    """KVKK compliance endpoint tests"""
    
    def test_get_kvkk_policy(self):
        """GET /api/kvkk/policy - Get KVKK policy with 6 sections"""
        response = requests.get(f"{BASE_URL}/api/kvkk/policy")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "sections" in data
        assert len(data["sections"]) == 6, f"Expected 6 KVKK sections, got {len(data['sections'])}"
        
        # Verify section titles
        section_titles = [s["title"] for s in data["sections"]]
        expected = ["Veri Sorumlusu", "Toplanan Veriler", "Veri Isleme Amaci", "Veri Saklama Suresi", "Haklariniz", "Iletisim"]
        for exp in expected:
            assert exp in section_titles, f"Missing KVKK section: {exp}"
        print(f"✓ KVKK policy: {len(data['sections'])} sections")


# ==================== I18N (Faz 4) ====================
class TestI18N:
    """Internationalization endpoint tests"""
    
    def test_get_languages(self):
        """GET /api/i18n - Returns 5 language options"""
        response = requests.get(f"{BASE_URL}/api/i18n")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) == 5, f"Expected 5 languages, got {len(data['languages'])}"
        
        # Verify language codes
        codes = [l["code"] for l in data["languages"]]
        expected = ["tr", "en", "de", "fr", "ru"]
        for exp in expected:
            assert exp in codes, f"Missing language: {exp}"
        print(f"✓ i18n: {len(data['languages'])} languages available")

    def test_get_english_translations(self):
        """GET /api/i18n/en - Returns English translations"""
        response = requests.get(f"{BASE_URL}/api/i18n/en")
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "en"
        assert "translations" in data
        trans = data["translations"]
        assert trans["dashboard"] == "Dashboard"
        assert trans["rooms"] == "Rooms"
        assert trans["guests"] == "Guests"
        print(f"✓ English translations: {len(trans)} keys")

    def test_get_german_translations(self):
        """GET /api/i18n/de - Returns German translations"""
        response = requests.get(f"{BASE_URL}/api/i18n/de")
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "de"
        assert "translations" in data
        trans = data["translations"]
        assert trans["dashboard"] == "Dashboard"
        assert trans["rooms"] == "Zimmer"
        assert trans["guests"] == "Gaste"
        print(f"✓ German translations: {len(trans)} keys")


# ==================== FOCA GUIDE & HOTEL HISTORY (Faz 3-4) ====================
class TestFocaGuide:
    """Foca local guide and hotel history tests"""
    
    def test_get_local_guide(self):
        """GET /api/hotel/guide - Returns Foca guide data"""
        response = requests.get(f"{BASE_URL}/api/hotel/guide")
        assert response.status_code == 200
        data = response.json()
        
        # Verify guide categories
        assert "beaches" in data
        assert "historical" in data
        assert "activities_family" in data
        assert "activities_couple" in data
        
        # Verify content
        assert len(data["beaches"]) > 0
        assert len(data["historical"]) > 0
        print(f"✓ Local guide: {len(data['beaches'])} beaches, {len(data['historical'])} historical sites")

    def test_get_hotel_history(self):
        """GET /api/hotel/history - Returns hotel history with timeline"""
        response = requests.get(f"{BASE_URL}/api/hotel/history")
        assert response.status_code == 200
        data = response.json()
        
        # Verify history data
        assert "history_tr" in data
        assert "village_age_years" in data
        assert "village_founder" in data
        assert "timeline" in data
        assert len(data["timeline"]) > 0
        print(f"✓ Hotel history: {data['village_age_years']} years, {len(data['timeline'])} timeline events")


# ==================== HOUSEKEEPING AUTO-SCHEDULE ====================
class TestHousekeepingAuto:
    """Housekeeping automation tests"""
    
    def test_auto_schedule_housekeeping(self):
        """POST /api/housekeeping/auto-schedule - Auto-create cleaning tasks for checked-out rooms"""
        response = requests.post(f"{BASE_URL}/api/housekeeping/auto-schedule")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "created" in data
        print(f"✓ Auto-housekeeping: {data['created']} tasks created")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
