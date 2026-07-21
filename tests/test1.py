import os
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
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-US")
    drv = webdriver.Chrome(options=options)
    drv.set_page_load_timeout(60)
    yield drv
    drv.quit()


def _save_screenshot(drv, name):
    try:
        path = os.path.join(os.getcwd(), name)
        drv.save_screenshot(path)
        print(f"Screenshot saved to: {path}")
    except Exception as e:
        print(f"Failed to save screenshot: {e}")


def _dismiss_consent_if_present(drv):
    try:
        wait = WebDriverWait(drv, 5)
        btn = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[.//span[contains(., 'Accept all') or contains(., 'I agree') or contains(., 'Reject all')]]"
        )))
        btn.click()
    except Exception:
        pass


def test_youtube_search_basic_query(driver):
    try:
        wait = WebDriverWait(driver, 30)

        # Step 1: Navigate to YouTube
        driver.get("https://www.youtube.com/")
        wait.until(EC.title_contains("YouTube"))
        _dismiss_consent_if_present(driver)

        # Step 2: Locate search input by name attribute (most reliable)
        search_input = wait.until(EC.element_to_be_clickable((By.NAME, "search_query")))
        search_input.clear()
        search_input.send_keys("vayuyantra")

        # Verify value was entered
        assert search_input.get_attribute("value") == "vayuyantra", "Search query did not match expected value"

        # Step 3: Submit the search
        search_input.send_keys(Keys.ENTER)

        # Wait for URL to reflect results page
        wait.until(EC.url_contains("/results"))
        assert "search_query=vayuyantra" in driver.current_url, (
            f"URL does not contain expected query parameter: {driver.current_url}"
        )

        # Wait for title to update
        wait.until(EC.title_contains("vayuyantra"))
        assert "vayuyantra" in driver.title.lower(), f"Page title did not include search term: {driver.title}"

        # Wait for results container to appear
        wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, "ytd-search, #contents ytd-video-renderer, ytd-item-section-renderer"
        )))

        results = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer, ytd-item-section-renderer")
        assert len(results) > 0, "No search results rendered on the results page"

    except Exception as e:
        _save_screenshot(driver, "youtube_search_basic_query_failure.png")
        raise