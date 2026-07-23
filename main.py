import os
import sys
import time
import subprocess
from rpa_core import BasePerformer
from pywinauto import Application
from PIL import ImageGrab


class NotepadSelectorPerformer(BasePerformer):
    QUEUE_NAME = "Invoices"

    def setup(self):
        self.log("Initializing PyWinAuto UI Automation Performer...")

    def process(self, item):
        text_to_type = item.data.get("text") or item.data.get("query") or item.data.get("invoice_num") or "Hello from Lattice PyWinAuto Selector Automation!"
        self.log(f"Starting Notepad PyWinAuto automation for item '{item.id}' with text: '{text_to_type}'")

        output_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(output_dir, exist_ok=True)
        screenshot_path = os.path.join(output_dir, f"notepad_{item.id}.png")

        # 1. Start Notepad application with UIA backend selector support
        app = Application(backend="uia").start("notepad.exe")
        time.sleep(1.5)

        try:
            # 2. Select main window using title_re selector
            dlg = app.window(title_re=".*Notepad.*")
            dlg.set_focus()

            # 3. Target text editor element via control_type selector ("Document" or "Edit")
            self.log("Targeting Notepad text element via UIA selectors...")
            try:
                editor = dlg.child_window(control_type="Document")
                editor.wait("visible", timeout=3)
            except Exception:
                editor = dlg.child_window(control_type="Edit")
                editor.wait("visible", timeout=3)

            # 4. Type formatted payload text into targeted selector element
            payload_text = (
                f"=== LATTICE RPA PYWINAUTO SELECTOR AUTOMATION ===\n\n"
                f"Queue Item ID : {item.id}\n"
                f"Reference     : {item.reference}\n"
                f"Text Payload  : {text_to_type}\n"
                f"Timestamp     : {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"UI Selector Status: SUCCESSFUL!\n"
            )

            self.log("Typing text directly into UI Automation element...")
            editor.type_keys(payload_text.replace("\n", "{ENTER}"), with_spaces=True, with_newlines=True)
            time.sleep(1.5)

            # 5. Capture screenshot of active screen
            self.log("Capturing desktop screenshot...")
            img = ImageGrab.grab()
            img.save(screenshot_path)

            self.log(f"Successfully saved screenshot to: {screenshot_path}")

            # 6. Mark transaction as successful with screenshot payload
            item.set_success(output={
                "screenshot_path": screenshot_path,
                "typed_text": text_to_type,
                "automation_engine": "PyWinAuto (UIA Selectors)"
            })
        except Exception as e:
            self.log(f"Error during PyWinAuto automation: {e}", level="Error")
            raise
        finally:
            # 7. Cleanly close Notepad process
            try:
                app.kill()
                subprocess.run("taskkill /f /im notepad.exe", shell=True, capture_output=True)
            except Exception:
                pass

    def cleanup(self):
        self.log("PyWinAuto automation session completed.")


if __name__ == "__main__":
    robot = NotepadSelectorPerformer()
    robot.run()
