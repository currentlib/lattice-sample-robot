import os
import sys
import subprocess
from rpa_core import BasePerformer, BusinessRuleException
from playwright.sync_api import sync_playwright


class GoogleSearchPerformer(BasePerformer):
    QUEUE_NAME = "Invoices"

    def setup(self):
        self.log("Initializing robot & checking Playwright browser setup...")
        try:
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        except Exception as e:
            self.log(f"Playwright browser install note: {e}", level="Warning")

    def process(self, item):
        query = item.data.get("query") or item.data.get("invoice_num") or "Lattice RPA Automation"
        self.log(f"Opening browser and searching Google for query: '{query}'")

        output_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(output_dir, exist_ok=True)
        screenshot_path = os.path.join(output_dir, f"search_{item.item_id}.png")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://www.google.com", wait_until="domcontentloaded")
            
            # Handle potential cookie banner
            try:
                page.click("button:has-text('Accept all')", timeout=2000)
            except Exception:
                pass

            # Search query
            search_box = page.query_selector("textarea[name='q']") or page.query_selector("input[name='q']")
            if search_box:
                search_box.fill(query)
                page.keyboard.press("Enter")
                page.wait_for_timeout(3000)

            # Capture screenshot
            page.screenshot(path=screenshot_path)
            browser.close()

        self.log(f"Successfully saved screenshot to: {screenshot_path}")

        # Set output on queue item
        item.set_successful(output={"screenshot_path": screenshot_path, "query": query})


if __name__ == "__main__":
    robot = GoogleSearchPerformer()
    robot.run()
