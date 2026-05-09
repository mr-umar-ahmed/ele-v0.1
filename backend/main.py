import os
import json
import sqlite3
import pyautogui
import subprocess
import difflib
import time
import shutil
import asyncio
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from duckduckgo_search import DDGS
import speech_recognition as sr
import edge_tts
import pygame

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
# 🔊 VOICE REPLIES (Neural TTS)
# ==========================================
async def speak(text: str):
    """Generates a sultry and attractive neural voice reply."""
    # Sonia is the top free pick for a sophisticated, velvety tone
    VOICE = "en-GB-SoniaNeural" 
    OUTPUT_FILE = "reply.mp3"
    
    try:
        # Stop any existing audio immediately
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()

        # --- SEDUCTIVE TUNING ---
        # rate="-18%": Slower pace makes the voice feel more intimate.
        # pitch="-12Hz": Lowering the pitch adds a warm, smoky resonance.
        communicate = edge_tts.Communicate(text, VOICE, rate="-18%", pitch="-12Hz")
        await communicate.save(OUTPUT_FILE)

        # Initialize and play
        pygame.mixer.init()
        pygame.mixer.music.load(OUTPUT_FILE)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.05)
        
        pygame.mixer.quit()
    except Exception as e:
        print(f"[VOICE ERROR] {e}")

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
    web_targets = {"youtube": "https://youtube.com", "google": "https://google.com", "github": "https://github.com"}
    if target in web_targets:
        os.system(f"start {web_targets[target]}")
        return f"Opening {target}."
    app_aliases = {"chrome": "chrome", "calculator": "calc", "calc": "calc", "notepad": "notepad", "code": "code"}
    if target in app_aliases:
        os.system(f"start {app_aliases[target]}")
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
    
    # Check Launch Commands
    for trigger in ["open", "launch", "run", "start"]:
        if t.startswith(trigger):
            target = t.replace(trigger, "").strip()
            
            # --- THE SPEED FIX ---
            # Define the reply first
            reply = f"Opening {target} now."
            
            # Trigger the voice immediately in the background
            asyncio.create_task(speak(reply))
            
            # Then perform the OS action
            smart_open(target)
            
            return {"intent": "open_action", "reply": reply}

    # Check Hardware Controls
    if "mute" in t:
        pyautogui.press("volumemute")
        asyncio.create_task(speak("Audio muted."))
        return {"intent": "system_control", "reply": "Audio muted."}
        
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
# 🛑 WAKE WORD: OPTIMIZED ACOUSTIC LOGIC
# ==========================================
@app.get("/api/wakeword")
def listen_for_wakeword():
    print("[ELE DAEMON] 🟢 Performance Mode Active. Listening...")
    r = sr.Recognizer()
    r.energy_threshold = 350 
    r.dynamic_energy_threshold = True
    r.dynamic_energy_adjustment_damping = 0.15 
    r.pause_threshold = 0.4 

    trigger_variants = ["ele", "ellie", "ali", "hey", "hello", "l a", "elliot", "early"]

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        while True:
            try:
                audio = r.listen(source, timeout=1, phrase_time_limit=1.5)
                text = r.recognize_google(audio).lower()
                words = text.split()
                is_triggered = any(len(difflib.get_close_matches(w, trigger_variants, cutoff=0.7)) > 0 for w in words)

                if is_triggered:
                    print("\n[ELE DAEMON] 🔥 TRIGGER DETECTED!")
                    return {"status": "detected", "trigger": text}
            except (sr.WaitTimeoutError, sr.UnknownValueError): continue
            except Exception: continue

# ==========================================
# 🎤 MAIN COMMAND LISTENER (Optimized Spans)
# ==========================================
@app.get("/api/listen")
async def listen_to_mic():
    r = sr.Recognizer()
    r.pause_threshold = 1.5 
    r.non_speaking_duration = 0.5 

    with sr.Microphone() as source:
        try:
            print("[ELE CORE] 🎤 Microphone open. Listening...")
            audio = r.listen(source, timeout=3, phrase_time_limit=15)
            text = r.recognize_google(audio)
            print(f"[ELE CORE] Transcribed: '{text}'")
            return {"text": text}
        except sr.WaitTimeoutError: return {"error": "Silence"}
        except sr.UnknownValueError: return {"error": "Unintelligible"}
        except Exception as e: return {"error": str(e)}

# ==========================================
# 🧠 CORE CHAT ENGINE
# ==========================================
@app.post("/api/chat", response_model=AIResponse)
async def process_chat(user_input: UserInput):
    # 1. SHUT UP immediately when a new command starts
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()

    # 2. Check for Quick Intents (Opening Apps, etc.)
    quick_fix = get_quick_intent(user_input.text)
    if quick_fix:
        # Voice reply is already handled inside get_quick_intent for speed
        return AIResponse(reply=quick_fix["reply"], intent=quick_fix["intent"], action_required=False)

    try:
        # 3. Prepare AI Context
        messages = [
            {"role": "system", "content": "You are ELE, an execution-focused OS agent. Respond in strict JSON: {\"reply\":\"Your response\",\"intent\":\"chat|search_web\",\"action_detail\":\"query\"}"},
            *get_memory(limit=5),
            {"role": "user", "content": user_input.text}
        ]

        # 4. Get AI Response (Cloud with Local Fallback)
        try:
            response = client_cloud.chat.completions.create(model="openrouter/free", messages=messages) # type: ignore
        except Exception:
            response = client_local.chat.completions.create(model="llama3", messages=messages) # type: ignore
        
        raw = (response.choices[0].message.content or "").strip()
            
        # 5. Clean JSON parsing logic (ASCII trick to avoid Pylance red lines)
        tick = chr(96) * 3 
        if f"{tick}json" in raw: 
            raw = raw.split(f"{tick}json")[1].split(tick)[0].strip()
        elif tick in raw:
            raw = raw.split(tick)[1].split(tick)[0].strip()
                
        parsed = json.loads(raw)
        intent = parsed.get("intent", "chat")
        
        # 6. Handle Web Search
        if intent == "search_web":
            parsed["reply"] = perform_web_search(parsed.get("action_detail", ""))

        # 7. Update Memory
        save_memory("user", user_input.text)
        save_memory("assistant", parsed.get("reply", ""))

        # 8. Trigger Voice Reply & Return
        final_reply = parsed.get("reply", "Understood.")
        asyncio.create_task(speak(final_reply))

        return AIResponse(reply=final_reply, intent=intent, action_required=False)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return AIResponse(reply="System hitch, try again.", intent="error", action_required=False)