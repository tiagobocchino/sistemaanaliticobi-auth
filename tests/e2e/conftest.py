"""
Selenium E2E test configuration and fixtures
"""
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from typing import Generator
import time


# Test configuration
FRONTEND_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:8000"

# Test user credentials
E2E_TEST_USER_EMAIL = f"e2e_test_{int(time.time())}@test.com"
E2E_TEST_USER_PASSWORD = "E2ETestPassword123#"
E2E_TEST_USER_NAME = "E2E Test User"

E2E_TEST_ADMIN_EMAIL = "tiago.bocchino@4pcapital.com.br"
E2E_TEST_ADMIN_PASSWORD = "Master123#"


@pytest.fixture(scope="function")
def browser() -> Generator[webdriver.Chrome, None, None]:
    """
    Selenium WebDriver fixture
    Creates a new Chrome browser instance for each test
    """
    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Uncomment for headless mode (faster, no UI)
    # chrome_options.add_argument("--headless")

    # Initialize driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Set implicit wait
    driver.implicitly_wait(10)

    yield driver

    # Cleanup
    driver.quit()


@pytest.fixture(scope="function")
def headless_browser() -> Generator[webdriver.Chrome, None, None]:
    """
    Headless browser for faster tests
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()


@pytest.fixture(scope="function")
def test_user_credentials():
    """Test user credentials for E2E tests"""
    return {
        "email": E2E_TEST_USER_EMAIL,
        "password": E2E_TEST_USER_PASSWORD,
        "full_name": E2E_TEST_USER_NAME
    }


@pytest.fixture(scope="function")
def admin_credentials():
    """Admin credentials for E2E tests"""
    return {
        "email": E2E_TEST_ADMIN_EMAIL,
        "password": E2E_TEST_ADMIN_PASSWORD
    }


@pytest.fixture(scope="function")
def logged_in_browser(browser: webdriver.Chrome, test_user_credentials: dict) -> webdriver.Chrome:
    """
    Browser with user already logged in
    """
    from tests.e2e.pages.login_page import LoginPage
    from tests.e2e.pages.signup_page import SignupPage

    # Go to signup page
    signup_page = SignupPage(browser)
    signup_page.navigate()

    # Try to signup (may fail if user exists)
    try:
        signup_page.signup(
            test_user_credentials["full_name"],
            test_user_credentials["email"],
            test_user_credentials["password"],
            test_user_credentials["password"]
        )
    except:
        pass  # User may already exist

    # Go to login page
    login_page = LoginPage(browser)
    login_page.navigate()

    # Login
    login_page.login(
        test_user_credentials["email"],
        test_user_credentials["password"]
    )

    # Wait for redirect
    time.sleep(2)

    return browser


@pytest.fixture(scope="function")
def logged_in_admin_browser(browser: webdriver.Chrome, admin_credentials: dict) -> webdriver.Chrome:
    """
    Browser with admin user already logged in
    """
    from tests.e2e.pages.login_page import LoginPage

    login_page = LoginPage(browser)
    login_page.navigate()

    login_page.login(
        admin_credentials["email"],
        admin_credentials["password"]
    )

    # Wait for redirect
    time.sleep(2)

    return browser


# E2E Test result tracking
e2e_test_results = {
    "passed": 0,
    "failed": 0,
    "skipped": 0
}


def pytest_runtest_logreport(report):
    """Hook to track E2E test results"""
    if report.when == "call" and "e2e" in report.keywords:
        if report.outcome == "passed":
            e2e_test_results["passed"] += 1
        elif report.outcome == "failed":
            e2e_test_results["failed"] += 1
        elif report.outcome == "skipped":
            e2e_test_results["skipped"] += 1
