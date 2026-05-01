import os
import json
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from duckduckgo_search import DDGS

# 1. Load Environment Variables
load_dotenv()

# 2. Initialize the OpenRouter Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# 3. Initialize FastAPI App
app = FastAPI(title="ELE Core API", version="0.5")

# 4. Attach CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

# 5. Define Data Structures
class UserInput(BaseModel):
    text: str
    user_id: str = "default_user"

class AIResponse(BaseModel):
    reply: str
    intent: str
    action_required: bool

# Basic Memory Array
chat_history = []

# 6. Web Scraping Tool
def perform_web_search(query: str):
    print(f"\n[SYSTEM] Executing live web search for: '{query}'...")
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "No results found."
        
        context = ""
        for i, res in enumerate(results):
            context += f"Result {i+1}: {res.get('body')}\n"
        return context
    except Exception as e:
        print(f"[SYSTEM] Search failed: {e}")
        return "Web search failed due to an error."

@app.get("/")
async def health_check():
    return {"status": "ELE Backend is online. Agentic Web Search active."}

@app.post("/api/chat", response_model=AIResponse)
async def process_chat(user_input: UserInput):
    global chat_history
    print(f"\nUser says: {user_input.text}")
    
    try:
        # 1. Get the current date to ground the AI in reality
        current_date = datetime.now().strftime("%B %d, %Y")

        # 2. Construct the payload with the STRICT, Time-Aware System Prompt
        messages = [
            {
                "role": "system", 
                "content": f"""You are ELE, an execution-focused autonomous agent. 
                Today's date is {current_date}.
                Always respond in strict, valid JSON format. 
                
                CRITICAL RULES:
                1. NEVER apologize. 
                2. NEVER say "I don't have access to the internet" or "I am an AI."
                3. If the user asks for news, real-time info, weather, or facts, set intent to 'search_web'.
                4. SEARCH QUERY ENGINEERING: Your 'search_query' MUST be highly specific, SEO-optimized keywords. 
                   - BAD: "What is the news today?" or "top"
                   - GOOD: "latest global news headlines {current_date}"
                   - GOOD: "AAPL stock price live {current_date}"
                
                Your JSON schema MUST be exactly: 
                {{"reply": "Your response (leave blank if searching)", "intent": "chat|open_app|search_web|create_note", "search_query": "your SEO-optimized query", "action_required": true/false}}"""
            }
        ]
        
        # 3. Inject Short-Term Memory
        for msg in chat_history:
            messages.append(msg)
            
        # 4. Add the Current User Input
        messages.append({"role": "user", "content": user_input.text})

        # --- PASS 1: The Initial Thought ---
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages # type: ignore
        )
        
        raw_content = response.choices[0].message.content or ""
        raw_text = raw_content.strip()
        
        if raw_text.startswith("```json"): raw_text = raw_text[7:]
        if raw_text.endswith("```"): raw_text = raw_text[:-3]
            
        parsed_data = json.loads(raw_text)
        current_intent = parsed_data.get('intent')
        
        # --- PASS 2: The Agentic Web Search Interception ---
        if current_intent == "search_web" and parsed_data.get("search_query"):
            search_data = perform_web_search(parsed_data.get("search_query"))
            
            print("[SYSTEM] Injecting web data back into ELE's brain...")
            
            messages.append({"role": "assistant", "content": json.dumps(parsed_data)})
            messages.append({
                "role": "user", 
                "content": f"Here is the live data from the internet:\n{search_data}\n\nBased ONLY on this data, provide a final JSON response summarizing the answer. Change the intent to 'chat'. Do NOT include a search_query field."
            })
            
            response2 = client.chat.completions.create(
                model="openrouter/free",
                messages=messages # type: ignore
            )
            
            raw_content = response2.choices[0].message.content or ""
            raw_text = raw_content.strip()
            if raw_text.startswith("```json"): raw_text = raw_text[7:]
            if raw_text.endswith("```"): raw_text = raw_text[:-3]
                
            parsed_data = json.loads(raw_text) 
        
        # 5. Update Memory
        chat_history.append({"role": "user", "content": user_input.text})
        chat_history.append({"role": "assistant", "content": json.dumps(parsed_data)})
        
        if len(chat_history) > 10:
            chat_history = chat_history[-10:]
        
        # 6. Return to Frontend
        return AIResponse(
            reply=parsed_data.get("reply", "Understood."),
            intent=parsed_data.get("intent", "chat"),
            action_required=parsed_data.get("action_required", False)
        )
        
    except json.JSONDecodeError:
        print(f"Error: LLM did not return valid JSON. Raw output: {raw_text}")
        return AIResponse(
            reply="My brain got confused and didn't format the data right.",
            intent="error",
            action_required=False
        )
    except Exception as e:
        print(f"System Error: {e}")
        return AIResponse(
            reply="System encountered a critical error.",
            intent="error",
            action_required=False
        )