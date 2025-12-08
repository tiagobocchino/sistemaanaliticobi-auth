"""
Dashboard Page Object
"""
from selenium.webdriver.common.by import By
from tests.e2e.pages.base_page import BasePage


class DashboardPage(BasePage):
    """Dashboard page object"""

    # Locators
    WELCOME_TEXT = (By.XPATH, "//h2[contains(text(), 'Bem-vindo')]")
    SIDEBAR = (By.CLASS_NAME, "sidebar")
    LOGOUT_BUTTON = (By.XPATH, "//button[contains(text(), 'Logout')]")
    DASHBOARD_LINK = (By.XPATH, "//a[contains(text(), 'Dashboard')]")
    ANALYSES_LINK = (By.XPATH, "//a[contains(text(), 'Análises')]")
    USERS_LINK = (By.XPATH, "//a[contains(text(), 'Gerenciar Usuários')]")
    USER_EMAIL = (By.CLASS_NAME, "user-email")

    def navigate(self):
        """Navigate to dashboard page"""
        super().navigate("/dashboard")

    def is_welcome_displayed(self) -> bool:
        """Check if welcome message is displayed"""
        return self.is_displayed(self.WELCOME_TEXT)

    def get_welcome_text(self) -> str:
        """Get welcome text"""
        return self.get_text(self.WELCOME_TEXT)

    def click_logout(self):
        """Click logout button"""
        self.click(self.LOGOUT_BUTTON)

    def click_analyses_link(self):
        """Click on analyses link"""
        self.click(self.ANALYSES_LINK)

    def click_users_link(self):
        """Click on users management link"""
        self.click(self.USERS_LINK)

    def is_users_link_visible(self) -> bool:
        """Check if users link is visible (admin only)"""
        return self.is_displayed(self.USERS_LINK)

    def get_user_email(self) -> str:
        """Get logged in user email"""
        try:
            return self.get_text(self.USER_EMAIL)
        except:
            return ""
