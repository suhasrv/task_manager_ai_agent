# 🛠️ Complete Project Setup Guide (HOW TO SETUP)

Welcome to the **Task Manager Agent Studio** setup guide! This document provides a complete, beginner-friendly, step-by-step walkthrough to get the entire autonomous agent orchestration platform running on your local machine.

---

## 📋 Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Step 1: Clone the Repository](#step-1-clone-the-repository)
3. [Step 2: Create & Activate Virtual Environment](#step-2-create--activate-virtual-environment)
4. [Step 3: Install Python Dependencies](#step-3-install-python-dependencies)
5. [Step 4: Set Up Relational Database (Supabase PostgreSQL)](#step-4-set-up-relational-database-supabase-postgresql)
6. [Step 5: Configure Environment Variables (.env)](#step-5-configure-environment-variables-env)
7. [Step 6: Launch the Application](#step-6-launch-the-application)
8. [Step 7: Verification & Testing](#step-7-verification--testing)
9. [Troubleshooting & Common Questions](#troubleshooting--common-questions)

---

## 1. Prerequisites

Ensure you have the following installed on your machine before starting:
- **Python**: Version `3.10`, `3.11`, or `3.12` installed ([Download Python](https://www.python.org/downloads/)).
  - *Verify:* `python --version`
- **Git**: Installed and configured ([Download Git](https://git-scm.com/)).
  - *Verify:* `git --version`
- **Supabase Account**: Free cloud PostgreSQL database ([supabase.com](https://supabase.com/)).
- **LLM API Key** (at least one):
  - **NVIDIA NIM API Key** (Recommended & Primary, free tier available at [build.nvidia.com](https://build.nvidia.com/))
  - *or* **Google Gemini API Key** ([aistudio.google.com](https://aistudio.google.com/))
  - *or* **OpenAI API Key** ([platform.openai.com](https://platform.openai.com/))

---

## Step 1: Clone the Repository

Open your terminal (PowerShell, Command Prompt, or Bash) and clone the repository:

```bash
git clone https://github.com/suhasrv/task_manager_ai_agent.git
cd task_manager_ai_agent
```

---

## Step 2: Create & Activate Virtual Environment

Always use an isolated virtual environment to avoid dependency conflicts:

### 🪟 Windows (PowerShell / Command Prompt):
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (PowerShell)
.\venv\Scripts\Activate.ps1

# (If you get an execution policy error in PowerShell, run once:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser)
```

### 🐧 Linux / 🍎 macOS / 🐚 Git Bash:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

*(When activated, you will see `(venv)` prepended to your terminal prompt).*

---

## Step 3: Install Python Dependencies

With your virtual environment activated, upgrade `pip` and install all required production dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 4: Set Up Relational Database (Supabase PostgreSQL)

The system uses **Supabase** for relational persistence of tasks, schedules, and reminders:

1. Log into your **[Supabase Dashboard](https://supabase.com/dashboard)**.
2. Click **New Project** and name it (e.g. `task-manager`).
3. Once the project is created, navigate to the **SQL Editor** tab (icon `<_` on the left sidebar).
4. Click **New query**.
5. Open the file **`supabase_schema.sql`** in this repository, copy its entire contents, paste it into the Supabase SQL editor, and click **Run**.
   - *This creates the `tasks`, `calendar_events`, and `reminders` tables along with automated updated-at triggers.*
6. Go to **Project Settings** $\to$ **API**:
   - Copy your **Project URL** (e.g., `https://xyzcompany.supabase.co`).
   - Copy your **Project API anon / service_role key**.

---

## Step 5: Configure Environment Variables (`.env`)

Copy the provided template to create your `.env` file:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux / Mac / Git Bash
cp .env.example .env
```

Open the newly created `.env` file in your favorite code editor and fill in your keys:

```ini
# ==============================================================================
# API Server Configuration
# ==============================================================================
API_URL=http://127.0.0.1:8000/api/v1
PORT=8000
DEBUG=False

# ==============================================================================
# Primary LLM: NVIDIA NIM (Nemotron-3-nano)
# ==============================================================================
NVIDIA_API_KEY=nvapi-your-key-here
LLM_MODEL=nvidia/nemotron-3-nano
LLM_TEMPERATURE=0.2

# ==============================================================================
# Fallback LLMs (Optional but recommended for automated failover)
# ==============================================================================
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# ==============================================================================
# Database: Supabase PostgreSQL
# ==============================================================================
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_API_KEY=your-supabase-key-here
SUPABASE_DB_NAME=task_manager

# ==============================================================================
# Vector Store: ChromaDB
# ==============================================================================
CHROMADB_PERSIST_DIR=./chroma_data
CHROMADB_COLLECTION_NAME=task_embeddings

# ==============================================================================
# Scheduler & Logging
# ==============================================================================
SCHEDULER_ENABLED=True
REMINDER_CHECK_INTERVAL_MINUTES=5
LOG_LEVEL=INFO
```

---

## Step 6: Launch the Application

We provide automated launch scripts for all operating systems.

### 🌟 Method A: Automated Launcher (Recommended)

- **Windows One-Click (File Explorer)**:
  Double-click **`restart_servers.bat`**. It will automatically clear ports, launch backend and frontend servers in separate popup windows, and open your browser!
- **Linux / macOS / Git Bash**:
  ```bash
  chmod +x restart_servers.bash
  ./restart_servers.bash
  ```
- **Windows PowerShell**:
  ```powershell
  .\restart_servers.ps1
  ```

---

### 💻 Method B: Manual Startup (Two Terminals)

If you prefer to start each service manually:

#### Terminal 1 — Start FastAPI Backend:
```powershell
cd task_manager_ai_agent
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend runs on: [http://127.0.0.1:8000](http://127.0.0.1:8000)*

#### Terminal 2 — Start Streamlit Frontend:
```powershell
cd task_manager_ai_agent
.\venv\Scripts\Activate.ps1
streamlit run frontend/app.py --server.port 8501
```
*Frontend runs on: [http://localhost:8501](http://localhost:8501)*

---

## Step 7: Verification & Testing

### 1. Verify Service Health
- **Backend Health Check**: Open [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health) $\to$ should return:
  ```json
  {"status": "healthy", "version": "1.0.0"}
  ```
- **Interactive API Documentation**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to explore all FastAPI endpoints.
- **Frontend AI Studio**: Open [http://localhost:8501](http://localhost:8501) in your browser. Verify the green dot shows *"Backend Online"*.

### 2. Run the Automated Unit Test Suite
To verify database connections, tool calls, and model initialization:
```bash
pytest -v
```
*Expected result: 29 passed (100% pass rate).*

### 3. Run the LLMOps Evaluation Benchmark (Optional)
To run the automated 40-prompt benchmark measuring Tool-Call Accuracy and Task Success:
```bash
python -m backend.evals.run_evals
```

---

## ❓ Troubleshooting & Common Questions

### Q1: `ModuleNotFoundError: No module named 'frontend'` or `backend`
- **Solution:** Always run your commands from the **root directory** of the project (`task_manager_ai_agent`). The application dynamically injects the root directory into `sys.path`.

### Q2: Port 8000 or 8501 is already in use
- **Solution:** Run the restart script:
  - Windows: `restart_servers.bat` or `.\restart_servers.ps1`
  - Linux/Git Bash: `./restart_servers.bash`
  This will automatically find and terminate any lingering zombie processes on ports 8000 and 8501.

### Q3: AI Agent returns *"Could not reach AI Agent: API key missing"*
- **Solution:** Verify that your `.env` file has a valid `NVIDIA_API_KEY` (or `GEMINI_API_KEY` / `OPENAI_API_KEY`). Ensure there are no surrounding quotes or extra spaces.

### Q4: ChromaDB vector search errors on first run
- **Solution:** ChromaDB automatically initializes its local database directory at `./chroma_data` on first run. If you ever want to reset the vector index from scratch, simply delete the `./chroma_data` folder and restart the backend.

---

### 🎉 You're all set!
Navigate to **[http://localhost:8501](http://localhost:8501)** to manage tasks, explore the Kanban board, and chat with your autonomous LangGraph AI Agent!
