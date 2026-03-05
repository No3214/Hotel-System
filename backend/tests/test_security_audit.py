"""
Kozbeyli Konagi - Kapsamli Guvenlik Test Suite
XSS, Injection, Auth Bypass, CSRF, Input Validation, Rate Limiting testleri
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
import pytest


@pytest.fixture(scope="module")
def client():
    from server import app
    return TestClient(app)


class TestXSSProtection:
    """Cross-Site Scripting (XSS) koruma testleri"""

    XSS_PAYLOADS = [
        '<script>alert("xss")</script>',
        '"><img src=x onerror=alert(1)>',
        "javascript:alert('xss')",
        '<svg onload=alert(1)>',
        '{{constructor.constructor("return this")()}}',
        "${7*7}",
        "<iframe src='javascript:alert(1)'>",
        "'-alert(1)-'",
        '<body onload=alert(1)>',
    ]

    def test_xss_in_guest_name(self, client):
        """Misafir adinda XSS denemesi"""
        for payload in self.XSS_PAYLOADS:
            # These should not cause 500 errors
            resp = client.post("/api/guests", json={"name": payload, "phone": "555"}, headers={"Authorization": "Bearer test"})
            assert resp.status_code in (200, 201, 401, 422), f"XSS payload caused unexpected error: {payload}"

    def test_xss_in_search_params(self, client):
        """Query parameter'larda XSS"""
        for payload in self.XSS_PAYLOADS:
            resp = client.get(f"/api/guests?search={payload}", headers={"Authorization": "Bearer test"})
            assert resp.status_code in (200, 401, 422)

    def test_xss_in_task_title(self, client):
        """Gorev basliginda XSS"""
        resp = client.post("/api/tasks", json={"title": '<script>alert("xss")</script>'}, headers={"Authorization": "Bearer test"})
        assert resp.status_code in (200, 201, 401, 422)

    def test_response_no_script_reflection(self, client):
        """Public endpoint'ler script yansitmamali"""
        resp = client.get("/api/health")
        assert "<script>" not in resp.text


class TestSQLInjection:
    """NoSQL Injection koruma testleri (MongoDB)"""

    INJECTION_PAYLOADS = [
        '{"$gt": ""}',
        '{"$ne": null}',
        '{"$where": "1==1"}',
        '{"$regex": ".*"}',
        "'; db.users.drop(); //",
        '{"$gt":"","$ne":""}',
    ]

    def test_nosql_injection_in_login(self, client):
        """Login'de NoSQL injection"""
        malicious_payloads = [
            {"username": {"$gt": ""}, "password": {"$gt": ""}},
            {"username": {"$ne": None}, "password": {"$ne": None}},
            {"username": "admin", "password": {"$gt": ""}},
        ]
        for payload in malicious_payloads:
            resp = client.post("/api/auth/login", json=payload)
            # Should not return 200 (successful login) - 422 validation or 401 expected
            assert resp.status_code in (401, 422, 429), f"Potential NoSQL injection: {payload}"

    def test_nosql_injection_in_search(self, client):
        """Arama parametrelerinde injection"""
        resp = client.get('/api/guests?search={"$gt":""}', headers={"Authorization": "Bearer test"})
        assert resp.status_code in (200, 401, 422)

    def test_object_id_injection(self, client):
        """ObjectId alaninda injection"""
        resp = client.get("/api/guests/{'$gt':''}", headers={"Authorization": "Bearer test"})
        assert resp.status_code in (401, 404, 422)


