#!/usr/bin/env python3
"""
Lumina CLI - Command-line interface for developers
"""
import sys
import click
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()


@click.group()
@click.version_option(version="2.0.0", prog_name="Lumina CLI")
def cli():
    """
    Lumina CLI - AI-Powered Meeting Assistant

    Manage recordings, transcriptions, and meeting minutes from the command line.
    """
    pass


# ============================================
# SERVER COMMANDS
# ============================================

@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind')
@click.option('--port', default=8000, help='Port to bind')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
def server(host, port, reload):
    """Start the Lumina FastAPI server"""
    import uvicorn
    click.echo(f"🚀 Starting Lumina server on {host}:{port}")
    uvicorn.run("src.core.lumina:app", host=host, port=port, reload=reload)


# ============================================
# RECORDING COMMANDS
# ============================================

@cli.group()
def recordings():
    """Manage audio recordings"""
    pass


@recordings.command('list')
@click.option('--format', type=click.Choice(['table', 'json']), default='table')
def list_recordings(format):
    """List all available recordings"""
    from datetime import datetime
    import json

    recordings_dir = Path('recordings')

    if not recordings_dir.exists():
        click.echo("No recordings directory found")
        return

    recordings = []
    for audio_file in recordings_dir.glob("*.wav"):
        file_stats = audio_file.stat()
        recordings.append({
            "Meeting ID": audio_file.stem,
            "Filename": audio_file.name,
            "Size (MB)": round(file_stats.st_size / (1024 * 1024), 2),
            "Created": datetime.fromtimestamp(file_stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
        })

    if format == 'json':
        click.echo(json.dumps(recordings, indent=2))
    else:
        if not recordings:
            click.echo("No recordings found")
            return

        click.echo(f"\n📊 Found {len(recordings)} recordings:\n")
        for rec in recordings:
            click.echo(f"  • {rec['Meeting ID']}")
            click.echo(f"    Size: {rec['Size (MB)']} MB | Created: {rec['Created']}\n")


@recordings.command('info')
@click.argument('meeting_id')
def recording_info(meeting_id):
    """Get information about a specific recording"""
    from datetime import datetime

    recordings_dir = Path('recordings')
    audio_file = recordings_dir / f"{meeting_id}.wav"

    if not audio_file.exists():
        click.secho(f"❌ Recording '{meeting_id}' not found", fg='red')
        return

    file_stats = audio_file.stat()

    click.echo(f"\n📁 Recording Information:")
    click.echo(f"  Meeting ID: {meeting_id}")
    click.echo(f"  Filename: {audio_file.name}")
    click.echo(f"  Path: {audio_file.absolute()}")
    click.echo(f"  Size: {round(file_stats.st_size / (1024 * 1024), 2)} MB")
    click.echo(f"  Created: {datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}")


@recordings.command('delete')
@click.argument('meeting_id')
@click.confirmation_option(prompt='Are you sure you want to delete this recording?')
def delete_recording(meeting_id):
    """Delete a recording"""
    recordings_dir = Path('recordings')
    audio_file = recordings_dir / f"{meeting_id}.wav"

    if not audio_file.exists():
        click.secho(f"❌ Recording '{meeting_id}' not found", fg='red')
        return

    audio_file.unlink()
    click.secho(f"✅ Deleted recording: {meeting_id}", fg='green')


# ============================================
# TRANSCRIPTION COMMANDS
# ============================================

@cli.group()
def transcribe():
    """Transcription operations"""
    pass


@transcribe.command('start')
@click.argument('meeting_id')
@click.option('--model', default='base', help='Whisper model: tiny, base, small, medium, large')
def transcribe_recording(meeting_id, model):
    """Transcribe a recording using Whisper"""
    recordings_dir = Path('recordings')
    audio_file = recordings_dir / f"{meeting_id}.wav"

    if not audio_file.exists():
        click.secho(f"❌ Recording '{meeting_id}' not found", fg='red')
        return

    click.echo(f"🎙️  Transcribing {meeting_id} using Whisper model '{model}'...")

    from src.transcription.local_speech_to_text import LocalSpeechToText as SpeechToText
    import os
    os.environ['WHISPER_MODEL'] = model

    try:
        stt = SpeechToText()
        result = stt.transcribe(str(audio_file), meeting_id=meeting_id)

        click.secho(f"✅ Transcription complete!", fg='green')
        click.echo(f"  Transcript saved to: storage/transcripts/transcript_{meeting_id}.txt")

        if result.get('text'):
            click.echo(f"\n📝 Preview (first 200 chars):")
            click.echo(f"  {result['text'][:200]}...")

    except Exception as e:
        click.secho(f"❌ Error: {e}", fg='red')


@transcribe.command('list')
def list_transcripts():
    """List all transcripts"""
    storage_dir = Path('storage/transcripts')

    if not storage_dir.exists():
        click.echo("No transcripts found")
        return

    transcripts = list(storage_dir.glob("transcript_*.txt"))

    if not transcripts:
        click.echo("No transcripts found")
        return

    click.echo(f"\n📝 Found {len(transcripts)} transcripts:\n")
    for transcript_file in transcripts:
        meeting_id = transcript_file.stem.replace("transcript_", "")
        file_stats = transcript_file.stat()
        click.echo(f"  • {meeting_id}")
        click.echo(f"    Size: {round(file_stats.st_size / 1024, 2)} KB\n")


@transcribe.command('show')
@click.argument('meeting_id')
@click.option('--lines', default=50, help='Number of lines to show')
def show_transcript(meeting_id, lines):
    """Show transcript content"""
    storage_dir = Path('storage/transcripts')
    transcript_file = storage_dir / f"transcript_{meeting_id}.txt"

    if not transcript_file.exists():
        click.secho(f"❌ Transcript '{meeting_id}' not found", fg='red')
        return

    content = transcript_file.read_text(encoding='utf-8')
    content_lines = content.split('\n')

    click.echo(f"\n📝 Transcript: {meeting_id}")
    click.echo(f"  Total lines: {len(content_lines)}\n")
    click.echo("─" * 80)

    for line in content_lines[:lines]:
        click.echo(line)

    if len(content_lines) > lines:
        click.echo(f"\n... ({len(content_lines) - lines} more lines)")


# ============================================
# MEETING MINUTES COMMANDS
# ============================================

@cli.group()
def minutes():
    """Meeting minutes operations"""
    pass


@minutes.command('generate')
@click.argument('meeting_id')
@click.option('--provider', default='ollama', help='LLM provider: ollama, llamacpp, azure')
@click.option('--model', default='llama3', help='Model name')
def generate_minutes(meeting_id, provider, model):
    """Generate meeting minutes from transcript"""
    storage_dir = Path('storage/transcripts')
    transcript_file = storage_dir / f"transcript_{meeting_id}.txt"

    if not transcript_file.exists():
        click.secho(f"❌ Transcript '{meeting_id}' not found. Run transcription first.", fg='red')
        return

    click.echo(f"🧠 Generating meeting minutes using {provider}/{model}...")

    from src.intelligence.meeting_minutes_generator import MeetingMinutesGenerator
    from datetime import datetime

    try:
        transcript_text = transcript_file.read_text(encoding='utf-8')

        generator = MeetingMinutesGenerator(
            llm_provider=provider,
            model_name=model
        )

        meeting_date = datetime.now().strftime("%Y-%m-%d")
        minutes_data = generator.generate_minutes(
            transcript=transcript_text,
            meeting_title=f"Meeting {meeting_id}",
            meeting_date=meeting_date
        )

        md_path = generator.save_minutes_to_file(minutes_data)
        json_path = generator.save_minutes_to_json(minutes_data)

        click.secho(f"✅ Meeting minutes generated!", fg='green')
        click.echo(f"  Markdown: {md_path}")
        click.echo(f"  JSON: {json_path}")

    except Exception as e:
        click.secho(f"❌ Error: {e}", fg='red')


@minutes.command('list')
def list_minutes():
    """List all meeting minutes"""
    storage_dir = Path('storage/minutes')

    if not storage_dir.exists():
        click.echo("No meeting minutes found")
        return

    minutes_files = list(storage_dir.glob("meeting_minutes_*.md"))

    if not minutes_files:
        click.echo("No meeting minutes found")
        return

    click.echo(f"\n📋 Found {len(minutes_files)} meeting minutes:\n")
    for minutes_file in minutes_files:
        meeting_id = minutes_file.stem.replace("meeting_minutes_", "")
        file_stats = minutes_file.stat()
        click.echo(f"  • {meeting_id}")
        click.echo(f"    Size: {round(file_stats.st_size / 1024, 2)} KB\n")


@minutes.command('show')
@click.argument('meeting_id')
@click.option('--format', type=click.Choice(['markdown', 'json']), default='markdown')
def show_minutes(meeting_id, format):
    """Show meeting minutes content"""
    storage_dir = Path('storage/minutes')

    if format == 'json':
        minutes_file = storage_dir / f"meeting_minutes_{meeting_id}.json"
    else:
        minutes_file = storage_dir / f"meeting_minutes_{meeting_id}.md"

    if not minutes_file.exists():
        click.secho(f"❌ Meeting minutes '{meeting_id}' ({format}) not found", fg='red')
        return

    content = minutes_file.read_text(encoding='utf-8')

    click.echo(f"\n📋 Meeting Minutes: {meeting_id}\n")
    click.echo("─" * 80)
    click.echo(content)


@minutes.command('email')
@click.argument('meeting_id')
@click.argument('recipients', nargs=-1, required=True)
@click.option('--subject', help='Email subject')
def email_minutes(meeting_id, recipients, subject):
    """Email meeting minutes to recipients"""
    storage_dir = Path('storage/minutes')
    md_file = storage_dir / f"meeting_minutes_{meeting_id}.md"

    if not md_file.exists():
        click.secho(f"❌ Meeting minutes '{meeting_id}' not found", fg='red')
        return

    click.echo(f"📧 Sending meeting minutes to {len(recipients)} recipients...")

    from src.intelligence.email_service import EmailService

    try:
        minutes_markdown = md_file.read_text(encoding='utf-8')
        email_service = EmailService()

        subject = subject or f"Meeting Minutes: {meeting_id}"

        email_service.send_meeting_minutes(
            to_emails=list(recipients),
            subject=subject,
            minutes_markdown=minutes_markdown,
            minutes_file_path=str(md_file)
        )

        click.secho(f"✅ Email sent to: {', '.join(recipients)}", fg='green')

    except Exception as e:
        click.secho(f"❌ Error: {e}", fg='red')


# ============================================
# PIPELINE COMMAND
# ============================================

@cli.command()
@click.argument('meeting_id')
@click.option('--skip-transcribe', is_flag=True, help='Skip transcription step')
@click.option('--skip-minutes', is_flag=True, help='Skip minutes generation')
@click.option('--skip-email', is_flag=True, help='Skip email sending')
@click.option('--provider', default='ollama', help='LLM provider')
@click.option('--model', default='llama3', help='LLM model')
def process(meeting_id, skip_transcribe, skip_minutes, skip_email, provider, model):
    """Process a recording through the complete pipeline"""
    recordings_dir = Path('recordings')
    audio_file = recordings_dir / f"{meeting_id}.wav"

    if not audio_file.exists():
        click.secho(f"❌ Recording '{meeting_id}' not found", fg='red')
        return

    click.echo(f"\n🚀 Processing pipeline for: {meeting_id}\n")

    # Step 1: Transcribe
    transcript_text = None
    if not skip_transcribe:
        click.echo("📝 Step 1/3: Transcribing...")
        from src.transcription.local_speech_to_text import LocalSpeechToText as SpeechToText

        try:
            stt = SpeechToText()
            result = stt.transcribe(str(audio_file), meeting_id=meeting_id)
            transcript_text = result.get('text', '')
            click.secho("  ✅ Transcription complete", fg='green')
        except Exception as e:
            click.secho(f"  ❌ Transcription failed: {e}", fg='red')
            return
    else:
        # Load existing transcript
        storage_dir = Path('storage/transcripts')
        transcript_file = storage_dir / f"transcript_{meeting_id}.txt"
        if transcript_file.exists():
            transcript_text = transcript_file.read_text(encoding='utf-8')
            click.echo("📝 Step 1/3: Using existing transcript")
        else:
            click.secho("  ❌ No transcript found. Remove --skip-transcribe flag.", fg='red')
            return

    # Step 2: Generate Minutes
    md_path = None
    if not skip_minutes and transcript_text:
        click.echo("\n🧠 Step 2/3: Generating meeting minutes...")
        from src.intelligence.meeting_minutes_generator import MeetingMinutesGenerator
        from datetime import datetime

        try:
            generator = MeetingMinutesGenerator(
                llm_provider=provider,
                model_name=model
            )

            meeting_date = datetime.now().strftime("%Y-%m-%d")
            minutes_data = generator.generate_minutes(
                transcript=transcript_text,
                meeting_title=f"Meeting {meeting_id}",
                meeting_date=meeting_date
            )

            md_path = generator.save_minutes_to_file(minutes_data)
            generator.save_minutes_to_json(minutes_data)
            click.secho("  ✅ Minutes generated", fg='green')
        except Exception as e:
            click.secho(f"  ❌ Minutes generation failed: {e}", fg='red')
            return
    else:
        # Load existing minutes
        storage_dir = Path('storage/minutes')
        md_path = storage_dir / f"meeting_minutes_{meeting_id}.md"
        if md_path.exists():
            click.echo("\n🧠 Step 2/3: Using existing minutes")
        else:
            click.echo("\n🧠 Step 2/3: Skipped (--skip-minutes)")

    # Step 3: Send Email
    if not skip_email and md_path and md_path.exists():
        click.echo("\n📧 Step 3/3: Sending email...")
        import os
        smtp_user = os.getenv('SMTP_USER', '')

        if not smtp_user:
            click.secho("  ⚠️  SMTP not configured, skipping email", fg='yellow')
        else:
            from src.intelligence.email_service import EmailService

            try:
                minutes_markdown = md_path.read_text(encoding='utf-8')
                email_service = EmailService()

                email_service.send_meeting_minutes(
                    to_emails=[smtp_user],
                    subject=f"Meeting Minutes: {meeting_id}",
                    minutes_markdown=minutes_markdown,
                    minutes_file_path=str(md_path)
                )
                click.secho("  ✅ Email sent", fg='green')
            except Exception as e:
                click.secho(f"  ❌ Email failed: {e}", fg='red')
    else:
        click.echo("\n📧 Step 3/3: Skipped (--skip-email or no minutes)")

    click.echo("\n✨ Pipeline complete!")


# ============================================
# CONFIG COMMANDS
# ============================================

@cli.command()
def config():
    """Show current configuration"""
    import os

    click.echo("\n⚙️  Lumina Configuration:\n")

    click.echo("🧠 LLM:")
    click.echo(f"  Provider: {os.getenv('LOCAL_LLM_PROVIDER', 'ollama')}")
    click.echo(f"  Model: {os.getenv('LOCAL_LLM_MODEL', 'llama3')}\n")

    click.echo("🎙️  Whisper:")
    click.echo(f"  Model: {os.getenv('WHISPER_MODEL', 'base')}\n")

    click.echo("📧 Email:")
    smtp_user = os.getenv('SMTP_USER', '')
    click.echo(f"  Configured: {('✅' if smtp_user else '❌')}")
    if smtp_user:
        click.echo(f"  Server: {os.getenv('SMTP_SERVER', 'smtp.gmail.com')}")
        click.echo(f"  User: {smtp_user}\n")

    click.echo("🗓️  Calendar:")
    click.echo(f"  Auto-start: {os.getenv('AUTO_START_CALENDAR_MONITOR', 'true')}\n")

    click.echo("🌐 Chrome:")
    click.echo(f"  Profile: {os.getenv('CHROME_PROFILE_NAME', 'Default')}\n")


if __name__ == '__main__':
    cli()
