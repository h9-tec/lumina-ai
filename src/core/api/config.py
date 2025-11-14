"""Configuration and status endpoints"""
from fastapi import APIRouter
import os

router = APIRouter(prefix="/api", tags=["config"])

# Will be set by main app
calendar_monitor_running = False
chrome_instance = None


@router.get("/status/")
async def get_status():
    """Get current status of Lumina"""
    return {
        "status": "running",
        "calendarMonitor": calendar_monitor_running,
        "chromeActive": chrome_instance is not None,
        "version": "2.0.0"
    }


@router.get("/config/")
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


@router.get("/")
async def root():
    """Health check endpoint with API documentation"""
    return {
        "name": "Lumina",
        "version": "2.0.0",
        "description": "AI-powered meeting assistant",
        "status": "operational",
        "endpoints": {
            "meetings": "/api/join-meeting/",
            "calendar": "/api/calendar/upcoming-meetings/",
            "recordings": "/api/recordings/",
            "transcripts": "/api/transcripts/",
            "minutes": "/api/minutes/",
            "process": "/api/minutes/process/{meeting_id}",
            "config": "/api/config/",
            "status": "/api/status/",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }
