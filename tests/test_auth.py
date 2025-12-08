"""
Authentication tests for Analytics Platform
"""
import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any


@pytest.mark.auth
class TestAuthentication:
    """Test authentication endpoints"""

    def test_health_check(self, client: TestClient):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    @pytest.mark.smoke
    def test_signup_new_user(self, client: TestClient):
        """Test user signup with valid data"""
        user_data = {
            "email": f"newuser_{pytest.timestamp}@test.com",
            "password": "SecurePassword123#",
            "full_name": "New Test User"
        }

        response = client.post("/auth/signup", json=user_data)

        # May return 201 (created) or 200 (requires confirmation)
        assert response.status_code in [200, 201]
        data = response.json()

        # Check response structure
        if response.status_code == 201:
            assert "tokens" in data or "message" in data
        else:
            assert "message" in data

    def test_signup_invalid_email(self, client: TestClient):
        """Test signup with invalid email"""
        user_data = {
            "email": "invalid-email",
            "password": "SecurePassword123#",
            "full_name": "Test User"
        }

        response = client.post("/auth/signup", json=user_data)
        assert response.status_code == 422  # Validation error

    def test_signup_weak_password(self, client: TestClient):
        """Test signup with weak password"""
        user_data = {
            "email": "test@example.com",
            "password": "123",  # Too weak
            "full_name": "Test User"
        }

        response = client.post("/auth/signup", json=user_data)
        # Supabase may reject or our validation may reject
        assert response.status_code in [400, 422]

    def test_signup_missing_fields(self, client: TestClient):
        """Test signup with missing required fields"""
        user_data = {
            "email": "test@example.com"
            # Missing password
        }

        response = client.post("/auth/signup", json=user_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.smoke
    def test_signin_valid_credentials(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test signin with valid credentials"""
        # First, ensure user exists
        client.post("/auth/signup", json=test_user_data)

        # Then login
        response = client.post("/auth/signin", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]

    def test_signin_invalid_email(self, client: TestClient):
        """Test signin with non-existent email"""
        response = client.post("/auth/signin", json={
            "email": "nonexistent@test.com",
            "password": "SomePassword123#"
        })

        assert response.status_code in [400, 401]

    def test_signin_wrong_password(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test signin with wrong password"""
        # Ensure user exists
        client.post("/auth/signup", json=test_user_data)

        # Try wrong password
        response = client.post("/auth/signin", json={
            "email": test_user_data["email"],
            "password": "WrongPassword123#"
        })

        assert response.status_code in [400, 401]

    def test_signin_missing_fields(self, client: TestClient):
        """Test signin with missing fields"""
        response = client.post("/auth/signin", json={
            "email": "test@example.com"
            # Missing password
        })

        assert response.status_code == 422

    @pytest.mark.smoke
    def test_get_current_user(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test getting current user data"""
        response = client.get("/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert "email" in data
        assert "full_name" in data

    def test_get_current_user_no_auth(self, client: TestClient):
        """Test getting current user without authentication"""
        response = client.get("/auth/me")

        assert response.status_code == 403  # Forbidden or Unauthorized

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)

        assert response.status_code in [401, 403]

    @pytest.mark.smoke
    def test_signout(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test user signout"""
        response = client.post("/auth/signout", headers=auth_headers)

        # Signout should succeed
        assert response.status_code in [200, 204]

    def test_signout_no_auth(self, client: TestClient):
        """Test signout without authentication"""
        response = client.post("/auth/signout")

        assert response.status_code == 403

    def test_refresh_token(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test token refresh"""
        # Signup and login
        client.post("/auth/signup", json=test_user_data)
        login_response = client.post("/auth/signin", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })

        assert login_response.status_code == 200
        refresh_token = login_response.json()["refresh_token"]

        # Refresh token
        response = client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_refresh_token_invalid(self, client: TestClient):
        """Test token refresh with invalid token"""
        response = client.post("/auth/refresh", json={
            "refresh_token": "invalid_token"
        })

        assert response.status_code in [400, 401]

    def test_protected_route_with_auth(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test accessing protected route with authentication"""
        response = client.get("/protected", headers=auth_headers)

        assert response.status_code == 200

    def test_protected_route_without_auth(self, client: TestClient):
        """Test accessing protected route without authentication"""
        response = client.get("/protected")

        assert response.status_code == 403

    def test_reset_password_request(self, client: TestClient, test_user_data: Dict[str, Any]):
        """Test password reset request"""
        # Ensure user exists
        client.post("/auth/signup", json=test_user_data)

        # Request password reset
        response = client.post("/auth/reset-password", json={
            "email": test_user_data["email"]
        })

        # Should succeed even if email doesn't exist (security best practice)
        assert response.status_code == 200

    def test_reset_password_invalid_email(self, client: TestClient):
        """Test password reset with invalid email format"""
        response = client.post("/auth/reset-password", json={
            "email": "invalid-email"
        })

        assert response.status_code == 422


# Add timestamp for unique emails
pytest.timestamp = 0


@pytest.fixture(autouse=True)
def increment_timestamp():
    """Auto-increment timestamp for unique emails"""
    import time
    pytest.timestamp = int(time.time() * 1000)
