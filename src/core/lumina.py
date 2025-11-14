"""
Lumina - Intelligent Meeting Assistant (Modular Version)

Automatically monitors your calendar and joins Google Meet sessions,
recording and analyzing conversations without manual intervention.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from dotenv import load_dotenv
import os
import time
import schedule
from datetime import datetime
from threading import Thread

# Import API routers
from src.core.api import (
    meetings_router,
    recordings_router,
    transcripts_router,
    minutes_router,
    config_router
)

# Import core services
from src.core.calendar_service import CalendarService
from src.core.chrome_manager import ChromeManager

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Lumina - AI Meeting Assistant",
    description="Enterprise-grade autonomous meeting assistant with calendar integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(meetings_router)
app.include_router(recordings_router)
app.include_router(transcripts_router)
app.include_router(minutes_router)
app.include_router(config_router)


# ============================================
# GLOBAL STATE
# ============================================

calendar_monitor_running = False
chrome_instance = None


# ============================================
# MEETING SESSION MANAGEMENT
# ============================================

class MeetingSession:
    """Manages a single meeting session"""

    def __init__(self, meet_link: str, meeting_id: str = None):
        self.meet_link = meet_link
        self.meeting_id = meeting_id or self._generate_meeting_id()
        self.recordings_dir = Path(__file__).parent.parent.parent / 'recordings'
        self.recordings_dir.mkdir(parents=True, exist_ok=True)

    def _generate_meeting_id(self):
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def get_audio_path(self):
        return self.recordings_dir / f"{self.meeting_id}.wav"

    def join_and_record(self, chrome: ChromeManager):
        """Join meeting and handle recording"""
        from src.recording.record_audio import AudioRecorder
        from src.transcription.local_speech_to_text import LocalSpeechToText as SpeechToText
        from src.transcription.local_storage_service import LocalStorageService as BlobStorageService
        from src.intelligence.meeting_minutes_generator import MeetingMinutesGenerator
        from src.intelligence.email_service import EmailService

        print(f"\n{'='*50}")
        print(f"Starting meeting session: {self.meeting_id}")
        print(f"Meeting link: {self.meet_link}")
        print(f"{'='*50}\n")

        try:
            # Navigate to meeting
            chrome.navigate_to_meet(self.meet_link)
            time.sleep(3)

            # Turn off mic and camera
            chrome.turn_off_mic_and_camera()
            time.sleep(1)

            # Join the meeting
            joined = chrome.join_meeting()

            if not joined:
                print("Failed to join meeting or waiting for approval")
                time.sleep(30)

                if not chrome.is_in_meeting():
                    raise Exception("Could not join meeting after waiting")

            # Start recording
            audio_path = self.get_audio_path()
            audio_recorder = AudioRecorder()

            print("Starting audio recording...")
            audio_recorder.start_recording(str(audio_path))

            # Monitor the meeting
            chrome.monitor_meeting()

            # Meeting ended, stop recording
            print("Stopping audio recording...")
            audio_recorder.stop_recording(str(audio_path))
            time.sleep(2)

            # Process the recording
            self.process_recording(audio_path)

        except Exception as e:
            print(f"Error in meeting session: {e}")
            raise

    def process_recording(self, audio_path: Path):
        """Process and upload the recording"""
        from src.transcription.local_speech_to_text import LocalSpeechToText as SpeechToText
        from src.transcription.local_storage_service import LocalStorageService as BlobStorageService
        from src.intelligence.meeting_minutes_generator import MeetingMinutesGenerator
        from src.intelligence.email_service import EmailService

        if not audio_path.exists() or audio_path.stat().st_size == 0:
            print("No audio recording found or file is empty")
            return

        file_size_mb = audio_path.stat().st_size / (1024 * 1024)
        print(f"Audio recorded: {file_size_mb:.2f} MB")

        try:
            # Store to local storage
            print("Saving to local storage...")
            storage_service = BlobStorageService()
            storage_url = storage_service.upload_file(str(audio_path))
            print(f"Saved to: {storage_url}")

            # Transcribe with local Whisper
            print("Transcribing with local Whisper...")
            stt = SpeechToText()
            result = stt.transcribe(str(audio_path), meeting_id=self.meeting_id)
            transcript = result.get('text', '')

            if transcript:
                # Generate meeting minutes with local LLM
                print("Generating meeting minutes with local LLM...")
                llm_provider = os.getenv('LOCAL_LLM_PROVIDER', 'ollama')
                llm_model = os.getenv('LOCAL_LLM_MODEL', 'llama3')

                minutes_generator = MeetingMinutesGenerator(
                    llm_provider=llm_provider,
                    model_name=llm_model
                )

                meeting_date = datetime.now().strftime("%Y-%m-%d")
                minutes = minutes_generator.generate_minutes(
                    transcript=transcript,
                    meeting_title=f"Meeting {self.meeting_id}",
                    meeting_date=meeting_date
                )

                # Save minutes to files
                md_path = minutes_generator.save_minutes_to_file(minutes)
                json_path = minutes_generator.save_minutes_to_json(minutes)
                print(f"Minutes saved to: {md_path}")

                # Send email if configured
                smtp_user = os.getenv('SMTP_USER', '')
                if smtp_user:
                    print("Sending meeting minutes via email...")
                    email_service = EmailService()
                    markdown_minutes = minutes_generator._format_as_markdown(minutes)

                    recipient_emails = [smtp_user]
                    email_service.send_meeting_minutes(
                        to_emails=recipient_emails,
                        subject=f"Meeting Minutes: {minutes['meeting_title']}",
                        minutes_markdown=markdown_minutes,
                        minutes_file_path=md_path
                    )
                    print("Email sent successfully!")

            print(f"\n{'='*50}")
            print(f"Meeting session completed: {self.meeting_id}")
            print(f"{'='*50}\n")

        except Exception as e:
            print(f"Error processing recording: {e}")


# ============================================
# CALENDAR MONITORING
# ============================================

def join_meeting_from_calendar(meeting_info: dict):
    """Join a meeting from calendar information"""
    global chrome_instance

    print(f"\n📅 Calendar meeting starting: {meeting_info['title']}")

    try:
        if chrome_instance is None:
            chrome_instance = ChromeManager(use_existing_profile=True)

        session = MeetingSession(
            meet_link=meeting_info['meet_link'],
            meeting_id=meeting_info['id']
        )

        session.join_and_record(chrome_instance)

    except Exception as e:
        print(f"Error joining meeting from calendar: {e}")


def check_calendar_for_meetings():
    """Check calendar for upcoming meetings"""
    try:
        cal = CalendarService()
        upcoming_meetings = cal.get_upcoming_meetings(minutes_ahead=2)

        if upcoming_meetings:
            for meeting in upcoming_meetings:
                print(f"Found upcoming meeting: {meeting['title']}")
                Thread(target=join_meeting_from_calendar, args=(meeting,), daemon=True).start()

    except Exception as e:
        print(f"Error checking calendar: {e}")


def start_calendar_monitor():
    """Start monitoring calendar for meetings"""
    global calendar_monitor_running

    if calendar_monitor_running:
        print("Calendar monitor already running")
        return

    print("\n🔍 Starting calendar monitor...")
    print("Lumina will automatically join Google Meet sessions from your calendar\n")

    calendar_monitor_running = True

    schedule.every(1).minutes.do(check_calendar_for_meetings)

    def run_schedule():
        while calendar_monitor_running:
            schedule.run_pending()
            time.sleep(1)

    Thread(target=run_schedule, daemon=True).start()


def stop_calendar_monitor():
    """Stop monitoring calendar"""
    global calendar_monitor_running, chrome_instance

    calendar_monitor_running = False
    schedule.clear()

    if chrome_instance:
        chrome_instance.close()
        chrome_instance = None

    print("Calendar monitor stopped")


# ============================================
# LIFECYCLE EVENTS
# ============================================

@app.on_event("startup")
async def startup_event():
    """Start calendar monitoring on app startup if enabled"""
    auto_start = os.getenv('AUTO_START_CALENDAR_MONITOR', 'true').lower() == 'true'

    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║              ✨ Lumina - Meeting Assistant ✨         ║
    ║                                                       ║
    ║  Automatically joins and records Google Meet sessions ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)

    if auto_start:
        start_calendar_monitor()


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    stop_calendar_monitor()


# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
