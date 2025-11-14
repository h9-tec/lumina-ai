import subprocess
import platform
from pathlib import Path
import os
from dotenv import load_dotenv
# from azure.storage.blob import BlobServiceClient, ContentSettings

class VideoRecorder:
    def __init__(self, output_path, duration, application_id):
        self.output_path = output_path
        self.duration = duration  # Duration in seconds
        self.application_id = application_id
        load_dotenv()  # Load environment variables from .env file
        self.container_url = os.getenv('CONTAINER_URL')
        self.sas_token = os.getenv('SAS_TOKEN')

    def start_recording(self):
        print("Recording video...")
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # Overwrite the output file if it exists
            '-f', 'gdigrab',  # Screen capture for Windows
            '-framerate', '30',  # Framerate
            '-i', 'desktop',  # Input source (entire screen)
            '-f', 'dshow',  # For audio capture on Windows
            '-i', 'audio=Microphone (2- High Definition Audio Device)',  # Replace with the correct device name from your output
            '-t', str(self.duration),  # Recording time
            '-c:v', 'libx264',  # Video codec
            '-c:a', 'aac',  # Audio codec
            str(self.output_path)  # Output file path
        ]

        # Run the ffmpeg command to record the screen
        subprocess.run(ffmpeg_cmd)
        print(f"Video recording finished. Saved as {self.output_path}.")
        
        # Upload the recorded video to Azure Blob Storage
        # self.upload_to_blob_storage()

    # def upload_to_blob_storage(self):
        # Extract only the file name from the full path
        blob_name = Path(self.output_path).name
        print(f"Uploading video to Azure Blob Storage: {blob_name}")
        
        try:
            # Create a BlobServiceClient object using the container URL and SAS token
            blob_service_client = BlobServiceClient(account_url=self.container_url, credential=self.sas_token)

            # Get the blob client for the specific container and blob (video file)
            container_client = blob_service_client.get_container_client(container=f"application-{self.application_id}")  # Replace with your container name
            blob_client = container_client.get_blob_client(blob_name)

            # Open the video file and upload it
            with open(self.output_path, "rb") as data:
                blob_client.upload_blob(
                    data,
                    overwrite=True,
                    timeout=100000,  # Increase timeout if needed
                    content_settings=ContentSettings(content_type="video/mp4")  # Ensure correct content type
                )

            print(f"Video uploaded successfully to Azure Blob Storage: {blob_name}")

        except Exception as e:
            print(f"An error occurred while uploading to Azure Blob Storage: {str(e)}")