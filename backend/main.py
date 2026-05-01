import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize the client pointing to OpenRouter instead of OpenAI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

app = FastAPI(title="ELE Core API", version="0.3")

class UserInput(BaseModel):
    text: str
    user_id: str = "default_user"

class AIResponse(BaseModel):
    reply: str
    intent: str
    action_required: bool

@app.get("/")
async def health_check():
    return {"status": "ELE Backend is running on OpenRouter (Llama 3)."}

@app.post("/api/chat", response_model=AIResponse)
async def process_chat(user_input: UserInput):
    print(f"\nUser says: {user_input.text}")
    
    try:
        # Call the free Llama 3 model via OpenRouter
        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct:free",
            messages=[
                {
                    "role": "system", 
                    "content": """You are ELE, an execution-focused AI assistant. 
                    Always respond in strict, valid JSON format. 
                    Analyze the user's input and determine the correct intent.
                    The intent MUST be exactly one of these strings: 'chat', 'open_app', 'search_web', 'create_note'.
                    If the intent is anything other than 'chat', set action_required to true.
                    Your JSON schema must be exactly: {"reply": "Your conversational response", "intent": "the intent", "action_required": true or false}"""
                },
                {"role": "user", "content": user_input.text}
            ]
        )
        
        # Extract and clean the text
        raw_text = response.choices[0].message.content.strip()
        
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        parsed_data = json.loads(raw_text)
        print(f"ELE intent: {parsed_data.get('intent')}")
        
        return AIResponse(
            reply=parsed_data.get("reply", "Understood."),
            intent=parsed_data.get("intent", "chat"),
            action_required=parsed_data.get("action_required", False)
        )
        
    except Exception as e:
        print(f"System Error: {e}")
        return AIResponse(
            reply="My new Llama brain hit a snag.",
            intent="error",
            action_required=False
        )