import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import secrets_info


class SeleniumBrowser:
    driver = None

    def __init__(self):
        self.driver = webdriver.Chrome()

    def open_url(self, url, cookie_value):
        self.driver.get(url)
        cookie = {'name': 'talkbank', 'value': cookie_value, 'domain': 'sla.talkbank.org'}
        self.driver.add_cookie(cookie)

    def close_url(self):
        self.driver.close()

    def add_input(self, by: By, value: str, text: str):
        field = self.driver.find_element(by, value)
        field.send_keys(text)
        time.sleep(1)

    def wait_and_click(self, by: By, value: str, timeout: int = 10):
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        ).click()

    def click_button(self, by: By, value: str):
        button = self.driver.find_element(by, value)
        button.click()
        time.sleep(1)

    def login_talkbank(self, email: str, password: str):
        self.click_button(by=By.CSS_SELECTOR, value="div._button_14b4t_1._blackWhite_14b4t_46")
        self.add_input(by=By.ID, value="authModals_userName", text=email)
        self.add_input(by=By.ID, value="authModals_pswd", text=password)
        self.click_button(by=By.ID, value="authModals_loginBtn")

    def show_metadata(self):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        print(soup.prettify())



value = "s%3AEnoOE80lGm9qWSHsYTc0d6zkc9GpxSuO.kPlnjpDHDTmMwPeYs3YGm9RMCR0cytI5i4WMRHJOvRE"
url = "https://sla.talkbank.org/TBB/childes/DutchAfrikaans/Asymmetries/CK-TD/c01.cha"

seleniumBrowser = SeleniumBrowser()
seleniumBrowser.open_url(url=url, cookie_value=value)

time.sleep(5)

seleniumBrowser.login_talkbank(secrets_info.email, secrets_info.password)

time.sleep(10)

seleniumBrowser.show_metadata()

time.sleep(10)

seleniumBrowser.close_url()
