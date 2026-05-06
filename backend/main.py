import os
import json
import sqlite3
import pyautogui
import subprocess
import difflib
import time
import shutil
import psutil 
import signal  # Added for shutdown logic
import sys     # Added for shutdown logic
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI
from controller import launch_app
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
# ⚡ SHUTDOWN HANDLER (Immediate Kill)
# ==========================================
def signal_handler(sig, frame):
    print("\n[ELE SYSTEM] 🛑 TERMINATING ALL THREADS...")
    os._exit(0) # Hard exit to kill zombie microphone threads immediately

signal.signal(signal.SIGINT, signal_handler)

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
    # Prioritize D:\Projects for your local setup
    base_path = r"D:\Projects" 
    if not os.path.exists(base_path): 
        base_path = r"C:\Users\DELL\OneDrive\Desktop\PROJECTS"
    
    if not os.path.exists(base_path): return "Base path not found."

    existing_projects = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    matches = difflib.get_close_matches(project_query.lower(), [p.lower() for p in existing_projects], n=1, cutoff=0.45)
    
    if not matches: return None

    target_folder = next(p for p in existing_projects if p.lower() == matches[0])
    full_path = os.path.join(base_path, target_folder)

    try:
        os.system(f'code "{full_path}"')
        if os.path.exists(os.path.join(full_path, "package.json")):
            launch_cmd = f'start cmd /k "cd /d {full_path} && title ELE Server: {target_folder} && npm run dev"'
            subprocess.Popen(launch_cmd, shell=True)
            return f"Project {target_folder} initialized. Dev server spinning up."
        return f"Project {target_folder} opened in VS Code."
    except Exception as e:
        return f"Error opening project: {e}"

def smart_open(target: str) -> str:
    web_targets = {"youtube": "https://youtube.com", "google": "https://google.com", "github": "https://github.com"}
    if target.lower() in web_targets:
        os.system(f"start {web_targets[target.lower()]}")
        return f"Opening {target}."

    app_aliases = {
        "chrome": "chrome", "calculator": "calc", "calc": "calc", "notepad": "notepad",
        "word": "winword", "excel": "excel", "powerpoint": "powerpnt", "spotify": "spotify",
        "code": "code", "vscode": "code"
    }
    
    t_clean = target.lower().strip()
    if t_clean in app_aliases:
        os.system(f"start {app_aliases[t_clean]}")
        return f"Launching {target}."

    project_result = launch_dev_environment(target)
    if project_result: return project_result

    if shutil.which(target):
        os.system(f"start {target}")
        return f"Launching {target}."

    search_url = f"https://www.google.com/search?q={target.replace(' ', '+')}"
    os.system(f"start chrome \"{search_url}\"")
    return f"Searching Chrome for {target}."

def get_quick_intent(text: str):
    t = text.lower().strip()
    words = t.split()
    
    # KILLSWITCH: Skip quick-logic for vague references so AI uses Memory
    vague_references = ["it", "again", "that", "those", "previous", "one"]
    if any(word in words for word in vague_references):
        return None

    # --- ENHANCED SYSTEM CONTROLS ---
    if "maximize" in t:
        pyautogui.hotkey('win', 'up')
        return {"intent": "system_control", "reply": "Window maximized."}
        
    if "minimize" in t:
        pyautogui.hotkey('win', 'd')
        return {"intent": "system_control", "reply": "Showing desktop."}

    if "task manager" in t:
        os.system("taskmgr")
        return {"intent": "system_control", "reply": "Opening Task Manager."}

    if "volume up" in t:
        for _ in range(5): pyautogui.press("volumeup")
        return {"intent": "system_control", "reply": "Increasing volume."}

    if "volume down" in t:
        for _ in range(5): pyautogui.press("volumedown")
        return {"intent": "system_control", "reply": "Decreasing volume."}

    if any(phrase in t for phrase in ["start working on", "open project", "load project"]):
        project_name = t.replace("start working on", "").replace("open project", "").replace("load project", "").strip()
        reply = launch_dev_environment(project_name)
        return {"intent": "project_launch", "reply": reply}

    launch_triggers = ["open", "launch", "run", "start", "get me"]
    for trigger in launch_triggers:
        if t.startswith(trigger):
            target = t.replace(trigger, "").strip()
            if not target: continue
            reply = smart_open(target)
            return {"intent": "open_action", "reply": reply}

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

@app.get("/api/system_stats")
async def get_system_stats():
    return {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "temp": "42°C"
    }

@app.post("/api/execute")
async def execute_command(command: dict):
    action = command.get("action")
    target = command.get("target")
    if action == "open":
        app_aliases = {"calculator": "calc", "calc": "calc", "notepad": "notepad", "code": "code"}
        final_target = app_aliases.get(target.lower(), target)
        os.system(f"start {final_target}")
        return {"status": "success"}
    return {"status": "unknown_action"}

@app.get("/api/wakeword")
def listen_for_wakeword():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            try:
                audio = r.listen(source, timeout=1, phrase_time_limit=2)
                text = r.recognize_google(audio).lower() # type: ignore
                if any(word in text for word in ["ele", "hey", "hello"]):
                    return {"status": "detected", "trigger": text}
            except: continue

@app.get("/api/listen")
async def listen_to_mic():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            text = r.recognize_google(audio) # type: ignore
            return {"text": text}
        except: return {"error": "Silence."}

@app.post("/api/chat", response_model=AIResponse)
async def process_chat(user_input: UserInput):
    quick_fix = get_quick_intent(user_input.text)
    if quick_fix:
        return AIResponse(reply=quick_fix["reply"], intent=quick_fix["intent"], action_required=False)

    try:
        history = get_memory(limit=5)
        messages = [
            {
                "role": "system", 
                "content": "You are ELE, an OS agent. If the user says 'again' or 'it', look at the last 'assistant' message in history, find the app name, and set 'action_detail' to THAT app name. Respond in JSON: {\"reply\":\"...\",\"intent\":\"open_action|chat|search_web\",\"action_detail\":\"...\"}"
            },
            *history,
            {"role": "user", "content": user_input.text}
        ]

        try:
            response = client_cloud.chat.completions.create(model="openrouter/free", messages=messages) # type: ignore
        except:
            response = client_local.chat.completions.create(model="llama3", messages=messages) # type: ignore
        
        raw = (response.choices[0].message.content or "").strip()
        if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
        parsed = json.loads(raw)
        
        intent = parsed.get("intent", "chat")
        detail = parsed.get("action_detail", "")

        if intent == "search_web":
            parsed["reply"] = perform_web_search(detail)
        elif (intent == "open_action" or "open" in user_input.text.lower()) and detail:
            parsed["reply"] = smart_open(detail)

        save_memory("user", user_input.text)
        save_memory("assistant", parsed.get("reply", ""))
        return AIResponse(reply=parsed.get("reply", "Understood."), intent=intent, action_required=False)

    except Exception as e:
        return AIResponse(reply=f"Core error: {e}", intent="error", action_required=False)