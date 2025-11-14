# Lumina - AI-Powered Meeting Intelligence Platform

<div align="center">

**Enterprise-grade autonomous meeting assistant with calendar integration, real-time transcription, and intelligent analysis**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

[Features](#features) • [Architecture](#architecture) • [Installation](#installation) • [Usage](#usage) • [API Reference](#api-reference) • [Documentation](#documentation)

</div>

---

## Overview

Lumina is a sophisticated meeting intelligence platform that autonomously monitors your Google Calendar, joins scheduled meetings, and transforms conversations into structured, actionable insights. Built with a modular architecture, Lumina supports both cloud-based (Azure) and local processing (Whisper + Ollama/LLaMA.cpp) for maximum flexibility and privacy.

### Key Differentiators

- **Zero-Touch Authentication**: Leverages persistent Chrome profiles—no repeated logins or 2FA prompts
- **Calendar-Driven Automation**: Intelligent scheduling system auto-joins meetings 1-2 minutes before start time
- **Hybrid Processing Pipeline**: Supports both Azure OpenAI and local LLM inference (Ollama, LLaMA.cpp)
- **Anti-Bot Detection**: Advanced human behavior simulation prevents Google Meet bot detection
- **Local-First Storage**: Optional local storage with Whisper transcription—no cloud dependency required
- **Meeting Minutes Automation**: Complete pipeline from audio capture to formatted minutes with email delivery

---

## Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **🗓️ Calendar Integration** | Google Calendar API integration with automatic meeting detection |
| **🔐 Persistent Sessions** | Uses existing Chrome profile with saved login state |
| **🎙️ Multi-Format Recording** | High-quality audio recording (16kHz mono WAV) |
| **🤖 AI Transcription** | Azure Speech-to-Text or local Whisper models |
| **📊 Meeting Analysis** | Automated summarization, key points extraction, sentiment analysis |
| **📧 Email Delivery** | Formatted meeting minutes sent via SMTP/Gmail API |
| **☁️ Cloud Storage** | Azure Blob Storage integration with retry logic |
| **💾 Local Storage** | File-based storage for complete data sovereignty |
| **🌐 REST API** | Full-featured FastAPI server for programmatic control |
| **🧠 Local LLM Support** | Ollama, LLaMA.cpp integration with Azure fallback |
| **🛡️ Bot Detection Avoidance** | Randomized human-like interactions (mouse movements, clicks) |

### Meeting Minutes Pipeline

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│   Meeting   │───▶│   Whisper    │───▶│ Local LLM   │───▶│   Email +   │
│  Recording  │    │ Transcription│    │  Analysis   │    │ File Export │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
```

- **Transcription**: Local Whisper (tiny, base, small, medium, large)
- **Analysis**: Ollama (Llama3, Mistral), LLaMA.cpp (GGUF), or Azure GPT-4
- **Output**: Markdown, JSON, HTML email with attachments
- **Content**: Summary, key points & decisions, action items with owners

---

## Architecture

### System Design

```
┌──────────────────────────────────────────────────────────────────┐
│                        Lumina Core (FastAPI)                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │    Calendar    │  │     Chrome     │  │   Audio/Video    │  │
│  │    Service     │  │    Manager     │  │    Recording     │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
│                                                                    │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ Local LLM      │  │   Speech-to-   │  │  Storage Layer   │  │
│  │ Service        │  │   Text (STT)   │  │  (Local/Cloud)   │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
│                                                                    │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ Meeting Minutes│  │     Email      │  │  Bot Detection   │  │
│  │   Generator    │  │    Service     │  │   Prevention     │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

### Component Overview

#### Core Modules

| Module | File | Description |
|--------|------|-------------|
| **Main Application** | `lumina.py` | FastAPI server with calendar monitoring and REST endpoints |
| **Calendar Service** | `calendar_service.py` | Google Calendar API integration, OAuth 2.0 authentication |
| **Chrome Manager** | `chrome_manager.py` | Selenium-based Chrome automation with profile persistence |
| **Audio Recording** | `record_audio.py` | System audio capture using sounddevice (16kHz mono) |
| **Video Recording** | `record_video.py` | Screen recording with OpenCV (optional) |

#### Processing Modules

| Module | File | Description |
|--------|------|-------------|
| **Speech-to-Text** | `speech_to_text.py` | Azure Speech Services integration |
| **Local STT** | `local_speech_to_text.py` | OpenAI Whisper local transcription |
| **Local LLM Service** | `local_llm_service.py` | Unified interface for Ollama, LLaMA.cpp, Azure GPT-4 |
| **Minutes Generator** | `meeting_minutes_generator.py` | Structured meeting minutes creation |
| **Email Service** | `email_service.py` | SMTP/Gmail API email delivery |

#### Storage Modules

| Module | File | Description |
|--------|------|-------------|
| **Blob Storage** | `blob_storage_service.py` | Azure Blob Storage with retry logic |
| **Local Storage** | `local_storage_service.py` | File-based local storage implementation |

#### Utility Scripts

| Script | File | Description |
|--------|------|-------------|
| **Process Recording** | `process_recording.py` | End-to-end pipeline: Audio → Transcript → Minutes → Email |
| **Auto Join** | `join_meeting_auto.py` | Automated meeting join with bot detection avoidance |
| **Standalone Join** | `join_meeting_standalone.py` | Single meeting join using Chrome profile |
| **Quick Join** | `quick_join.py` | Minimal meeting join script |
| **Legacy Join** | `join_google_meet.py` | Original implementation (email/password login) |

### Technology Stack

**Backend Framework**
- FastAPI 0.100+ (async REST API)
- Uvicorn (ASGI server)

**Browser Automation**
- Selenium WebDriver 4.21+
- Chrome/Chromium (headless/headed modes)

**Audio/Video Processing**
- sounddevice (audio capture)
- OpenCV (video recording)
- PyAudio (audio streaming)

**Machine Learning**
- OpenAI Whisper (local transcription)
- Azure OpenAI GPT-4 (cloud analysis)
- Ollama (local LLM server)
- llama-cpp-python (GGUF model inference)
- LangChain (LLM orchestration)

**Cloud Services**
- Azure Speech Services (transcription)
- Azure Blob Storage (recordings)
- Google Calendar API (scheduling)

**Data Formats**
- WAV (audio recordings)
- JSON (structured data)
- Markdown (meeting minutes)
- HTML (email formatting)

---

## Installation

### Prerequisites

- **Python**: 3.8 or higher
- **Chrome Browser**: With active Google account login
- **Operating System**: Linux (tested), macOS, Windows
- **RAM**: 8GB minimum (16GB recommended for local LLM)
- **Disk Space**: 10GB for dependencies and models

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/M-Aboelgoud/Lumina.git
cd Lumina

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 5. Set up Google Calendar API
# Download credentials.json from Google Cloud Console
# Place in project root

# 6. Authenticate with Google Calendar
python calendar_service.py

# 7. Install Ollama (optional, for local LLM)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3

# 8. Run Lumina
python lumina.py
```

### Detailed Setup

#### 1. Google Calendar API Setup

**a. Create Google Cloud Project**
1. Navigate to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "Lumina"
3. Enable **Google Calendar API**

**b. Create OAuth Credentials**
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Configure consent screen (External, add your email)
4. Application type: **Desktop app**
5. Download JSON, rename to `credentials.json`
6. Place in project root directory

**c. First-Time Authentication**
```bash
python calendar_service.py
```
- Opens browser for Google login
- Grants calendar read permissions
- Saves `token.pickle` for future use

#### 2. Azure Services Setup (Optional)

**For Cloud Processing:**

**a. Azure OpenAI**
1. Create Azure OpenAI resource
2. Deploy GPT-4 model
3. Note: API key, endpoint, deployment name

**b. Azure Blob Storage**
1. Create Storage Account
2. Create container: "meeting-recordings"
3. Copy access key

**c. Azure Speech Services**
1. Create Speech resource
2. Copy API key and region

#### 3. Local LLM Setup (Optional)

**Option A: Ollama (Recommended)**

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull llama3       # 4.7GB - Balanced
ollama pull mistral      # 4.1GB - Fast
ollama pull phi3         # 2.3GB - Lightweight
ollama pull llama3:70b   # 40GB - Highest quality

# Test
ollama run llama3
```

**Option B: LLaMA.cpp**

```bash
# Download GGUF model
wget https://huggingface.co/TheBloke/Llama-3-8B-Instruct-GGUF/resolve/main/llama-3-8b-instruct.Q4_K_M.gguf \
  -O ~/models/llama3.gguf

# Configure path in .env
LLAMACPP_MODEL_PATH="/home/user/models/llama3.gguf"
```

#### 4. Email Configuration (Optional)

**Gmail Setup:**

1. Enable 2-Factor Authentication: [Google Security](https://myaccount.google.com/security)
2. Create App Password: [App Passwords](https://myaccount.google.com/apppasswords)
3. Add to `.env`:
   ```bash
   SMTP_USER="your-email@gmail.com"
   SMTP_PASSWORD="16-char-app-password"
   ```

---

## Configuration

### Environment Variables

Complete `.env` configuration reference:

```bash
# ============================================
# CHROME CONFIGURATION
# ============================================
# Chrome profile to use (Default, Profile 1, Profile 2, etc.)
CHROME_PROFILE_NAME="Default"

# ============================================
# CALENDAR INTEGRATION
# ============================================
# Auto-start calendar monitoring on launch
AUTO_START_CALENDAR_MONITOR="true"

# ============================================
# STORAGE CONFIGURATION
# ============================================
# Local storage path for recordings and outputs
LOCAL_STORAGE_PATH="./storage"

# Azure Blob Storage (optional)
STORAGE_ACCOUNT_NAME="your_storage_account"
STORAGE_ACCOUNT_KEY="your_storage_key"
CONTAINER_NAME="meeting-recordings"

# ============================================
# WHISPER CONFIGURATION
# ============================================
# Model size: tiny, base, small, medium, large
WHISPER_MODEL="base"

# ============================================
# LOCAL LLM CONFIGURATION
# ============================================
# Provider: ollama, llamacpp, azure
LOCAL_LLM_PROVIDER="ollama"

# Model name for Ollama
LOCAL_LLM_MODEL="llama3"

# Model path for LLaMA.cpp
LLAMACPP_MODEL_PATH="/path/to/model.gguf"

# ============================================
# AZURE OPENAI (FALLBACK)
# ============================================
OPENAI_API_KEY="your_azure_openai_key"
API_VERSION="2024-08-01-preview"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"

# ============================================
# AZURE SPEECH SERVICES
# ============================================
AZURE_SPEECH_KEY="your_speech_key"
AZURE_SPEECH_REGION="eastus"

# ============================================
# EMAIL CONFIGURATION
# ============================================
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"
```

### Model Selection Guide

#### Whisper Models

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny | 39 MB | Fastest | Basic | Testing, development |
| base | 74 MB | Fast | Good | Default, most meetings |
| small | 244 MB | Medium | Better | Important meetings |
| medium | 769 MB | Slow | High | Critical transcription |
| large | 1.5 GB | Slowest | Best | Professional, archival |

#### Ollama Models

| Model | Size | RAM | Speed | Quality | Best For |
|-------|------|-----|-------|---------|----------|
| phi3 | 2.3 GB | 4 GB | Fast | Good | Quick summaries, low-resource |
| mistral | 4.1 GB | 6 GB | Fast | Great | General purpose, fast inference |
| llama3 | 4.7 GB | 8 GB | Medium | Great | Balanced (recommended) |
| llama3:70b | 40 GB | 48 GB | Slow | Excellent | Enterprise, highest quality |

---

## Usage

### Mode 1: Auto Mode (Calendar-Driven)

**Start automatic calendar monitoring:**

```bash
python lumina.py
```

**Behavior:**
- Polls calendar every 60 seconds
- Detects meetings with Google Meet links
- Auto-joins 1-2 minutes before start time
- Records and processes automatically
- Generates minutes and sends emails

**Output:**
```
✨ Lumina - Meeting Assistant ✨
Automatically joins and records Google Meet sessions

🔍 Starting calendar monitor...
📅 Checking calendar for upcoming meetings...
📅 Found 3 upcoming meetings
🔗 Meeting: "Team Standup" starts in 1.5 minutes
🚀 Joining meeting...
```

### Mode 2: Manual API Control

**Start Lumina server:**

```bash
python lumina.py
```

**Join specific meeting:**

```bash
curl -X POST "http://localhost:8000/join-meeting/" \
  -H "Content-Type: application/json" \
  -d '{
    "meetLink": "https://meet.google.com/xxx-xxxx-xxx",
    "meetingId": "team-standup-2025-11-14",
    "autoRecord": true
  }'
```

**Check status:**

```bash
curl http://localhost:8000/status/
```

**Get upcoming meetings:**

```bash
curl http://localhost:8000/calendar/upcoming-meetings/
```

**Start/Stop calendar monitor:**

```bash
# Start
curl -X POST http://localhost:8000/calendar/start-monitor/

# Stop
curl -X POST http://localhost:8000/calendar/stop-monitor/
```

### Mode 3: Standalone Scripts

**Quick join (no API server):**

```bash
python join_meeting_auto.py "https://meet.google.com/xxx-xxxx-xxx" "Bot Name"
```

**Process existing recording:**

```bash
python process_recording.py recordings/meeting.wav \
  --title "Q4 Planning Meeting" \
  --email "team@company.com,manager@company.com" \
  --llm-provider ollama \
  --llm-model llama3
```

**Arguments:**
- `--title`: Meeting title
- `--email`: Comma-separated recipient list
- `--llm-provider`: `ollama`, `llamacpp`, `azure`
- `--llm-model`: Model name (for Ollama)
- `--no-email`: Skip email delivery
- `--no-save`: Skip file saving

### Mode 4: Local Meeting Minutes Pipeline

**Process recording end-to-end:**

```bash
# Basic usage
python process_recording.py recordings/20251114_194510.wav

# With all options
python process_recording.py recordings/team_meeting.wav \
  --title "Sprint Review & Retrospective" \
  --email "dev-team@company.com,product@company.com" \
  --llm-provider ollama \
  --llm-model mistral
```

**Pipeline stages:**
1. ✅ Whisper transcription (local)
2. ✅ LLM analysis (Ollama/LLaMA.cpp/Azure)
3. ✅ Markdown/JSON export
4. ✅ HTML email with attachments

**Example output:**

```
╔═══════════════════════════════════════════════════════════╗
║     🌟 Lumina - Meeting Recording Processor             ║
║     Processing: Sprint Review & Retrospective            ║
╚═══════════════════════════════════════════════════════════╝

📝 Step 1/4: Transcribing audio with Whisper...
   Loading Whisper model: base
   Transcribing: team_meeting.wav
✅ Transcription complete (4532 characters)
   💾 Transcript saved: ./storage/transcripts/transcript_20251114_194510.txt

🤖 Step 2/4: Generating minutes with ollama...
📝 Generating meeting minutes...
✅ Minutes generated successfully!
✅ Minutes generated!

💾 Step 3/4: Saving minutes to files...
💾 Minutes saved to: ./storage/minutes/meeting_minutes_20251114_194510.md
💾 Minutes (JSON) saved to: ./storage/minutes/meeting_minutes_20251114_194510.json
✅ Saved 3 files

📧 Step 4/4: Sending minutes to 2 recipient(s)...
✅ Email sent successfully!

============================================================
📊 PROCESSING COMPLETE
============================================================
Meeting: Sprint Review & Retrospective
Transcript length: 4532 characters
Summary: The team reviewed completed stories, discussed blockers...
Key points: 8
Action items: 5
Files saved: 3
Email sent: ✅ Yes
============================================================
```

---

## API Reference

### FastAPI Endpoints

#### Meeting Management

**POST /join-meeting/**

Join a Google Meet session.

**Request:**
```json
{
  "meetLink": "https://meet.google.com/xxx-xxxx-xxx",
  "meetingId": "optional-custom-id",
  "autoRecord": true
}
```

**Response:**
```json
{
  "status": "success",
  "meetingId": "meeting-20251114-194510",
  "recordingPath": "recordings/meeting-20251114-194510.wav",
  "message": "Joined meeting successfully"
}
```

#### Calendar Management

**GET /calendar/upcoming-meetings/**

Get list of upcoming meetings with Google Meet links.

**Query Parameters:**
- `max_results`: Maximum meetings to return (default: 10)
- `time_min`: Start time (ISO 8601, default: now)
- `time_max`: End time (ISO 8601, default: 24h from now)

**Response:**
```json
{
  "meetings": [
    {
      "id": "event-id-123",
      "summary": "Team Standup",
      "start": "2025-11-14T10:00:00Z",
      "meetLink": "https://meet.google.com/abc-defg-hij"
    }
  ],
  "total": 3
}
```

**POST /calendar/start-monitor/**

Start automatic calendar monitoring.

**Response:**
```json
{
  "status": "started",
  "message": "Calendar monitor started"
}
```

**POST /calendar/stop-monitor/**

Stop automatic calendar monitoring.

**Response:**
```json
{
  "status": "stopped",
  "message": "Calendar monitor stopped"
}
```

**GET /status/**

Get system status.

**Response:**
```json
{
  "status": "running",
  "calendar_monitor_active": true,
  "active_meetings": 1,
  "uptime": "2h 34m",
  "version": "2.0.0"
}
```

### Python API

#### Local LLM Service

```python
from local_llm_service import LocalLLMService

# Initialize with Ollama
llm = LocalLLMService(provider="ollama", model_name="llama3")

# Generate response
response = llm.generate("Summarize this meeting transcript...")

# Automatic fallback to Azure if local LLM fails
```

#### Meeting Minutes Generator

```python
from meeting_minutes_generator import MeetingMinutesGenerator

# Initialize
generator = MeetingMinutesGenerator(
    llm_provider="ollama",
    model_name="mistral"
)

# Generate minutes
minutes = generator.generate_minutes(
    transcript="Meeting transcript text...",
    meeting_title="Q4 Planning",
    meeting_date="2025-11-14"
)

# Save to files
md_path = generator.save_minutes_to_file(minutes)
json_path = generator.save_minutes_to_json(minutes)
```

#### Email Service

```python
from email_service import EmailService

# Initialize
email_service = EmailService(use_gmail_api=False)

# Send minutes
success = email_service.send_meeting_minutes(
    to_emails=["team@company.com"],
    subject="Meeting Minutes: Q4 Planning",
    minutes_markdown=markdown_content,
    minutes_file_path="./storage/minutes/meeting.md"
)
```

---

## File Structure

```
Lumina/
├── README.md                      # This file
├── CLAUDE.md                      # AI assistant instructions
├── SETUP_GUIDE.md                 # Detailed setup guide
├── requirements.txt               # Python dependencies
├── .env                          # Environment configuration
├── .gitignore                    # Git ignore rules
│
├── lumina.py                     # Main FastAPI application
├── calendar_service.py           # Google Calendar integration
├── chrome_manager.py             # Chrome automation
│
├── record_audio.py               # Audio recording
├── record_video.py               # Video recording (optional)
│
├── speech_to_text.py             # Azure STT
├── local_speech_to_text.py       # Local Whisper STT
│
├── local_llm_service.py          # Local LLM abstraction
├── meeting_minutes_generator.py  # Minutes generation
├── email_service.py              # Email delivery
├── process_recording.py          # Complete pipeline script
│
├── blob_storage_service.py       # Azure Blob Storage
├── local_storage_service.py      # Local file storage
│
├── join_meeting_auto.py          # Auto join with bot detection
├── join_meeting_standalone.py    # Standalone Chrome profile join
├── quick_join.py                 # Minimal join script
├── join_current_meeting.py       # Join from calendar
├── join_google_meet.py           # Legacy login-based join
│
├── credentials.json              # Google OAuth credentials (you create)
├── token.pickle                  # Generated after first auth
│
└── storage/                      # Local storage directory
    ├── recordings/               # Meeting audio files
    ├── transcripts/             # Transcription text files
    └── minutes/                 # Meeting minutes (MD + JSON)
```

---

## Advanced Topics

### Bot Detection Prevention

Google Meet implements anti-bot detection. Lumina counters this with:

**Techniques:**
- Randomized mouse movements (every 20-40 seconds)
- Occasional clicks (30% probability)
- Random key presses (20% probability)
- Variable timing patterns

**Implementation:**
```python
def simulate_human_behavior(driver):
    """Simulate human-like interactions"""
    actions = ActionChains(driver)

    # Random mouse movement
    body = driver.find_element(By.TAG_NAME, 'body')
    x_offset = random.randint(-100, 100)
    y_offset = random.randint(-100, 100)
    actions.move_to_element_with_offset(body, x_offset, y_offset).perform()

    # Occasional click
    if random.random() < 0.3:
        actions.click().perform()
```

### Chrome Profile Management

Lumina uses persistent Chrome profiles to avoid repeated authentication.

**Profile Paths:**
- **Linux**: `~/.config/google-chrome`
- **macOS**: `~/Library/Application Support/Google/Chrome`
- **Windows**: `%USERPROFILE%\AppData\Local\Google\Chrome\User Data`

**Profile Detection:**
```bash
# Open Chrome and visit
chrome://version/

# Look for "Profile Path"
# Example: .../Chrome/User Data/Default
#                               ^^^^^^^^ This is the profile name
```

### Storage Strategies

**Local Storage (Privacy-First):**
```python
from local_storage_service import LocalStorageService

storage = LocalStorageService(base_path="./storage")
storage.save_recording("meeting.wav", audio_data)
storage.save_transcript("meeting.txt", transcript)
```

**Azure Blob Storage (Cloud):**
```python
from blob_storage_service import BlobStorageService

storage = BlobStorageService()
storage.upload_file("meeting.wav", container="recordings")
```

### Custom LLM Integration

Extend `LocalLLMService` to add custom providers:

```python
class LocalLLMService:
    def _initialize_custom_provider(self):
        """Add your custom LLM provider"""
        from custom_llm import CustomLLM
        self.llm = CustomLLM(api_key=os.getenv('CUSTOM_API_KEY'))
```

### Transcription Optimization

**GPU Acceleration:**
```bash
# Install CUDA-enabled PyTorch
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Whisper will automatically use GPU
```

**Model Selection:**
```bash
# Fast (development): tiny
WHISPER_MODEL="tiny"

# Balanced (production): base
WHISPER_MODEL="base"

# High-accuracy (archival): large
WHISPER_MODEL="large"
```

### Scheduling and Automation

**Systemd Service (Linux):**

```ini
# /etc/systemd/system/lumina.service
[Unit]
Description=Lumina Meeting Assistant
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/Lumina
ExecStart=/path/to/Lumina/venv/bin/python lumina.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable:**
```bash
sudo systemctl enable lumina
sudo systemctl start lumina
```

---

## Troubleshooting

### Common Issues

#### Chrome Profile Locked

**Error:**
```
selenium.common.exceptions.InvalidArgumentException: invalid argument: user data directory is already in use
```

**Solution:**
1. Close all Chrome windows
2. Kill Chrome processes: `pkill -9 chrome` (Linux)
3. Verify profile name in `.env`: `CHROME_PROFILE_NAME`

#### Calendar API Not Working

**Error:**
```
google.auth.exceptions.RefreshError: ('invalid_grant: Token has been expired or revoked.')
```

**Solution:**
1. Delete `token.pickle`
2. Re-authenticate: `python calendar_service.py`
3. Verify `credentials.json` exists

#### Whisper Out of Memory

**Error:**
```
RuntimeError: CUDA out of memory
```

**Solution:**
1. Use smaller model: `WHISPER_MODEL="tiny"`
2. Reduce audio length
3. Add swap space (Linux): `sudo fallocate -l 4G /swapfile`

#### Ollama Connection Failed

**Error:**
```
ConnectionError: Cannot connect to Ollama server
```

**Solution:**
```bash
# Check if Ollama is running
ollama list

# Start Ollama
ollama serve

# Verify model exists
ollama pull llama3
```

#### Email Not Sending

**Error:**
```
SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')
```

**Solution:**
1. Use Gmail App Password (not account password)
2. Enable 2FA: [Google Security](https://myaccount.google.com/security)
3. Create app password: [App Passwords](https://myaccount.google.com/apppasswords)

#### Meeting Not Auto-Joining

**Checklist:**
- ✅ Lumina running: `python lumina.py`
- ✅ Calendar monitor active: Check logs for "Starting calendar monitor"
- ✅ Meeting has Google Meet link
- ✅ Meeting starts within 2 minutes
- ✅ Chrome is closed before starting Lumina
- ✅ Logged into Chrome profile

### Debug Mode

Enable verbose logging:

```python
# Add to lumina.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

1. Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions
2. Review [CLAUDE.md](CLAUDE.md) for architecture details
3. Search existing GitHub issues
4. Create new issue with:
   - Full error message
   - Python version
   - OS details
   - Steps to reproduce

---

## Performance Optimization

### Recommended System Specs

**Minimum (Cloud Processing):**
- CPU: 2 cores
- RAM: 4 GB
- Disk: 5 GB
- Network: 10 Mbps

**Recommended (Local LLM):**
- CPU: 4+ cores
- RAM: 16 GB
- Disk: 20 GB SSD
- GPU: Optional (8GB VRAM for GPU acceleration)

**Enterprise (High-Volume):**
- CPU: 8+ cores
- RAM: 32 GB
- Disk: 100 GB NVMe SSD
- GPU: NVIDIA RTX 3090 or better

### Benchmarks

**Whisper Transcription Speed (1 hour audio):**
- `tiny` model: ~2 minutes (CPU)
- `base` model: ~5 minutes (CPU)
- `large` model: ~20 minutes (CPU) | ~5 minutes (GPU)

**LLM Analysis Speed (5000 token transcript):**
- Ollama Llama3: ~30 seconds
- LLaMA.cpp Q4: ~45 seconds
- Azure GPT-4: ~10 seconds

---

## Security Considerations

### Data Privacy

- **Local Storage**: All data stays on your machine
- **Local LLM**: No cloud API calls for analysis
- **Encrypted Transit**: HTTPS for all API calls
- **Token Storage**: OAuth tokens stored locally in `token.pickle`

### Best Practices

1. **Never commit credentials**: Use `.env` and `.gitignore`
2. **Rotate API keys**: Regular key rotation policy
3. **Limit OAuth scopes**: Only request needed calendar permissions
4. **Secure storage**: Encrypt recordings at rest (optional)
5. **Access control**: Run Lumina under dedicated user account

### Compliance

- **GDPR**: Local storage option for EU data residency
- **HIPAA**: Not HIPAA-compliant by default (requires encryption)
- **SOC 2**: Use Azure services with SOC 2 certification

---

## Contributing

We welcome contributions! Please follow these guidelines:

### Development Setup

```bash
# Fork repository
git clone https://github.com/your-username/Lumina.git
cd Lumina

# Create branch
git checkout -b feature/your-feature-name

# Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Make changes
# ...

# Run tests
pytest

# Format code
black .
flake8 .

# Commit and push
git add .
git commit -m "feat: add your feature"
git push origin feature/your-feature-name
```

### Contribution Types

- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🎨 UI/UX enhancements
- ⚡️ Performance optimizations
- 🔒 Security patches

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Write tests for new features

---

## Roadmap

### Version 2.1 (Q1 2025)

- [ ] Multi-meeting concurrent recording
- [ ] Speaker diarization (who said what)
- [ ] Real-time transcription display
- [ ] Zoom/Teams integration
- [ ] Mobile app (iOS/Android)

### Version 2.2 (Q2 2025)

- [ ] Custom vocabulary support
- [ ] Translation to multiple languages
- [ ] Meeting analytics dashboard
- [ ] Slack/Discord integration
- [ ] Browser extension

### Version 3.0 (Q3 2025)

- [ ] On-premise deployment
- [ ] Multi-user support
- [ ] Role-based access control
- [ ] Advanced search and retrieval
- [ ] Meeting insights and trends

---

## License

MIT License

Copyright (c) 2024 Lumina Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Acknowledgments

**Core Technologies:**
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [Ollama](https://ollama.ai/) - Local LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Selenium](https://www.selenium.dev/) - Browser automation
- [LangChain](https://langchain.com/) - LLM orchestration

**Inspired By:**
- Meeting automation tools (Otter.ai, Fireflies.ai)
- Open-source AI projects
- Privacy-focused software movement

---

## Contact

**Project Maintainer**: M-Aboelgoud

**Repository**: [https://github.com/M-Aboelgoud/Lumina](https://github.com/M-Aboelgoud/Lumina)

**Issues**: [GitHub Issues](https://github.com/M-Aboelgoud/Lumina/issues)

---

<div align="center">

**Built with ❤️ for meeting productivity**

[⬆ Back to Top](#lumina---ai-powered-meeting-intelligence-platform)

</div>
