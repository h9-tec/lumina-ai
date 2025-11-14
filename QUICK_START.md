# Lumina Quick Start Guide (Local Version)

## What's Different Now?

✅ **Local Whisper** - Transcription runs on your machine (no Azure Whisper API needed)
✅ **Local Storage** - All recordings saved to your local `./storage` folder
✅ **Azure GPT-4** - Uses provided Azure credentials for meeting analysis
✅ **Google Calendar** - Uses your existing credentials file

## Prerequisites

Make sure you have:
- Python 3.8+
- Chrome browser (logged into your Google account)
- FFmpeg installed (for audio processing)
- At least 2GB free disk space (for Whisper model)

### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH

## Step 1: Install Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install all dependencies (this will download Whisper model on first run)
pip install -r requirements.txt
```

**Note:** This will download PyTorch and Whisper models. First installation may take 5-10 minutes.

## Step 2: Set Up Your Environment

Create a `.env` file (or copy from `.env.example`):

```bash
# Chrome Profile
CHROME_PROFILE_NAME="Default"

# Auto-start calendar monitor
AUTO_START_CALENDAR_MONITOR="true"

# Local Storage Path
LOCAL_STORAGE_PATH="./storage"

# Whisper Model (base is recommended for speed/accuracy balance)
WHISPER_MODEL="base"
```

**Whisper Model Options:**
- `tiny` - Fastest, least accurate
- `base` - **Recommended** - Good balance
- `small` - Better accuracy, slower
- `medium` - Even better, much slower
- `large` - Best accuracy, very slow

## Step 3: Authenticate with Google Calendar

Your credentials file is already in the directory:
`client_secret_966764886522-8ch0p4ln423ktj2eb9c08s5p15eigr8g.apps.googleusercontent.com.json`

Now authenticate:

```bash
python calendar_service.py
```

This will:
1. Open your browser
2. Ask you to log in to Google
3. Request calendar read permission
4. Create `token.pickle` for future use

## Step 4: Test Local Transcription (Optional)

Test that Whisper is working:

```bash
# This will download the model on first run
python local_speech_to_text.py <path-to-audio-file.wav>
```

On first run, Whisper will download the model (~140MB for base model).

## Step 5: Run Lumina!

```bash
python lumina.py
```

You should see:
```
✨ Lumina - Meeting Assistant ✨

Loading local Whisper model...
Whisper model 'base' loaded successfully
Azure GPT-4 initialized for analysis
Local storage initialized at: /path/to/storage

🔍 Starting calendar monitor...
Lumina will automatically join Google Meet sessions from your calendar
```

## What Happens Now?

1. **Lumina monitors your calendar** every minute
2. **Auto-joins meetings** 1-2 minutes before they start
3. **Records audio** using local Whisper
4. **Transcribes locally** (no cloud API calls for transcription)
5. **Analyzes with Azure GPT-4** (summary, key points, actions, sentiment)
6. **Saves everything locally** to `./storage/`

## Storage Structure

```
storage/
├── recordings/          # Audio files (.wav)
├── transcripts/         # Transcription text files
└── analysis/           # Meeting analysis JSON files
```

## API Endpoints

While Lumina is running, you can use these endpoints:

**Manual join:**
```bash
curl -X POST "http://localhost:8000/join-meeting/" \
  -H "Content-Type: application/json" \
  -d '{"meetLink": "https://meet.google.com/xxx-xxxx-xxx"}'
```

**Check upcoming meetings:**
```bash
curl http://localhost:8000/calendar/upcoming-meetings/
```

**Check status:**
```bash
curl http://localhost:8000/status/
```

**View storage info:**
```bash
curl http://localhost:8000/storage/info/
```

## Troubleshooting

### "No module named 'whisper'"
Run: `pip install openai-whisper`

### "FFmpeg not found"
Install FFmpeg (see Prerequisites section above)

### "Chrome profile locked"
Close ALL Chrome windows before starting Lumina

### Whisper is slow
- Use a smaller model: `WHISPER_MODEL="tiny"` or `WHISPER_MODEL="base"`
- Consider GPU acceleration (install PyTorch with CUDA)

### Out of memory
- Use a smaller Whisper model
- The `base` model uses ~1GB RAM
- The `large` model uses ~10GB RAM

## Performance Notes

**Transcription Speed (base model on CPU):**
- 1 minute of audio ≈ 10-15 seconds to transcribe
- 30 minute meeting ≈ 5-7 minutes to transcribe

**GPU Acceleration:**
If you have an NVIDIA GPU, install PyTorch with CUDA:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

This can make transcription 5-10x faster!

## What's Hardcoded

The Azure GPT-4 configuration is hardcoded in `local_speech_to_text.py`:
- Model: `gpt-4-32k`
- API Version: `2024-08-01-preview`
- API Key: `161a11270d03448fb67e707c12005909`
- Endpoint: `https://prodnancyazure3277074411.openai.azure.com/`

If you need to change these, edit `local_speech_to_text.py`.

## Next Steps

1. Add meetings to your Google Calendar with Meet links
2. Let Lumina run in the background
3. Check `./storage/` for your recordings and analysis
4. Review meeting transcripts and insights

Enjoy! 🌟
