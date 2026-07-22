from rpa_core import BasePerformer, BusinessRuleException
import os
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

class InvoicePerformer(BasePerformer):
    QUEUE_NAME = "Google Test"

    def setup(self):
        self.log("Initializing robot state and checking assets...")

    def process(self, item):
        from playwright.sync_api import sync_playwright



def send_to_telegram(image_path, runner):
    if not BOT_TOKEN or not CHAT_ID:
        runner.log("Telegram credentials missing. Skipping upload.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    runner.log("Sending screenshot to Telegram...")
    
    with open(image_path, "rb") as image_file:
        response = requests.post(
            url,
            data={"chat_id": CHAT_ID, "caption": f"Search results for: '{SEARCH_QUERY}'"},
            files={"photo": image_file}
        )
    
    if response.status_code == 200:
        runner.log("Successfully sent to Telegram!")
    else:
        runner.log(f"Failed to send to Telegram: {response.text}")


def run():
    SEARCH_QUERY = item.data.get("search")
    with sync_playwright() as p:
        self.log("Launching browser...")
        # Headless is True by default in Playwright, which is perfect for Docker
        browser = p.chromium.launch()
        page = browser.new_page()

        self.log("Navigating to Google...")
        page.goto("https://www.google.com")

        # Handle the European cookie consent banner if it appears
        try:
            self.log("Checking for cookie consent...")
            page.get_by_role("button", name="Accept all").click(timeout=3000)
        except Exception:
            pass # No banner appeared, proceed normally

        self.log(f"Typing query: '{SEARCH_QUERY}'...")
        # Locate the search box (Google uses name="q")
        search_box = page.locator("[name='q']")
        search_box.fill(SEARCH_QUERY)
        
        # Simulate pressing the Enter key
        search_box.press("Enter")

        # Wait for the search results page to load
        self.log("Waiting for results to load...")
        page.wait_for_load_state("domcontentloaded")

        # Take the screenshot
        screenshot_path = "/output/search_result.png"
        page.screenshot(path=screenshot_path)
        self.log(f"Success! Screenshot saved to {screenshot_path}")

        send_to_telegram(screenshot_path, self)

        browser.close()
        self.log(f"Invoice #{SEARCH_QUERY} processed successfully!")

    def cleanup(self):
        self.log("Closing robot session.")

if __name__ == "__main__":
    robot = InvoicePerformer()
    robot.run()
