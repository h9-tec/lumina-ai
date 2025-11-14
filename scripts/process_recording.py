"""
Process Recording - Complete pipeline: Audio → Transcript → Minutes → Email
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import whisper

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.intelligence.local_llm_service import LocalLLMService
from src.intelligence.meeting_minutes_generator import MeetingMinutesGenerator
from src.intelligence.email_service import EmailService
from src.transcription.local_storage_service import LocalStorageService


def process_meeting_recording(
    audio_file_path: str,
    meeting_title: str = "Meeting",
    recipient_emails: list = None,
    llm_provider: str = "ollama",
    llm_model: str = "llama3",
    send_email: bool = True,
    save_files: bool = True
):
    """
    Complete pipeline to process meeting recording

    Args:
        audio_file_path: Path to audio recording (.wav, .mp3, etc.)
        meeting_title: Title of the meeting
        recipient_emails: List of emails to send minutes to
        llm_provider: "ollama", "llamacpp", or "azure"
        llm_model: Model name (e.g., "llama3", "mistral")
        send_email: Whether to send email
        save_files: Whether to save files

    Returns:
        Dictionary with paths and status
    """

    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║     🌟 Lumina - Meeting Recording Processor             ║
    ║                                                           ║
    ║     Processing: {meeting_title[:43]:<43}║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    if not Path(audio_file_path).exists():
        print(f"❌ Audio file not found: {audio_file_path}")
        return None

    meeting_date = datetime.now().isoformat()
    results = {
        "audio_file": audio_file_path,
        "meeting_title": meeting_title,
        "meeting_date": meeting_date,
        "transcript": None,
        "minutes": None,
        "files_saved": [],
        "email_sent": False
    }

    try:
        # Step 1: Transcribe audio with Whisper
        print("\n📝 Step 1/4: Transcribing audio with Whisper...")
        transcript = transcribe_audio(audio_file_path)

        if not transcript:
            print("❌ Transcription failed")
            return results

        results["transcript"] = transcript
        print(f"✅ Transcription complete ({len(transcript)} characters)")

        # Save transcript if requested
        if save_files:
            transcript_path = save_transcript(transcript, meeting_title)
            results["files_saved"].append(transcript_path)

        # Step 2: Generate meeting minutes with local LLM
        print(f"\n🤖 Step 2/4: Generating minutes with {llm_provider}...")
        minutes_generator = MeetingMinutesGenerator(
            llm_provider=llm_provider,
            model_name=llm_model
        )

        minutes = minutes_generator.generate_minutes(
            transcript=transcript,
            meeting_title=meeting_title,
            meeting_date=meeting_date
        )

        results["minutes"] = minutes
        print("✅ Minutes generated!")

        # Step 3: Save minutes to files
        if save_files:
            print("\n💾 Step 3/4: Saving minutes to files...")

            # Save markdown
            md_path = minutes_generator.save_minutes_to_file(minutes)
            results["files_saved"].append(md_path)

            # Save JSON
            json_path = minutes_generator.save_minutes_to_json(minutes)
            results["files_saved"].append(json_path)

            print(f"✅ Saved {len(results['files_saved'])} files")
        else:
            print("\n⏭️  Step 3/4: Skipping file save")

        # Step 4: Send email
        if send_email and recipient_emails:
            print(f"\n📧 Step 4/4: Sending minutes to {len(recipient_emails)} recipient(s)...")

            email_service = EmailService(use_gmail_api=False)
            markdown_minutes = minutes_generator._format_as_markdown(minutes)

            success = email_service.send_meeting_minutes(
                to_emails=recipient_emails,
                subject=f"Meeting Minutes: {meeting_title}",
                minutes_markdown=markdown_minutes,
                minutes_file_path=md_path if save_files else None
            )

            results["email_sent"] = success
            if success:
                print("✅ Email sent successfully!")
        else:
            print("\n⏭️  Step 4/4: Skipping email send")

        # Summary
        print("\n" + "="*60)
        print("📊 PROCESSING COMPLETE")
        print("="*60)
        print(f"Meeting: {meeting_title}")
        print(f"Transcript length: {len(transcript)} characters")
        print(f"Summary: {minutes['summary'][:100]}...")
        print(f"Key points: {len(minutes['key_points'])}")
        print(f"Action items: {len(minutes['action_items'])}")
        if save_files:
            print(f"Files saved: {len(results['files_saved'])}")
        if send_email:
            print(f"Email sent: {'✅ Yes' if results['email_sent'] else '❌ No'}")
        print("="*60 + "\n")

        return results

    except Exception as e:
        print(f"❌ Error processing recording: {e}")
        import traceback
        traceback.print_exc()
        return results


def transcribe_audio(audio_file_path: str) -> str:
    """Transcribe audio using local Whisper"""
    try:
        # Load Whisper model
        model_name = os.getenv('WHISPER_MODEL', 'base')
        print(f"   Loading Whisper model: {model_name}")
        model = whisper.load_model(model_name)

        # Transcribe
        print(f"   Transcribing: {Path(audio_file_path).name}")
        result = model.transcribe(audio_file_path, language='en')

        return result['text'].strip()

    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return None


def save_transcript(transcript: str, meeting_title: str) -> str:
    """Save transcript to text file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transcript_{timestamp}.txt"
    output_path = f"./storage/transcripts/{filename}"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {meeting_title}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(transcript)

    print(f"   💾 Transcript saved: {output_path}")
    return output_path


def main():
    """Main entry point for CLI usage"""

    if len(sys.argv) < 2:
        print("""
Usage: python process_recording.py <audio_file> [options]

Arguments:
  audio_file          Path to audio recording file

Options:
  --title            Meeting title (default: "Meeting")
  --email            Recipient email(s), comma-separated
  --llm-provider     LLM provider: ollama, llamacpp, azure (default: ollama)
  --llm-model        Model name (default: llama3)
  --no-email         Don't send email
  --no-save          Don't save files

Examples:
  python process_recording.py recordings/20251114_194510.wav

  python process_recording.py recordings/meeting.wav \\
    --title "Q4 Planning" \\
    --email "team@company.com,manager@company.com" \\
    --llm-provider ollama \\
    --llm-model llama3

  python process_recording.py recordings/meeting.wav \\
    --title "Sprint Review" \\
    --no-email
        """)
        sys.exit(1)

    # Parse arguments
    audio_file = sys.argv[1]
    meeting_title = "Meeting"
    recipient_emails = []
    llm_provider = "ollama"
    llm_model = "llama3"
    send_email = True
    save_files = True

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--title" and i + 1 < len(sys.argv):
            meeting_title = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--email" and i + 1 < len(sys.argv):
            recipient_emails = [e.strip() for e in sys.argv[i + 1].split(',')]
            i += 2
        elif sys.argv[i] == "--llm-provider" and i + 1 < len(sys.argv):
            llm_provider = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--llm-model" and i + 1 < len(sys.argv):
            llm_model = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--no-email":
            send_email = False
            i += 1
        elif sys.argv[i] == "--no-save":
            save_files = False
            i += 1
        else:
            i += 1

    # Process recording
    results = process_meeting_recording(
        audio_file_path=audio_file,
        meeting_title=meeting_title,
        recipient_emails=recipient_emails if send_email else None,
        llm_provider=llm_provider,
        llm_model=llm_model,
        send_email=send_email,
        save_files=save_files
    )

    if results and results["minutes"]:
        print("✅ SUCCESS - Meeting processed successfully!")
    else:
        print("❌ FAILED - Meeting processing incomplete")
        sys.exit(1)


if __name__ == "__main__":
    main()
