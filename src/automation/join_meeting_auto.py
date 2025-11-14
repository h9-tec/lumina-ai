"""
Auto Join Meeting - Handles name entry, mic/camera off, auto-join
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

        # Random mouse movements
        body = driver.find_element(By.TAG_NAME, 'body')
        x_offset = random.randint(-100, 100)
        y_offset = random.randint(-100, 100)
        actions.move_to_element_with_offset(body, x_offset, y_offset).perform()

        # Occasionally click in safe area (just move and click, not on any button)
        if random.random() < 0.3:  # 30% chance to click
            actions.click().perform()

        # Occasionally press a harmless key (like shift)
        if random.random() < 0.2:  # 20% chance
            actions.send_keys(Keys.SHIFT).perform()

    except Exception as e:
        # Silently ignore errors in behavior simulation
        pass


def join_meeting_auto(meet_link, bot_name="Lumina Bot"):
    """Join meeting automatically handling all steps"""

    meeting_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║     🌟 Lumina Auto Join                                  ║
    ║                                                           ║
    ║     Meeting ID: {meeting_id}                     ║
    ║     Bot Name: {bot_name:<43}║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Create recordings directory
    recordings_dir = Path(__file__).parent / 'recordings'
    recordings_dir.mkdir(parents=True, exist_ok=True)
    audio_path = recordings_dir / f"{meeting_id}.wav"

    # Setup Chrome
    opt = Options()
    lumina_profile = Path(__file__).parent / 'lumina_chrome_profile'
    lumina_profile.mkdir(exist_ok=True)

    opt.add_argument(f'--user-data-dir={lumina_profile}')
    opt.add_argument('--profile-directory=Default')
    opt.add_argument('--disable-blink-features=AutomationControlled')
    opt.add_experimental_option("excludeSwitches", ["enable-automation"])
    opt.add_experimental_option('useAutomationExtension', False)
    opt.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 1,
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.geolocation": 1,
        "profile.default_content_setting_values.notifications": 1
    })
    opt.add_argument('--start-maximized')
    opt.add_argument('--remote-debugging-port=9223')

    # Disable camera/mic at OS level
    opt.add_argument('--use-fake-ui-for-media-stream')
    opt.add_argument('--use-fake-device-for-media-stream')

    try:
        print("🌐 Opening Chrome...")
        driver = webdriver.Chrome(options=opt)

        print(f"📍 Navigating to meeting...")
        driver.get(meet_link)
        time.sleep(5)

        # Check if name input is present (guest mode)
        print("📝 Checking for name input...")
        try:
            name_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="name" i]'))
            )
            print(f"   ✓ Found name field, entering: {bot_name}")
            name_input.clear()
            name_input.send_keys(bot_name)
            time.sleep(1)
        except:
            print("   - No name input found (might be logged in)")

        # Turn off microphone
        print("🔇 Turning off microphone...")
        try:
            # Look for microphone button
            mic_buttons = driver.find_elements(By.CSS_SELECTOR, 'div[role="button"][aria-label*="microphone" i]')
            for mic_button in mic_buttons:
                aria_label = mic_button.get_attribute("aria-label")
                if "Turn off" in aria_label or "Mute" in aria_label:
                    mic_button.click()
                    print("   ✓ Microphone turned off")
                    time.sleep(0.5)
                    break
        except Exception as e:
            print(f"   - Could not turn off mic: {e}")

        # Turn off camera
        print("📷 Turning off camera...")
        try:
            camera_buttons = driver.find_elements(By.CSS_SELECTOR, 'div[role="button"][aria-label*="camera" i]')
            for camera_button in camera_buttons:
                aria_label = camera_button.get_attribute("aria-label")
                if "Turn off" in aria_label or "off camera" in aria_label.lower():
                    camera_button.click()
                    print("   ✓ Camera turned off")
                    time.sleep(0.5)
                    break
        except Exception as e:
            print(f"   - Could not turn off camera: {e}")

        time.sleep(2)

        # Click "Ask to join" button
        print("🚪 Clicking 'Ask to join' button...")
        try:
            # Try multiple selectors
            join_selectors = [
                'button:has-text("Ask to join")',
                'button[jsname="Qx7uuf"]',
                'button:has-text("Join")',
                '//button[contains(., "Ask to join")]',
                '//button[contains(., "Join")]',
                'span:has-text("Ask to join")',
            ]

            joined_button = False
            for selector in join_selectors:
                try:
                    if selector.startswith('//'):
                        button = driver.find_element(By.XPATH, selector)
                    else:
                        button = driver.find_element(By.CSS_SELECTOR, selector)

                    if button and button.is_enabled():
                        button.click()
                        print("   ✓ Join button clicked")
                        joined_button = True
                        break
                except:
                    continue

            if not joined_button:
                # Try finding by text content
                buttons = driver.find_elements(By.TAG_NAME, 'button')
                for button in buttons:
                    if 'ask to join' in button.text.lower() or button.text.lower() == 'join':
                        button.click()
                        print("   ✓ Join button clicked (found by text)")
                        joined_button = True
                        break

            if not joined_button:
                print("   ⚠️  Could not find join button automatically")
                print("   Please click 'Ask to join' manually in the browser")

        except Exception as e:
            print(f"   - Join button error: {e}")

        time.sleep(5)

        # Check if joined
        print("⏳ Checking if joined meeting...")
        try:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[jscontroller="kAPMuc"]'))
            )
            print("✅ Successfully joined the meeting!")
        except:
            print("⏳ Waiting for host approval or already in meeting...")

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
                    if interaction_counter >= random.randint(10, 20):  # Every 20-40 seconds (2s * 10-20)
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

            storage = LocalStorageService()
            storage_path = storage.upload_file(str(audio_path))
            print(f"💾 Saved to storage: {storage_path}")
        else:
            print("⚠️  No audio recorded or file is empty")

        print("\n" + "="*60)
        print(f"Meeting session completed: {meeting_id}")
        print("="*60 + "\n")

        driver.quit()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python join_meeting_auto.py <meet_link> [bot_name]")
        print("\nExample:")
        print("  python join_meeting_auto.py https://meet.google.com/abc-defg-hij")
        print("  python join_meeting_auto.py https://meet.google.com/abc-defg-hij 'My Bot'")
        sys.exit(1)

    meet_link = sys.argv[1]
    bot_name = sys.argv[2] if len(sys.argv) > 2 else "Lumina Bot"

    if "meet.google.com" not in meet_link:
        print("❌ Invalid Google Meet link")
        sys.exit(1)

    join_meeting_auto(meet_link, bot_name)
