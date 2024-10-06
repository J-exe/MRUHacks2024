import time
import pyautogui
from pywinauto import Application, Desktop, keyboard
import mss
import base64
import requests
from PIL import Image
from interaction_utils import *
import json
from openai import OpenAI
import subprocess  # Added to allow opening applications


client = OpenAI(api_key=api_key)

def open_application(app_name):
    # Simulate pressing the Windows key
    keyboard.send_keys('{VK_LWIN down}{VK_LWIN up}')
    time.sleep(1)  # Wait for the Start Menu to open

    # Type the application name
    keyboard.send_keys(app_name, with_spaces=True)
    time.sleep(1)  # Wait for the search results to appear

    # Press Enter to launch the application
    keyboard.send_keys('{ENTER}')
    time.sleep(5)  # Wait for the application to open


# Compress the image (reduce size) before uploading it
def compress_image(input_image_path, output_image_path, quality=85, max_width=800):
    # Open the image
    with Image.open(input_image_path) as img:
        # Resize the image while maintaining aspect ratio
        img.thumbnail((max_width, img.height * max_width // img.width))
        # Save the image with reduced quality
        img.save(output_image_path, "JPEG", quality=quality)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def create_task():
    
    user_input = input("Enter a task: ")
    task = user_input.strip()

    return task


def try_perform_action(element, action, text=""):

    if element:
        element_obj = element['element_obj']
        element_obj.set_focus()
            
        element_type = element_obj.friendly_class_name()

        if action == "click":
            try:
                click_element(element)
            except Exception as e:
                print(f"Error clicking on element: {e}")

        elif action == "set_text":
            try:
                type_into_element(element, text)
                keyboard.send_keys('{ENTER}')
                time.sleep(5)

            except ValueError:
                print(f"Error typing to element: {e}")

        else:
            print("Unknown action.")
    else:
        print(f"Element not found.")


def main():

    print("Hi how can I help you today? ")

    task = create_task()

    time.sleep(5)

    width, height = pyautogui.size()
    print(f"\nScreen Resolution - Width: {width}, Height: {height}\n")

    # Connect to the desktop using the UI Automation (uia) backend
    desktop = Desktop(backend="uia")

    response = ""
    messagHistory = "Message / Action History (Things you have already done): "

    # open_application("Chrome")

    # Start a loop to accept multiple inputs until user decides to quit
    while response != "DONE":
        # Get the currently active (focused) window
        active_window = desktop.window(active_only=True)

        # Print details for the active window and its elements
        if active_window:
            print(f"Active Window: {active_window.window_text()} (Type: {active_window.friendly_class_name()})")
            print(f"Bounding Box: {active_window.rectangle()}\n")
            
            element_list = get_visible_elements(active_window)
            element_data = format_element_list(element_list)
            print(element_data)

            with mss.mss() as sct:
                sct.shot(output="screenshot.png")

            # Compress the image
            compressed_image_path = "screenshot_compressed.jpg"
            compress_image("screenshot.png", compressed_image_path)

            image_path = "screenshot_compressed.jpg"

            base64_image = encode_image(image_path)

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            payload = {
                "model": "gpt-4o-mini",  # Make sure this is the correct model that supports images
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Respond with the following JSON format (ONE ACTION AT A TIME), if and only if you want to open an app do you say the apps name beside the openAPP feild else leave it blank/empty, if u decide to open an app you must leave every other feild blank:\n"
                                    "{\n"
                                    '    "element_name": "<name_of_element>",\n'
                                    '    "action": "<action_to_perform (click/set_text)>",\n'
                                    '    "openAPP": "",\n'
                                    '    "text": "<text_to_type (optional, leave empty if action is click)>"\n'
                                    "}\n"
                                    "Only respond with the JSON format. For example:\n"
                                    '{\n'
                                    '    "element_name": "SubmitButton",\n'
                                    '    "action": "click",\n'
                                    '    "openAPP": "",\n'
                                    '    "text": ""\n'
                                    "}\n"
                                    "or\n"
                                    '{\n'
                                    '    "element_name": "UsernameField",\n'
                                    '    "action": "set_text",\n'
                                    '    "openAPP": "notepad",\n'
                                    '    "text": "your_username"\n'
                                    "}\n"
                                    "If you want to open an app this is the only valid way (all other fields must be blank)\n"
                                    '{\n'
                                    '    "element_name": "",\n'
                                    '    "action": "",\n'
                                    '    "openAPP": "chrome",\n'
                                    '    "text": ""\n'
                                    "}\n"
                                    "When the task is complete, respond with:\n"
                                    '{\n'
                                    '    "element_name": "DONE",\n'
                                    '    "action": "none",\n'
                                    '    "openAPP": "",\n'
                                    '    "text": ""\n'
                                    "}"

                                )
                            },
                            {
                                "type": "text",
                                "text": task
                            },
                            {
                                "type": "text",
                                "text": messagHistory
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            },
                            {
                                "type": "text",
                                "text": element_data
                            }
                        ]
                    }
                ],
                "max_tokens": 16000
            }


            # Send the request to the OpenAI API
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

            # After receiving the response
            responseText = response.json()['choices'][0]['message']['content']
            print(f"Response: {responseText}")
            messagHistory += responseText
            print(messagHistory)

            # Parse the response JSON
            try:
                response_json = json.loads(responseText)  # Convert the JSON string to a Python dictionary
                element_name = response_json['element_name']
                action = response_json['action']
                text = response_json['text']  # Will be empty if the action is 'click'
                appToOpen = response_json['openAPP']
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing response JSON: {e}")
                element_name, action, text = None, None, None

            # Check if the task is marked as done
            if element_name == "DONE":
                print("Task complete. Exiting loop.")
                response = "DONE"  # Break out of the 
            elif appToOpen == "":
                # Find the element and perform the action
                element = find_element_by_name(element_name, element_list)

                if element:
                    try:
                        try_perform_action(element, action, text)
                    except Exception as e:
                        print(f"Error performing action '{action}' on element '{element_name}': {e}")
                else:
                    print(f"Element '{element_name}' not found.")
            else:
                    open_application("appToOpen")



if __name__ == '__main__':
    main()