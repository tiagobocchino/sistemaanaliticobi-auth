"""
Users Management Page Object
"""
from selenium.webdriver.common.by import By
from tests.e2e.pages.base_page import BasePage


class UsersPage(BasePage):
    """Users management page object"""

    # Locators
    PAGE_TITLE = (By.TAG_NAME, "h3")
    USERS_TABLE = (By.TAG_NAME, "table")
    TABLE_ROWS = (By.XPATH, "//table/tbody/tr")
    CARGO_INPUTS = (By.XPATH, "//input[@placeholder='Cargo']")
    DIVISAO_INPUTS = (By.XPATH, "//input[@placeholder='Divisão']")
    SAVE_BUTTONS = (By.XPATH, "//button[contains(text(), 'Salvar')]")
    ERROR_MESSAGE = (By.CLASS_NAME, "error")
    LOADING_MESSAGE = (By.XPATH, "//*[contains(text(), 'Carregando')]")

    def navigate(self):
        """Navigate to users page"""
        super().navigate("/users")

    def is_table_displayed(self) -> bool:
        """Check if users table is displayed"""
        return self.is_displayed(self.USERS_TABLE)

    def get_page_title(self) -> str:
        """Get page title"""
        return self.get_text(self.PAGE_TITLE)

    def get_users_count(self) -> int:
        """Get number of users in table"""
        rows = self.find_elements(self.TABLE_ROWS)
        return len(rows)

    def edit_user_cargo(self, row_index: int, new_cargo: str):
        """Edit cargo for a specific user (0-indexed)"""
        cargo_inputs = self.find_elements(self.CARGO_INPUTS)
        if row_index < len(cargo_inputs):
            cargo_inputs[row_index].clear()
            cargo_inputs[row_index].send_keys(new_cargo)

    def edit_user_divisao(self, row_index: int, new_divisao: str):
        """Edit divisao for a specific user (0-indexed)"""
        divisao_inputs = self.find_elements(self.DIVISAO_INPUTS)
        if row_index < len(divisao_inputs):
            divisao_inputs[row_index].clear()
            divisao_inputs[row_index].send_keys(new_divisao)

    def click_save_button(self, row_index: int):
        """Click save button for a specific user (0-indexed)"""
        save_buttons = self.find_elements(self.SAVE_BUTTONS)
        if row_index < len(save_buttons):
            save_buttons[row_index].click()

    def is_error_displayed(self) -> bool:
        """Check if error message is displayed"""
        return self.is_displayed(self.ERROR_MESSAGE)

    def get_error_message(self) -> str:
        """Get error message"""
        try:
            return self.get_text(self.ERROR_MESSAGE)
        except:
            return ""
