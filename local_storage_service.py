"""
Local Storage Service - Replaces Azure Blob Storage with local file system
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class LocalStorageService:
    """Manages local file storage for meeting recordings"""

    def __init__(self):
        # Get storage path from env or use default
        self.storage_path = os.getenv('LOCAL_STORAGE_PATH', './storage')
        self.storage_path = Path(self.storage_path)

        # Create storage directory if it doesn't exist
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.recordings_path = self.storage_path / 'recordings'
        self.transcripts_path = self.storage_path / 'transcripts'
        self.analysis_path = self.storage_path / 'analysis'

        self.recordings_path.mkdir(exist_ok=True)
        self.transcripts_path.mkdir(exist_ok=True)
        self.analysis_path.mkdir(exist_ok=True)

        print(f"Local storage initialized at: {self.storage_path.absolute()}")

    def upload_file(self, file_path: str, blob_name: str = None, max_retries: int = 3) -> str:
        """
        Copy file to local storage

        Args:
            file_path (str): Path to the local file
            blob_name (str, optional): Name for the stored file. If None, uses the file name
            max_retries (int): For compatibility with blob storage (not used)

        Returns:
            str: Path to the stored file
        """
        try:
            source_path = Path(file_path)

            if not source_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # If blob_name is not provided, use the file name
            if not blob_name:
                blob_name = source_path.name

            # Determine destination based on file type
            if source_path.suffix.lower() in ['.wav', '.mp3', '.mp4', '.avi']:
                dest_path = self.recordings_path / blob_name
            else:
                dest_path = self.recordings_path / blob_name

            # Copy the file
            shutil.copy2(source_path, dest_path)

            file_size_mb = dest_path.stat().st_size / (1024 * 1024)
            print(f"File stored locally: {dest_path} ({file_size_mb:.2f} MB)")

            return str(dest_path.absolute())

        except Exception as e:
            print(f"Error storing file locally: {str(e)}")
            raise

    def save_transcript(self, meeting_id: str, transcript: str) -> str:
        """
        Save transcript to local storage

        Args:
            meeting_id: Unique meeting identifier
            transcript: Transcript text

        Returns:
            Path to saved transcript
        """
        try:
            filename = f"{meeting_id}_transcript.txt"
            filepath = self.transcripts_path / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(transcript)

            print(f"Transcript saved: {filepath}")
            return str(filepath.absolute())

        except Exception as e:
            print(f"Error saving transcript: {str(e)}")
            raise

    def save_analysis(self, meeting_id: str, analysis: dict) -> str:
        """
        Save meeting analysis to local storage

        Args:
            meeting_id: Unique meeting identifier
            analysis: Analysis dictionary

        Returns:
            Path to saved analysis
        """
        try:
            import json

            filename = f"{meeting_id}_analysis.json"
            filepath = self.analysis_path / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)

            print(f"Analysis saved: {filepath}")
            return str(filepath.absolute())

        except Exception as e:
            print(f"Error saving analysis: {str(e)}")
            raise

    def delete_file(self, file_path: str):
        """Delete a file from storage"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                print(f"File deleted: {file_path}")
            else:
                print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            raise

    def list_recordings(self):
        """List all recordings in storage"""
        try:
            recordings = list(self.recordings_path.glob('*'))
            return [str(r.absolute()) for r in recordings]
        except Exception as e:
            print(f"Error listing recordings: {str(e)}")
            return []

    def get_storage_info(self):
        """Get storage statistics"""
        try:
            total_size = 0
            file_count = 0

            for path in [self.recordings_path, self.transcripts_path, self.analysis_path]:
                for file in path.rglob('*'):
                    if file.is_file():
                        total_size += file.stat().st_size
                        file_count += 1

            return {
                'storage_path': str(self.storage_path.absolute()),
                'total_size_mb': total_size / (1024 * 1024),
                'file_count': file_count,
                'recordings': len(list(self.recordings_path.glob('*'))),
                'transcripts': len(list(self.transcripts_path.glob('*'))),
                'analyses': len(list(self.analysis_path.glob('*')))
            }

        except Exception as e:
            print(f"Error getting storage info: {str(e)}")
            return {}


if __name__ == "__main__":
    # Test the local storage service
    storage = LocalStorageService()

    print("\n=== Storage Information ===")
    info = storage.get_storage_info()
    for key, value in info.items():
        print(f"{key}: {value}")

    print("\n=== Storage Directories ===")
    print(f"Recordings: {storage.recordings_path}")
    print(f"Transcripts: {storage.transcripts_path}")
    print(f"Analysis: {storage.analysis_path}")
