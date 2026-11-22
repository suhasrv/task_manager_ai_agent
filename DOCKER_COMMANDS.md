# 🐳 Docker Commands Reference

## Quick Start

### 1. Build Docker Images

**Build both images:**
```powershell
docker-compose build
```

**Build individual images:**
```powershell
# Backend
docker build -f Dockerfile.backend -t suhasvr/task_manager_agent:backend-latest .

# Frontend
docker build -f Dockerfile.frontend -t suhasvr/task_manager_agent:frontend-latest .
```

### 2. Run the Project

**Start all services:**
```powershell
docker-compose up -d
```

**View logs:**
```powershell
docker-compose logs -f          # All services
docker-compose logs backend      # Backend only
docker-compose logs frontend     # Frontend only
```

**Stop services:**
```powershell
docker-compose down
```

**Restart services:**
```powershell
docker-compose restart
```

**Check status:**
```powershell
docker-compose ps
```

### 3. Push Images to Docker Hub

**Using the script (recommended):**
```powershell
.\build-and-push.ps1 -Tag "v1.0.0"
```

**Manual push:**
```powershell
# Tag images
docker tag suhasvr/task_manager_agent:backend-latest suhasvr/task_manager_agent:backend-v1.0.0
docker tag suhasvr/task_manager_agent:frontend-latest suhasvr/task_manager_agent:frontend-v1.0.0

# Push to Docker Hub (login first: docker login)
docker push suhasvr/task_manager_agent:backend-v1.0.0
docker push suhasvr/task_manager_agent:backend-latest
docker push suhasvr/task_manager_agent:frontend-v1.0.0
docker push suhasvr/task_manager_agent:frontend-latest
```

### 4. Pull and Run from Docker Hub

**Pull images:**
```powershell
docker pull suhasvr/task_manager_agent:backend-latest
docker pull suhasvr/task_manager_agent:frontend-latest
```

**Run using docker-compose:**
```powershell
docker-compose up -d
```

## Access Points

- **Frontend:** http://localhost:8501
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/v1/health

## Environment Variables

Create a `.env` file in the project root with:
```env
# LLM Configuration
GOOGLE_GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_claude_key

# Database Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_key

# Optional
LLM_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.7
```

## Troubleshooting

**View container logs:**
```powershell
docker-compose logs backend
docker-compose logs frontend
```

**Restart a specific service:**
```powershell
docker-compose restart backend
docker-compose restart frontend
```

**Rebuild and restart:**
```powershell
docker-compose up -d --build
```

**Remove everything (containers, networks, volumes):**
```powershell
docker-compose down -v
```

