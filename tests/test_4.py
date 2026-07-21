import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


@pytest.fixture
def driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--lang=en-US')
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US,en'})
    drv = webdriver.Chrome(options=options)
    drv.set_page_load_timeout(45)
    yield drv
    drv.quit()


def _save_screenshot(driver, name):
    try:
        path = f"/tmp/{name}_{int(time.time())}.png"
        driver.save_screenshot(path)
        print(f"Screenshot saved to {path}")
    except Exception as e:
        print(f"Failed to save screenshot: {e}")


def _try_accept_cookies(driver, wait):
    consent_xpaths = [
        "//button[.//span[contains(text(),'Accept all')]]",
        "//button[.//span[contains(text(),'I agree')]]",
        "//button[.//span[contains(text(),'Reject all')]]",
        "//button[@aria-label='Accept all']",
        "//button[@aria-label='Reject all']"
    ]
    for xp in consent_xpaths:
        try:
            btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xp)))
            btn.click()
            return True
        except TimeoutException:
            continue
        except Exception:
            continue
    return False


def test_youtube_subscriptions_redirects_to_signin(driver):
    wait = WebDriverWait(driver, 20)
    try:
        # Step 1: Navigate to YouTube
        driver.get('https://www.youtube.com/')
        wait.until(EC.title_contains('YouTube'))

        # Step 2: Accept cookies if presented (consent page may or may not appear)
        _try_accept_cookies(driver, wait)

        # Step 3: Navigate directly to Subscriptions feed (mirrors clicking the Subscriptions tab)
        driver.get('https://www.youtube.com/feed/subscriptions')
        wait.until(EC.url_contains('/feed/subscriptions'))
        wait.until(EC.title_contains('Subscriptions'))
        assert '/feed/subscriptions' in driver.current_url, f"Expected subscriptions URL, got {driver.current_url}"
        assert 'Subscriptions' in driver.title, f"Expected 'Subscriptions' in title, got {driver.title}"

        # Step 4: Click the Sign in link
        sign_in_locators = [
            (By.XPATH, "//a[@aria-label='Sign in']"),
            (By.XPATH, "//a[.//span[normalize-space(text())='Sign in']]"),
            (By.XPATH, "//a[contains(@href,'accounts.google.com') and contains(@href,'ServiceLogin')]"),
            (By.CSS_SELECTOR, "input#identifierId")
        ]
        sign_in_el = None
        for by, sel in sign_in_locators:
            try:
                sign_in_el = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, sel)))
                break
            except TimeoutException:
                continue
        assert sign_in_el is not None, 'Sign in link not found on subscriptions page'
        sign_in_el.click()

        # Step 5: Verify redirect to Google sign-in
        wait.until(EC.url_contains('accounts.google.com'))
        assert 'accounts.google.com' in driver.current_url, f"Expected redirect to Google sign-in, got {driver.current_url}"
        assert 'service=youtube' in driver.current_url or 'continue=' in driver.current_url, \
            f"Expected youtube service continue param in URL, got {driver.current_url}"

        # Step 6: Verify the Sign in heading on the Google page
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//h1[normalize-space(text())='Sign in']")))
        except TimeoutException:
            # Fallback: check page source contains 'Sign in'
            assert 'Sign in' in driver.page_source, 'Sign in heading/text not found on Google sign-in page'

    except (TimeoutException, NoSuchElementException, AssertionError) as e:
        _save_screenshot(driver, 'youtube_subscriptions_signin_failure')
        raise
    except Exception as e:
        _save_screenshot(driver, 'youtube_subscriptions_signin_unexpected')
        raise
