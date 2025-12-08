"""
Login Page Object
"""
from selenium.webdriver.common.by import By
from tests.e2e.pages.base_page import BasePage


class LoginPage(BasePage):
    """Login page object"""

    # Locators
    EMAIL_INPUT = (By.NAME, "email")
    PASSWORD_INPUT = (By.NAME, "password")
    SUBMIT_BUTTON = (By.XPATH, "//button[@type='submit']")
    ERROR_MESSAGE = (By.CLASS_NAME, "error")
    SIGNUP_LINK = (By.XPATH, "//a[contains(text(), 'Criar uma conta')]")

    def navigate(self):
        """Navigate to login page"""
        super().navigate("/login")

    def login(self, email: str, password: str):
        """Perform login"""
        self.type(self.EMAIL_INPUT, email)
        self.type(self.PASSWORD_INPUT, password)
        self.click(self.SUBMIT_BUTTON)

    def get_error_message(self) -> str:
        """Get error message if present"""
        try:
            return self.get_text(self.ERROR_MESSAGE)
        except:
            return ""

    def click_signup_link(self):
        """Click on signup link"""
        self.click(self.SIGNUP_LINK)

    def is_error_displayed(self) -> bool:
        """Check if error message is displayed"""
        return self.is_displayed(self.ERROR_MESSAGE)
