"""
Pytest configuration and fixtures for Analytics Platform tests
"""
import pytest
import os
from typing import Generator, Dict, Any
from httpx import AsyncClient
from fastapi.testclient import TestClient
import sys
from unittest.mock import patch, MagicMock, Mock

# Add src to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock Supabase BEFORE importing anything else
from tests.mocks import (
    MockSupabaseClient,
    MockSupabaseAuth,
    create_mock_user,
    create_mock_token,
    create_mock_refresh_token
)

# Patch supabase create_client before any imports
mock_supabase_global = MockSupabaseClient()
mock_supabase_global.auth = MockSupabaseAuth()

with patch('supabase.create_client', return_value=mock_supabase_global):
    with patch('supabase._sync.client.create_client', return_value=mock_supabase_global):
        from main import app
        from src.config import get_settings

# Test user credentials
TEST_USER_EMAIL = "test_user@test.com"
TEST_USER_PASSWORD = "TestPassword123#"
TEST_USER_NAME = "Test User"

TEST_ADMIN_EMAIL = "test_admin@test.com"
TEST_ADMIN_PASSWORD = "AdminPassword123#"
TEST_ADMIN_NAME = "Test Admin"


@pytest.fixture(scope="session")
def test_settings():
    """Get test settings"""
    settings = get_settings()
    return settings


@pytest.fixture(scope="function", autouse=True)
def mock_supabase(monkeypatch):
    """
    Mock Supabase client for all tests
    This fixture runs automatically for every test
    """
    # Create mock Supabase client and auth
    mock_client = MockSupabaseClient()
    mock_auth = MockSupabaseAuth()
    mock_client.auth = mock_auth

    # Mock at module level where they are imported
    import src.supabase_client
    monkeypatch.setattr(src.supabase_client, "supabase_client", mock_client)
    monkeypatch.setattr(src.supabase_client, "supabase_admin_client", mock_client)

    # Mock in auth service
    import src.auth.service
    monkeypatch.setattr(src.auth.service, "supabase_client", mock_client)

    # Mock in dependencies
    try:
        import dependencies
        monkeypatch.setattr(dependencies, "supabase_client", mock_client)
    except:
        pass

    # Mock in routes
    try:
        import routes
        monkeypatch.setattr(routes, "supabase_client", mock_client)
    except:
        pass

    return mock_client


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """FastAPI TestClient fixture"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def async_client() -> Generator[AsyncClient, None, None]:
    """Async HTTP client fixture"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
def test_user_data() -> Dict[str, Any]:
    """Test user data"""
    return {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "full_name": TEST_USER_NAME
    }


@pytest.fixture(scope="function")
def test_admin_data() -> Dict[str, Any]:
    """Test admin user data"""
    return {
        "email": TEST_ADMIN_EMAIL,
        "password": TEST_ADMIN_PASSWORD,
        "full_name": TEST_ADMIN_NAME
    }


@pytest.fixture(scope="function")
def auth_headers(client: TestClient, test_user_data: Dict[str, Any], mock_supabase) -> Dict[str, str]:
    """
    Create a test user, login, and return auth headers
    This fixture creates a new user for each test
    """
    # Signup
    signup_response = client.post("/auth/signup", json=test_user_data)

    # If signup successful, get token from response
    if signup_response.status_code in [200, 201]:
        data = signup_response.json()
        if "tokens" in data and data["tokens"]:
            token = data["tokens"]["access_token"]
            return {"Authorization": f"Bearer {token}"}

    # Login
    response = client.post("/auth/signin", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })

    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return {}


@pytest.fixture(scope="function")
def admin_headers(client: TestClient, test_admin_data: Dict[str, Any], mock_supabase) -> Dict[str, str]:
    """
    Create a test admin user, login, and return auth headers
    This fixture creates a new admin for each test
    """
    # Signup admin
    signup_response = client.post("/auth/signup", json=test_admin_data)

    # Login
    response = client.post("/auth/signin", json={
        "email": test_admin_data["email"],
        "password": test_admin_data["password"]
    })

    if response.status_code == 200:
        token = response.json()["access_token"]
        user_id = response.json()["user"]["id"]

        # Mock the user as admin in the database
        mock_user_data = {
            "id": user_id,
            "email": test_admin_data["email"],
            "full_name": test_admin_data["full_name"],
            "role": "admin",
            "cargo": None,
            "divisao": None,
        }
        mock_supabase.mock_data["users"] = [mock_user_data]

        return {
            "Authorization": f"Bearer {token}",
            "user_id": user_id
        }

    return {}


@pytest.fixture(scope="function")
def cleanup_test_users(client: TestClient):
    """
    Cleanup fixture that runs after test
    Ideally should delete test users from Supabase
    """
    yield
    # TODO: Implement cleanup logic to delete test users from Supabase
    # This requires admin access to Supabase
    pass


# Test result tracking for accuracy calculation
test_results = {
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "errors": 0
}


def pytest_runtest_logreport(report):
    """Hook to track test results"""
    if report.when == "call":
        if report.outcome == "passed":
            test_results["passed"] += 1
        elif report.outcome == "failed":
            test_results["failed"] += 1
        elif report.outcome == "skipped":
            test_results["skipped"] += 1


def pytest_sessionfinish(session, exitstatus):
    """Hook to calculate and display accuracy at the end"""
    total = test_results["passed"] + test_results["failed"]
    if total > 0:
        accuracy = (test_results["passed"] / total) * 100
        print(f"\n{'='*60}")
        print(f"TEST ACCURACY REPORT")
        print(f"{'='*60}")
        print(f"Passed:   {test_results['passed']}")
        print(f"Failed:   {test_results['failed']}")
        print(f"Skipped:  {test_results['skipped']}")
        print(f"Total:    {total}")
        print(f"Accuracy: {accuracy:.2f}%")
        print(f"{'='*60}")

        if accuracy >= 85.0:
            print(f"[PASSED] - Accuracy >= 85% (Target: 85%)")
        else:
            print(f"[FAILED] - Accuracy < 85% (Target: 85%)")
        print(f"{'='*60}\n")
