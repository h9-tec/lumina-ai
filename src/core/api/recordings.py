"""Recording management endpoints"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
from datetime import datetime

router = APIRouter(prefix="/api/recordings", tags=["recordings"])


@router.get("/")
async def list_recordings():
    """List all available recordings"""
    try:
        recordings_dir = Path(__file__).parent.parent.parent.parent / 'recordings'
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


@router.get("/{meeting_id}")
async def get_recording(meeting_id: str):
    """Get information about a specific recording"""
    try:
        recordings_dir = Path(__file__).parent.parent.parent.parent / 'recordings'
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


@router.delete("/{meeting_id}")
async def delete_recording(meeting_id: str):
    """Delete a recording"""
    try:
        recordings_dir = Path(__file__).parent.parent.parent.parent / 'recordings'
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
