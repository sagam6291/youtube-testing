import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture
def driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--lang=en-US')
    drv = webdriver.Chrome(options=options)
    drv.set_page_load_timeout(60)
    yield drv
    drv.quit()


def test_youtube_search_intellicredence(driver):
    wait = WebDriverWait(driver, 20)
    screenshot_path = 'youtube_search_failure.png'
    try:
        driver.get('https://www.youtube.com/')
        wait.until(EC.title_contains('YouTube'))

        search_box = wait.until(
            EC.element_to_be_clickable((By.NAME, 'search_query'))
        )
        search_box.clear()
        search_box.send_keys('intellicredence')

        assert search_box.get_attribute('value') == 'intellicredence', \
            'Search box did not contain the expected query.'

        search_box.send_keys(Keys.ENTER)

        wait.until(EC.url_contains('/results'))
        wait.until(EC.url_contains('search_query=intellicredence'))

        wait.until(EC.title_contains('intellicredence'))

        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ytd-search'))
        )

        current_url = driver.current_url
        assert 'search_query=intellicredence' in current_url, \
            f'Unexpected URL after search: {current_url}'

        page_title = driver.title.lower()
        assert 'intellicredence' in page_title, \
            f'Page title did not include search keyword: {driver.title}'

    except Exception as e:
        try:
            driver.save_screenshot(screenshot_path)
        except Exception:
            pass
        raise e
