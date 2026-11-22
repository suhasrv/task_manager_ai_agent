# Docker Setup Guide

This guide explains how to build, run, and push Docker images for the Task Manager Agent.

## 📦 Docker Images

The project consists of two Docker images:
- **Backend**: FastAPI application (port 8000)
- **Frontend**: Streamlit application (port 8501)

## 🏗️ Building Images

### Build Individual Images

**Backend:**
```bash
docker build -f Dockerfile.backend -t suhasvr/task_manager_agent:backend-latest .
```

**Frontend:**
```bash
docker build -f Dockerfile.frontend -t suhasvr/task_manager_agent:frontend-latest .
```

### Build with Tag

**Windows (PowerShell):**
```powershell
.\build-and-push.ps1 -Tag "v1.0.0"
```

**Linux/Mac:**
```bash
chmod +x build-and-push.sh
./build-and-push.sh v1.0.0
```

## 🚀 Running Containers

### Using Docker Compose (Recommended)

1. **Create `.env` file** with your configuration:
```env
GOOGLE_GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_key
```

2. **Start services:**
```bash
docker-compose up -d
```

3. **View logs:**
```bash
docker-compose logs -f
```

4. **Stop services:**
```bash
docker-compose down
```

### Running Individual Containers

**Backend:**
```bash
docker run -d \
  --name task_manager_backend \
  -p 8000:8000 \
  -e SUPABASE_URL=your_url \
  -e SUPABASE_API_KEY=your_key \
  -e GOOGLE_GEMINI_API_KEY=your_key \
  -v chroma_data:/app/chroma_data \
  suhasvr/task_manager_agent:backend-latest
```

**Frontend:**
```bash
docker run -d \
  --name task_manager_frontend \
  -p 8501:8501 \
  -e API_URL=http://localhost:8000/api/v1 \
  suhasvr/task_manager_agent:frontend-latest
```

## 📤 Pushing to Docker Hub

### Prerequisites

1. **Login to Docker Hub:**
```bash
docker login
```

2. **Ensure you have push access** to `suhasvr/task_manager_agent`

### Push Images

**Using Script (Recommended):**

**Windows:**
```powershell
.\build-and-push.ps1 -Tag "v1.0.0"
```

**Linux/Mac:**
```bash
./build-and-push.sh v1.0.0
```

**Manual Push:**
```bash
# Tag and push backend
docker tag suhasvr/task_manager_agent:backend-latest suhasvr/task_manager_agent:backend-v1.0.0
docker push suhasvr/task_manager_agent:backend-v1.0.0
docker push suhasvr/task_manager_agent:backend-latest

# Tag and push frontend
docker tag suhasvr/task_manager_agent:frontend-latest suhasvr/task_manager_agent:frontend-v1.0.0
docker push suhasvr/task_manager_agent:frontend-v1.0.0
docker push suhasvr/task_manager_agent:frontend-latest
```

## 🔍 Image Tags

Images are tagged with:
- `backend-latest` / `frontend-latest` - Latest stable version
- `backend-<tag>` / `frontend-<tag>` - Specific version (e.g., `v1.0.0`)

## 📥 Pulling Images

```bash
# Pull latest
docker pull suhasvr/task_manager_agent:backend-latest
docker pull suhasvr/task_manager_agent:frontend-latest

# Pull specific version
docker pull suhasvr/task_manager_agent:backend-v1.0.0
docker pull suhasvr/task_manager_agent:frontend-v1.0.0
```

## 🐳 Docker Compose Configuration

The `docker-compose.yml` file includes:
- **Health checks** for both services
- **Volume persistence** for ChromaDB data
- **Environment variable** management
- **Service dependencies** (frontend waits for backend)

## 🔧 Environment Variables

### Backend Required:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_API_KEY` - Your Supabase API key
- `GOOGLE_GEMINI_API_KEY` - Google Gemini API key (or OpenAI/Anthropic)

### Frontend Required:
- `API_URL` - Backend API URL (automatically set in docker-compose)

See `.env.example` for all available variables.

## 🏥 Health Checks

Both containers include health checks:
- **Backend**: `http://localhost:8000/api/v1/health`
- **Frontend**: `http://localhost:8501/_stcore/health`

## 📊 Monitoring

**View container status:**
```bash
docker ps
docker-compose ps
```

**View logs:**
```bash
docker logs task_manager_backend
docker logs task_manager_frontend
docker-compose logs -f
```

## 🛠️ Troubleshooting

### Backend won't start
- Check environment variables are set correctly
- Verify Supabase credentials
- Check logs: `docker logs task_manager_backend`

### Frontend can't connect to backend
- Ensure backend is running and healthy
- Check `API_URL` environment variable
- Verify network connectivity in docker-compose

### Port conflicts
- Change ports in `docker-compose.yml` or use different ports when running containers

## 🔐 Security Notes

- Never commit `.env` files with real credentials
- Use Docker secrets or environment variables for production
- Regularly update base images for security patches
- Use specific version tags in production, not `latest`

