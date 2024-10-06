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
import subprocess
import tkinter as tk
from tkinter import messagebox


client = OpenAI(api_key=api_key)

def display_welcome_ui():
    include_debug = [False]

    def start():
        include_debug[0] = debug_var.get()
        root.destroy()

    root = tk.Tk()
    root.title("Welcome")

    # Create a label with "JUSTDOIT" in large green text
    label = tk.Label(root, text="JUSTDOIT", font=("Helvetica", 32), fg="green")
    label.pack(pady=20)

    # Create a checkbox for including/excluding debug info
    debug_var = tk.BooleanVar()
    debug_check = tk.Checkbutton(root, text="Include debug info", variable=debug_var)
    debug_check.pack(pady=10)

    # Create a Start button
    start_button = tk.Button(root, text="Start", command=start)
    start_button.pack(pady=10)

    root.mainloop()

    return include_debug[0]

def open_application(app_name):
    keyboard.send_keys('{VK_LWIN down}{VK_LWIN up}')
    time.sleep(1)  # Wait for the Start Menu to open

    keyboard.send_keys(app_name, with_spaces=True)
    time.sleep(1)  # Wait for the search results to appear

    keyboard.send_keys('{ENTER}')
    time.sleep(5)  # Wait for the application to open

def compress_image(input_image_path, output_image_path, quality=85, max_width=800):
    with Image.open(input_image_path) as img:
        img.thumbnail((max_width, img.height * max_width // img.width))
        img.save(output_image_path, "JPEG", quality=quality)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def create_task():
    user_input = input("Enter a task: ")
    task = user_input.strip()
    return task

def try_perform_action(element, action, text="", include_debug=False):
    if element:
        element_obj = element['element_obj']
        element_obj.set_focus()
        element_type = element_obj.friendly_class_name()

        if action == "click":
            try:
                click_element(element)
            except Exception as e:
                if include_debug:
                    print(f"Error clicking on element: {e}")

        elif action == "set_text":
            try:
                type_into_element(element, text)
            except ValueError as e:
                if include_debug:
                    print(f"Error typing to element: {e}")

        else:
            if include_debug:
                print("Unknown action.")
    else:
        if include_debug:
            print(f"Element not found.")

def main():
    include_debug = display_welcome_ui()

    if include_debug:
        print("Hi, how can I help you today?")

    task = create_task()

    time.sleep(5)

    width, height = pyautogui.size()
    if include_debug:
        print(f"\nScreen Resolution - Width: {width}, Height: {height}\n")

    # Connect to the desktop using the UI Automation (uia) backend
    desktop = Desktop(backend="uia")

    response = ""

    # Start a loop to accept multiple inputs until user decides to quit
    while response != "DONE":
        # Get the currently active (focused) window
        active_window = desktop.window(active_only=True)

        if active_window:
            if include_debug:
                print(f"Active Window: {active_window.window_text()} (Type: {active_window.friendly_class_name()})")
                print(f"Bounding Box: {active_window.rectangle()}\n")

            element_list = get_visible_elements(active_window)
            element_data = format_element_list(element_list)
            if include_debug:
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
                                    "Respond with the following JSON format (ONE ACTION AT A TIME):\n"
                                    "{\n"
                                    '    "element_name": "<name_of_element>",\n'
                                    '    "action": "<action_to_perform (click/set_text)>",\n'
                                    '    "text": "<text_to_type (optional, leave empty if action is click)>"\n'
                                    "}\n"
                                    "Only respond with the JSON format. For example:\n"
                                    '{\n'
                                    '    "element_name": "SubmitButton",\n'
                                    '    "action": "click",\n'
                                    '    "text": ""\n'
                                    "}\n"
                                    "or\n"
                                    '{\n'
                                    '    "element_name": "UsernameField",\n'
                                    '    "action": "set_text",\n'
                                    '    "text": "your_username"\n'
                                    "}\n"
                                    "When the task is complete, respond with:\n"
                                    '{\n'
                                    '    "element_name": "DONE",\n'
                                    '    "action": "none",\n'
                                    '    "text": ""\n'
                                    "}"
                                )
                            },
                            {
                                "type": "text",
                                "text": task
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
                "max_tokens": 5000
            }

            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

            responseText = response.json()['choices'][0]['message']['content']
            if include_debug:
                print(f"Response: {responseText}")

            try:
                response_json = json.loads(responseText)  # Convert the JSON string to a Python dictionary
                element_name = response_json['element_name']
                action = response_json['action']
                text = response_json['text']  # Will be empty if the action is 'click'
            except (json.JSONDecodeError, KeyError) as e:
                if include_debug:
                    print(f"Error parsing response JSON: {e}")
                element_name, action, text = None, None, None

            if element_name == "DONE":
                if include_debug:
                    print("Task complete. Exiting loop.")
                response = "DONE"  # Break out of the loop
            else:
                element = find_element_by_name(element_name, element_list)

                if element:
                    try:
                        try_perform_action(element, action, text, include_debug)
                    except Exception as e:
                        if include_debug:
                            print(f"Error performing action '{action}' on element '{element_name}': {e}")
                else:
                    if include_debug:
                        print(f"Element '{element_name}' not found.")

    else:
        if include_debug:
            print("No active window found.")

if __name__ == '__main__':
    main()
