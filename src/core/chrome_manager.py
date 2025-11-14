from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
import platform
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class ChromeManager:
    """Manages Chrome browser with persistent user profile to avoid re-login"""

    def __init__(self, use_existing_profile: bool = True):
        """
        Initialize Chrome Manager

        Args:
            use_existing_profile: If True, uses your existing Chrome profile (recommended)
        """
        self.driver = None
        self.use_existing_profile = use_existing_profile
        self._init_driver()

    def _get_chrome_profile_path(self):
        """Get the default Chrome user data directory based on OS"""
        system = platform.system()

        if system == "Windows":
            base_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
        elif system == "Darwin":  # macOS
            base_path = os.path.join(os.environ['HOME'], 'Library', 'Application Support', 'Google', 'Chrome')
        else:  # Linux
            base_path = os.path.join(os.environ['HOME'], '.config', 'google-chrome')

        return base_path

    def _init_driver(self):
        """Initialize Chrome driver with appropriate options"""
        opt = Options()

        if self.use_existing_profile:
            # Use your existing Chrome profile (you're already logged in)
            chrome_profile_path = self._get_chrome_profile_path()

            # Use custom profile name from env or default
            profile_name = os.getenv('CHROME_PROFILE_NAME', 'Default')

            print(f"Using Chrome profile: {chrome_profile_path}/{profile_name}")

            opt.add_argument(f"--user-data-dir={chrome_profile_path}")
            opt.add_argument(f"--profile-directory={profile_name}")

            # Important: Use a different remote debugging port to avoid conflicts
            opt.add_argument("--remote-debugging-port=9222")

        # Disable automation flags
        opt.add_argument('--disable-blink-features=AutomationControlled')
        opt.add_experimental_option("excludeSwitches", ["enable-automation"])
        opt.add_experimental_option('useAutomationExtension', False)

        # Media permissions
        opt.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 1,
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.geolocation": 1,
            "profile.default_content_setting_values.notifications": 1
        })

        # Start maximized
        opt.add_argument('--start-maximized')

        # Disable GPU if needed (helps with some systems)
        # opt.add_argument('--disable-gpu')

        try:
            self.driver = webdriver.Chrome(options=opt)
            print("Chrome browser initialized successfully")
        except Exception as e:
            print(f"Error initializing Chrome: {e}")
            print("\nTroubleshooting:")
            print("1. Close all Chrome windows before running")
            print("2. Make sure ChromeDriver is installed and in PATH")
            print("3. Check if Chrome profile path is correct")
            raise

    def navigate_to_meet(self, meet_link: str):
        """Navigate to Google Meet link"""
        print(f"Navigating to: {meet_link}")
        self.driver.get(meet_link)

    def turn_off_mic_and_camera(self):
        """Turn off microphone and camera before joining"""
        try:
            # Wait for the preview screen to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[jscontroller="Vkjr6e"]'))
            )

            # Try to turn off microphone
            try:
                mic_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[aria-label="Turn off microphone"]'))
                )
                mic_button.click()
                print("Microphone turned off")
            except TimeoutException:
                # Microphone might already be off
                print("Microphone already off or not found")

            # Try to turn off camera
            try:
                camera_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[aria-label="Turn off camera"]'))
                )
                camera_button.click()
                print("Camera turned off")
            except TimeoutException:
                # Camera might already be off
                print("Camera already off or not found")

        except Exception as e:
            print(f"Note: Could not toggle mic/camera: {e}")
            # Not critical, continue anyway

    def join_meeting(self):
        """Click the join/ask to join button"""
        try:
            # Wait for and click the join button
            # The button text can be "Join now" or "Ask to join"
            join_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[jsname="Qx7uuf"]'))
            )
            join_button.click()
            print("Join button clicked")

            return self.check_if_joined()

        except TimeoutException:
            print("Could not find join button")
            return False
        except Exception as e:
            print(f"Error joining meeting: {e}")
            return False

    def check_if_joined(self, timeout: int = 60):
        """Check if successfully joined the meeting"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[jscontroller="kAPMuc"]'))
            )
            print("Successfully joined the meeting!")
            return True
        except (TimeoutException, NoSuchElementException):
            print("Failed to join meeting or waiting for host approval")
            return False

    def is_in_meeting(self):
        """Check if currently in a meeting"""
        try:
            self.driver.find_element(By.CSS_SELECTOR, 'div[jscontroller="kAPMuc"]')
            return True
        except NoSuchElementException:
            return False

    def monitor_meeting(self, check_interval: int = 2):
        """
        Monitor the meeting and detect when it ends

        Args:
            check_interval: How often to check if still in meeting (seconds)

        Returns:
            False when meeting ends
        """
        print("Monitoring meeting...")
        try:
            while True:
                if not self.is_in_meeting():
                    print("Meeting has ended")
                    return False

                import time
                time.sleep(check_interval)

        except Exception as e:
            print(f"Error monitoring meeting: {e}")
            return False

    def leave_meeting(self):
        """Leave the current meeting"""
        try:
            # Click the leave call button
            leave_button = self.driver.find_element(
                By.CSS_SELECTOR, 'button[aria-label*="Leave call"]'
            )
            leave_button.click()
            print("Left the meeting")
        except NoSuchElementException:
            print("Leave button not found, meeting might have already ended")

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("Browser closed")


if __name__ == "__main__":
    # Test the Chrome manager
    chrome = ChromeManager(use_existing_profile=True)

    # Test navigation
    chrome.navigate_to_meet("https://meet.google.com/")

    input("Press Enter to close browser...")
    chrome.close()
