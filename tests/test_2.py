import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshots')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


@pytest.fixture
def driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--lang=en-US')
    options.add_argument('--mute-audio')
    drv = webdriver.Chrome(options=options)
    drv.set_page_load_timeout(60)
    yield drv
    drv.quit()


def _save_screenshot(drv, name):
    try:
        path = os.path.join(SCREENSHOT_DIR, name + '.png')
        drv.save_screenshot(path)
        print('Saved screenshot:', path)
    except Exception as e:
        print('Failed to save screenshot:', e)


def _dismiss_consent(drv, wait):
    try:
        consent_btn = WebDriverWait(drv, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(., 'Accept all')] or contains(., 'Accept all') or contains(., 'I agree') or contains(., 'Reject all')]"))
        )
        consent_btn.click()
    except TimeoutException:
        pass


def test_youtube_search_then_navigate_home(driver):
    wait = WebDriverWait(driver, 20)
    try:
        # Step 1: navigate to YouTube
        driver.get('https://www.youtube.com/')
        _dismiss_consent(driver, wait)

        # Step 2: locate search input by name attribute (most stable)
        search_box = wait.until(
            EC.element_to_be_clickable((By.NAME, 'search_query'))
        )
        search_box.clear()
        search_box.send_keys('test')
        assert search_box.get_attribute('value') == 'test', 'Search box did not contain typed text'

        # Step 3: submit the search
        search_box.send_keys(Keys.ENTER)

        # Wait for results page
        wait.until(EC.url_contains('/results?search_query=test'))
        wait.until(EC.title_contains('test'))
        assert 'search_query=test' in driver.current_url, 'URL did not include the search query'
        assert driver.title.lower().startswith('test'), 'Page title did not start with the search term'

        # Step 4: navigate to Home via the guide/side nav
        # Open guide if needed, then click Home entry
        try:
            guide_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Guide"]'))
            )
            guide_btn.click()
        except TimeoutException:
            pass

        home_item = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@title='Home'] | //tp-yt-paper-item[.//yt-formatted-string[normalize-space(text())='Home']] | //ytd-guide-entry-renderer//a[.//yt-formatted-string[normalize-space(text())='Home']]"))
        )
        home_item.click()

        # Wait for navigation back to home
        wait.until(lambda d: d.current_url.rstrip('/') == 'https://www.youtube.com')
        wait.until(EC.title_is('YouTube'))

        assert driver.current_url.rstrip('/') == 'https://www.youtube.com', 'Did not return to YouTube home URL'
        assert driver.title == 'YouTube', 'Page title is not YouTube after clicking Home'

    except (TimeoutException, WebDriverException, AssertionError) as e:
        _save_screenshot(driver, 'youtube_search_then_navigate_home_failure')
        raise
