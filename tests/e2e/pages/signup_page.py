"""
Signup Page Object
"""
from selenium.webdriver.common.by import By
from tests.e2e.pages.base_page import BasePage


class SignupPage(BasePage):
    """Signup page object"""

    # Locators
    NAME_INPUT = (By.NAME, "full_name")
    EMAIL_INPUT = (By.NAME, "email")
    PASSWORD_INPUT = (By.NAME, "password")
    CONFIRM_PASSWORD_INPUT = (By.NAME, "confirmPassword")
    SUBMIT_BUTTON = (By.XPATH, "//button[@type='submit']")
    ERROR_MESSAGE = (By.CLASS_NAME, "error")
    SUCCESS_MESSAGE = (By.CLASS_NAME, "success")
    LOGIN_LINK = (By.XPATH, "//a[contains(text(), 'Já tem uma conta?')]")

    def navigate(self):
        """Navigate to signup page"""
        super().navigate("/signup")

    def signup(self, full_name: str, email: str, password: str, confirm_password: str):
        """Perform signup"""
        self.type(self.NAME_INPUT, full_name)
        self.type(self.EMAIL_INPUT, email)
        self.type(self.PASSWORD_INPUT, password)
        self.type(self.CONFIRM_PASSWORD_INPUT, confirm_password)
        self.click(self.SUBMIT_BUTTON)

    def get_error_message(self) -> str:
        """Get error message if present"""
        try:
            return self.get_text(self.ERROR_MESSAGE)
        except:
            return ""

    def get_success_message(self) -> str:
        """Get success message if present"""
        try:
            return self.get_text(self.SUCCESS_MESSAGE)
        except:
            return ""

    def click_login_link(self):
        """Click on login link"""
        self.click(self.LOGIN_LINK)

    def is_error_displayed(self) -> bool:
        """Check if error message is displayed"""
        return self.is_displayed(self.ERROR_MESSAGE)

    def is_success_displayed(self) -> bool:
        """Check if success message is displayed"""
        return self.is_displayed(self.SUCCESS_MESSAGE)
