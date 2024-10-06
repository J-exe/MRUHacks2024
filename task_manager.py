import time
import pyautogui
from pywinauto import Desktop
from interaction_utils import *


SWITCH_DELAY = 5


def try_perform_action(element):

    if element:
        element_obj = element['element_obj']
        element_obj.set_focus()
            
        element_type = element_obj.friendly_class_name()

        print(f"\nWhat action would you like to perform on {element['name']} ({element_type})?")
        print("Options: click, set_text")
        action = input("Enter action: ").strip()

        if action == "click":
            try:
                click_element(element)
            except Exception as e:
                print(f"Error clicking on element: {e}")

        elif action == "set_text":
            try:
                text = input("Enter text to set: ").strip()
                type_into_element(element, text)
            except ValueError:
                print(f"Error typing to element: {e}")

        else:
            print("Unknown action.")
    else:
        print(f"Element not found.")


def main():

    width, height = pyautogui.size()
    print(f"\nScreen Resolution - Width: {width}, Height: {height}\n")

    # Connect to the desktop using the UI Automation (uia) backend
    desktop = Desktop(backend="uia")

    # Start a loop to accept multiple inputs until user decides to quit
    while True:
        # Add a delay before each refresh
        print(f"Debug sleep. Resuming in {SWITCH_DELAY} seconds...")
        time.sleep(SWITCH_DELAY)

        # Get the currently active (focused) window
        active_window = desktop.window(active_only=True)

        # Print details for the active window and its elements
        if active_window:
            print(f"Active Window: {active_window.window_text()} (Type: {active_window.friendly_class_name()})")
            print(f"Bounding Box: {active_window.rectangle()}\n")
            element_list = get_visible_elements(active_window)
            element_data = format_element_list(element_list)
            print(element_data)
        else:
            print("No active window found.")
            element_list = []

        # Simple terminal GUI interaction
        user_input = input("\nEnter the name of the element you want to interact with or 'quit' to exit: ")
        
        # Break the loop if user wants to quit
        if user_input.lower() == 'quit':
            print("Exiting the script. Goodbye!")
            break

        element_name = user_input.strip()
        target_element = find_element_by_name(element_name, element_list)

        try_perform_action(target_element)


if __name__ == '__main__':
    main()