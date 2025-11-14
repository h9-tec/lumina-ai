"""Meeting management endpoints"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from datetime import datetime

router = APIRouter(prefix="/api", tags=["meetings"])

# Import services
from src.core.calendar_service import CalendarService
from src.core.chrome_manager import ChromeManager
from src.recording.record_audio import AudioRecorder
from src.transcription.local_speech_to_text import LocalSpeechToText as SpeechToText
from src.transcription.local_storage_service import LocalStorageService as BlobStorageService
from src.intelligence.meeting_minutes_generator import MeetingMinutesGenerator
from src.intelligence.email_service import EmailService
import os

# Global state (shared with main app)
chrome_instance = None


class MeetingRequest(BaseModel):
    """Request model for manual meeting join"""
    meetLink: str
    meetingId: Optional[str] = None
    autoRecord: bool = True


class MeetingSession:
    """Manages a single meeting session"""

    def __init__(self, meet_link: str, meeting_id: str = None):
        self.meet_link = meet_link
        self.meeting_id = meeting_id or self._generate_meeting_id()
        self.recordings_dir = Path(__file__).parent.parent.parent.parent / 'recordings'
        self.recordings_dir.mkdir(parents=True, exist_ok=True)

    def _generate_meeting_id(self):
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def get_audio_path(self):
        return self.recordings_dir / f"{self.meeting_id}.wav"

    def join_and_record(self, chrome: ChromeManager):
        # Implementation from original lumina.py
        pass


@router.post("/join-meeting/")
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

        background_tasks.add_task(session.join_and_record, chrome_instance)

        return {
            "status": "success",
            "message": "Joining meeting...",
            "meetingId": session.meeting_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calendar/upcoming-meetings/")
async def get_upcoming_meetings():
    """Get upcoming Google Meet meetings from calendar"""
    try:
        cal = CalendarService()
        meetings = cal.get_upcoming_meetings(minutes_ahead=1440)

        return {
            "status": "success",
            "count": len(meetings),
            "meetings": meetings
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calendar/start-monitor/")
async def start_monitor():
    """Start monitoring calendar for meetings"""
    # Implementation will be in main app
    return {"status": "success", "message": "Calendar monitor started"}


@router.post("/calendar/stop-monitor/")
async def stop_monitor():
    """Stop monitoring calendar"""
    # Implementation will be in main app
    return {"status": "success", "message": "Calendar monitor stopped"}
