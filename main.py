import os
import sys
from types import ModuleType

# Fix pywin32 DLL search path for virtual environments (.venv)
if sys.platform == "win32":
    site_pkg = os.path.join(os.path.dirname(os.path.dirname(sys.executable)), "Lib", "site-packages")
    for d in [os.path.join(site_pkg, "win32"), os.path.join(site_pkg, "win32", "lib"), os.path.join(site_pkg, "pywin32_system32")]:
        if os.path.isdir(d):
            if hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(d)
                except Exception:
                    pass
            os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
            if d not in sys.path:
                sys.path.insert(0, d)

# Mock win32ui if C++ MFC runtime DLL is missing on host OS
try:
    import win32ui
except ImportError:
    win32ui_mock = ModuleType("win32ui")
    sys.modules["win32ui"] = win32ui_mock

import time
import subprocess
from rpa_core import BasePerformer
from pywinauto import Application, Desktop
from PIL import ImageGrab


class NotepadSelectorPerformer(BasePerformer):
    QUEUE_NAME = "Invoices"

    def setup(self):
        self.log("Initializing PyWinAuto UI Automation Performer...")
        self.log("Testing assets...")
        self.assetText = self.get_asset("AssetText")
        self.log(f"Asset loaded successfully: {self.assetText}")
        self.assetNumber = self.get_asset_int("AssetNumber")
        self.log(f"Asset loaded successfully: {self.assetNumber}")
        self.assetBoolean = self.get_asset_bool("AssetBool")
        self.log(f"Asset loaded successfully: {self.assetBoolean}")
        self.assetJson = self.get_asset_json("AssetJson")
        self.log(f"Asset loaded successfully: {self.assetJson["key2"]}")
        self.assetCredential = self.get_credential("AssetCredential")
        self.log(f"Asset loaded successfully: {self.assetCredential}")
        

    def process(self, item):
        text_to_type = item.data.get("text") or item.data.get("query") or item.data.get("invoice_num") or "Hello from Lattice PyWinAuto Selector Automation!"
        self.log(f"Starting Notepad PyWinAuto automation for item '{item.id}' with text: '{text_to_type}'")

        output_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(output_dir, exist_ok=True)
        screenshot_path = os.path.join(output_dir, f"notepad_{item.id}.png")

        # 1. Start Notepad process
        proc = subprocess.Popen(["notepad.exe"])
        time.sleep(2)  # Wait for Notepad window to render

        try:
            # 2. Select main window across desktop using Desktop(backend="uia")
            self.log("Connecting to Notepad window using Desktop UIA selector...")
            dlg = Desktop(backend="uia").window(title_re=".*Notepad.*")
            dlg.wait("visible", timeout=10)
            dlg.maximize()
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
            editor.set_edit_text(payload_text)
            time.sleep(1.5)

            # 5. Capture screenshot of active screen
            self.log("Capturing desktop screenshot...")
            try:
                # With tscon restoring the physical console, ImageGrab.grab() captures the full 1080p desktop
                img = ImageGrab.grab(all_screens=True)
                img.save(screenshot_path)
                self.log(f"Successfully saved screenshot to: {screenshot_path}")
            except Exception as e:
                self.log(f"Failed to capture screenshot (locked/headless session): {e}", level="Warning")
                screenshot_path = ""

            # Try to send a notification if a connection named "TelegramNotifier" is set up
            try:
                self.log("Attempting to send Telegram notification with screenshot...")
                self.send_notification(
                    connection_name="TelegramNotifier",
                    title=f"New Invoice Processed - {item.id[:8]}",
                    message=f"Successfully processed invoice reference: {item.reference}\n\nStatus: UI Automation Completed",
                    attachment_file_path=screenshot_path if screenshot_path else None
                )
                self.log("Telegram notification sent successfully.")
            except Exception as e:
                self.log(f"Failed to send Telegram notification: {e}", level="Warning")

            # 6. Mark transaction as successful with screenshot payload
            item.set_success(output={
                "screenshot_path": screenshot_path,
                "typed_text": text_to_type,
                "automation_engine": "PyWinAuto (Desktop UIA Selectors)"
            })
        except Exception as e:
            self.log(f"Error during PyWinAuto automation: {e}", level="Error")
            raise
        finally:
            # 7. Cleanly close Notepad process
            try:
                proc.terminate()
                subprocess.run("taskkill /f /im notepad.exe", shell=True, capture_output=True)
            except Exception:
                pass

    def cleanup(self):
        self.log("PyWinAuto automation session completed.")


if __name__ == "__main__":
    robot = NotepadSelectorPerformer()
    robot.run()
