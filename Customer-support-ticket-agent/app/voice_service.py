import os
import time
import speech_recognition as sr
from gtts import gTTS
import io

class RealSTTService:
    def transcribe(self, audio_bytes: bytes) -> dict:
        start_time = time.time()
        recognizer = sr.Recognizer()
        
        # Convert audio bytes to audio file stream format for SpeechRecognition
        audio_file = sr.AudioFile(io.BytesIO(audio_bytes))
        try:
            with audio_file as source:
                audio_data = recognizer.record(source)
            # Using Google Speech Recognition (free tier built-in)
            transcript = recognizer.recognize_google(audio_data)
            processing_time = int((time.time() - start_time) * 1000)
            return {
                "success": True,
                "transcript": transcript,
                "processing_time_ms": processing_time
            }
        except Exception as e:
            return {
                "success": False,
                "transcript": "",
                "processing_time_ms": 0,
                "error": str(e)
            }

class RealTTSService:
    def synthesize(self, text: str) -> bytes:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()