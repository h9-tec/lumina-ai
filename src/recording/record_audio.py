import sounddevice as sd
from scipy.io.wavfile import write
import threading
import numpy as np


class AudioRecorder:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.recording = False
        self.audio_data = []
        self.stream = None
        self.thread = None

    def callback(self, indata, frames, time, status):
        if self.recording:
            mono_data = np.mean(indata, axis=1, dtype=np.float32)
            mono_data = (mono_data * 32767).astype(np.int16)
            self.audio_data.append(mono_data)

    def start_recording(self, filename):
        self.recording = True
        self.audio_data = []
        
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32,
            callback=self.callback
        )
        self.stream.start()
        print("Recording started...")

    def stop_recording(self, filename):
        if self.recording:
            self.recording = False
            if self.stream:
                self.stream.stop()
                self.stream.close()
            
            if self.audio_data:
                combined_data = np.concatenate(self.audio_data, axis=0)
                write(filename, self.sample_rate, combined_data)
                print(f"Recording finished. Saved as {filename}.")
            
            self.audio_data = []