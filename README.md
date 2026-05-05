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


6 may 
# ELE: Stealth Neural Assistant 🧠

> An execution-focused, autonomous OS AI agent built for high-performance desktop automation and developer workflows.

ELE is a real-time, voice-activated AI operating system bridge. It sits silently in the background, processes acoustic triggers with zero-download wake word technology, and executes intelligent routing to open applications, initialize development environments, or query the web.

## ✨ Core Architecture & Features

*   **Acoustic Stealth Daemon:** Continuous, lightweight background wake word detection ("Hey ELE") using highly optimized audio chunking—no heavy local model downloads required.
*   **Zero-Latency Fast-Path:** A heuristic interceptor that catches basic system commands (e.g., "Open Chrome", "Mute Audio") and executes them instantly, bypassing the LLM entirely.
*   **Dual-Engine Brain:** Cloud-first reasoning via OpenRouter with an automatic failsafe connection to local Ollama (Llama 3) models, ensuring 100% uptime even if the cloud drops.
*   **Smart Workflow Router:** Dynamically maps spoken project names to local file paths, launches VS Code, and spins up local `npm run dev` servers autonomously.
*   **Neural Dashboard UI:** A desktop-first React frontend featuring glassmorphism, 3D CSS orb animations, and a real-time hardware sync monitor.

## 🛠️ Tech Stack

*   **Frontend:** React, Vanilla CSS (Custom 3D Animations & Glassmorphism)
*   **Backend:** Python 3.13, FastAPI
*   **AI/LLM:** OpenAI SDK, OpenRouter, Ollama (Local)
*   **Speech & Audio:** `SpeechRecognition`, `PyAudio`
*   **System Automation:** `pyautogui`, `subprocess`, `os`
*   **Memory:** SQLite (Short-term chat context)

## 🚀 Getting Started

### Prerequisites
*   Node.js & npm
*   Python 3.13+
*   Microphone access

### 1. Backend Setup
Navigate to the backend directory and install the required Python packages.
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # On Windows
pip install -r requirements.txt
Create a .env file in the backend directory and add your OpenRouter API key:

Code snippet
OPENROUTER_API_KEY=your_api_key_here
Start the ELE Core API:

Bash
uvicorn main:app
(Note: Do not use the --reload flag during normal operation to prevent audio hardware lock collisions).

2. Frontend Setup
Navigate to the frontend directory and start the Neural Dashboard.

Bash
cd frontend
npm install
npm run dev
🎙️ Usage
Wait for the System Status to show IDLE.

Say "Hey ELE" to wake the acoustic daemon.

Once the UI transitions to LISTENING, state your command (e.g., "Open Calculator", "Launch Save Era", or "Search the web for the latest AI news").

ELE will execute the OS-level command or respond via the neural text-to-speech UI.

Author: Umar Ahmed


---

### 2. Push Your Code to GitHub

Once you have saved the `README.md`, open your terminal at the root of your project folder (the folder containing both your `frontend` and `backend` folders) and run these commands step-by-step:

**Step 1: Initialize the repository (if you haven't already)**
```bash
git init
Step 2: Add all your files to the staging area

Bash
git add .
Step 3: Commit your code with a descriptive message

Bash
git commit -m "V3 Release: Integrated Acoustic Daemon, Fast-Path Heuristics, and Neural Dashboard UI"
Step 4: Connect to your GitHub repository
(If you haven't created a blank repo on GitHub yet, go do that now. Grab the URL it gives you, which looks like [https://github.com/yourusername/ele-v0.1.git](https://github.com/yourusername/ele-v0.1.git))

Bash
git remote add origin YOUR_GITHUB_REPO_URL_HERE
Step 5: Push the code to the main branch

Bash
git branch -M main
git push -u origin main