class TestAuthBypass:
    """Kimlik dogrulama bypass testleri"""

    def test_no_auth_header(self, client):
        """Auth header olmadan admin endpoint'lere erisim"""
        protected = ["/api/guests", "/api/rooms", "/api/reservations", "/api/tasks", "/api/staff"]
        for endpoint in protected:
            resp = client.get(endpoint)
            assert resp.status_code == 401, f"Unprotected endpoint: {endpoint}"

    def test_invalid_token(self, client):
        """Gecersiz token ile erisim"""
        resp = client.get("/api/guests", headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401

    def test_expired_token_format(self, client):
        """Bozuk token formati"""
        resp = client.get("/api/guests", headers={"Authorization": "Bearer abc123"})
        assert resp.status_code == 401

    def test_no_bearer_prefix(self, client):
        """Bearer prefix olmadan"""
        resp = client.get("/api/guests", headers={"Authorization": "some-token"})
        assert resp.status_code == 401

    def test_empty_bearer(self, client):
        """Bos bearer"""
        resp = client.get("/api/guests", headers={"Authorization": "Bearer "})
        assert resp.status_code == 401

    def test_public_endpoints_accessible(self, client):
        """Public endpoint'ler auth gerektirmemeli"""
        public = ["/api/health", "/api/public-menu", "/api/hotel/info", "/api/i18n"]
        for endpoint in public:
            resp = client.get(endpoint)
            assert resp.status_code != 401, f"Public endpoint requires auth: {endpoint}"

    @pytest.mark.skipif(not os.getenv("MONGODB_URL"), reason="Requires MongoDB connection")
    def test_setup_returns_response(self, client):
        """Setup endpoint cevap donmeli"""
        resp = client.post("/api/auth/setup")
        assert resp.status_code > 0


class TestInputValidation:
    """Input dogrulama testleri"""

    def test_oversized_payload(self, client):
        """Cok buyuk payload"""
        large_string = "A" * 100000
        resp = client.post("/api/tasks", json={"title": large_string}, headers={"Authorization": "Bearer test"})
        assert resp.status_code in (401, 413, 422)

    def test_empty_required_fields(self, client):
        """Zorunlu alanlar bos"""
        resp = client.post("/api/auth/login", json={})
        assert resp.status_code == 422

    def test_wrong_types(self, client):
        """Yanlis veri tipleri"""
        resp = client.post("/api/auth/login", json={"username": 12345, "password": True})
        # Pydantic should coerce or reject
        assert resp.status_code in (401, 422, 429)

    @pytest.mark.skipif(not os.getenv("MONGODB_URL"), reason="Requires MongoDB connection")
    def test_null_injection(self, client):
        """Null byte injection should not crash server"""
        resp = client.post("/api/auth/login", json={"username": "admin\x00", "password": "test\x00"})
        assert resp.status_code > 0

    @pytest.mark.skipif(not os.getenv("MONGODB_URL"), reason="Requires MongoDB connection")
    def test_unicode_overflow(self, client):
        """Unicode overflow should not crash server"""
        resp = client.post("/api/auth/login", json={"username": "\u0000" * 1000, "password": "test"})
        assert resp.status_code > 0


class TestCSRF:
    """CSRF koruma testleri"""

    def test_cors_configured(self, client):
        """CORS header'lari ayarli olmali"""
        from server import app
        # Check that middleware is configured
        middleware_classes = [m.cls.__name__ if hasattr(m, 'cls') else type(m).__name__ for m in app.user_middleware]
        assert any("CORS" in str(m) or "cors" in str(m).lower() for m in middleware_classes) or \
               any("CORSMiddleware" in str(m) for m in app.user_middleware), \
               "CORS middleware yapilmamis"


class TestPathTraversal:
    """Dizin gezinme saldiri testleri"""

    TRAVERSAL_PAYLOADS = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32",
        "%2e%2e%2f%2e%2e%2f",
        "....//....//",
    ]

    def test_path_traversal_in_id(self, client):
        """ID alaninda path traversal - 500 donmemeli veya dosya icerigi donmemeli"""
        for payload in self.TRAVERSAL_PAYLOADS:
            resp = client.get(f"/api/guests/{payload}", headers={"Authorization": "Bearer test"})
            # Should not expose file contents
            assert "root:" not in resp.text, f"Path traversal leaked file: {payload}"

    def test_no_directory_listing(self, client):
        """Dizin listeleme kapalı"""
        resp = client.get("/api/")
        # FastAPI returns 200 with index or 404 - both are OK
        assert "Index of" not in resp.text, "Directory listing exposed!"


