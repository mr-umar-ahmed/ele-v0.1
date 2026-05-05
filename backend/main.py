import os
import json
import sqlite3
import pyautogui
import subprocess
import difflib
import time
import shutil
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from duckduckgo_search import DDGS
import speech_recognition as sr

# ==========================================
# ⚙️ SYSTEM INITIALIZATION
# ==========================================
load_dotenv()

client_cloud = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
client_local = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# ==========================================
# 🗄️ SQLITE MEMORY LAYER
# ==========================================
def init_db():
    conn = sqlite3.connect('ele_memory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS memory 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db() 

def save_memory(role: str, content: str):
    conn = sqlite3.connect('ele_memory.db')
    c = conn.cursor()
    c.execute("INSERT INTO memory (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def get_memory(limit: int = 5) -> List[Dict[str, str]]:
    conn = sqlite3.connect('ele_memory.db')
    c = conn.cursor()
    c.execute("SELECT role, content FROM memory ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in reversed(rows)]

# ==========================================
# 🛠️ ADVANCED TOOLKIT & SMART OPEN
# ==========================================
def perform_web_search(query: str) -> str:
    print(f"\n[ELE CORE] Scraping live web data for: '{query}'...")
    try:
        results = DDGS().news(query, max_results=3)
        if not results: return "No results found."
        return "\n".join([f"Source {i+1}: {res.get('body', '')}" for i, res in enumerate(results)])
    except Exception as e:
        return f"Search offline. Error: {e}"

def launch_dev_environment(project_query: str) -> str | None: 
    base_path = r"C:\Users\DELL\OneDrive\Desktop\PROJECTS"
    if not os.path.exists(base_path): return None

    existing_projects = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    
    # Strict cutoff to prevent false positives (like Chrome triggering Code-Crew)
    matches = difflib.get_close_matches(project_query.lower(), [p.lower() for p in existing_projects], n=1, cutoff=0.45)
    
    if not matches: return None

    target_folder = next(p for p in existing_projects if p.lower() == matches[0])
    full_path = os.path.join(base_path, target_folder)

    try:
        os.system(f'code "{full_path}"')
        if os.path.exists(os.path.join(full_path, "package.json")):
            launch_cmd = f'start cmd /k "cd /d {full_path} && title ELE Server: {target_folder} && npm run dev"'
            subprocess.Popen(launch_cmd, shell=True)
            return f"Project {target_folder} initialized. Server started."
        return f"Project {target_folder} opened."
    except Exception as e:
        return f"Error opening project: {e}"

def smart_open(target: str) -> str:
    """The Ultimate OS Router: Decides whether to launch an app, open a project, or search Chrome."""
    
    # 1. Check for standard Web targets
    web_targets = {"youtube": "https://youtube.com", "google": "https://google.com", "github": "https://github.com"}
    if target in web_targets:
        os.system(f"start {web_targets[target]}")
        return f"Opening {target}."

    # 2. Check for known OS Applications
    app_aliases = {
        "chrome": "chrome", "calculator": "calc", "calc": "calc", "notepad": "notepad",
        "word": "winword", "excel": "excel", "powerpoint": "powerpnt", "spotify": "spotify",
        "code": "code", "vscode": "code"
    }
    if target in app_aliases:
        os.system(f"start {app_aliases[target]}")
        return f"Launching {target}."

    # 3. Check if it's one of your Coding Projects
    project_result = launch_dev_environment(target)
    if project_result:
        return project_result

    # 4. Check if the app is physically installed in the Windows PATH
    if shutil.which(target):
        os.system(f"start {target}")
        return f"Launching {target}."

    # 5. FALLBACK: App not installed? Search for it on Google via Chrome!
    print(f"[ELE CORE] '{target}' not found locally. Falling back to Web Search...")
    search_url = f"https://www.google.com/search?q={target.replace(' ', '+')}"
    os.system(f"start chrome \"{search_url}\"")
    return f"I couldn't find {target} installed on your system. Searching Chrome instead."

def get_quick_intent(text: str):
    """Zero-Latency Interceptor"""
    t = text.lower().strip()
    
    # Check Launch Commands
    for trigger in ["open", "launch", "run", "start"]:
        if t.startswith(trigger):
            target = t.replace(trigger, "").strip()
            reply = smart_open(target)
            return {"intent": "open_action", "reply": reply}

    # Check Hardware Controls
    if "mute" in t:
        pyautogui.press("volumemute")
        return {"intent": "system_control", "reply": "Audio muted."}
    if "lock" in t and "screen" in t:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return {"intent": "system_control", "reply": "Screen locked."}
    
    return None

# ==========================================
# 🚀 FASTAPI ROUTES
# ==========================================
app = FastAPI(title="ELE Core API", version="3.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class UserInput(BaseModel):
    text: str
    user_id: str = "default_user"

class AIResponse(BaseModel):
    reply: str
    intent: str
    action_required: bool

# ==========================================
# 🛑 WAKE WORD: ACOUSTIC DAEMON
# ==========================================
@app.get("/api/wakeword")
def listen_for_wakeword():
    """Zero-download acoustic trigger loop."""
    print("[ELE DAEMON] 🟢 Acoustic Stealth Mode Active. Waiting for 'Hey ELE'...")
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.5 

    # Phonetic variations to catch mispronunciations
    trigger_words = ["ele", "ellie", "l a", "elliot", "ali", "hello", "hey"]

    with sr.Microphone() as source:
        while True:
            try:
                audio = r.listen(source, timeout=1, phrase_time_limit=2)
                text = r.recognize_google(audio).lower() # type: ignore
                
                print(f"[DAEMON HEARD] -> '{text}'")

                if any(word in text for word in trigger_words):
                    print("\n[ELE DAEMON] 🔥 WAKE WORD CONFIRMED! Releasing hardware...")
                    time.sleep(0.3) 
                    return {"status": "detected", "trigger": text}
                    
            except sr.WaitTimeoutError: continue
            except Exception: continue

# ==========================================
# 🎤 MAIN COMMAND LISTENER
# ==========================================
@app.get("/api/listen")
async def listen_to_mic():
    r = sr.Recognizer()
    r.pause_threshold = 0.8 

    with sr.Microphone() as source:
        try:
            print("[ELE CORE] Microphone open. Listening for command...")
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            text = r.recognize_google(audio) # type: ignore
            print(f"[ELE CORE] Transcribed: {text}")
            return {"text": text}
        except Exception:
            return {"error": "Silence or mic failure."}

# ==========================================
# 🧠 CORE CHAT ENGINE
# ==========================================
@app.post("/api/chat", response_model=AIResponse)
async def process_chat(user_input: UserInput):
    
    quick_fix = get_quick_intent(user_input.text)
    if quick_fix:
        return AIResponse(reply=quick_fix["reply"], intent=quick_fix["intent"], action_required=False)

    try:
        messages: List[Any] = [
            {"role": "system", "content": "You are ELE, an execution-focused OS agent. Respond in strict JSON: {\"reply\":\"Your response\",\"intent\":\"chat|search_web\",\"action_detail\":\"query\"}"},
            *get_memory(limit=5),
            {"role": "user", "content": user_input.text}
        ]

        try:
            response = client_cloud.chat.completions.create(model="openrouter/free", messages=messages) # type: ignore
        except Exception:
            response = client_local.chat.completions.create(model="llama3", messages=messages) # type: ignore
        
        raw = (response.choices[0].message.content or "").strip()
        if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
        parsed = json.loads(raw)
        
        intent = parsed.get("intent", "chat")
        detail = parsed.get("action_detail", "")

        if intent == "search_web":
            parsed["reply"] = perform_web_search(detail)

        save_memory("user", user_input.text)
        save_memory("assistant", parsed.get("reply", ""))

        return AIResponse(reply=parsed.get("reply", "Understood."), intent=intent, action_required=False)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return AIResponse(reply="System hitch, try again.", intent="error", action_required=False)