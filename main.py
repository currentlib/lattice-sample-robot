import os
import time
from rpa_core import BasePerformer, BusinessRuleException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class GoogleSearchPerformer(BasePerformer):
    QUEUE_NAME = "Invoices"

    def setup(self):
        self.log("Initializing Selenium browser performer...")

    def process(self, item):
        query = item.data.get("query") or item.data.get("invoice_num") or "Lattice RPA Automation"
        self.log(f"Opening Chrome browser and searching Google for query: '{query}'")

        output_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(output_dir, exist_ok=True)
        screenshot_path = os.path.join(output_dir, f"search_{item.id}.png")

        # Configure Chrome options for visible interactive VM desktop execution
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        try:
            driver.get("https://www.google.com")
            time.sleep(1)

            # Find Google search input and type query
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
