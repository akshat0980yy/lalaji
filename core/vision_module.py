import pyautogui
from PIL import Image
import base64
from io import BytesIO
import time
import re


class VisionModule:
    """Handles screen capture and vision analysis for JARVIS AI"""

    def __init__(self, config):
        """
        Initialize vision module

        Args:
            config: Configuration object with system settings
        """
        self.config = config
        self._configure_pyautogui()

    def _configure_pyautogui(self):
        """Configure PyAutoGUI settings"""
        if self.config.PYAUTOGUI_FAILSAFE:
            pyautogui.FAILSAFE = True
        pyautogui.PAUSE = self.config.PYAUTOGUI_PAUSE

    def capture_screen(self):
        """
        Capture current screen

        Returns:
            PIL.Image: Screenshot or None if capture failed
        """
        try:
            screenshot = pyautogui.screenshot()
            return screenshot
        except Exception as e:
            print(f"Screen capture error: {e}")
            return None

    def image_to_base64(self, image):
        """
        Convert PIL image to base64 string

        Args:
            image (PIL.Image): Image to convert

        Returns:
            str: Base64 encoded image string
        """
        try:
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            print(f"Image conversion error: {e}")
            return None

    def click_screen_position(self, x_percent, y_percent):
        """
        Click at screen position given as percentages

        Args:
            x_percent (float): X coordinate as percentage (0-100)
            y_percent (float): Y coordinate as percentage (0-100)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            screen_width, screen_height = pyautogui.size()
            x = int(screen_width * x_percent / 100)
            y = int(screen_height * y_percent / 100)

            pyautogui.moveTo(x, y, duration=0.5)
            time.sleep(0.2)
            pyautogui.click()
            print(f"✅ Clicked at ({x}, {y})")
            return True
        except Exception as e:
            print(f"Click error: {e}")
            return False

    def scroll_action(self, direction, amount=3):
        """
        Scroll up or down

        Args:
            direction (str): Direction to scroll ('up', 'down', 'top', 'bottom')
            amount (int): Number of scroll actions

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if direction.lower() in ['up', 'top']:
                pyautogui.scroll(amount * 100)
                print(f"✅ Scrolled up")
            elif direction.lower() in ['down', 'bottom']:
                pyautogui.scroll(-amount * 100)
                print(f"✅ Scrolled down")
            else:
                print(f"❌ Invalid scroll direction: {direction}")
                return False
            return True
        except Exception as e:
            print(f"Scroll error: {e}")
            return False

    def type_text(self, text, interval=0.05):
        """
        Type text on keyboard

        Args:
            text (str): Text to type
            interval (float): Interval between keystrokes

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            pyautogui.write(text, interval=interval)
            print(f"✅ Typed: {text}")
            return True
        except Exception as e:
            print(f"Typing error: {e}")
            return False

    def press_key(self, key):
        """
        Press a specific key or key combination

        Args:
            key (str): Key or key combination (e.g., 'ctrl+c', 'enter')

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if '+' in key:
                keys = key.split('+')
                pyautogui.hotkey(*keys)
                print(f"✅ Pressed: {key}")
            else:
                pyautogui.press(key)
                print(f"✅ Pressed: {key}")
            return True
        except Exception as e:
            print(f"Key press error: {e}")
            return False

    def get_screen_size(self):
        """
        Get current screen resolution

        Returns:
            tuple: (width, height) of screen
        """
        try:
            return pyautogui.size()
        except Exception as e:
            print(f"Screen size error: {e}")
            return (1920, 1080)  # Default fallback

    def get_mouse_position(self):
        """
        Get current mouse position

        Returns:
            tuple: (x, y) coordinates
        """
        try:
            return pyautogui.position()
        except Exception as e:
            print(f"Mouse position error: {e}")
            return (0, 0)