# **Task Manager Agent**

An intelligent AI-powered task management system with natural language task creation, semantic search, automated reminders, and an interactive dashboard.
Built with **FastAPI**, **Streamlit**, **LangChain**, **Supabase**, and **ChromaDB**.

---

##  **Features**

### **Core Functionality**

* **AI-Powered Task Management** — Create and update tasks using natural language.
* **Conversational Task Agent** — Chat with an intelligent agent to manage tasks.
* **Semantic Search (ChromaDB)** — Find tasks using vector embeddings.
* **Complete Task CRUD** — Create, read, update, delete operations.
* **Priority & Status Workflow** — Low, medium, high, urgent + pending/in-progress/completed.
* **Smart Due Dates** — “Today”, “Tomorrow”, “Evening”, etc.
* **Time Estimation** — Track estimated hours and minutes.
* **Tags/Categories** — Organize tasks with custom tags.
* **Reminders** — Automated reminder scheduling.
* **Calendar Integration Ready** — Google Calendar–ready schema.

### **User Interface**

* **Interactive Dashboard** — task stats, recent activity, quick actions.
* **Task Creation Form** — intuitive UI for task input.
* **Task List View** — filter, search, sort.
* **Calendar View** — visual timeline of tasks.
* **AI Chat Interface** — manage tasks with conversational AI.

---

##  **Prerequisites**

* Python 3.10+
* Supabase project (database)
* OpenAI API Key (required for AI agent)
* Anthropic API Key (optional)

---

##  **Installation**

### **1. Clone Repository**



### **2. Create Virtual Environment**

**Windows**

```powershell
python -m venv venv
. venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
python -m venv venv
source venv/bin/activate
```

### **3. Install Dependencies**

```bash
pip install -r requirements-final.txt
```

### **4. Environment Variables**

Create a `.env` file:

```env
# API Configuration
API_TITLE=Task Manager Agent API
API_VERSION=1.0.0
DEBUG=False

# LLM Configuration
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=optional
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7

# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your_supabase_api_key
SUPABASE_DB_NAME=task_manager

# ChromaDB
CHROMADB_PERSIST_DIR=./chroma_data
CHROMADB_COLLECTION_NAME=task_embeddings

# Scheduler
SCHEDULER_ENABLED=True
REMINDER_CHECK_INTERVAL_MINUTES=5

# Logging
LOG_LEVEL=INFO

# Frontend
API_URL=http://localhost:8000/api/v1
```

---

##  **Supabase Setup**

1. Open Supabase Dashboard
2. Go to **SQL Editor**
3. Run:

   * `supabase_schema.sql`
   * `setup_reminders_table.sql`
   * (optional) `setup_notifications_table.sql`

Tables created:

* `tasks`
* `reminders`
* `calendar_events`

---

##  **Running the App**

### **Start Backend**

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

* API → [http://localhost:8000](http://localhost:8000)
* Docs → [http://localhost:8000/docs](http://localhost:8000/docs)
* Base Path → `/api/v1`

### **Start Frontend**

```bash
streamlit run frontend/app.py --server.port 8501
```

Frontend → **[http://localhost:8501](http://localhost:8501)**

---

##  **Usage**

### **AI Agent — Example Commands**

* Create tasks:

  * “Create a task to walk in the evening”
  * “Create a high priority task to finish report today”
* Read tasks:

  * “Show me all pending tasks”
  * “List all high priority tasks”
* Update tasks:

  * “Update task 14 to completed”
* Reminders:

  * “Create a reminder for task 7 in 1 hour”

### **Manual UI**

* Dashboard → overview
* Create Task → form input
* Task List → browse/filter/search
* Calendar → timeline view

---

##  **Project Structure**

```
Suhas_projects/
├── backend/
│   ├── agents/
│   ├── api/
│   ├── database/
│   ├── models/
│   ├── services/
│   ├── config.py
│   └── main.py
├── frontend/
│   ├── app.py
│   ├── components/
│   ├── pages/
│   └── utils/
├── supabase_schema.sql
├── setup_reminders_table.sql
├── setup_notifications_table.sql
├── requirements-final.txt
└── README.md
```

---

##  **API Endpoints**

### **Tasks**

* `POST /api/v1/tasks`
* `GET /api/v1/tasks`
* `GET /api/v1/tasks/{task_id}`
* `PUT /api/v1/tasks/{task_id}`
* `DELETE /api/v1/tasks/{task_id}`

### **AI Agent**

* `POST /api/v1/agent/chat`
* `GET /api/v1/agent/summary`
* `GET /api/v1/agent/next-task`

### **Search**

* `GET /api/v1/search?q=query`

---

##  **Testing**

Available tests:

* `test_backend.py`
* `test_api.py`
* `test_databases.py`
* `test_agent_chat.py`
* `test_frontend.py`

Run tests:

```bash
python test_backend.py
python test_api.py
```

---

##  **Troubleshooting**

### **Common Issues**

| Issue                    | Fix                                    |
| ------------------------ | -------------------------------------- |
| OpenAI Quota Exceeded    | Check usage & billing                  |
| ModuleNotFoundError      | Activate venv + reinstall requirements |
| Supabase connection fail | Verify `.env` values                   |
| Port already in use      | Change backend/ frontend ports         |

---

##  **Future Enhancements**

* [ ] Google Calendar Sync
* [ ] Email + Push Notifications
* [ ] Notion Integration
* [ ] Task Templates
* [ ] Team/Collaboration Support
* [ ] Mobile App
* [ ] Advanced Analytics

---

##  **License**

This project is part of the **AI Agent Development Challenge**.

---

##  **Contributing**

Contributions & improvements are welcome!

