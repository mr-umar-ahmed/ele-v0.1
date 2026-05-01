import os
import json
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai  # NEW SDK
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
# The new SDK automatically looks for GEMINI_API_KEY env var
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    text: str
    user_id: str = "dev_c"

@app.post("/api/chat")
async def process_chat(user_input: UserInput):
    print(f"User Request: {user_input.text}")
    try:
        # 2. Use the new 'models.generate' syntax
        response = client.models.generate_content(
            model='gemini-2.0-flash', # Use the latest stable 2026 model
            contents=user_input.text,
            config={
                'system_instruction': "You are ELE. Respond ONLY in valid JSON. Schema: {\"reply\": \"text\", \"intent\": \"chat|open_app|search_web\", \"action_required\": bool}"
            }
        )
        
        raw_text = response.text.strip()
        print(f"AI Output: {raw_text}")

        # 3. Robust JSON Extraction
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return {
                "reply": data.get("reply", "Understood."),
                "intent": data.get("intent", "chat"),
                "action_required": data.get("action_required", False) or (data.get("intent") != "chat")
            }
        
        # Manual Fallback if AI skips JSON
        return {"reply": raw_text, "intent": "chat", "action_required": False}

    except Exception as e:
        print(f"New SDK Error: {e}")
        return {"reply": "Connection issue with Gemini 2.0.", "intent": "error", "action_required": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)