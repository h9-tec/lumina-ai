from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError
import os
from pathlib import Path
from dotenv import load_dotenv
import time

load_dotenv()

class BlobStorageService:
    def __init__(self):
        self.account_name = os.getenv('STORAGE_ACCOUNT_NAME')
        self.account_key = os.getenv('STORAGE_ACCOUNT_KEY')
        self.container_name = os.getenv('CONTAINER_NAME')
        
        # Connection string format
        self.connection_string = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={self.account_name};"
            f"AccountKey={self.account_key};"
            f"EndpointSuffix=core.windows.net"
        )
        
        # Initialize the blob service client
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        
        # Ensure container exists
        self._ensure_container_exists()

    def _ensure_container_exists(self):
        try:
            container_client = self.blob_service_client.create_container(self.container_name)
            print(f"Container {self.container_name} created successfully")
        except ResourceExistsError:
            print(f"Container {self.container_name} already exists")
        except Exception as e:
            print(f"Error creating container: {str(e)}")
            raise

    def upload_file(self, file_path: str, blob_name: str = None, max_retries: int = 3) -> str:
        """
        Upload a file to blob storage with retries
        
        Args:
            file_path (str): Path to the local file
            blob_name (str, optional): Name for the blob. If None, uses the file name
            max_retries (int): Maximum number of retry attempts
            
        Returns:
            str: URL of the uploaded blob
        """
        retry_count = 0
        last_exception = None

        while retry_count < max_retries:
            try:
                # If blob_name is not provided, use the file name
                if not blob_name:
                    blob_name = Path(file_path).name

                # Get blob client
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=blob_name
                )

                # Get file size
                file_size = os.path.getsize(file_path)
                
                print(f"Starting upload attempt {retry_count + 1} of {max_retries} "
                      f"for {blob_name} ({file_size/1024/1024:.2f} MB)")

                # Upload the file with shorter timeout but multiple retries
                with open(file_path, "rb") as data:
                    blob_client.upload_blob(
                        data, 
                        blob_type="BlockBlob",
                        overwrite=True,
                        max_concurrency=4,
                        timeout=300  # 5 minutes timeout per attempt
                    )
                    
                print(f"File {file_path} uploaded successfully as {blob_name}")
                return blob_client.url

            except Exception as e:
                last_exception = e
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count  # Exponential backoff
                    print(f"Upload attempt {retry_count} failed: {str(e)}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Error uploading file after {max_retries} attempts: {str(e)}")
                    error_details = f"File: {file_path}, Size: {file_size/1024/1024:.2f} MB"
                    print(f"Upload failed with details: {error_details}")
                    raise last_exception

    def delete_blob(self, blob_name: str):
        """Delete a blob from storage"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            blob_client.delete_blob()
            print(f"Blob {blob_name} deleted successfully")
        except Exception as e:
            print(f"Error deleting blob: {str(e)}")
            raise