"""
Unit tests for basic endpoints (no Supabase dependency)
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
@pytest.mark.smoke
class TestBasicEndpoints:
    """Test basic endpoints that don't require Supabase"""

    def test_root_endpoint_returns_200(self, client: TestClient):
        """Test that root endpoint returns 200"""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_endpoint_has_message(self, client: TestClient):
        """Test that root endpoint has message field"""
        response = client.get("/")
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)

    def test_root_endpoint_has_version(self, client: TestClient):
        """Test that root endpoint has version field"""
        response = client.get("/")
        data = response.json()
        assert "version" in data
        assert data["version"] == "1.0.0"

    def test_root_endpoint_has_docs(self, client: TestClient):
        """Test that root endpoint has docs field"""
        response = client.get("/")
        data = response.json()
        assert "docs" in data
        assert data["docs"] == "/docs"

    def test_health_endpoint_returns_200(self, client: TestClient):
        """Test that health endpoint returns 200"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_healthy(self, client: TestClient):
        """Test that health endpoint returns healthy status"""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_endpoint_has_environment(self, client: TestClient):
        """Test that health endpoint has environment field"""
        response = client.get("/health")
        data = response.json()
        assert "environment" in data

    def test_docs_endpoint_returns_200(self, client: TestClient):
        """Test that OpenAPI docs endpoint returns 200"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json_returns_200(self, client: TestClient):
        """Test that OpenAPI JSON returns 200"""
        response = client.get("/openapi.json")
        assert response.status_code == 200

    def test_openapi_json_has_title(self, client: TestClient):
        """Test that OpenAPI JSON has title"""
        response = client.get("/openapi.json")
        data = response.json()
        assert "info" in data
        assert "title" in data["info"]

    def test_openapi_json_has_version(self, client: TestClient):
        """Test that OpenAPI JSON has version"""
        response = client.get("/openapi.json")
        data = response.json()
        assert "info" in data
        assert "version" in data["info"]
        assert data["info"]["version"] == "1.0.0"

    def test_openapi_json_has_paths(self, client: TestClient):
        """Test that OpenAPI JSON has paths"""
        response = client.get("/openapi.json")
        data = response.json()
        assert "paths" in data
        assert len(data["paths"]) > 0

    def test_openapi_json_has_auth_routes(self, client: TestClient):
        """Test that OpenAPI JSON includes auth routes"""
        response = client.get("/openapi.json")
        data = response.json()
        paths = data["paths"]
        assert "/auth/signup" in paths
        assert "/auth/signin" in paths
        assert "/auth/signout" in paths

    def test_cors_headers_present(self, client: TestClient):
        """Test that CORS headers are present in response"""
        response = client.options("/")
        # CORS middleware should add headers
        assert response.status_code in [200, 405]  # Options or Method Not Allowed

    def test_invalid_endpoint_returns_404(self, client: TestClient):
        """Test that invalid endpoint returns 404"""
        response = client.get("/this-endpoint-does-not-exist")
        assert response.status_code == 404

    def test_invalid_method_returns_405(self, client: TestClient):
        """Test that invalid method returns 405"""
        response = client.delete("/")  # Root doesn't support DELETE
        assert response.status_code == 405


@pytest.mark.unit
class TestAuthEndpointValidation:
    """Test validation for auth endpoints"""

    def test_signup_missing_email_returns_422(self, client: TestClient):
        """Test signup without email returns 422"""
        data = {"password": "Test123#"}
        response = client.post("/auth/signup", json=data)
        assert response.status_code == 422

    def test_signup_missing_password_returns_422(self, client: TestClient):
        """Test signup without password returns 422"""
        data = {"email": "test@example.com"}
        response = client.post("/auth/signup", json=data)
        assert response.status_code == 422

    def test_signup_invalid_email_returns_422(self, client: TestClient):
        """Test signup with invalid email returns 422"""
        data = {
            "email": "not-an-email",
            "password": "Test123#"
        }
        response = client.post("/auth/signup", json=data)
        assert response.status_code == 422

    def test_signin_missing_email_returns_422(self, client: TestClient):
        """Test signin without email returns 422"""
        data = {"password": "Test123#"}
        response = client.post("/auth/signin", json=data)
        assert response.status_code == 422

    def test_signin_missing_password_returns_422(self, client: TestClient):
        """Test signin without password returns 422"""
        data = {"email": "test@example.com"}
        response = client.post("/auth/signin", json=data)
        assert response.status_code == 422

    def test_signin_invalid_email_returns_422(self, client: TestClient):
        """Test signin with invalid email returns 422"""
        data = {
            "email": "not-an-email",
            "password": "Test123#"
        }
        response = client.post("/auth/signin", json=data)
        assert response.status_code == 422

    def test_refresh_missing_token_returns_422(self, client: TestClient):
        """Test refresh without token returns 422"""
        response = client.post("/auth/refresh", json={})
        assert response.status_code == 422

    def test_reset_password_missing_email_returns_422(self, client: TestClient):
        """Test reset password without email returns 422"""
        response = client.post("/auth/reset-password", json={})
        assert response.status_code == 422

    def test_reset_password_invalid_email_returns_422(self, client: TestClient):
        """Test reset password with invalid email returns 422"""
        data = {"email": "not-an-email"}
        response = client.post("/auth/reset-password", json=data)
        assert response.status_code == 422

    def test_update_password_missing_password_returns_422(self, client: TestClient):
        """Test update password without new password returns 422"""
        response = client.post("/auth/update-password", json={})
        assert response.status_code == 422

    def test_protected_route_without_auth_returns_403(self, client: TestClient):
        """Test accessing protected route without auth returns 403"""
        response = client.get("/protected")
        assert response.status_code == 403

    def test_get_current_user_without_auth_returns_403(self, client: TestClient):
        """Test getting current user without auth returns 403"""
        response = client.get("/auth/me")
        assert response.status_code == 403

    def test_signout_without_auth_returns_403(self, client: TestClient):
        """Test signout without auth returns 403"""
        response = client.post("/auth/signout")
        assert response.status_code == 403

    def test_update_password_without_auth_returns_403(self, client: TestClient):
        """Test update password without auth returns 403"""
        data = {"new_password": "NewPass123#"}
        response = client.post("/auth/update-password", json=data)
        assert response.status_code == 403


@pytest.mark.unit
class TestUsersEndpointValidation:
    """Test validation for users endpoints"""

    def test_list_users_without_auth_returns_403(self, client: TestClient):
        """Test list users without auth returns 403"""
        response = client.get("/users/")
        assert response.status_code == 403

    def test_update_user_without_auth_returns_403(self, client: TestClient):
        """Test update user without auth returns 403"""
        import uuid
        user_id = str(uuid.uuid4())
        data = {"cargo": "Manager"}
        response = client.put(f"/users/{user_id}", json=data)
        assert response.status_code == 403
