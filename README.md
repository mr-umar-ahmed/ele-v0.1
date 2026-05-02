# ELE: Autonomous Local Desktop OS

ELE is a privacy-first, offline-capable AI desktop assistant. It bypasses standard browser sandboxes to interact directly with the local Windows operating system, hardware microphones, and application binaries.

## 🚀 Architecture: What We Built (Sprints 1-5)

* **The React + Electron Frontend:** A sleek, glassmorphic UI that acts as the visual terminal.
* **The Python FastAPI Backend:** The core logic server that processes all commands and hardware requests.
* **The Dual-Engine Brain:** 
  * *Primary:* OpenRouter Cloud (Fast, lightweight).
  * *Failover:* Local Ollama + Llama 3 (Triggers instantly if Wi-Fi drops, ensuring 100% offline uptime).
* **The Python Ear:** Direct hardware microphone integration using `SpeechRecognition` and `PyAudio`, completely bypassing Electron's blocked web audio APIs.
* **The Memory Layer:** A local SQLite database that logs conversation history for context awareness.
* **The OS God Mode & App Automator:** Uses Python's `os` and `pyautogui` modules to execute system-level commands (Volume, Lock Screen) and launch development applications (VS Code, Chrome).

---

## 🛠️ Sprint 6: Team Task Delegation

The core infrastructure is stable. We are now splitting up to build the "Magic" features. Please claim a task and branch off `main`.

### Task 1: The Wake Word Engine (Background Listener)
* **Goal:** Remove the need to click the "Initialize Microphone" button. 
* **Details:** Integrate a lightweight audio model (like Picovoice Porcupine) into the Python backend so ELE is always listening for "Hey ELE", triggering the main recording loop automatically.
* **Assigned To:** [Teammate Name Here]

### Task 2: The Real-Time Audio Visualizer
* **Goal:** Make the frontend react to the user's voice.
* **Details:** Update `App.jsx` to capture live microphone data and render a pulsing, dynamic waveform or glowing orb that changes based on pitch/volume and system state (Idle, Listening, Thinking).
* **Assigned To:** [Teammate Name Here]

### Task 3: Advanced Developer Workflows
* **Goal:** Upgrade the App Automator to handle complex directory setups.
* **Details:** Instead of just opening VS Code, teach Python to navigate to specific project folders, split the terminal, and automatically run `npm run dev` or Python virtual environments based on the project requested.
* **Assigned To:** [Teammate Name Here]

---

## ⚙️ How to Run Locally

1. **Start the Backend:**
   ```bash
   cd backend
   venv\Scripts\activate
   uvicorn main:app --reload
Start the Frontend (Electron + Vite):

Bash
cd frontend
npm run dev
npm run electron:start

### Step 2: Push to GitHub
Once you have saved the `README.md`, open a new terminal in your root folder (outside of `backend` and `frontend`) and run these exact commands to push the entire Sprint 1-5 package to your repository.

## 🚀 Sprint 6 Updates (ELE Core Daemon)
We have successfully upgraded ELE from a click-to-talk chatbot to a hands-free, autonomous background daemon.

**New Features Engineered:**
* **Stealth Wake Word Engine:** Integrated `openwakeword` for a zero-click, offline background listener. (Currently using the "Hey Jarvis" acoustic model as a placeholder for ELE).
* **Python Audio Bridge:** Bypassed Electron's strict microphone API blocks by building a custom hardware audio router in FastAPI using `speech_recognition` and `PyAudio`.
* **SQLite Memory Layer:** Added short-term contextual memory so ELE remembers conversational facts without breaking OS commands.
* **Developer Automator:** Added the `dev_workflow` intent. ELE can now dynamically locate project folders (like Save Era or ShopSync AI), launch VS Code, and spin up local `npm run dev` servers via voice command.

**Setup Instructions for Teammates:**
1. Pull the latest code.
2. Navigate to `/backend` and run `pip install -r requirements.txt`.
3. You may need to install standard C++ build tools if `PyAudio` throws a compilation error on Windows.