import os
import time
from rpa_core import BasePerformer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


class GoogleSearchPerformer(BasePerformer):
    QUEUE_NAME = "Invoices"

    def setup(self):
        self.log("Initializing browser performer (Chrome / Edge)...")

    def _get_driver(self):
        # Try Chrome first, fallback to pre-installed Microsoft Edge
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        except Exception as e:
            self.log(f"Chrome not available ({e}), falling back to Microsoft Edge...", level="Warning")
            options = webdriver.EdgeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)

    def process(self, item):
        query = item.data.get("query") or item.data.get("invoice_num") or "Lattice RPA Automation"
        self.log(f"Opening browser and searching DuckDuckGo/Google for query: '{query}'")

        output_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(output_dir, exist_ok=True)
        screenshot_path = os.path.join(output_dir, f"search_{item.id}.png")

        driver = self._get_driver()

        try:
            # Use DuckDuckGo to avoid bot reCAPTCHA blocking during automated testing
            driver.get("https://html.duckduckgo.com/html/")
            time.sleep(1)

            # Find search input and type query
            search_box = driver.find_element(By.NAME, "q")
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)

            time.sleep(3)

            # Capture screenshot
            driver.save_screenshot(screenshot_path)
            self.log(f"Successfully saved search screenshot to: {screenshot_path}")

            # Mark item successful with output payload
            item.set_success(output={"screenshot_path": screenshot_path, "query": query})
        except Exception as e:
            self.log(f"Error during browser automation: {e}", level="Error")
            raise
        finally:
            driver.quit()

    def cleanup(self):
        self.log("Browser automation session closed.")


if __name__ == "__main__":
    robot = GoogleSearchPerformer()
    robot.run()
