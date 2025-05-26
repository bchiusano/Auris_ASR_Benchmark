import os
import time

import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import secrets


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

    def click_button(self, by: By, value: str):
        button = self.driver.find_element(by, value)
        button.click()
        time.sleep(1)

    def login_talkbank(self, email: str, password: str):
        self.click_button(by=By.CLASS_NAME, value="_button_14b4t_1 _blackWhite_14b4t_46")
        self.add_input(by=By.ID, value="authModals_userName", text=email)
        self.add_input(by=By.ID, value="authModals_pswd", text= password)
        self.click_button(by=By.ID, value="authModals_loginBtn")

    def show_metadata(self):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        print(soup.prettify())


def downloader(cookie_value, url):
    """
    Downloader from webscrapingChildes
    :param cookie: The personal childes talkbank cookie value manually obtained by the user
    :param url: The url from which to access all desired download links, for instance:
    :return: will download files
    """

    """
    # Building the path name for the output directory
    path = url.split("/")
    output_dir = "./CHILDES data"
    for e in path:
        if path.index(e) > path.index("childes"):
            output_dir += ("/" + e)

    # Creating the output directoryhttps://media.talkbank.org/childes/Clinical-Other/Zwitserlood/TD/8910/0wav
    os.makedirs(output_dir, exist_ok=True)
    """

    # Specifying the necessary info for the website to allow the download, i.e. the referer page, and the personal cookie ID
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Referer": url,
        'Cookie': f'talkbank={cookie_value}'
    }

    time.sleep(30)

    # page = requests.get(url, headers=headers)

    # TODO:
    # Save audio file name
    # Save child's transcript lines
    # Save time stamps


value = "s%3AEnoOE80lGm9qWSHsYTc0d6zkc9GpxSuO.kPlnjpDHDTmMwPeYs3YGm9RMCR0cytI5i4WMRHJOvRE"
url = "https://sla.talkbank.org/TBB/childes/DutchAfrikaans/Asymmetries/CK-TD/c01.cha"

downloader(cookie_value=value, url=url)
