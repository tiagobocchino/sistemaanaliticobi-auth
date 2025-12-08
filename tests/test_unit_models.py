"""
Unit tests for models (no Supabase dependency)
"""
import pytest
from src.auth.models import (
    UserSignUp,
    UserSignIn,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordUpdateRequest
)
from pydantic import ValidationError
import uuid
from datetime import datetime


@pytest.mark.unit
class TestAuthModels:
    """Test Pydantic models"""

    def test_user_signup_valid(self):
        """Test UserSignUp with valid data"""
        data = {
            "email": "test@example.com",
            "password": "SecurePass123#",
            "full_name": "Test User"
        }
        user = UserSignUp(**data)
        assert user.email == "test@example.com"
        assert user.password == "SecurePass123#"
        assert user.full_name == "Test User"

    def test_user_signup_invalid_email(self):
        """Test UserSignUp with invalid email"""
        data = {
            "email": "invalid-email",
            "password": "SecurePass123#"
        }
        with pytest.raises(ValidationError):
            UserSignUp(**data)

    def test_user_signup_missing_password(self):
        """Test UserSignUp with missing password"""
        data = {
            "email": "test@example.com"
        }
        with pytest.raises(ValidationError):
            UserSignUp(**data)

    def test_user_signin_valid(self):
        """Test UserSignIn with valid data"""
        data = {
            "email": "test@example.com",
            "password": "SecurePass123#"
        }
        user = UserSignIn(**data)
        assert user.email == "test@example.com"
        assert user.password == "SecurePass123#"

    def test_user_signin_invalid_email(self):
        """Test UserSignIn with invalid email"""
        data = {
            "email": "not-an-email",
            "password": "password"
        }
        with pytest.raises(ValidationError):
            UserSignIn(**data)

    def test_user_response_valid(self):
        """Test UserResponse with valid data"""
        data = {
            "id": str(uuid.uuid4()),
            "email": "test@example.com",
            "full_name": "Test User",
            "created_at": datetime.now().isoformat()
        }
        user = UserResponse(**data)
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"

    def test_token_response_valid(self):
        """Test TokenResponse with valid data"""
        user_data = {
            "id": str(uuid.uuid4()),
            "email": "test@example.com",
            "full_name": "Test User",
            "created_at": datetime.now().isoformat()
        }
        data = {
            "access_token": "token123",
            "refresh_token": "refresh123",
            "expires_in": 3600,
            "user": user_data
        }
        token = TokenResponse(**data)
        assert token.access_token == "token123"
        assert token.refresh_token == "refresh123"
        assert token.expires_in == 3600

    def test_refresh_token_request_valid(self):
        """Test RefreshTokenRequest with valid data"""
        data = {"refresh_token": "refresh123"}
        req = RefreshTokenRequest(**data)
        assert req.refresh_token == "refresh123"

    def test_refresh_token_request_missing(self):
        """Test RefreshTokenRequest with missing token"""
        with pytest.raises(ValidationError):
            RefreshTokenRequest(**{})

    def test_password_reset_request_valid(self):
        """Test PasswordResetRequest with valid email"""
        data = {"email": "test@example.com"}
        req = PasswordResetRequest(**data)
        assert req.email == "test@example.com"

    def test_password_reset_request_invalid_email(self):
        """Test PasswordResetRequest with invalid email"""
        data = {"email": "not-an-email"}
        with pytest.raises(ValidationError):
            PasswordResetRequest(**data)

    def test_password_update_request_valid(self):
        """Test PasswordUpdateRequest with valid password"""
        data = {"new_password": "NewSecure123#"}
        req = PasswordUpdateRequest(**data)
        assert req.new_password == "NewSecure123#"

    def test_password_update_request_missing(self):
        """Test PasswordUpdateRequest with missing password"""
        with pytest.raises(ValidationError):
            PasswordUpdateRequest(**{})


@pytest.mark.unit
class TestUserUpdateModel:
    """Test User Update model"""

    def test_user_update_all_fields(self):
        """Test UserUpdate with all fields"""
        from src.users.models import UserUpdate

        data = {
            "cargo": "Manager",
            "divisao": "IT",
            "role": "admin"
        }
        update = UserUpdate(**data)
        assert update.cargo == "Manager"
        assert update.divisao == "IT"
        assert update.role == "admin"

    def test_user_update_partial(self):
        """Test UserUpdate with partial data"""
        from src.users.models import UserUpdate

        data = {"cargo": "Director"}
        update = UserUpdate(**data)
        assert update.cargo == "Director"
        assert update.divisao is None
        assert update.role is None

    def test_user_update_empty(self):
        """Test UserUpdate with no data"""
        from src.users.models import UserUpdate

        update = UserUpdate()
        assert update.cargo is None
        assert update.divisao is None
        assert update.role is None
