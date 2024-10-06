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

    # Start a loop to accept multiple inputs until user decides to quit
    while True:
        # Add a 2-second delay before each refresh

        # Get the currently active (focused) window
        active_window = desktop.window(active_only=True)

        # Print details for the active window and its elements
        if active_window:
            print(f"Active Window: {active_window.window_text()} (Type: {active_window.friendly_class_name()})")
            print(f"Bounding Box: {active_window.rectangle()}")
            
            # Re-scan and refresh the UI elements list each time
            element_list = print_visible_elements(active_window)   # active_window.print_control_identifiers()
        else:
            print("No active window found.")
            element_list = []

        # Simple terminal GUI interaction
        user_input = input("\nEnter your input ('Type: [text], [element_name]' for typing, '[element_name]' for clicking, or 'quit' to exit): ")

        time.sleep(2)

        # Break the loop if user wants to quit
        if user_input.lower() == 'quit':
            print("Exiting the script. Goodbye!")
            break

        # Check if the user input starts with "Type:" for typing into an element
        if user_input.startswith("Type: "):
            # Split the input into the text to type and the element name
            try:
                text_to_type, element_name = user_input[6:].split(", ")
                # Find the element by name and type into it
                target_element = find_element_by_name(element_name, element_list)
                if target_element:
                    # Optionally print bounding box details here
                    print(f"Found element: {target_element['name']}, Bounding Box: {target_element['rectangle']}, Type: {target_element['type']}")
                    type_into_element(target_element, text_to_type)
                else:
                    print(f"Element '{element_name}' not found.")
            except ValueError:
                print("Invalid input format! Please use the format: 'Type: [text], [element_name]'")
        else:
            # If input does not start with "Type:", treat it as a click request
            element_name = user_input.strip()
            target_element = find_element_by_name(element_name, element_list)
            if target_element:
                print(f"Found element: {target_element['name']}, Bounding Box: {target_element['rectangle']}, Type: {target_element['type']}")
                click_element(target_element)
            else:
                print(f"Element '{element_name}' not found.")