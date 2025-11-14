"""
Lumina - Intelligent Meeting Assistant

Automatically monitors your calendar and joins Google Meet sessions,
recording and analyzing conversations without manual intervention.
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional
import os
import time
import schedule
from datetime import datetime, timedelta
from threading import Thread

from src.core.calendar_service import CalendarService
from src.core.chrome_manager import ChromeManager
from src.recording.record_audio import AudioRecorder
from src.transcription.local_speech_to_text import LocalSpeechToText as SpeechToText
from src.transcription.local_storage_service import LocalStorageService as BlobStorageService
from src.intelligence.local_llm_service import LocalLLMService
from src.intelligence.meeting_minutes_generator import MeetingMinutesGenerator
from src.intelligence.email_service import EmailService

load_dotenv()

app = FastAPI(title="Lumina - AI Meeting Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class MeetingRequest(BaseModel):
    """Request model for manual meeting join"""
    meetLink: str
    meetingId: Optional[str] = None
    autoRecord: bool = True


class CalendarConfig(BaseModel):
    """Configuration for calendar monitoring"""
    enabled: bool = True
    checkIntervalMinutes: int = 2
    joinBeforeMinutes: int = 1


# Global state
calendar_monitor_running = False
chrome_instance = None


class MeetingSession:
    """Manages a single meeting session"""

    def __init__(self, meet_link: str, meeting_id: str = None):
        self.meet_link = meet_link
        self.meeting_id = meeting_id or self._generate_meeting_id()
        # Use project root for recordings
        self.recordings_dir = Path(__file__).parent.parent.parent / 'recordings'
        self.recordings_dir.mkdir(parents=True, exist_ok=True)

    def _generate_meeting_id(self):
        """Generate a unique meeting ID based on timestamp"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def get_audio_path(self):
        """Get path for audio recording"""
        return self.recordings_dir / f"{self.meeting_id}.wav"

    def join_and_record(self, chrome: ChromeManager):
        """Join meeting and handle recording"""
        print(f"\n{'='*50}")
        print(f"Starting meeting session: {self.meeting_id}")
        print(f"Meeting link: {self.meet_link}")
        print(f"{'='*50}\n")

        try:
            # Navigate to meeting
            chrome.navigate_to_meet(self.meet_link)
            time.sleep(3)  # Wait for page to load

            # Turn off mic and camera
            chrome.turn_off_mic_and_camera()
            time.sleep(1)

            # Join the meeting
            joined = chrome.join_meeting()

            if not joined:
                print("Failed to join meeting or waiting for approval")
                # Still try to record in case we get approved later
                time.sleep(30)  # Wait 30 seconds for approval

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
            time.sleep(2)  # Wait for file to be written

            # Process the recording
            self.process_recording(audio_path)

        except Exception as e:
            print(f"Error in meeting session: {e}")
            raise

    def process_recording(self, audio_path: Path):
        """Process and upload the recording"""
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

                    recipient_emails = [smtp_user]  # Send to self
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


def join_meeting_from_calendar(meeting_info: dict):
    """Join a meeting from calendar information"""
    global chrome_instance

    print(f"\n📅 Calendar meeting starting: {meeting_info['title']}")

    try:
        # Initialize Chrome if not already running
        if chrome_instance is None:
            chrome_instance = ChromeManager(use_existing_profile=True)

        # Create meeting session
        session = MeetingSession(
            meet_link=meeting_info['meet_link'],
            meeting_id=meeting_info['id']
        )

        # Join and record
        session.join_and_record(chrome_instance)

    except Exception as e:
        print(f"Error joining meeting from calendar: {e}")


def check_calendar_for_meetings():
    """Check calendar for upcoming meetings"""
    try:
        cal = CalendarService()

        # Look for meetings starting in the next 2 minutes
        upcoming_meetings = cal.get_upcoming_meetings(minutes_ahead=2)

        if upcoming_meetings:
            for meeting in upcoming_meetings:
                print(f"Found upcoming meeting: {meeting['title']}")
                # Join the meeting in a separate thread
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

    # Schedule calendar checks every 1 minute
    schedule.every(1).minutes.do(check_calendar_for_meetings)

    def run_schedule():
        while calendar_monitor_running:
            schedule.run_pending()
            time.sleep(1)

    # Run scheduler in background thread
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


# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Start calendar monitoring on app startup if enabled"""
    auto_start = os.getenv('AUTO_START_CALENDAR_MONITOR', 'true').lower() == 'true'

    if auto_start:
        start_calendar_monitor()


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    stop_calendar_monitor()


