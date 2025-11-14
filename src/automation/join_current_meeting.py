"""
Join Current Meeting - Automatically detect and join the meeting happening RIGHT NOW
"""
from calendar_service import CalendarService
from chrome_manager import ChromeManager
from record_audio import AudioRecorder
from local_storage_service import LocalStorageService
from pathlib import Path
from datetime import datetime, timedelta
import time

def get_current_meeting():
    """Find the meeting that is happening RIGHT NOW"""
    cal = CalendarService()

    # Get meetings from 10 minutes ago to 10 minutes from now
    # This catches meetings that just started or are about to start
    now = datetime.utcnow()
    time_min = (now - timedelta(minutes=10)).isoformat() + 'Z'
    time_max = (now + timedelta(minutes=10)).isoformat() + 'Z'

    print("🔍 Checking your calendar for current meetings...")

    try:
        events_result = cal.service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        # Find meetings with Google Meet links
        current_meetings = []

        for event in events:
            # Get start and end times
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            # Parse times
            start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))

            # Check if meeting is happening now
            now_aware = datetime.now(start_time.tzinfo)

            if start_time <= now_aware <= end_time:
                # This meeting is happening NOW!
                meet_link = None

                # Check for Google Meet link
                if 'hangoutLink' in event:
                    meet_link = event['hangoutLink']
                elif 'conferenceData' in event:
                    entry_points = event['conferenceData'].get('entryPoints', [])
                    for entry in entry_points:
                        if entry.get('entryPointType') == 'video':
                            meet_link = entry.get('uri')
                            break

                if meet_link:
                    current_meetings.append({
                        'id': event.get('id'),
                        'title': event.get('summary', 'Untitled Meeting'),
                        'meet_link': meet_link,
                        'start_time': start,
                        'end_time': end
                    })

        return current_meetings

    except Exception as e:
        print(f"❌ Error fetching calendar: {e}")
        return []


def join_meeting(meeting_info):
    """Join the detected meeting and record"""

    meeting_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║     🌟 Lumina - Joining Current Meeting                  ║
    ║                                                           ║
    ║     Title: {meeting_info['title']:<43}║
    ║     Meeting ID: {meeting_id}                     ║
    ╚═══════════════════════════════════════════════════════════╝
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
        print(f"📍 Navigating to meeting...")
        chrome.navigate_to_meet(meeting_info['meet_link'])
        time.sleep(3)

        # Turn off mic and camera
        print("🔇 Turning off microphone and camera...")
        chrome.turn_off_mic_and_camera()
        time.sleep(1)

        # Join the meeting
        print("🚪 Joining meeting...")
        joined = chrome.join_meeting()

        if not joined:
            print("⏳ Waiting for approval or checking if already in meeting...")
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

        print("\n" + "="*60)
        print(f"Meeting session completed: {meeting_id}")
        print("="*60 + "\n")

        # Close Chrome
        chrome.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║              🌟 Lumina - Auto Join Current Meeting       ║
    ║                                                           ║
    ║     Detecting which meeting you're in right now...       ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Get current meetings
    current_meetings = get_current_meeting()

    if not current_meetings:
        print("❌ No meetings with Google Meet links are happening right now.")
        print("\n💡 Options:")
        print("   1. Check your calendar - is there a meeting scheduled now?")
        print("   2. Make sure the meeting has a Google Meet link")
        print("   3. The meeting might have ended or not started yet")
    elif len(current_meetings) == 1:
        # One meeting found - join it!
        meeting = current_meetings[0]
        print(f"✅ Found current meeting: {meeting['title']}")
        print(f"🔗 Meet link: {meeting['meet_link']}\n")

        # Join it
        join_meeting(meeting)

    else:
        # Multiple meetings happening now
        print(f"⚠️  Found {len(current_meetings)} meetings happening right now:\n")
        for i, meeting in enumerate(current_meetings, 1):
            print(f"   {i}. {meeting['title']}")
            print(f"      Link: {meeting['meet_link']}\n")

        print("🤔 Joining the first one...")
        join_meeting(current_meetings[0])
