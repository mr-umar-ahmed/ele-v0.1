import os
import json
import sqlite3
import pyautogui
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from duckduckgo_search import DDGS
import speech_recognition as sr

# 1. Load Environment Variables
load_dotenv()

# ==========================================
# 🧠 DUAL-ENGINE SETUP
# ==========================================
client_cloud = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

client_local = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama", 
)

# ==========================================
# 🗄️ MEMORY LAYER (SQLite)
# ==========================================
def init_db():
    conn = sqlite3.connect('ele_memory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS memory
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  role TEXT,
                  content TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db() 

def save_memory(role: str, content: str):
    conn = sqlite3.connect('ele_memory.db')
    c = conn.cursor()
    c.execute("INSERT INTO memory (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def get_memory(limit=10):
    conn = sqlite3.connect('ele_memory.db')
    c = conn.cursor()
    c.execute("SELECT role, content FROM memory ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in reversed(rows)]

# ==========================================
# 🛠️ TOOLS LAYER
# ==========================================
def perform_web_search(query: str):
    print(f"\n[SYSTEM] Executing live web search for: '{query}'...")
    try:
        results = DDGS().news(query, max_results=3)
        if not results: return "No results found."
        
        context = ""
        for i, res in enumerate(results): context += f"Result {i+1}: {res.get('body')}\n"
        return context
    except Exception as e:
        print(f"[SYSTEM] Search failed: {e}")
        return "Web search failed."

def execute_system_control(action: str):
    print(f"\n[OS CONTROL] Executing: {action}")
    try:
        if action == "mute":
            pyautogui.press("volumemute")
            return "System volume muted."
        elif action == "volume_up":
            for _ in range(5): pyautogui.press("volumeup")
            return "Volume increased."
        elif action == "volume_down":
            for _ in range(5): pyautogui.press("volumedown")
            return "Volume decreased."
        elif action == "lock_screen":
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Screen locked successfully."
        else:
            return f"Unknown command: {action}"
    except Exception as e:
        print(f"[OS ERROR] {e}")
        return "Execution failed."

# ==========================================
# 🚀 FASTAPI & ROUTER LAYER
# ==========================================
app = FastAPI(title="ELE Core API", version="1.1 (App Automator + Master Prompt)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

class UserInput(BaseModel):
    text: str
    user_id: str = "default_user"

class AIResponse(BaseModel):
    reply: str
    intent: str
    action_required: bool

@app.get("/")
async def health_check():
    return {"status": "ELE Backend is online. App Automator active."}

# ==========================================
# 🎤 THE PYTHON EAR (Hardware Mic Access)
# ==========================================
@app.get("/api/listen")
async def listen_to_mic():
    print("\n[AUDIO] Waking up microphone...")
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("[AUDIO] Adjusting for ambient noise...")
        r.adjust_for_ambient_noise(source, duration=1)
        print("[AUDIO] Listening now...")
        
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            print("[AUDIO] Processing voice data...")
            
            text = r.recognize_google(audio)  # type: ignore
            print(f"[AUDIO] Heard: {text}")
            return {"text": text}
            
        except sr.WaitTimeoutError:
            return {"error": "Listening timed out. No speech detected."}
        except sr.UnknownValueError:
            return {"error": "Could not understand the audio."}
        except sr.RequestError as e:
            return {"error": f"Speech API error: {e}"}

# ==========================================
# 🧠 CORE CHAT ENGINE
# ==========================================
@app.post("/api/chat", response_model=AIResponse)
async def process_chat(user_input: UserInput):
    print(f"\nUser says: {user_input.text}")
    
    try:
        current_date = datetime.now().strftime("%B %d, %Y")

        messages = [
            {
                "role": "system", 
                "content": f"""You are ELE, an execution-focused autonomous agent. 
                Today's date is {current_date}.
                Always respond in strict, valid JSON format. Do not include extra text.
                
                CRITICAL RULES:
                1. NEVER apologize or say you cannot do something.
                2. NEVER say "I am an AI." You control the OS.
                3. Intents available: 'chat', 'open_app', 'create_note', 'search_web', 'system_control'.
                4. OPEN APP: If the user says "open [app]", intent MUST be 'open_app', and action_detail MUST be the app name (e.g., 'chrome', 'vscode').
                
                EXAMPLES OF CORRECT RESPONSES:
                User: "open chrome"
                Assistant: {{"reply": "Opening Google Chrome.", "intent": "open_app", "search_query": "", "action_detail": "chrome", "action_required": false}}
                
                User: "mute the volume"
                Assistant: {{"reply": "Muting volume.", "intent": "system_control", "search_query": "", "action_detail": "mute", "action_required": false}}
                
                User: "what is the capital of France?"
                Assistant: {{"reply": "The capital of France is Paris.", "intent": "chat", "search_query": "", "action_detail": "", "action_required": false}}
                
                Your JSON schema MUST be exactly: 
                {{"reply": "Your response", "intent": "the_intent", "search_query": "query", "action_detail": "detail", "action_required": true/false}}"""
            }
        ]
        
        # Load Memory
        past_context = get_memory(limit=8)
        for msg in past_context:
            messages.append(msg)
            
        messages.append({"role": "user", "content": user_input.text})

        # Dual-Engine Failover Loop
        try:
            print("[SYSTEM] Firing Engine A (OpenRouter Cloud)...")
            response = client_cloud.chat.completions.create(
                model="openrouter/free", 
                messages=messages # type: ignore
            )
            print("[SYSTEM] Engine A Success.")
        except Exception as cloud_error:
            print(f"[WARNING] Cloud connection failed: {cloud_error}")
            print("[SYSTEM] Engaging Engine B (Local Llama 3 Fallback)...")
            
            response = client_local.chat.completions.create(
                model="llama3", 
                messages=messages # type: ignore
            )
            print("[SYSTEM] Engine B Success.")

        raw_text = (response.choices[0].message.content or "").strip()
        if raw_text.startswith("```json"): raw_text = raw_text[7:]
        if raw_text.endswith("```"): raw_text = raw_text[:-3]
            
        parsed_data = json.loads(raw_text)
        current_intent = parsed_data.get('intent')
        
        # --- PASS 2.A: Web Search Interception ---
        if current_intent == "search_web" and parsed_data.get("search_query"):
            search_data = perform_web_search(parsed_data.get("search_query"))
            messages.append({"role": "assistant", "content": json.dumps(parsed_data)})
            messages.append({"role": "user", "content": f"Live data:\n{search_data}\n\nBased ONLY on this, provide a final JSON response summarizing the answer. Change intent to 'chat'. No search_query field."})
            
            try:
                response2 = client_cloud.chat.completions.create(model="openrouter/free", messages=messages) # type: ignore
            except:
                response2 = client_local.chat.completions.create(model="llama3", messages=messages) # type: ignore
                
            raw_text2 = (response2.choices[0].message.content or "").strip()
            if raw_text2.startswith("```json"): raw_text2 = raw_text2[7:]
            if raw_text2.endswith("```"): raw_text2 = raw_text2[:-3]
            parsed_data = json.loads(raw_text2) 
            
        # --- PASS 2.B: OS System Control Interception ---
        elif current_intent == "system_control":
            action_detail = parsed_data.get("action_detail")
            if action_detail:
                os_result = execute_system_control(action_detail)
                parsed_data["reply"] = f"Action complete. {os_result}"
                parsed_data["action_required"] = False 

        # --- PASS 2.C: App Opener Interception ---
        elif current_intent == "open_app":
            app_to_open = parsed_data.get("action_detail", "").lower()
            print(f"[OS CONTROL] Attempting to open application: {app_to_open}")
            
            try:
                if "chrome" in app_to_open:
                    os.system("start chrome")
                    parsed_data["reply"] = "Opening Google Chrome."
                elif "code" in app_to_open or "vs code" in app_to_open or "vscode" in app_to_open:
                    os.system("code")
                    parsed_data["reply"] = "Opening Visual Studio Code."
                elif "notepad" in app_to_open:
                    os.system("notepad")
                    parsed_data["reply"] = "Opening Notepad."
                else:
                    # Generic Windows fallback for other apps
                    os.system(f"start {app_to_open}")
                    parsed_data["reply"] = f"Attempting to launch {app_to_open}."
            except Exception as e:
                parsed_data["reply"] = f"I encountered an error opening {app_to_open}."
                
            parsed_data["action_required"] = False 

        # Save Memory
        save_memory("user", user_input.text)
        save_memory("assistant", json.dumps(parsed_data))
        
        return AIResponse(
            reply=parsed_data.get("reply", "Understood."),
            intent=parsed_data.get("intent", "chat"),
            action_required=parsed_data.get("action_required", False)
        )
        
    except json.JSONDecodeError:
        return AIResponse(reply="Data format error.", intent="error", action_required=False)
    except Exception as e:
        print(f"System Error: {e}")
        return AIResponse(reply="Critical system error.", intent="error", action_required=False)