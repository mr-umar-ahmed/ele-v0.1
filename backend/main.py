import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="""You are ELE, an execution-focused AI assistant. 
    Always respond in strict, valid JSON format. 
    Analyze the user's input and determine the correct intent.
    The intent MUST be exactly one of these strings: 'chat', 'open_app', 'search_web', 'create_note'.
    If the intent is anything other than 'chat', set action_required to true.
    Your JSON schema must be: {"reply": "Your conversational response", "intent": "the intent", "action_required": true or false}"""
)

app = FastAPI(title="ELE Core API", version="0.2")

# --- THE SECURITY PASS (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --------------------------------

class UserInput(BaseModel):
    text: str
    user_id: str = "default_user"

class AIResponse(BaseModel):
    reply: str
    intent: str
    action_required: bool

@app.get("/")
async def health_check():
    return {"status": "ELE Backend is running."}

@app.post("/api/chat", response_model=AIResponse)
async def process_chat(user_input: UserInput):
    print(f"\nUser says: {user_input.text}")
    try:
        response = model.generate_content(user_input.text)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        parsed_data = json.loads(raw_text)
        print(f"ELE determined intent: {parsed_data.get('intent')}")
        
        return AIResponse(
            reply=parsed_data.get("reply", "I processed that, but lost the reply string."),
            intent=parsed_data.get("intent", "chat"),
            action_required=parsed_data.get("action_required", False)
        )
    except Exception as e:
        print(f"System Error: {e}")
        return AIResponse(
            reply="System failure.",
            intent="error",
            action_required=False
        )