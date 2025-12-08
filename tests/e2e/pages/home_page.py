"""
Home Page Object
"""
from selenium.webdriver.common.by import By
from tests.e2e.pages.base_page import BasePage


class HomePage(BasePage):
    """Home page object"""

    # Locators
    TITLE = (By.TAG_NAME, "h1")
    LOGIN_BUTTON = (By.XPATH, "//button[contains(text(), 'Entrar')]")
    SIGNUP_BUTTON = (By.XPATH, "//button[contains(text(), 'Criar Conta')]")
    DASHBOARD_BUTTON = (By.XPATH, "//button[contains(text(), 'Dashboard')]")

    def navigate(self):
        """Navigate to home page"""
        super().navigate("/")

    def click_login(self):
        """Click on login button"""
        self.click(self.LOGIN_BUTTON)

    def click_signup(self):
        """Click on signup button"""
        self.click(self.SIGNUP_BUTTON)

    def click_dashboard(self):
        """Click on dashboard button (for logged in users)"""
        self.click(self.DASHBOARD_BUTTON)

    def is_login_button_visible(self) -> bool:
        """Check if login button is visible"""
        return self.is_displayed(self.LOGIN_BUTTON)

    def is_dashboard_button_visible(self) -> bool:
        """Check if dashboard button is visible (user is logged in)"""
        return self.is_displayed(self.DASHBOARD_BUTTON)

    def get_title_text(self) -> str:
        """Get page title text"""
        return self.get_text(self.TITLE)
