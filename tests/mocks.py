"""
Mock utilities for testing without Supabase connection
"""
from typing import Dict, Any, List, Optional
from unittest.mock import MagicMock, AsyncMock
import uuid
from datetime import datetime, timezone


class MockSupabaseResponse:
    """Mock Supabase response"""
    def __init__(self, data: Any, error: Optional[Dict] = None):
        self.data = data
        self.error = error

    def execute(self):
        """Execute method for query builder"""
        return self


class MockSupabaseQueryBuilder:
    """Mock Supabase query builder"""
    def __init__(self, data: Any):
        self._data = data
        self._filters = []

    def select(self, *args, **kwargs):
        return self

    def eq(self, column: str, value: Any):
        self._filters.append((column, value))
        return self

    def single(self):
        return self

    def insert(self, data: Dict):
        return self

    def update(self, data: Dict):
        return self

    def delete(self):
        return self

    def execute(self):
        return MockSupabaseResponse(self._data)


class MockSupabaseTable:
    """Mock Supabase table"""
    def __init__(self, table_name: str, mock_data: Dict[str, List[Dict]]):
        self.table_name = table_name
        self.mock_data = mock_data

    def select(self, *args, **kwargs):
        data = self.mock_data.get(self.table_name, [])
        return MockSupabaseQueryBuilder(data)

    def insert(self, data: Dict):
        return MockSupabaseQueryBuilder(data)

    def update(self, data: Dict):
        return MockSupabaseQueryBuilder(data)

    def delete(self):
        return MockSupabaseQueryBuilder(None)


class MockSupabaseClient:
    """Mock Supabase client"""
    def __init__(self, mock_data: Dict[str, List[Dict]] = None):
        self.mock_data = mock_data or {}
        self.auth = MockSupabaseAuth()

    def table(self, table_name: str):
        return MockSupabaseTable(table_name, self.mock_data)


class MockSupabaseAuth:
    """Mock Supabase Auth"""
    def __init__(self):
        self.users = {}  # Store mock users

    def sign_up(self, credentials: Dict) -> Dict:
        """Mock sign up"""
        user_id = str(uuid.uuid4())
        email = credentials.get("email")
        password = credentials.get("password")

        # Mock user data
        user_data = {
            "id": user_id,
            "email": email,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "email_confirmed_at": datetime.now(timezone.utc).isoformat(),
            "full_name": credentials.get("data", {}).get("full_name", ""),
        }

        self.users[email] = {
            "password": password,
            "user_data": user_data
        }

        # Mock response
        mock_response = MagicMock()
        mock_response.user = MagicMock(**user_data)
        mock_response.session = MagicMock(
            access_token=f"mock_access_token_{user_id}",
            refresh_token=f"mock_refresh_token_{user_id}",
            expires_in=3600
        )

        return mock_response

    def sign_in_with_password(self, credentials: Dict) -> Dict:
        """Mock sign in"""
        email = credentials.get("email")
        password = credentials.get("password")

        # Check if user exists
        if email not in self.users:
            raise Exception("Invalid login credentials")

        # Check password
        if self.users[email]["password"] != password:
            raise Exception("Invalid login credentials")

        user_data = self.users[email]["user_data"]

        # Mock response
        mock_response = MagicMock()
        mock_response.user = MagicMock(**user_data)
        mock_response.session = MagicMock(
            access_token=f"mock_access_token_{user_data['id']}",
            refresh_token=f"mock_refresh_token_{user_data['id']}",
            expires_in=3600
        )

        return mock_response

    def sign_out(self, jwt: str = None) -> None:
        """Mock sign out"""
        return None

    def refresh_session(self, refresh_token: str) -> Dict:
        """Mock refresh session"""
        # Extract user_id from refresh token
        user_id = refresh_token.replace("mock_refresh_token_", "")

        mock_response = MagicMock()
        mock_response.session = MagicMock(
            access_token=f"mock_new_access_token_{user_id}",
            refresh_token=f"mock_new_refresh_token_{user_id}",
            expires_in=3600
        )

        return mock_response

    def get_user(self, jwt: str) -> Dict:
        """Mock get user"""
        # Extract user_id from token
        user_id = jwt.replace("mock_access_token_", "").replace("mock_new_access_token_", "")

        # Find user by id
        for email, user_info in self.users.items():
            if user_info["user_data"]["id"] == user_id:
                mock_response = MagicMock()
                mock_response.user = MagicMock(**user_info["user_data"])
                return mock_response

        raise Exception("Invalid token")

    def reset_password_email(self, email: str) -> None:
        """Mock reset password email"""
        return None

    def update_user(self, attributes: Dict, jwt: str = None) -> Dict:
        """Mock update user"""
        mock_response = MagicMock()
        mock_response.user = MagicMock(id=str(uuid.uuid4()))
        return mock_response


def create_mock_user(
    user_id: str = None,
    email: str = "test@example.com",
    full_name: str = "Test User",
    role: str = "user",
    cargo: str = None,
    divisao: str = None
) -> Dict[str, Any]:
    """Create mock user data"""
    return {
        "id": user_id or str(uuid.uuid4()),
        "email": email,
        "full_name": full_name,
        "role": role,
        "cargo": cargo,
        "divisao": divisao,
        "cargo_id": None,
        "divisao_id": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "email_confirmed_at": datetime.now(timezone.utc).isoformat(),
    }


def create_mock_token(user_id: str = None) -> str:
    """Create mock JWT token"""
    user_id = user_id or str(uuid.uuid4())
    return f"mock_access_token_{user_id}"


def create_mock_refresh_token(user_id: str = None) -> str:
    """Create mock refresh token"""
    user_id = user_id or str(uuid.uuid4())
    return f"mock_refresh_token_{user_id}"
