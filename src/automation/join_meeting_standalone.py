"""
Standalone Meeting Joiner - Uses separate Chrome profile, won't interfere with your existing Chrome
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from record_audio import AudioRecorder
from local_storage_service import LocalStorageService
from pathlib import Path
from datetime import datetime
import time
import sys
import random

def simulate_human_behavior(driver):
    """Simulate human-like interactions to avoid bot detection"""
    try:
        actions = ActionChains(driver)
        body = driver.find_element(By.TAG_NAME, 'body')
        x_offset = random.randint(-100, 100)
        y_offset = random.randint(-100, 100)
        actions.move_to_element_with_offset(body, x_offset, y_offset).perform()
        if random.random() < 0.3:
            actions.click().perform()
        if random.random() < 0.2:
            actions.send_keys(Keys.SHIFT).perform()
    except:
        pass

def join_meeting_standalone(meet_link):
    """Join meeting with standalone Chrome instance"""

    meeting_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║     🌟 Lumina - Standalone Join (Separate Chrome)       ║
    ║                                                           ║
    ║     Meeting ID: {meeting_id}                     ║
    ║     Meeting Link: {meet_link[:40]}...        ║
    ║                                                           ║
    ║     This will open a NEW Chrome window                   ║
    ║     Your existing Chrome will not be affected            ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Create recordings directory
    recordings_dir = Path(__file__).parent / 'recordings'
    recordings_dir.mkdir(parents=True, exist_ok=True)
    audio_path = recordings_dir / f"{meeting_id}.wav"

    # Setup Chrome with separate profile
    opt = Options()

    # Create a separate profile directory for Lumina
    lumina_profile = Path(__file__).parent / 'lumina_chrome_profile'
    lumina_profile.mkdir(exist_ok=True)

    opt.add_argument(f'--user-data-dir={lumina_profile}')
    opt.add_argument('--profile-directory=Default')

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

    # Remote debugging on different port
    opt.add_argument('--remote-debugging-port=9223')

    try:
        print("🌐 Opening separate Chrome window for Lumina...")
        driver = webdriver.Chrome(options=opt)

        # Navigate to meeting
        print(f"📍 Navigating to meeting...")
        driver.get(meet_link)
        time.sleep(4)

        print("""
        ⚠️  IMPORTANT: You may need to LOGIN to Google in this new window!

        This is a separate Chrome profile just for Lumina.
        Please:
        1. Login to your Google account if prompted
        2. I'll wait 30 seconds for you to login
        """)

        time.sleep(30)  # Give time to login if needed

        # Turn off mic and camera
        print("🔇 Turning off microphone and camera...")
        try:
            mic_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[aria-label*="microphone" i]'))
            )
            if "Turn off" in mic_button.get_attribute("aria-label"):
                mic_button.click()
                print("   ✓ Microphone off")
        except:
            print("   - Microphone already off or not found")

        try:
            camera_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[aria-label*="camera" i]'))
            )
            if "Turn off" in camera_button.get_attribute("aria-label"):
                camera_button.click()
                print("   ✓ Camera off")
        except:
            print("   - Camera already off or not found")

        time.sleep(1)

        # Join the meeting
        print("🚪 Joining meeting...")
        try:
            join_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[jsname="Qx7uuf"]'))
            )
            join_button.click()
            print("   ✓ Join button clicked")
        except Exception as e:
            print(f"   - Could not find join button: {e}")

        # Check if joined
        try:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[jscontroller="kAPMuc"]'))
            )
            print("✅ Successfully joined the meeting!")
        except:
            print("⏳ Waiting for approval or already in meeting...")

        # Start recording
        print(f"🎙️  Starting audio recording: {audio_path}")
        audio_recorder = AudioRecorder()
        audio_recorder.start_recording(str(audio_path))

        # Monitor the meeting
        print("📊 Monitoring meeting (recording until meeting ends)...")
        print("   🤖 Simulating human behavior to avoid bot detection...")
        print("   Press Ctrl+C to stop manually\n")

        try:
            interaction_counter = 0
            while True:
                try:
                    driver.find_element(By.CSS_SELECTOR, 'div[jscontroller="kAPMuc"]')

                    # Simulate human behavior every 20-40 seconds
                    interaction_counter += 1
                    if interaction_counter >= random.randint(10, 20):
                        simulate_human_behavior(driver)
                        interaction_counter = 0

                    time.sleep(2)
                except NoSuchElementException:
                    print("\n🔔 Meeting ended")
                    break
        except KeyboardInterrupt:
            print("\n⏹️  Stopping recording (Ctrl+C pressed)...")

        # Stop recording
        print("🛑 Stopping audio recording...")
        audio_recorder.stop_recording(str(audio_path))
        time.sleep(2)

        # Save to local storage
        if audio_path.exists() and audio_path.stat().st_size > 0:
            file_size_mb = audio_path.stat().st_size / (1024 * 1024)
            print(f"✅ Recording saved: {audio_path} ({file_size_mb:.2f} MB)")

            # Copy to local storage
            storage = LocalStorageService()
            storage_path = storage.upload_file(str(audio_path))
            print(f"💾 Saved to storage: {storage_path}")
        else:
            print("⚠️  No audio recorded or file is empty")

        print("\n" + "="*60)
        print(f"Meeting session completed: {meeting_id}")
        print("="*60 + "\n")

        # Close Chrome
        driver.quit()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python join_meeting_standalone.py <meet_link>")
        print("\nExample:")
        print("  python join_meeting_standalone.py https://meet.google.com/abc-defg-hij")
        sys.exit(1)

    meet_link = sys.argv[1]

    if "meet.google.com" not in meet_link:
        print("❌ Invalid Google Meet link")
        sys.exit(1)

    join_meeting_standalone(meet_link)
