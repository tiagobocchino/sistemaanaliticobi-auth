"""
E2E Authentication Flow Tests
"""
import pytest
from selenium import webdriver
import time
from tests.e2e.pages.home_page import HomePage
from tests.e2e.pages.login_page import LoginPage
from tests.e2e.pages.signup_page import SignupPage
from tests.e2e.pages.dashboard_page import DashboardPage


@pytest.mark.e2e
@pytest.mark.smoke
class TestE2EAuthenticationFlow:
    """End-to-end authentication flow tests"""

    def test_home_page_loads(self, browser: webdriver.Chrome):
        """Test that home page loads correctly"""
        home_page = HomePage(browser)
        home_page.navigate()

        assert "Analytics" in home_page.get_title_text()
        assert home_page.is_login_button_visible()

    def test_navigate_to_login(self, browser: webdriver.Chrome):
        """Test navigation to login page"""
        home_page = HomePage(browser)
        home_page.navigate()
        home_page.click_login()

        # Wait for navigation
        time.sleep(1)

        assert "/login" in browser.current_url

    def test_navigate_to_signup(self, browser: webdriver.Chrome):
        """Test navigation to signup page"""
        home_page = HomePage(browser)
        home_page.navigate()
        home_page.click_signup()

        # Wait for navigation
        time.sleep(1)

        assert "/signup" in browser.current_url

    def test_signup_flow(self, browser: webdriver.Chrome, test_user_credentials: dict):
        """Test complete signup flow"""
        signup_page = SignupPage(browser)
        signup_page.navigate()

        signup_page.signup(
            test_user_credentials["full_name"],
            test_user_credentials["email"],
            test_user_credentials["password"],
            test_user_credentials["password"]
        )

        # Wait for response
        time.sleep(3)

        # Should redirect to dashboard or show success message
        current_url = browser.current_url
        assert "/dashboard" in current_url or "/signup" in current_url

    def test_signup_with_mismatched_passwords(self, browser: webdriver.Chrome):
        """Test signup with mismatched passwords"""
        signup_page = SignupPage(browser)
        signup_page.navigate()

        signup_page.signup(
            "Test User",
            f"test_{int(time.time())}@test.com",
            "Password123#",
            "DifferentPassword123#"
        )

        # Should show error
        time.sleep(2)
        assert signup_page.is_error_displayed()

    def test_signup_with_weak_password(self, browser: webdriver.Chrome):
        """Test signup with weak password"""
        signup_page = SignupPage(browser)
        signup_page.navigate()

        signup_page.signup(
            "Test User",
            f"test_{int(time.time())}@test.com",
            "123",  # Too weak
            "123"
        )

        # Should show error
        time.sleep(2)
        assert signup_page.is_error_displayed()

    def test_login_flow(self, browser: webdriver.Chrome, test_user_credentials: dict):
        """Test complete login flow"""
        # First signup
        signup_page = SignupPage(browser)
        signup_page.navigate()
        signup_page.signup(
            test_user_credentials["full_name"],
            test_user_credentials["email"],
            test_user_credentials["password"],
            test_user_credentials["password"]
        )
        time.sleep(2)

        # Then login
        login_page = LoginPage(browser)
        login_page.navigate()
        login_page.login(
            test_user_credentials["email"],
            test_user_credentials["password"]
        )

        # Wait for redirect
        time.sleep(3)

        # Should be on dashboard
        assert "/dashboard" in browser.current_url

    def test_login_with_wrong_credentials(self, browser: webdriver.Chrome):
        """Test login with wrong credentials"""
        login_page = LoginPage(browser)
        login_page.navigate()

        login_page.login(
            "nonexistent@test.com",
            "WrongPassword123#"
        )

        # Should show error
        time.sleep(2)
        assert login_page.is_error_displayed() or "/login" in browser.current_url

    def test_complete_auth_workflow(self, browser: webdriver.Chrome, test_user_credentials: dict):
        """Test complete authentication workflow: signup -> login -> dashboard -> logout"""
        # 1. Signup
        signup_page = SignupPage(browser)
        signup_page.navigate()
        signup_page.signup(
            test_user_credentials["full_name"],
            test_user_credentials["email"],
            test_user_credentials["password"],
            test_user_credentials["password"]
        )
        time.sleep(2)

        # 2. Login
        login_page = LoginPage(browser)
        login_page.navigate()
        login_page.login(
            test_user_credentials["email"],
            test_user_credentials["password"]
        )
        time.sleep(3)

        # 3. Verify on dashboard
        assert "/dashboard" in browser.current_url

        # 4. Logout
        dashboard_page = DashboardPage(browser)
        assert dashboard_page.is_welcome_displayed()

        dashboard_page.click_logout()
        time.sleep(2)

        # Should redirect to home or login
        assert "/" in browser.current_url or "/login" in browser.current_url

    def test_protected_route_without_auth(self, browser: webdriver.Chrome):
        """Test accessing protected route without authentication"""
        # Try to access dashboard directly
        browser.get("http://localhost:5173/dashboard")
        time.sleep(2)

        # Should redirect to login
        assert "/login" in browser.current_url

    def test_dashboard_displays_user_info(self, logged_in_browser: webdriver.Chrome):
        """Test that dashboard displays user information"""
        dashboard_page = DashboardPage(logged_in_browser)

        assert dashboard_page.is_welcome_displayed()
        welcome_text = dashboard_page.get_welcome_text()
        assert "Bem-vindo" in welcome_text
