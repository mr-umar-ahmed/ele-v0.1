import speech_recognition as sr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# FASTAPI SETUP
# ==========================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# OPENROUTER CLIENT
# ==========================================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

# ==========================================
# REQUEST MODEL
# ==========================================

class ChatRequest(BaseModel):
    text: str
    user_id: str

# ==========================================
# CHAT ENDPOINT
# ==========================================

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):

    user_input = request.text

    system_prompt = """
    You are ELE, an advanced execution AI.

    Analyze the user's command and return a JSON object with these exact keys:

    - "action"
    - "target"
    - "reply"

    Example:

   {
  "action": "open_app",
  "target": "calculator",
  "reply": "Opening Calculator"
}
{
  "action": "open_website",
  "target": "youtube.com",
  "reply": "Opening YouTube"
}

    You MUST output valid JSON only.
    """

    try:

        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",

            response_format={
                "type": "json_object"
            },

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )

        ai_decision = json.loads(
            response.choices[0].message.content
        )

        action = ai_decision.get("action")
        target = ai_decision.get("target")
        reply = ai_decision.get("reply")

        # ==========================================
        # RETURN CLEAN INTENT OBJECT
        # ==========================================

        return {
            "intent": action,
            "target": target,
            "reply": reply
        }

    except Exception as e:

        return {
            "intent": "error",
            "target": "none",
            "reply": f"ERR: BRAIN_OFFLINE. Details: {str(e)}"
        }

# ==========================================
# WAKEWORD ENDPOINT
# ==========================================

@app.get("/api/wakeword")
async def wakeword():

    return {
        "status": "detected"
    }

# ==========================================
# LISTEN ENDPOINT
# ==========================================

# ==========================================
# LISTEN ENDPOINT
# ==========================================

@app.get("/api/listen")
async def listen():

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            print("Listening...")

            # Noise calibration
            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            # Better sensitivity
            recognizer.energy_threshold = 250

            recognizer.dynamic_energy_threshold = True

            # Listen
            audio = recognizer.listen(

                source,

                timeout=8,

                phrase_time_limit=6
            )

        print("Recognizing...")

        text = recognizer.recognize_google(audio)

        print("You said:", text)

        return {
            "text": text
        }

    except sr.WaitTimeoutError:

        return {
            "error": "Listening timeout."
        }

    except sr.UnknownValueError:

        return {
            "error": "Could not understand audio."
        }

    except Exception as e:

        return {
            "error": str(e)
        }