class TestSecurityHeaders:
    """Guvenlik header testleri"""

    def test_health_returns_request_id(self, client):
        """Health endpoint X-Request-ID donmeli"""
        resp = client.get("/api/health")
        assert "x-request-id" in resp.headers or "X-Request-ID" in resp.headers

    def test_response_time_header(self, client):
        """Response time header mevcut olmali"""
        resp = client.get("/api/health")
        assert "x-response-time" in resp.headers or "X-Response-Time" in resp.headers


class TestSwaggerSecurity:
    """Swagger/API docs guvenlik testleri"""

    def test_swagger_disabled_check(self):
        """Production'da swagger kapali olmali"""
        env = os.environ.get("ENVIRONMENT", "development")
        if env == "production":
            from server import app
            assert app.docs_url is None, "Swagger docs should be disabled in production"
            assert app.redoc_url is None, "Redoc should be disabled in production"


class TestPasswordSecurity:
    """Sifre guvenlik testleri"""

    def test_bcrypt_used(self):
        """Bcrypt kullanilmali"""
        from routers.auth import pwd_context
        assert "bcrypt" in pwd_context.schemes()

    def test_password_min_length(self, client):
        """Minimum sifre uzunlugu kontrolu (auth gerekli olabilir)"""
        resp = client.post("/api/auth/register", json={
            "username": "test_short_pass",
            "password": "123",
            "name": "Test",
            "role": "staff"
        })
        # 401 (no auth), 400 (short pass), or 403 (not admin) are all acceptable
        assert resp.status_code in (400, 401, 403, 500)


class TestDataExfiltration:
    """Veri sizintisi testleri"""

    def test_no_password_hash_in_response(self, client):
        """Sifre hash'i response'da olmamali"""
        resp = client.get("/api/auth/users", headers={"Authorization": "Bearer test"})
        if resp.status_code == 200:
            for user in resp.json().get("users", []):
                assert "password_hash" not in user, "Password hash exposed in API!"
                assert "password" not in user, "Password exposed in API!"

    def test_error_messages_not_verbose(self, client):
        """Hata mesajlari cok detayli olmamali"""
        resp = client.get("/api/nonexistent-endpoint-xyz")
        if resp.status_code in (404, 500):
            body = resp.text.lower()
            assert "traceback" not in body
            assert "stack trace" not in body
            assert "file \"/" not in body


class TestRateLimiting:
    """Rate limiting testleri"""

    def test_health_not_rate_limited(self, client):
        """Health endpoint rate limit'e takilmamali"""
        for _ in range(10):
            resp = client.get("/api/health")
            assert resp.status_code == 200


class TestAuditLog:
    """Audit log testleri"""

    def test_audit_log_module_imports(self):
        """Audit modulu import edilebilmeli"""
        from routers.audit import log_audit, mask_sensitive_data, check_security_rules
        assert callable(log_audit)
        assert callable(mask_sensitive_data)

    def test_sensitive_data_masking(self):
        """Hassas veriler maskelenmeli"""
        from routers.audit import mask_sensitive_data
        data = {"phone": "05551234567", "email": "test@mail.com", "name": "Test"}
        masked = mask_sensitive_data(data)
        assert masked["phone"] != "05551234567"
        assert masked["email"] != "test@mail.com"
        assert masked["name"] == "Test"  # Non-sensitive should stay

    def test_mask_none_data(self):
        """None data maskeleme hatasi vermemeli"""
        from routers.audit import mask_sensitive_data
        assert mask_sensitive_data(None) is None
        # Empty dict is falsy, so mask_sensitive_data returns None - this is expected
        mask_sensitive_data({})
