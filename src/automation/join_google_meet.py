from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from concurrent.futures import ThreadPoolExecutor

from record_audio import AudioRecorder
from record_video import VideoRecorder
from speech_to_text import SpeechToText
from blob_storage_service import BlobStorageService

import time

app = FastAPI()
# Add CORS middleware to allow requests from specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, or specify a list like ["http://example.com"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Modify MeetingRequest to accept applicationId and resumeId as integers
class MeetingRequest(BaseModel):
    interviewLink: str
    resumeId: int  # Changed to int
    applicationId: int  # Changed to int

class JoinGoogleMeet:
    def __init__(self):
        self.mail_address = os.environ.get('email_id')
        self.password = os.environ.get('email_password')
        print("Email: ", self.mail_address)
        opt = Options()
        opt.add_argument('--disable-blink-features=AutomationControlled')
        opt.add_argument('--start-maximized')
        opt.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 1,
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.geolocation": 0,
            "profile.default_content_setting_values.notifications": 1
        })
        self.driver = webdriver.Chrome(options=opt)

    def Glogin(self):
        try:
            self.driver.get('https://accounts.google.com/ServiceLogin?hl=en&passive=true&continue=https://www.google.com/&ec=GAZAAQ')
            
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            email_field.send_keys(self.mail_address)
            self.driver.find_element(By.ID, "identifierNext").click()
            self.driver.implicitly_wait(10)

            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input'))
            )
            password_field.send_keys(self.password)
            self.driver.implicitly_wait(10)
            self.driver.find_element(By.ID, "passwordNext").click()
            self.driver.implicitly_wait(10)

            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[aria-label*="Google Account"]'))
            )
            print("Logged in successfully.")

            self.driver.get('https://google.com/')
            self.driver.implicitly_wait(10)
            print("Gmail login activity: Done")
        
        except TimeoutException:
            print("Login failed. Unable to find login fields or profile icon.")
            raise
        except Exception as e:
            print(f"An error occurred during login: {e}")
            raise

    def turnOffMicCam(self, interviewLink):
        self.driver.get(interviewLink)

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[aria-label="Turn off microphone"]'))
        ).click()
        print("Microphone turned off")

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[aria-label="Turn off camera"]'))
        ).click()
        print("Camera turned off")

    def checkIfJoined(self):
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[jscontroller="kAPMuc"]'))
            )
            print("Meeting has been joined")
            return True
        except (TimeoutException, NoSuchElementException):
            print("Meeting has not been joined")
            return False

    def AskToJoin(self, audio_path, video_path):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[jsname="Qx7uuf"]'))
        ).click()
        print("Ask to join activity: Done")
        
        return self.checkIfJoined()

    def monitor_meeting(self):
        try:
            # Wait until the meeting interface is no longer present
            while True:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, 'div[jscontroller="kAPMuc"]')
                    # Still in meeting, wait a bit
                    time.sleep(2)
                except NoSuchElementException:
                    # Meeting element not found, assume meeting ended
                    print("Meeting ended")
                    return False
        except Exception as e:
            print(f"Error monitoring meeting: {e}")
            return False

# Convert applicationId and resumeId to string when used
def join_meeting(interviewLink: str, resumeId: int, applicationId: int):
    project_dir = Path(__file__).parent
    recordings_dir = project_dir / 'recordings'
    recordings_dir.mkdir(parents=True, exist_ok=True)

    # Convert to string before use
    audio_path = recordings_dir / f"{str(resumeId)}.wav"
    video_path = recordings_dir / f"{str(resumeId)}.mp4"

    obj = JoinGoogleMeet()
    obj.Glogin()
    obj.turnOffMicCam(interviewLink)
    joined = obj.AskToJoin(str(audio_path), str(video_path))

    if not joined:
        raise HTTPException(status_code=408, detail="Failed to join the meeting")

    return obj, audio_path, video_path, str(applicationId)  # Convert applicationId to string

def background_processing(obj, audio_path, video_path, application_id):
    print("Started recording and processing")

    # Initialize audio recorder and blob storage service
    audio_recorder = AudioRecorder()
    blob_service = BlobStorageService()
    
    try:
        # Start audio recording
        audio_recorder.start_recording(str(audio_path))
        
        # Monitor meeting in the same thread
        obj.monitor_meeting()
        
        # When monitor_meeting returns, stop recording
        audio_recorder.stop_recording(str(audio_path))
        
        # Wait a moment for the file to be fully written
        time.sleep(2)
        
        # Verify the file exists and has content
        if os.path.exists(str(audio_path)) and os.path.getsize(str(audio_path)) > 0:
            print(f"Audio file saved successfully. Size: {os.path.getsize(str(audio_path))/1024/1024:.2f} MB")
            
            # Upload with retries
            max_upload_attempts = 3
            for attempt in range(max_upload_attempts):
                try:
                    blob_url = blob_service.upload_file(str(audio_path))
                    print(f"Audio file uploaded successfully to: {blob_url}")
                    
                    # Process the recorded audio only after successful upload
                    SpeechToText().transcribe(str(audio_path))
                    break
                except Exception as upload_error:
                    if attempt == max_upload_attempts - 1:
                        print(f"Final upload attempt failed: {str(upload_error)}")
                        raise
                    print(f"Upload attempt {attempt + 1} failed, retrying...")
                    time.sleep(5)  # Wait before retry
        else:
            raise Exception("Audio file not found or empty after recording")
        
    except Exception as e:
        print(f"Error in background processing: {e}")
        if audio_recorder.recording:
            audio_recorder.stop_recording(str(audio_path))
    finally:
        # Clean up
        if obj.driver:
            obj.driver.quit()

@app.post("/join-meet/")
async def join_meet(request: MeetingRequest, background_tasks: BackgroundTasks):
    with ThreadPoolExecutor() as executor:
        future = executor.submit(join_meeting, request.interviewLink, request.resumeId, request.applicationId)
        try:
            obj, audio_path, video_path, application_id = future.result(timeout=700)  # 700 seconds timeout
            background_tasks.add_task(background_processing, obj, audio_path, video_path, application_id)
            return {"message": "Meeting join process started", "status": "processing"}
        except TimeoutError:
            return {"message": "Operation timed out", "status": "timeout"}
        except HTTPException as http_exc:
            return {"message": http_exc.detail, "status": "error"}
        except Exception as e:
            return {"message": f"An unexpected error occurred: {str(e)}", "status": "error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
