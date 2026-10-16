import os
import io
import time
import tempfile
import speech_recognition as sr
from gtts import gTTS
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from app.agent import agent
from app.ticket_service import ticket_store

app = FastAPI(title="Customer Support & Ticket Agent API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class SynthesizeRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"status": "Customer Support Agent API is running successfully."}

@app.post("/chat")
def chat_endpoint(payload: ChatRequest):
    try:
        result = agent.process_message(payload.session_id, payload.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticket/{ticket_id}")
def get_ticket_endpoint(ticket_id: str):
    ticket = ticket_store.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

# --- Voice Integration Endpoints (Mid-Session Requirements) ---

@app.post("/voice/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    start_time = time.time()
    try:
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio data received.")
        
        # Save audio bytes temporarily to be read by SpeechRecognition
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name

        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(temp_audio_path) as source:
                audio_data = recognizer.record(source)
            
            transcript = recognizer.recognize_google(audio_data)
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Clean up temp file
            os.unlink(temp_audio_path)
            
            return {
                "success": True,
                "transcript": transcript,
                "processing_time_ms": processing_time_ms
            }
        except sr.UnknownValueError:
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
            return {
                "success": False,
                "transcript": "",
                "processing_time_ms": int((time.time() - start_time) * 1000),
                "error": "Could not understand audio"
            }
        except Exception as inner_e:
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
            raise inner_e

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Transcription error: {str(e)}")

@app.post("/voice/synthesize")
async def synthesize_text(payload: SynthesizeRequest):
    text = payload.text
    if not text:
        raise HTTPException(status_code=400, detail="Text is required for synthesis.")
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_bytes = fp.read()
        return Response(content=audio_bytes, media_type="audio/mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synthesis error: {str(e)}")