# Lumina Setup Guide

Complete guide for setting up Lumina's local LLM and meeting minutes features.

## Table of Contents

1. [Local LLM Setup](#local-llm-setup)
2. [Email Configuration](#email-configuration)
3. [Processing Recordings](#processing-recordings)
4. [Configuration Options](#configuration-options)
5. [Troubleshooting](#troubleshooting)

---

## Local LLM Setup

Lumina supports three LLM providers:
- **Ollama** (Recommended) - Easy setup, runs locally
- **LLaMA.cpp** - Direct GGUF model loading
- **Azure GPT-4** - Cloud fallback (already configured)

### Option 1: Ollama (Recommended)

**1. Install Ollama**

```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

**2. Pull a Model**

```bash
# Recommended models:
ollama pull llama3          # Best balance (4.7GB)
ollama pull llama3:70b      # Most powerful (40GB)
ollama pull mistral         # Fast and efficient (4.1GB)
ollama pull phi3            # Lightweight (2.3GB)
```

**3. Test Ollama**

```bash
ollama run llama3
# Type a message to test, then /bye to exit
```

**4. Configure in .env**

```bash
LOCAL_LLM_PROVIDER="ollama"
LOCAL_LLM_MODEL="llama3"
```

### Option 2: LLaMA.cpp (Advanced)

**1. Download a GGUF Model**

Download from Hugging Face:
- [Llama 3 GGUF](https://huggingface.co/models?search=llama-3-gguf)
- [Mistral GGUF](https://huggingface.co/models?search=mistral-gguf)

Example:
```bash
wget https://huggingface.co/TheBloke/Llama-3-8B-Instruct-GGUF/resolve/main/llama-3-8b-instruct.Q4_K_M.gguf -O ~/models/llama3.gguf
```

**2. Configure in .env**

```bash
LOCAL_LLM_PROVIDER="llamacpp"
LLAMACPP_MODEL_PATH="/home/hesham/models/llama3.gguf"
```

### Option 3: Azure GPT-4 (Already Configured)

No setup needed! Azure GPT-4 is already configured and will be used as automatic fallback if local LLMs fail.

```bash
LOCAL_LLM_PROVIDER="azure"
```

---

## Email Configuration

Configure email to automatically send meeting minutes after each meeting.

### Gmail Setup (Recommended)

**1. Enable 2-Factor Authentication**

Go to [Google Account Security](https://myaccount.google.com/security)

**2. Create App Password**

1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select "Mail" and your device
3. Copy the 16-character password

**3. Configure in .env**

```bash
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-16-char-app-password"
```

### Other Email Providers

**Outlook/Office 365:**
```bash
SMTP_SERVER="smtp.office365.com"
SMTP_PORT="587"
SMTP_USER="your-email@outlook.com"
SMTP_PASSWORD="your-password"
```

**Custom SMTP:**
```bash
SMTP_SERVER="smtp.yourdomain.com"
SMTP_PORT="587"
SMTP_USER="your-email@yourdomain.com"
SMTP_PASSWORD="your-password"
```

---

## Processing Recordings

Lumina provides a complete pipeline: Audio → Transcript → Minutes → Email

### Basic Usage

```bash
python process_recording.py recordings/20251114_194510.wav
```

This will:
1. Transcribe audio using Whisper
2. Generate meeting minutes using local LLM
3. Save transcript and minutes to `./storage/`
4. Send email (if configured)

### Advanced Usage

**Custom Meeting Title:**
```bash
python process_recording.py recordings/meeting.wav \
  --title "Q4 Planning Meeting"
```

**Send to Multiple Recipients:**
```bash
python process_recording.py recordings/meeting.wav \
  --title "Team Standup" \
  --email "team@company.com,manager@company.com,cto@company.com"
```

**Use Specific LLM Provider:**
```bash
# Use Ollama with Mistral
python process_recording.py recordings/meeting.wav \
  --llm-provider ollama \
  --llm-model mistral

# Use LLaMA.cpp
python process_recording.py recordings/meeting.wav \
  --llm-provider llamacpp

# Use Azure GPT-4
python process_recording.py recordings/meeting.wav \
  --llm-provider azure
```

**Skip Email:**
```bash
python process_recording.py recordings/meeting.wav \
  --no-email
```

**Skip File Saving:**
```bash
python process_recording.py recordings/meeting.wav \
  --no-save
```

### Complete Example

```bash
python process_recording.py recordings/team_meeting.wav \
  --title "Sprint Review & Planning" \
  --email "dev-team@company.com,product@company.com" \
  --llm-provider ollama \
  --llm-model llama3
```

---

## Configuration Options

### Complete .env Example

```bash
# ============================================
# Chrome Profile
# ============================================
CHROME_PROFILE_NAME="Default"

# ============================================
# Auto-start Calendar Monitor
# ============================================
AUTO_START_CALENDAR_MONITOR="true"

# ============================================
# Local Storage Path
# ============================================
LOCAL_STORAGE_PATH="./storage"

# ============================================
# Whisper Model
# ============================================
# Options: tiny, base, small, medium, large
WHISPER_MODEL="base"

# ============================================
# Local LLM Settings
# ============================================
LOCAL_LLM_PROVIDER="ollama"  # Options: ollama, llamacpp, azure
LOCAL_LLM_MODEL="llama3"     # For Ollama: llama3, mistral, phi3, etc.
# For LLaMA.cpp, set path to GGUF file:
# LLAMACPP_MODEL_PATH="/path/to/model.gguf"

# ============================================
# Azure OpenAI (Fallback)
# ============================================
OPENAI_API_KEY="161a11270d03448fb67e707c12005909"
API_VERSION="2024-08-01-preview"
AZURE_OPENAI_ENDPOINT="https://prodnancyazure3277074411.openai.azure.com/"

# ============================================
# Email Settings (for sending meeting minutes)
# ============================================
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER=""  # Your email address
SMTP_PASSWORD=""  # Your app password (not regular password!)
# Get Gmail app password: https://myaccount.google.com/apppasswords
```

### Whisper Model Comparison

| Model  | Size   | Speed      | Accuracy   | Recommended For        |
|--------|--------|------------|------------|------------------------|
| tiny   | 39 MB  | Very Fast  | Basic      | Quick tests            |
| base   | 74 MB  | Fast       | Good       | Most meetings (default)|
| small  | 244 MB | Medium     | Better     | Important meetings     |
| medium | 769 MB | Slow       | High       | Critical transcription |
| large  | 1.5 GB | Very Slow  | Best       | Professional use       |

### Ollama Model Comparison

| Model      | Size   | Speed  | Quality | Best For                |
|------------|--------|--------|---------|-------------------------|
| phi3       | 2.3 GB | Fast   | Good    | Quick summaries         |
| mistral    | 4.1 GB | Fast   | Great   | General use             |
| llama3     | 4.7 GB | Medium | Great   | Balanced (recommended)  |
| llama3:70b | 40 GB  | Slow   | Best    | Highest quality minutes |

---

## Troubleshooting

### Issue: "Ollama not found"

**Solution:**
```bash
# Check if Ollama is running
ollama list

# Start Ollama service (if not running)
ollama serve
```

### Issue: "Model not found"

**Solution:**
```bash
# Pull the model you want to use
ollama pull llama3

# List available models
ollama list
```

### Issue: "Email not sending"

**Solution:**
1. Verify SMTP credentials in .env
2. For Gmail, ensure you're using App Password, not regular password
3. Check if 2FA is enabled on your Google account
4. Test with a simple email first

### Issue: "LLaMA.cpp model not loading"

**Solution:**
1. Verify model file exists at specified path
2. Ensure model is in GGUF format (not PyTorch .bin)
3. Check model file is not corrupted:
   ```bash
   ls -lh /path/to/model.gguf
   ```

### Issue: "Out of memory"

**Solution:**
1. Use smaller Whisper model: `WHISPER_MODEL="base"`
2. Use smaller LLM: `ollama pull phi3`
3. Use Azure fallback: `LOCAL_LLM_PROVIDER="azure"`

### Issue: "Transcription is slow"

**Solution:**
1. Use faster Whisper model: `WHISPER_MODEL="tiny"` or `base`
2. Enable GPU acceleration (if available):
   ```bash
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

### Issue: "Minutes quality is poor"

**Solution:**
1. Use better Whisper model: `WHISPER_MODEL="medium"`
2. Use better LLM:
   ```bash
   ollama pull llama3:70b
   LOCAL_LLM_MODEL="llama3:70b"
   ```
3. Or use Azure GPT-4: `LOCAL_LLM_PROVIDER="azure"`

---

## Testing the Pipeline

**Test Whisper Only:**
```bash
python -c "
import whisper
model = whisper.load_model('base')
result = model.transcribe('recordings/test.wav')
print(result['text'])
"
```

**Test Local LLM Only:**
```bash
python local_llm_service.py
```

**Test Meeting Minutes Generator:**
```bash
python meeting_minutes_generator.py
```

**Test Email Service:**
```bash
python email_service.py
```

**Test Complete Pipeline:**
```bash
# Create a test recording first, then:
python process_recording.py recordings/test.wav \
  --title "Test Meeting" \
  --no-email
```

---

## File Outputs

All files are saved to `./storage/` directory:

```
storage/
├── transcripts/
│   └── transcript_20251114_194510.txt
├── minutes/
│   ├── meeting_minutes_20251114_194510.md
│   └── meeting_minutes_20251114_194510.json
└── recordings/
    └── 20251114_194510.wav
```

**Markdown Format (.md):**
```markdown
# Q4 Planning Meeting

**Date:** 2025-11-14

---

## Summary

Discussed Q4 roadmap and decided to prioritize mobile app launch...

---

## Key Points & Decisions

- Mobile app launch prioritized for Q4
- Target date: November 15th for beta release
- Marketing budget: $50k approved

---

## Action Items

- [ ] Backend API updates (Owner: Mike) - Due: Nov 1st
- [ ] UI coordination with design team (Owner: Sarah)
```

**JSON Format (.json):**
```json
{
  "meeting_title": "Q4 Planning Meeting",
  "date": "2025-11-14",
  "summary": "Discussed Q4 roadmap...",
  "key_points": [
    "Mobile app launch prioritized for Q4",
    "Target date: November 15th for beta release"
  ],
  "action_items": [
    "Backend API updates (Owner: Mike) - Due: Nov 1st",
    "UI coordination with design team (Owner: Sarah)"
  ]
}
```

---

## Next Steps

1. **Install Ollama:** `curl -fsSL https://ollama.com/install.sh | sh`
2. **Pull a model:** `ollama pull llama3`
3. **Configure email:** Add SMTP credentials to .env
4. **Test the pipeline:** Process a test recording
5. **Join a meeting:** Let Lumina record and process automatically

For questions or issues, check the main [README.md](README.md) or [CLAUDE.md](CLAUDE.md).
