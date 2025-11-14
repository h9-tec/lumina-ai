"""Transcription endpoints"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pathlib import Path
from datetime import datetime

router = APIRouter(prefix="/api/transcripts", tags=["transcripts"])

from src.transcription.local_speech_to_text import LocalSpeechToText as SpeechToText


@router.post("/transcribe/{meeting_id}")
async def transcribe_recording(meeting_id: str, background_tasks: BackgroundTasks):
    """Transcribe a specific recording using local Whisper"""
    try:
        recordings_dir = Path(__file__).parent.parent.parent.parent / 'recordings'
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


@router.get("/")
async def list_transcripts():
    """List all available transcripts"""
    try:
        storage_dir = Path(__file__).parent.parent.parent.parent / 'storage' / 'transcripts'
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


@router.get("/{meeting_id}")
async def get_transcript(meeting_id: str):
    """Get the transcript for a specific meeting"""
    try:
        storage_dir = Path(__file__).parent.parent.parent.parent / 'storage' / 'transcripts'
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
