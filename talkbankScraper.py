import os
import time

import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


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


    driver = webdriver.Chrome()
    driver.get(url=url)
    cookie = {'name' : 'talkbank', 'value' : cookie_value, 'domain': 'sla.talkbank.org'}
    driver.add_cookie(cookie)

    time.sleep(30)

    #page = requests.get(url, headers=headers)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    print(soup.prettify())

    # TODO:
    # Save audio file name
    # Save child's transcript lines
    # Save time stamps


value = "s%3AEnoOE80lGm9qWSHsYTc0d6zkc9GpxSuO.kPlnjpDHDTmMwPeYs3YGm9RMCR0cytI5i4WMRHJOvRE"
url = "https://sla.talkbank.org/TBB/childes/DutchAfrikaans/Asymmetries/CK-TD/c01.cha"

downloader(cookie_value=value, url=url)