@app.post("/join-meeting/")
async def join_meeting_manual(request: MeetingRequest, background_tasks: BackgroundTasks):
    """Manually join a meeting by providing the meet link"""
    global chrome_instance

    try:
        if chrome_instance is None:
            chrome_instance = ChromeManager(use_existing_profile=True)

        session = MeetingSession(
            meet_link=request.meetLink,
            meeting_id=request.meetingId
        )

        # Run in background
        background_tasks.add_task(session.join_and_record, chrome_instance)

        return {
            "status": "success",
            "message": "Joining meeting...",
            "meetingId": session.meeting_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calendar/start-monitor/")
async def start_monitor():
    """Start monitoring calendar for meetings"""
    start_calendar_monitor()
    return {"status": "success", "message": "Calendar monitor started"}


@app.post("/calendar/stop-monitor/")
async def stop_monitor():
    """Stop monitoring calendar"""
    stop_calendar_monitor()
    return {"status": "success", "message": "Calendar monitor stopped"}


@app.get("/calendar/upcoming-meetings/")
async def get_upcoming_meetings():
    """Get upcoming Google Meet meetings from calendar"""
    try:
        cal = CalendarService()
        meetings = cal.get_upcoming_meetings(minutes_ahead=1440)  # Next 24 hours

        return {
            "status": "success",
            "count": len(meetings),
            "meetings": meetings
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/")
async def get_status():
    """Get current status of Lumina"""
    return {
        "status": "running",
        "calendarMonitor": calendar_monitor_running,
        "chromeActive": chrome_instance is not None,
        "version": "2.0.0"
    }


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "name": "Lumina",
        "version": "2.0.0",
        "description": "AI-powered meeting assistant",
        "status": "operational",
        "endpoints": {
            "meetings": "/join-meeting/",
            "calendar": "/calendar/upcoming-meetings/",
            "recordings": "/recordings/",
            "transcripts": "/transcripts/",
            "minutes": "/minutes/",
            "process": "/process/{meeting_id}",
            "docs": "/docs"
        }
    }


# ============================================
# RECORDING MANAGEMENT ENDPOINTS
# ============================================

@app.get("/recordings/")
async def list_recordings():
    """List all available recordings"""
    try:
        recordings_dir = Path(__file__).parent.parent.parent / 'recordings'
        recordings_dir.mkdir(parents=True, exist_ok=True)

        recordings = []
        for audio_file in recordings_dir.glob("*.wav"):
            file_stats = audio_file.stat()
            recordings.append({
                "meetingId": audio_file.stem,
                "filename": audio_file.name,
                "path": str(audio_file),
                "size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(file_stats.st_ctime).isoformat()
            })

        recordings.sort(key=lambda x: x['created'], reverse=True)

        return {
            "status": "success",
            "count": len(recordings),
            "recordings": recordings
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/recordings/{meeting_id}")
async def get_recording(meeting_id: str):
    """Get information about a specific recording"""
    try:
        recordings_dir = Path(__file__).parent.parent.parent / 'recordings'
        audio_file = recordings_dir / f"{meeting_id}.wav"

        if not audio_file.exists():
            raise HTTPException(status_code=404, detail="Recording not found")

        file_stats = audio_file.stat()

        return {
            "status": "success",
            "recording": {
                "meetingId": meeting_id,
                "filename": audio_file.name,
                "path": str(audio_file),
                "size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                "duration_estimate": "calculating..."
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/recordings/{meeting_id}")
async def delete_recording(meeting_id: str):
    """Delete a recording"""
    try:
        recordings_dir = Path(__file__).parent.parent.parent / 'recordings'
        audio_file = recordings_dir / f"{meeting_id}.wav"

        if not audio_file.exists():
            raise HTTPException(status_code=404, detail="Recording not found")

        audio_file.unlink()

        return {
            "status": "success",
            "message": f"Recording {meeting_id} deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# TRANSCRIPTION ENDPOINTS
# ============================================

@app.post("/transcribe/{meeting_id}")
async def transcribe_recording(meeting_id: str, background_tasks: BackgroundTasks):
    """Transcribe a specific recording using local Whisper"""
    try:
        recordings_dir = Path(__file__).parent.parent.parent / 'recordings'
        audio_file = recordings_dir / f"{meeting_id}.wav"

        if not audio_file.exists():
            raise HTTPException(status_code=404, detail="Recording not found")

        def transcribe_task():
            stt = SpeechToText()
            stt.transcribe(str(audio_file), meeting_id=meeting_id)

        background_tasks.add_task(transcribe_task)

        return {
            "status": "success",
            "message": "Transcription started",
            "meetingId": meeting_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/transcripts/")
async def list_transcripts():
    """List all available transcripts"""
    try:
        storage_dir = Path(__file__).parent.parent.parent / 'storage' / 'transcripts'
        storage_dir.mkdir(parents=True, exist_ok=True)

        transcripts = []
        for transcript_file in storage_dir.glob("transcript_*.txt"):
            file_stats = transcript_file.stat()
            meeting_id = transcript_file.stem.replace("transcript_", "")

            transcripts.append({
                "meetingId": meeting_id,
                "filename": transcript_file.name,
                "path": str(transcript_file),
                "size_kb": round(file_stats.st_size / 1024, 2),
                "created": datetime.fromtimestamp(file_stats.st_ctime).isoformat()
            })

        transcripts.sort(key=lambda x: x['created'], reverse=True)

        return {
            "status": "success",
            "count": len(transcripts),
            "transcripts": transcripts
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/transcripts/{meeting_id}")
async def get_transcript(meeting_id: str):
    """Get the transcript for a specific meeting"""
    try:
        storage_dir = Path(__file__).parent.parent.parent / 'storage' / 'transcripts'
        transcript_file = storage_dir / f"transcript_{meeting_id}.txt"

        if not transcript_file.exists():
            raise HTTPException(status_code=404, detail="Transcript not found")

        transcript_text = transcript_file.read_text(encoding='utf-8')

        return {
            "status": "success",
            "meetingId": meeting_id,
            "transcript": transcript_text,
            "length": len(transcript_text)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# MEETING MINUTES ENDPOINTS
# ============================================

@app.post("/minutes/generate/{meeting_id}")
async def generate_minutes(meeting_id: str, background_tasks: BackgroundTasks):
    """Generate meeting minutes from transcript using local LLM"""
    try:
        storage_dir = Path(__file__).parent.parent.parent / 'storage' / 'transcripts'
        transcript_file = storage_dir / f"transcript_{meeting_id}.txt"

        if not transcript_file.exists():
            raise HTTPException(status_code=404, detail="Transcript not found. Transcribe the recording first.")

        transcript_text = transcript_file.read_text(encoding='utf-8')

        def generate_task():
            llm_provider = os.getenv('LOCAL_LLM_PROVIDER', 'ollama')
            llm_model = os.getenv('LOCAL_LLM_MODEL', 'llama3')

            generator = MeetingMinutesGenerator(
                llm_provider=llm_provider,
                model_name=llm_model
            )

            meeting_date = datetime.now().strftime("%Y-%m-%d")
            minutes = generator.generate_minutes(
                transcript=transcript_text,
                meeting_title=f"Meeting {meeting_id}",
                meeting_date=meeting_date
            )

            generator.save_minutes_to_file(minutes)
            generator.save_minutes_to_json(minutes)

        background_tasks.add_task(generate_task)

        return {
            "status": "success",
            "message": "Meeting minutes generation started",
            "meetingId": meeting_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/minutes/")
async def list_minutes():
    """List all available meeting minutes"""
    try:
        storage_dir = Path(__file__).parent.parent.parent / 'storage' / 'minutes'
        storage_dir.mkdir(parents=True, exist_ok=True)

        minutes_list = []
        for minutes_file in storage_dir.glob("meeting_minutes_*.md"):
            file_stats = minutes_file.stat()
            meeting_id = minutes_file.stem.replace("meeting_minutes_", "")

            minutes_list.append({
                "meetingId": meeting_id,
                "filename": minutes_file.name,
                "path": str(minutes_file),
                "size_kb": round(file_stats.st_size / 1024, 2),
                "created": datetime.fromtimestamp(file_stats.st_ctime).isoformat()
            })

        minutes_list.sort(key=lambda x: x['created'], reverse=True)

        return {
            "status": "success",
            "count": len(minutes_list),
            "minutes": minutes_list
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/minutes/{meeting_id}")
async def get_minutes(meeting_id: str, format: str = "markdown"):
    """Get meeting minutes for a specific meeting (markdown or json)"""
    try:
        storage_dir = Path(__file__).parent.parent.parent / 'storage' / 'minutes'

        if format == "json":
            minutes_file = storage_dir / f"meeting_minutes_{meeting_id}.json"
            if not minutes_file.exists():
                raise HTTPException(status_code=404, detail="Meeting minutes (JSON) not found")

            import json
            minutes_data = json.loads(minutes_file.read_text(encoding='utf-8'))

            return {
                "status": "success",
                "meetingId": meeting_id,
                "format": "json",
                "minutes": minutes_data
            }
        else:
            minutes_file = storage_dir / f"meeting_minutes_{meeting_id}.md"
            if not minutes_file.exists():
                raise HTTPException(status_code=404, detail="Meeting minutes (Markdown) not found")

            minutes_text = minutes_file.read_text(encoding='utf-8')

            return {
                "status": "success",
                "meetingId": meeting_id,
                "format": "markdown",
                "minutes": minutes_text
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class EmailRequest(BaseModel):
    """Request model for sending email"""
    recipients: list[str]
    subject: Optional[str] = None


@app.post("/minutes/email/{meeting_id}")
async def email_minutes(meeting_id: str, request: EmailRequest):
    """Send meeting minutes via email"""
    try:
        storage_dir = Path(__file__).parent.parent.parent / 'storage' / 'minutes'
        md_file = storage_dir / f"meeting_minutes_{meeting_id}.md"

        if not md_file.exists():
            raise HTTPException(status_code=404, detail="Meeting minutes not found")

        minutes_markdown = md_file.read_text(encoding='utf-8')

        email_service = EmailService()
        subject = request.subject or f"Meeting Minutes: {meeting_id}"

        email_service.send_meeting_minutes(
            to_emails=request.recipients,
            subject=subject,
            minutes_markdown=minutes_markdown,
            minutes_file_path=str(md_file)
        )

        return {
            "status": "success",
            "message": f"Meeting minutes sent to {len(request.recipients)} recipients",
            "recipients": request.recipients
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# COMPLETE PROCESSING PIPELINE
# ============================================

@app.post("/process/{meeting_id}")
async def process_complete_pipeline(meeting_id: str, background_tasks: BackgroundTasks):
    """
    Complete processing pipeline: Transcribe → Generate Minutes → Send Email
    This processes a recording end-to-end
    """
    try:
        recordings_dir = Path(__file__).parent.parent.parent / 'recordings'
        audio_file = recordings_dir / f"{meeting_id}.wav"

        if not audio_file.exists():
            raise HTTPException(status_code=404, detail="Recording not found")

        def complete_pipeline():
            try:
                # Step 1: Transcribe
                print(f"[Pipeline] Step 1: Transcribing {meeting_id}...")
                stt = SpeechToText()
                result = stt.transcribe(str(audio_file), meeting_id=meeting_id)
                transcript = result.get('text', '')

                if not transcript:
                    print("[Pipeline] No transcript generated, aborting pipeline")
                    return

                # Step 2: Generate Minutes
                print(f"[Pipeline] Step 2: Generating meeting minutes...")
                llm_provider = os.getenv('LOCAL_LLM_PROVIDER', 'ollama')
                llm_model = os.getenv('LOCAL_LLM_MODEL', 'llama3')

                generator = MeetingMinutesGenerator(
                    llm_provider=llm_provider,
                    model_name=llm_model
                )

                meeting_date = datetime.now().strftime("%Y-%m-%d")
                minutes = generator.generate_minutes(
                    transcript=transcript,
                    meeting_title=f"Meeting {meeting_id}",
                    meeting_date=meeting_date
                )

                md_path = generator.save_minutes_to_file(minutes)
                generator.save_minutes_to_json(minutes)
                print(f"[Pipeline] Minutes saved to: {md_path}")

                # Step 3: Send Email (if configured)
                smtp_user = os.getenv('SMTP_USER', '')
                if smtp_user:
                    print(f"[Pipeline] Step 3: Sending email...")
                    email_service = EmailService()
                    markdown_minutes = generator._format_as_markdown(minutes)

                    email_service.send_meeting_minutes(
                        to_emails=[smtp_user],
                        subject=f"Meeting Minutes: {minutes['meeting_title']}",
                        minutes_markdown=markdown_minutes,
                        minutes_file_path=md_path
                    )
                    print("[Pipeline] Email sent successfully!")
                else:
                    print("[Pipeline] SMTP not configured, skipping email")

                print(f"[Pipeline] Complete! Processed {meeting_id}")

            except Exception as e:
                print(f"[Pipeline] Error: {e}")

        background_tasks.add_task(complete_pipeline)

        return {
            "status": "success",
            "message": "Complete processing pipeline started",
            "meetingId": meeting_id,
            "steps": ["transcribe", "generate_minutes", "send_email"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# CONFIGURATION ENDPOINTS
# ============================================

@app.get("/config/")
async def get_config():
    """Get current Lumina configuration"""
    return {
        "status": "success",
        "config": {
            "llm": {
                "provider": os.getenv('LOCAL_LLM_PROVIDER', 'ollama'),
                "model": os.getenv('LOCAL_LLM_MODEL', 'llama3')
            },
            "whisper": {
                "model": os.getenv('WHISPER_MODEL', 'base')
            },
            "email": {
                "configured": bool(os.getenv('SMTP_USER', '')),
                "smtp_server": os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            },
            "calendar": {
                "auto_start": os.getenv('AUTO_START_CALENDAR_MONITOR', 'true'),
                "monitor_running": calendar_monitor_running
            },
            "chrome": {
                "profile": os.getenv('CHROME_PROFILE_NAME', 'Default')
            }
        }
    }


if __name__ == "__main__":
    import uvicorn

    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║              ✨ Lumina - Meeting Assistant ✨         ║
    ║                                                       ║
    ║  Automatically joins and records Google Meet sessions ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)

    uvicorn.run(app, host="0.0.0.0", port=8000)
