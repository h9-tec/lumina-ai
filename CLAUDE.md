# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Lumina is an AI-powered meeting companion that autonomously joins Google Meet sessions, captures audio, and transforms conversations into actionable insights. The system has been refactored to use persistent Chrome profiles (avoiding login/2FA) and Google Calendar integration for automatic meeting detection.

## Architecture

### Core Components (Refactored)

**Main Application** (`lumina.py`)
- FastAPI service with calendar monitoring capabilities
- Two modes: Auto (calendar-based) and Manual (API-based)
- Background scheduler checks calendar every minute
- Automatically joins meetings 1-2 minutes before start time
- Endpoints: `/join-meeting/`, `/calendar/upcoming-meetings/`, `/status/`

**Calendar Service** (`calendar_service.py`)
- Google Calendar API integration using OAuth 2.0
- Stores credentials in `token.pickle` after first auth
- `get_upcoming_meetings()` - finds meets within time window
- Extracts Google Meet links from various event fields (hangoutLink, conferenceData, description)
- Requires `credentials.json` from Google Cloud Console

**Chrome Manager** (`chrome_manager.py`)
- Uses existing Chrome user profile instead of creating new sessions
- Detects profile path based on OS (Windows/Mac/Linux)
- Sets `--user-data-dir` and `--profile-directory` arguments
- Uses remote debugging port 9222 to avoid conflicts
- No login required - user already authenticated in their Chrome profile
- Methods: `navigate_to_meet()`, `turn_off_mic_and_camera()`, `join_meeting()`, `monitor_meeting()`

**Audio Recording** (`record_audio.py`)
- Unchanged - captures system audio using sounddevice
- 16kHz mono WAV format

**Azure Services**
- `blob_storage_service.py`: Uploads with retry logic
- `speech_to_text.py`: Whisper transcription + GPT-4 analysis

**Legacy** (`join_google_meet.py`)
- Old approach with manual email/password login
- Kept for backward compatibility
- Not recommended for new usage

### Data Flow (New Architecture)

1. Lumina starts → Calendar monitor begins polling
2. Every minute: Check calendar for meetings starting soon
3. Meeting found → ChromeManager opens using existing profile
4. Navigate to Meet → Turn off mic/cam → Join
5. Audio recording starts
6. Monitor meeting until it ends
7. Upload to blob storage → Transcribe → Analyze
8. Results saved to JSON

### Key Differences from Old Version

**Old (`join_google_meet.py`):**
- Manual login flow with Selenium
- Email/password required in env vars
- 2FA verification needed
- New Chrome session every run
- API-driven only (no calendar)

**New (`lumina.py` + `chrome_manager.py` + `calendar_service.py`):**
- Uses existing Chrome profile (user already logged in)
- No email/password needed
- No 2FA hassle
- Persistent session
- Calendar auto-detection + API manual control

## Environment Configuration

Required `.env` variables:
```
# Azure OpenAI
OPENAI_API_KEY="key"
API_VERSION="2024-02-15-preview"
AZURE_OPENAI_ENDPOINT="endpoint"

# Azure Blob Storage
STORAGE_ACCOUNT_NAME="account"
STORAGE_ACCOUNT_KEY="key"
CONTAINER_NAME="container"

# Chrome Profile (optional)
CHROME_PROFILE_NAME="Default"  # or "Profile 1", "Profile 2", etc.

# Auto-start calendar (optional)
AUTO_START_CALENDAR_MONITOR="true"
```

**No longer needed:**
- `email_id` (old approach)
- `email_password` (old approach)

**New requirement:**
- `credentials.json` - Google Cloud OAuth credentials for Calendar API

## Development Commands

**Setup**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

**First-time Calendar Setup**
```bash
python calendar_service.py
# Opens browser for OAuth, creates token.pickle
```

**Run Lumina (Auto Mode)**
```bash
python lumina.py
# Starts FastAPI + calendar monitor
# Server: http://localhost:8000
```

**Run Legacy Version**
```bash
python join_google_meet.py
# Old approach - requires email/password
```

**Manual Meeting Join**
```bash
curl -X POST "http://localhost:8000/join-meeting/" \
  -H "Content-Type: application/json" \
  -d '{"meetLink": "https://meet.google.com/xxx-xxxx-xxx"}'
```

**Check Calendar**
```bash
curl http://localhost:8000/calendar/upcoming-meetings/
```

## Key Implementation Details

**Chrome Profile Detection:**
- Windows: `%USERPROFILE%\AppData\Local\Google\Chrome\User Data`
- macOS: `~/Library/Application Support/Google/Chrome`
- Linux: `~/.config/google-chrome`

**Calendar Polling:**
- Runs on background thread using `schedule` library
- Checks every 1 minute for meetings starting within 2 minutes
- Spawns new thread for each meeting to join

**Meeting Detection Logic:**
- Checks `hangoutLink` field (primary)
- Falls back to `conferenceData.entryPoints`
- Regex searches description for `meet.google.com` links

**Chrome Constraints:**
- Must close all Chrome windows before running (profile lock)
- Uses remote debugging port 9222
- Headless mode not supported (Meet requires visible browser)

**Session Management:**
- Global `chrome_instance` shared across meetings
- Not closed between meetings (persistent)
- Cleaned up on app shutdown

## Common Issues

**Chrome profile locked:**
Close all Chrome windows before starting Lumina. Only one process can access a profile.

**Calendar not working:**
1. Check `credentials.json` exists
2. Run `python calendar_service.py` to authenticate
3. Delete `token.pickle` and re-auth if expired

**Meeting not auto-joining:**
- Verify calendar has Google Meet links
- Check `AUTO_START_CALENDAR_MONITOR=true` in .env
- Look at server logs for calendar check results

**Still getting login prompts:**
- You're not logged into Chrome
- Wrong Chrome profile selected
- Try setting `CHROME_PROFILE_NAME` to your actual profile

**Audio not recording:**
Ensure Chrome has microphone permissions and sounddevice can access system audio.

## File Naming

- Audio: `recordings/{meetingId}.wav` (meetingId = timestamp or event ID)
- JSON: `meeting_data_{timestamp}.json`
- Token: `token.pickle` (Calendar API credentials)

## Testing

**Test Calendar Service:**
```bash
python calendar_service.py
# Lists today's meetings and upcoming Meet links
```

**Test Chrome Manager:**
```bash
python chrome_manager.py
# Opens Chrome with your profile to test
```

**Test Full Flow:**
```bash
python lumina.py
# Monitor logs for calendar checks and meeting joins
```
