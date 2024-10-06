import pyautogui
import pywinauto

def print_visible_elements(element, level=0):
    """
    Function to recursively print all visible child elements in the active window

    :param element: The current window or element inside the window
    :param level: current level of the element tree
    """
    element_list = []  # Initialize a fresh list for elements each time this function is called
    # Print and store the current element's details
    if element.window_text() != "" or element.class_name() != "":
        element_details = {
            "name": element.window_text() or element.class_name(),
            "rectangle": element.rectangle(),
            "type": element.friendly_class_name(),
            "element_obj": element
        }
        element_list.append(element_details)
        
        print(f"{'    '}- Element: {element_details['name']}, Bounding Box: {element_details['rectangle']}, Type: {element_details['type']}")
        print()

    # Recursively check and print all child elements
    for child in element.children():
        if child.is_visible():  # Only process visible child elements
            element_list.extend(print_visible_elements(child, level + 2))  # Extend the element list with the children's elements

    return element_list  # Return the list of elements


def move_to_center(bounding_box):
    """
    Moves the mouse to the center of the given bounding box.

    :param bounding_box: The bounding box as a RECT object (from pywinauto)
    """
    # Calculate the center of the bounding box
    center_x = (bounding_box.left + bounding_box.right) // 2
    center_y = (bounding_box.top + bounding_box.bottom) // 2
    
    # Move the mouse to the center of the bounding box
    pyautogui.moveTo(center_x, center_y)


def click_center(bounding_box):
    """
    Clicks the center of the given bounding box.

    :param bounding_box: The bounding box as a RECT object (from pywinauto)
    """
    # Calculate the center of the bounding box
    center_x = (bounding_box.left + bounding_box.right) // 2
    center_y = (bounding_box.top + bounding_box.bottom) // 2
    
    # Move to the center of the bounding box and click
    pyautogui.click(center_x, center_y)


def click_element(element):
    # Use pywinauto to click the given element
    if element:
        element_obj = element['element_obj']
        element_obj.set_focus()  # Focus the element
        
        # Get the class type of the element
        element_type = element_obj.friendly_class_name()

        if element_type == "MenuItem":  # Special handling for menu items
            click_center(element['rectangle'])  # Click the center of the bounding box
            print(f"Expanded menu item: {element['name']}")
        else:
            element_obj.click_input()  # Click the element
            print(f"Clicked on element: {element['name']}")
    else:
        print("Element not found")


def find_element_by_name(name, element_list):
    # Function to search for the element by name in the stored element list
    for elem in element_list:
        if elem['name'] == name:
            return elem
    return None


def type_into_element(element, text):
    # Use pywinauto to type into the given element
    if element:
        element_obj = element['element_obj']
        element_obj.set_focus()  # Focus the element
        element_obj.type_keys(text, with_spaces=True)  # Type into the element
        print(f"Typed '{text}' into element: {element['name']}")
    else:
        print("Element not found!")
