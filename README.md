# ELE v0.1 (Execution-Focused AI System)

ELE is a modular, task-executing AI system. This is the MVP (v0.1). It takes voice input, processes intent via an LLM, and executes local actions.

## 👥 Team Structure & Folders

* **`backend/` (Dev A - Core AI):** FastAPI server, Gemini LLM integration, intent detection, and memory.
* **`voice/` (Friend 1 - Voice Layer):** Speech-to-text (STT), text-to-speech (TTS), and the audio interaction loop.
* **`frontend/` (Friend 2 - UI & Execution):** React/Electron dashboard, command display, and system automation (opening apps, writing notes).

## 🚀 How to Run the Backend (Core API)

Right now, the Core API is up and running with Gemini 1.5 Flash and Intent Detection. To run it locally:

1. **Navigate to the backend:**
   ```bash
   cd backend
Create and activate a virtual environment:

Bash
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
Install dependencies:

Bash
pip install -r requirements.txt
Environment Variables:
Create a .env file in the backend/ folder and add your Gemini API key:

Code snippet
GEMINI_API_KEY=your_api_key_here
Start the server:

Bash
uvicorn main:app --reload
Test the API: Open http://127.0.0.1:8000/docs in your browser.

🔁 Git Workflow (MANDATORY)
NEVER push directly to main.

Always create a feature branch: git checkout -b feature/your-feature-name

Push your branch and open a Pull Request (PR).

Review and merge into main.


### Step 2: Push Everything to GitHub
Make sure you are on the `main` branch, then commit and push the README so your friends can see it.

Run these commands in your terminal:
```bash
# Make sure you are on main and up to date
git checkout main
git pull origin main

# Add the README
git add README.md

# Commit the changes
git commit -m "docs: add project overview and setup instructions to README"

# Push to the main repository
git push origin main
Step 3: Send This Message to Your Friends
Copy and paste this message to your friends (Discord, WhatsApp, etc.) to get them moving:

"Yo, the ELE monorepo is set up and the Core API (brain) is live on the main branch. It connects to Gemini and has intent detection working (chat, open_app, search_web, create_note).

Action items:

git pull origin main to get the latest code.

Read the README.md for instructions on how to spin up the backend locally. You'll need your own free Gemini API key in a .env file to test it.

Friend 1 (Voice): Start setting up the STT script in the voice/ folder. We need it to capture mic input and send the text to http://127.0.0.1:8000/api/chat.

Friend 2 (Frontend): Start scaffolding the React app in the frontend/ folder. Build a basic UI that can hit the API and display the returned intent and reply. Let's go! 🚀"

Once they pull the code, the ball is in their court to start building the UI and Voice modules.