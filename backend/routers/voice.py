import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize the router for this specific module
router = APIRouter()

# Note: Whisper requires a standard OpenAI API key, not OpenRouter.
# Ensure OPENAI_API_KEY is in your .env file.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    print(f"\n[VOICE MODULE] Receiving audio file: {audio_file.filename}")
    
    # 1. Save the incoming file temporarily
    temp_file_path = f"temp_{audio_file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)
        
    try:
        # 2. Send to OpenAI Whisper for Speech-to-Text
        print("[VOICE MODULE] Sending to Whisper for transcription...")
        with open(temp_file_path, "rb") as file_to_transcribe:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=file_to_transcribe
            )
            
        text = transcription.text
        print(f"[VOICE MODULE] Transcribed Text: {text}")
        
        # 3. Clean up the temporary file
        os.remove(temp_file_path)
        
        # 4. Return the text to the frontend
        return {"text": text, "status": "success"}

    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        print(f"[VOICE MODULE ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))