"""Meeting minutes endpoints"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from datetime import datetime
import os
import json

router = APIRouter(prefix="/api/minutes", tags=["minutes"])

from src.intelligence.meeting_minutes_generator import MeetingMinutesGenerator
from src.intelligence.email_service import EmailService


class EmailRequest(BaseModel):
    """Request model for sending email"""
    recipients: list[str]
    subject: Optional[str] = None


@router.post("/generate/{meeting_id}")
async def generate_minutes(meeting_id: str, background_tasks: BackgroundTasks):
    """Generate meeting minutes from transcript using local LLM"""
    try:
        storage_dir = Path(__file__).parent.parent.parent.parent / 'storage' / 'transcripts'
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


@router.get("/")
async def list_minutes():
    """List all available meeting minutes"""
    try:
        storage_dir = Path(__file__).parent.parent.parent.parent / 'storage' / 'minutes'
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


@router.get("/{meeting_id}")
async def get_minutes(meeting_id: str, format: str = "markdown"):
    """Get meeting minutes for a specific meeting (markdown or json)"""
    try:
        storage_dir = Path(__file__).parent.parent.parent.parent / 'storage' / 'minutes'

        if format == "json":
            minutes_file = storage_dir / f"meeting_minutes_{meeting_id}.json"
            if not minutes_file.exists():
                raise HTTPException(status_code=404, detail="Meeting minutes (JSON) not found")

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


@router.post("/email/{meeting_id}")
async def email_minutes(meeting_id: str, request: EmailRequest):
    """Send meeting minutes via email"""
    try:
        storage_dir = Path(__file__).parent.parent.parent.parent / 'storage' / 'minutes'
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


@router.post("/process/{meeting_id}")
async def process_complete_pipeline(meeting_id: str, background_tasks: BackgroundTasks):
    """
    Complete processing pipeline: Transcribe → Generate Minutes → Send Email
    """
    try:
        recordings_dir = Path(__file__).parent.parent.parent.parent / 'recordings'
        audio_file = recordings_dir / f"{meeting_id}.wav"

        if not audio_file.exists():
            raise HTTPException(status_code=404, detail="Recording not found")

        from src.transcription.local_speech_to_text import LocalSpeechToText as SpeechToText

        def complete_pipeline():
            try:
                print(f"[Pipeline] Step 1: Transcribing {meeting_id}...")
                stt = SpeechToText()
                result = stt.transcribe(str(audio_file), meeting_id=meeting_id)
                transcript = result.get('text', '')

                if not transcript:
                    print("[Pipeline] No transcript generated, aborting")
                    return

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
                    print("[Pipeline] Email sent!")

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
