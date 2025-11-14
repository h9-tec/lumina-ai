"""
Quick Join - Join a Google Meet right now without transcription
"""
from chrome_manager import ChromeManager
from record_audio import AudioRecorder
from local_storage_service import LocalStorageService
from pathlib import Path
from datetime import datetime
import time
import sys

def quick_join_meeting(meet_link):
    """Quickly join a meeting and record audio"""

    # Generate meeting ID
    meeting_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"""
    ╔═══════════════════════════════════════════╗
    ║     Lumina Quick Join                     ║
    ║     Meeting ID: {meeting_id}     ║
    ╚═══════════════════════════════════════════╝
    """)

    # Create recordings directory
    recordings_dir = Path(__file__).parent / 'recordings'
    recordings_dir.mkdir(parents=True, exist_ok=True)
    audio_path = recordings_dir / f"{meeting_id}.wav"

    try:
        # Initialize Chrome with your profile
        print("🌐 Opening Chrome with your profile...")
        chrome = ChromeManager(use_existing_profile=True)

        # Navigate to meeting
        print(f"📍 Navigating to: {meet_link}")
        chrome.navigate_to_meet(meet_link)
        time.sleep(3)

        # Turn off mic and camera
        print("🔇 Turning off microphone and camera...")
        chrome.turn_off_mic_and_camera()
        time.sleep(1)

        # Join the meeting
        print("🚪 Joining meeting...")
        joined = chrome.join_meeting()

        if not joined:
            print("⏳ Waiting for host approval...")
            time.sleep(30)
            if not chrome.is_in_meeting():
                print("❌ Could not join meeting")
                chrome.close()
                return

        print("✅ Successfully joined the meeting!")

        # Start recording
        print(f"🎙️  Starting audio recording: {audio_path}")
        audio_recorder = AudioRecorder()
        audio_recorder.start_recording(str(audio_path))

        # Monitor the meeting
        print("📊 Monitoring meeting (recording until you leave)...")
        print("   Press Ctrl+C to stop manually\n")

        try:
            chrome.monitor_meeting()
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

        print("\n" + "="*50)
        print(f"Meeting session completed: {meeting_id}")
        print("="*50 + "\n")

        # Close Chrome
        chrome.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_join.py <meet_link>")
        print("\nExample:")
        print("  python quick_join.py https://meet.google.com/abc-defg-hij")
        sys.exit(1)

    meet_link = sys.argv[1]

    # Validate link
    if "meet.google.com" not in meet_link:
        print("❌ Invalid Google Meet link. Must contain 'meet.google.com'")
        sys.exit(1)

    quick_join_meeting(meet_link)
