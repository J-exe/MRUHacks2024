import pyautogui
import pywinauto
from io import StringIO


def get_visible_elements(element, element_list=None, level=0):
    """
    Function to recursively gather and print all visible child elements in the given window.
    
    :param element: The current window or element inside the window.
    :param element_list: List to accumulate the elements during recursion.
    :param level: The current level in the element tree.
    :return: List of visible elements with their details.
    """
    # Initialize the element list only once at the top-level call
    if element_list is None:
        element_list = []

    # Cache properties to avoid repeated function calls
    window_text = element.window_text()
    class_name = element.class_name()
    
    if window_text or class_name:  # If there's a meaningful window text or class name
        element_details = {
            "name": window_text or class_name,
            "rectangle": element.rectangle(),
            "type": element.friendly_class_name(),
            "element_obj": element
        }
        element_list.append(element_details)

        # Delay printing until after all recursion is done
        print(f"\t+  Element: {element_details['name']}, Bounding Box: {element_details['rectangle']}, Type: {element_details['type']}\n")

    # Iteratively process all visible child elements
    for child in element.children():
        if child.is_visible():
            get_visible_elements(child, element_list, level + 2)

    return element_list


def format_element_list(element_list):
    """
    Converts a list of UI elements into a formatted string, showing the name and type of each element.

    This function takes a list of element dictionaries (with 'name' and 'type' fields) and formats them into a 
    string where each element is represented by its name and type on a new line.

    :param element_list: List of dictionaries representing UI elements. 
                         Each dictionary should contain 'name' and 'type' keys.
    :return: A formatted string representation of the element names and types.
    """
    string_builder = StringIO()

    if element_list:
        for element in element_list:
            string_builder.write(f"Element Name: {element['name']}, Element Type: {element['type']}\n")

    return string_builder.getvalue()



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

        try:
            click_center(element['rectangle'])  # Click the center of the bounding box (this should expand or select the item)
            print(f"Expanded menu item: {element['name']}")
        except Exception as e:
            print(f"Error while interacting with {element['name']} ({element_type}): {e}")

        # clickable_element_types = ["Button", ]
        # expandable_element_types = ["Hyperlink", "MenuItem", "TabItem", "ListItem", "TreeItem"]

        # if element_type in clickable_element_types:
        #     try:
        #         element_obj.click_input()  # Click the element
        #         print(f"Clicked on element: {element['name']}")
        #     except Exception as e:
        #         print(f"Error while interacting with {element['name']} ({element_type}): {e}")

        # elif element_type in expandable_element_types:
        #     try:
        #         click_center(element['rectangle'])  # Click the center of the bounding box (this should expand or select the item)
        #         print(f"Expanded menu item: {element['name']}")
        #     except Exception as e:
        #         print(f"Error while interacting with {element['name']} ({element_type}): {e}")
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
        print("Element not found")
