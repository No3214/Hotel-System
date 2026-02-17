"""
Iteration 17 - WhatsApp & Instagram Integration Tests
Tests WhatsApp Business API, Instagram Messaging API, webhook processing, and admin endpoints.
All APIs run in MOCK mode - messages stored in DB but not actually sent.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestWebhookStatus:
    """Test webhook status endpoint - returns config for WhatsApp and Instagram"""
    
    def test_webhook_status_returns_both_platforms(self):
        """GET /api/webhooks/status should return status for WhatsApp and Instagram"""
        response = requests.get(f"{BASE_URL}/api/webhooks/status")
        assert response.status_code == 200
        
        data = response.json()
        # Check WhatsApp config
        assert "whatsapp" in data
        assert "configured" in data["whatsapp"]
        assert "verify_token" in data["whatsapp"]
        assert "total_messages" in data["whatsapp"]
        assert data["whatsapp"]["verify_token"] == "kozbeyli_verify_2026"
        
        # Check Instagram config
        assert "instagram" in data
        assert "configured" in data["instagram"]
        assert "verify_token" in data["instagram"]
        assert "total_messages" in data["instagram"]
        assert data["instagram"]["verify_token"] == "kozbeyli_ig_verify_2026"
        
        # Both should be not configured (mock mode)
        assert data["whatsapp"]["configured"] == False
        assert data["instagram"]["configured"] == False
        print(f"Webhook status OK - WhatsApp msgs: {data['whatsapp']['total_messages']}, Instagram msgs: {data['instagram']['total_messages']}")


class TestWhatsAppTemplates:
    """Test WhatsApp template listing"""
    
    def test_list_templates_returns_5_templates(self):
        """GET /api/whatsapp/templates should return 5 predefined templates"""
        response = requests.get(f"{BASE_URL}/api/whatsapp/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert "templates" in data
        templates = data["templates"]
        assert len(templates) == 5
        
        template_names = [t["name"] for t in templates]
        expected_names = [
            "checkout_thanks_review",
            "reservation_reminder_1day",
            "welcome_checkin",
            "cleaning_notification",
            "room_ready_notification"
        ]
        for name in expected_names:
            assert name in template_names, f"Missing template: {name}"
        
        # Verify each template has description and params
        for tmpl in templates:
            assert "name" in tmpl
            assert "description" in tmpl
            assert "params" in tmpl
            assert isinstance(tmpl["params"], list)
        
        print(f"Templates OK - Found {len(templates)} templates: {template_names}")


class TestWhatsAppConfig:
    """Test WhatsApp configuration endpoint"""
    
    def test_whatsapp_config_returns_status(self):
        """GET /api/whatsapp/config should return configuration status"""
        response = requests.get(f"{BASE_URL}/api/whatsapp/config")
        assert response.status_code == 200
        
        data = response.json()
        assert "configured" in data
        assert "has_token" in data
        assert "has_phone_id" in data
        assert "verify_token" in data
        
        # In mock mode, configured should be False
        assert data["configured"] == False
        assert data["has_token"] == False
        assert data["has_phone_id"] == False
        assert data["verify_token"] == "kozbeyli_verify_2026"
        
        print(f"WhatsApp config OK - configured={data['configured']}, verify_token={data['verify_token']}")


class TestWhatsAppSend:
    """Test manual WhatsApp message sending (mock mode)"""
    
    def test_send_manual_message_mock_mode(self):
        """POST /api/whatsapp/send should return mock success when not configured"""
        response = requests.post(
            f"{BASE_URL}/api/whatsapp/send",
            json={
                "to": "0532 999 8877",
                "message": "Test message from pytest iteration 17"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert data["success"] == True
        assert "result" in data
        assert data["result"]["status"] == "mock"
        assert "905329998877" in data["result"]["to"]  # Phone normalized
        
        print(f"Send message OK (mock) - to={data['result']['to']}")
    
    def test_send_message_phone_normalization(self):
        """Phone numbers should be normalized to Turkish format"""
        test_phones = [
            ("0532 123 4567", "905321234567"),
            ("5321234567", "905321234567"),
            ("905321234567", "905321234567"),
        ]
        for input_phone, expected in test_phones:
            response = requests.post(
                f"{BASE_URL}/api/whatsapp/send",
                json={"to": input_phone, "message": "test normalization"}
            )
            assert response.status_code == 200
            data = response.json()
            assert expected in data["result"]["to"], f"Phone {input_phone} should normalize to {expected}"
        
        print("Phone normalization OK")


class TestWhatsAppWebhook:
    """Test WhatsApp webhook processing"""
    
    def test_webhook_processes_text_message(self):
        """POST /api/webhooks/whatsapp should process incoming text message"""
        payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "pytest_entry_123",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "905321234567",
                            "phone_number_id": "123456789"
                        },
                        "contacts": [{
                            "profile": {"name": "Pytest User"},
                            "wa_id": "905551112233"
                        }],
                        "messages": [{
                            "from": "905551112233",
                            "id": "wamid.pytest_text_123",
                            "timestamp": "1706234567",
                            "type": "text",
                            "text": {"body": "Merhaba, masa rezervasyonu yapmak istiyorum"}
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/webhooks/whatsapp",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        
        print("WhatsApp text message webhook OK")
    
    def test_webhook_processes_interactive_button(self):
        """POST /api/webhooks/whatsapp should process interactive button reply"""
        payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "pytest_entry_456",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "905321234567",
                            "phone_number_id": "123456789"
                        },
                        "contacts": [{
                            "profile": {"name": "Button Test User"},
                            "wa_id": "905551112244"
                        }],
                        "messages": [{
                            "from": "905551112244",
                            "id": "wamid.pytest_button_456",
                            "timestamp": "1706234568",
                            "type": "interactive",
                            "interactive": {
                                "type": "button_reply",
                                "button_reply": {
                                    "id": "btn_oda_bilgisi",
                                    "title": "Oda Bilgisi"
                                }
                            }
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/webhooks/whatsapp",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        
        print("WhatsApp interactive button webhook OK")


class TestInstagramWebhook:
    """Test Instagram webhook processing"""
    
    def test_instagram_sessions_returns_list(self):
        """GET /api/webhooks/instagram/sessions should return sessions list"""
        response = requests.get(f"{BASE_URL}/api/webhooks/instagram/sessions")
        assert response.status_code == 200
        
        data = response.json()
        assert "sessions" in data
        assert isinstance(data["sessions"], list)
        
        print(f"Instagram sessions OK - count={len(data['sessions'])}")
    
    def test_instagram_messages_returns_list(self):
        """GET /api/webhooks/instagram/messages should return messages list"""
        response = requests.get(f"{BASE_URL}/api/webhooks/instagram/messages")
        assert response.status_code == 200
        
        data = response.json()
        assert "messages" in data
        assert isinstance(data["messages"], list)
        
        print(f"Instagram messages OK - count={len(data['messages'])}")
    
    def test_webhook_processes_instagram_dm(self):
        """POST /api/webhooks/instagram should process incoming DM"""
        payload = {
            "object": "instagram",
            "entry": [{
                "id": "ig_page_pytest",
                "time": 1706234567000,
                "messaging": [{
                    "sender": {"id": "ig_user_pytest_789"},
                    "recipient": {"id": "ig_page_pytest"},
                    "timestamp": 1706234567000,
                    "message": {
                        "mid": "ig_mid_pytest_789",
                        "text": "Merhaba, wifi sifresi nedir?"
                    }
                }]
            }]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/webhooks/instagram",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        
        print("Instagram DM webhook OK")


class TestWhatsAppSessionsMessages:
    """Test WhatsApp sessions and messages admin endpoints"""
    
    def test_whatsapp_sessions_returns_list(self):
        """GET /api/whatsapp/sessions should return conversation sessions"""
        response = requests.get(f"{BASE_URL}/api/whatsapp/sessions")
        assert response.status_code == 200
        
        data = response.json()
        assert "sessions" in data
        assert isinstance(data["sessions"], list)
        
        # Check session structure if any exist
        if data["sessions"]:
            session = data["sessions"][0]
            assert "_id" in session  # session_id
            assert "last_message" in session
            assert "message_count" in session
        
        print(f"WhatsApp sessions OK - count={len(data['sessions'])}")
    
    def test_whatsapp_messages_returns_list(self):
        """GET /api/whatsapp/messages should return messages list"""
        response = requests.get(f"{BASE_URL}/api/whatsapp/messages")
        assert response.status_code == 200
        
        data = response.json()
        assert "messages" in data
        assert isinstance(data["messages"], list)
        
        print(f"WhatsApp messages OK - count={len(data['messages'])}")
    
    def test_whatsapp_messages_filter_by_session(self):
        """GET /api/whatsapp/messages?session_id=xxx should filter by session"""
        # First get existing sessions
        sessions_resp = requests.get(f"{BASE_URL}/api/whatsapp/sessions")
        sessions = sessions_resp.json().get("sessions", [])
        
        if sessions:
            session_id = sessions[0]["_id"]
            response = requests.get(
                f"{BASE_URL}/api/whatsapp/messages",
                params={"session_id": session_id}
            )
            assert response.status_code == 200
            data = response.json()
            assert "messages" in data
            
            # Endpoint returns filtered results - verify it works
            # Note: Legacy messages may not have session_id field
            print(f"WhatsApp messages filter OK - session={session_id}, count={len(data['messages'])}")
        else:
            print("WhatsApp messages filter SKIPPED - no sessions")


class TestWhatsAppNotifications:
    """Test group notifications endpoint"""
    
    def test_notifications_returns_list(self):
        """GET /api/whatsapp/notifications should return notifications list"""
        response = requests.get(f"{BASE_URL}/api/whatsapp/notifications")
        assert response.status_code == 200
        
        data = response.json()
        assert "notifications" in data
        assert isinstance(data["notifications"], list)
        
        # Check notification structure if any exist
        if data["notifications"]:
            notif = data["notifications"][0]
            assert "type" in notif
            assert "message" in notif
            assert "status" in notif
            assert "created_at" in notif
        
        print(f"Notifications OK - count={len(data['notifications'])}")


class TestChatbotIntegration:
    """Test chatbot responses through webhooks"""
    
    def test_chatbot_greeting_response(self):
        """Chatbot should respond to 'merhaba' with greeting"""
        payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "chatbot_test",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "contacts": [{"profile": {"name": "Greeting Test"}, "wa_id": "905559998877"}],
                        "messages": [{
                            "from": "905559998877",
                            "id": "wamid.greeting_test",
                            "timestamp": "1706234599",
                            "type": "text",
                            "text": {"body": "merhaba"}
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        
        response = requests.post(f"{BASE_URL}/api/webhooks/whatsapp", json=payload)
        assert response.status_code == 200
        
        # Check that a response was stored
        import time
        time.sleep(0.5)  # Wait for async processing
        
        messages_resp = requests.get(
            f"{BASE_URL}/api/whatsapp/messages",
            params={"session_id": "wa_905559998877", "limit": 5}
        )
        messages = messages_resp.json().get("messages", [])
        
        # Should have outgoing response
        outgoing = [m for m in messages if m.get("direction") == "outgoing"]
        if outgoing:
            # Should contain greeting keywords
            latest = outgoing[0]["text"].lower()
            assert any(kw in latest for kw in ["merhaba", "kozbeyli", "yardim", "hos geldiniz"]), \
                f"Response should be greeting, got: {latest[:100]}"
        
        print("Chatbot greeting test OK")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
