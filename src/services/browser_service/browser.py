from playwright.sync_api import sync_playwright
from src.services.browser_service.security import validate_url

def inspect_webpage(url:str) -> dict:
    url = validate_url(url)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)

        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page_data = {
                "url":page.url,
                "title":page.title(),
                "html":page.content(),
            }

            return page_data

        finally:
            browser.close()