import time
import pyautogui
from pywinauto.application import Application
from pywinauto import Desktop
from interaction_utils import *


if __name__ == '__main__':

    width, height = pyautogui.size()
    print(f"Screen Resolution - Width: {width}, Height: {height}\n")

    time.sleep(5)
    print("Debug sleep. Resuming in 5 seconds...")

    # Connect to the desktop using the UI Automation (uia) backend
    desktop: Desktop = Desktop(backend="uia")

    # Get the currently active (focused) window
    active_window = desktop.window(active_only=True)

    # Print details for the active window and its elements
    if active_window:
        print(f"Active Window: {active_window.window_text()} (Type: {active_window.friendly_class_name()})")
        print(f"Bounding Box: {active_window.rectangle()}")
        print_visible_elements(active_window)   # active_window.print_control_identifiers()
    else:
        print("No active window found.")

    