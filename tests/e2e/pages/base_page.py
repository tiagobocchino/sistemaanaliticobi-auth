"""
Base Page Object for all pages
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from typing import Tuple


class BasePage:
    """Base class for all page objects"""

    def __init__(self, driver: webdriver.Chrome, base_url: str = "http://localhost:5173"):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)

    def navigate(self, path: str = ""):
        """Navigate to a specific path"""
        url = f"{self.base_url}{path}"
        self.driver.get(url)

    def find_element(self, locator: Tuple[By, str]):
        """Find element with explicit wait"""
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_elements(self, locator: Tuple[By, str]):
        """Find multiple elements"""
        return self.driver.find_elements(*locator)

    def click(self, locator: Tuple[By, str]):
        """Click on element"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def type(self, locator: Tuple[By, str], text: str):
        """Type text into element"""
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: Tuple[By, str]) -> str:
        """Get text from element"""
        element = self.find_element(locator)
        return element.text

    def is_displayed(self, locator: Tuple[By, str]) -> bool:
        """Check if element is displayed"""
        try:
            element = self.find_element(locator)
            return element.is_displayed()
        except TimeoutException:
            return False

    def wait_for_url(self, expected_url: str, timeout: int = 10):
        """Wait for URL to match"""
        WebDriverWait(self.driver, timeout).until(
            EC.url_to_be(expected_url)
        )

    def wait_for_url_contains(self, url_part: str, timeout: int = 10):
        """Wait for URL to contain a specific part"""
        WebDriverWait(self.driver, timeout).until(
            EC.url_contains(url_part)
        )

    @property
    def current_url(self) -> str:
        """Get current URL"""
        return self.driver.current_url

    @property
    def title(self) -> str:
        """Get page title"""
        return self.driver.title
