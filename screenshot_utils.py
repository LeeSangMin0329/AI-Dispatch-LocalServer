import os
import pyautogui
import base64

IMAGE_PATH = "./temp/screenshot.png"

def capture_screen():
    screenshot = pyautogui.screenshot()

    screenshot.thumbnail((1920, 1080))
    screenshot.save(IMAGE_PATH)

    print(f"Save screen shot {IMAGE_PATH}")

def get_screenshot_to_base64():
    if not os.path.exists(IMAGE_PATH):
        print(f"screenshot file not exist. {IMAGE_PATH}")
        return ""

    with open(IMAGE_PATH, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")