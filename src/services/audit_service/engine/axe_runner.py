from pathlib import Path
from playwright.sync_api import sync_playwright

AXE_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "assets"
    / "axe.min.js"
)

def run_axe_audit(html: str) -> dict:
    if not isinstance(html, str) or not html.strip():
        raise ValueError("HTML content must be a non-empty string.")

    if not AXE_SCRIPT_PATH.is_file():
        raise FileNotFoundError(
            f"axe-core JavaScript file not found: {AXE_SCRIPT_PATH}"
        )

    axe_script = AXE_SCRIPT_PATH.read_text(encoding="utf-8")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)

        try:
            page = browser.new_page()
            page.set_content(html, wait_until="domcontentloaded")

            page.add_script_tag(content=axe_script)

            results = page.evaluate(
                """async () => {
                    return await axe.run(document);
                }"""
            )

            return results

        finally:
            browser.close()