from playwright.sync_api import sync_playwright

def inspect_webpage(url:str) -> dict:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)

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