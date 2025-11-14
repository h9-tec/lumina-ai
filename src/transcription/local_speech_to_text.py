"""
Local Speech to Text - Uses local Whisper model and Azure GPT-4 for analysis
"""
import whisper
import json
import os
import subprocess
import tempfile
import datetime
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from local_storage_service import LocalStorageService

load_dotenv()


class LocalSpeechToText:
    def __init__(self):
        """Initialize with local Whisper and Azure GPT-4"""
        # Load local Whisper model
        print("Loading local Whisper model...")
        whisper_model = os.getenv('WHISPER_MODEL', 'base')  # base, small, medium, large
        self.whisper_model = whisper.load_model(whisper_model)
        print(f"Whisper model '{whisper_model}' loaded successfully")

        # Initialize Azure GPT-4 for analysis
        self.llm = AzureChatOpenAI(
            model="gpt-4-32k",
            api_version="2024-08-01-preview",
            api_key="161a11270d03448fb67e707c12005909",
            azure_endpoint="https://prodnancyazure3277074411.openai.azure.com/",
            temperature=0
        )
        print("Azure GPT-4 initialized for analysis")

        # Initialize local storage
        self.storage = LocalStorageService()

        self.MAX_AUDIO_SIZE_BYTES = 500 * 1024 * 1024  # 500MB for local processing

    def get_file_size(self, file_path):
        """Get file size in bytes"""
        return os.path.getsize(file_path)

    def get_audio_duration(self, audio_file_path):
        """Get audio duration using ffprobe"""
        try:
            result = subprocess.run(
                ['ffprobe', '-i', audio_file_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            return float(result.stdout)
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return 0

    def resize_audio_if_needed(self, audio_file_path):
        """Resize audio if it exceeds maximum size"""
        audio_size = self.get_file_size(audio_file_path)

        if audio_size > self.MAX_AUDIO_SIZE_BYTES:
            # Calculate a reasonable duration reduction
            current_duration = self.get_audio_duration(audio_file_path)
            target_duration = current_duration * self.MAX_AUDIO_SIZE_BYTES / audio_size

            # Create a temporary directory for storing compressed audio
            temp_dir = tempfile.mkdtemp()
            print(f"Audio too large, compressing to {temp_dir}")

            # Generate a unique filename based on current timestamp
            compressed_audio_path = os.path.join(
                temp_dir,
                f'compressed_audio_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.wav'
            )

            # Use ffmpeg to compress the audio file
            subprocess.run([
                'ffmpeg', '-i', audio_file_path,
                '-ss', '0', '-t', str(target_duration),
                compressed_audio_path
            ])

            return compressed_audio_path

        return audio_file_path

    def transcribe_audio(self, audio_file_path):
        """Transcribe audio using local Whisper model"""
        print("Transcribing audio with local Whisper...")

        try:
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(
                audio_file_path,
                language='en',  # Set to None for auto-detection
                task='transcribe',
                verbose=False
            )

            transcription = result['text']
            print(f"Transcription complete: {len(transcription)} characters")

            return transcription

        except Exception as e:
            print(f"Error transcribing audio: {e}")
            raise

    def abstract_summary_extraction(self, transcription):
        """Extract summary using Azure GPT-4"""
        messages = [
            SystemMessage(content="""You are a highly skilled AI trained in language comprehension and summarization.
I would like you to read the following text and summarize it into a concise abstract paragraph.
Aim to retain the most important points, providing a coherent and readable summary that could help
a person understand the main points of the discussion without needing to read the entire text.
Please avoid unnecessary details or tangential points."""),
            HumanMessage(content=transcription)
        ]

        response = self.llm.invoke(messages)
        print("Summary: Done")
        return response.content

    def key_points_extraction(self, transcription):
        """Extract key points using Azure GPT-4"""
        messages = [
            SystemMessage(content="""You are a proficient AI with a specialty in distilling information into key points.
Based on the following text, identify and list the main points that were discussed or brought up.
These should be the most important ideas, findings, or topics that are crucial to the essence of the discussion.
Your goal is to provide a list that someone could read to quickly understand what was talked about."""),
            HumanMessage(content=transcription)
        ]

        response = self.llm.invoke(messages)
        print("Key Points: Done")
        return response.content

    def action_item_extraction(self, transcription):
        """Extract action items using Azure GPT-4"""
        messages = [
            SystemMessage(content="""You are an AI expert in analyzing conversations and extracting action items.
Please review the text and identify any tasks, assignments, or actions that were agreed upon or mentioned as
needing to be done. These could be tasks assigned to specific individuals, or general actions that the group
has decided to take. Please list these action items clearly and concisely."""),
            HumanMessage(content=transcription)
        ]

        response = self.llm.invoke(messages)
        print("Action Items: Done")
        return response.content

    def sentiment_analysis(self, transcription):
        """Analyze sentiment using Azure GPT-4"""
        messages = [
            SystemMessage(content="""As an AI with expertise in language and emotion analysis, your task is to analyze
the sentiment of the following text. Please consider the overall tone of the discussion, the emotion conveyed by
the language used, and the context in which words and phrases are used. Indicate whether the sentiment is generally
positive, negative, or neutral, and provide brief explanations for your analysis where possible."""),
            HumanMessage(content=transcription)
        ]

        response = self.llm.invoke(messages)
        print("Sentiment: Done")
        return response.content

    def meeting_minutes(self, transcription):
        """Generate complete meeting minutes"""
        abstract_summary = self.abstract_summary_extraction(transcription)
        key_points = self.key_points_extraction(transcription)
        action_items = self.action_item_extraction(transcription)
        sentiment = self.sentiment_analysis(transcription)

        return {
            'transcription': transcription,
            'abstract_summary': abstract_summary,
            'key_points': key_points,
            'action_items': action_items,
            'sentiment': sentiment,
            'timestamp': datetime.datetime.now().isoformat()
        }

    def store_results(self, meeting_id, transcription, analysis):
        """Store transcription and analysis to local storage"""
        # Save transcript
        self.storage.save_transcript(meeting_id, transcription)

        # Save analysis
        self.storage.save_analysis(meeting_id, analysis)

        print(f"Results saved for meeting {meeting_id}")

    def transcribe(self, audio_file_path, meeting_id=None):
        """
        Main transcription and analysis pipeline

        Args:
            audio_file_path: Path to audio file
            meeting_id: Optional meeting ID for storage
        """
        try:
            # Generate meeting ID if not provided
            if not meeting_id:
                meeting_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

            # Resize if needed
            audio_file_path = self.resize_audio_if_needed(audio_file_path)

            # Transcribe
            transcription = self.transcribe_audio(audio_file_path)

            # Generate analysis
            print("\nGenerating meeting analysis...")
            analysis = self.meeting_minutes(transcription)

            # Store results
            self.store_results(meeting_id, transcription, analysis)

            # Print summary
            print("\n" + "=" * 60)
            print("MEETING ANALYSIS COMPLETE")
            print("=" * 60)
            print(f"\nMeeting ID: {meeting_id}")
            print(f"\nAbstract Summary:\n{analysis['abstract_summary']}")
            print(f"\nKey Points:\n{analysis['key_points']}")
            print(f"\nAction Items:\n{analysis['action_items']}")
            print(f"\nSentiment:\n{analysis['sentiment']}")
            print("=" * 60)

            return analysis

        except Exception as e:
            print(f"Error in transcription pipeline: {e}")
            raise


# Maintain backward compatibility
SpeechToText = LocalSpeechToText


if __name__ == "__main__":
    # Test the speech to text service
    import sys

    if len(sys.argv) < 2:
        print("Usage: python local_speech_to_text.py <audio_file_path>")
        sys.exit(1)

    audio_path = sys.argv[1]

    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found: {audio_path}")
        sys.exit(1)

    stt = LocalSpeechToText()
    stt.transcribe(audio_path)
