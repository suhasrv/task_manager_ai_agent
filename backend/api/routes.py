from fastapi import APIRouter, HTTPException, Query, Body, Response
from typing import List, Optional
from datetime import datetime
from functools import lru_cache
from backend.models.schemas import (
    TaskCreate, TaskResponse, TaskUpdate, TaskStatus, TaskPriority
)
from backend.config import get_settings
from backend.services.task_service import TaskService
from backend.agents.task_agent import TaskManagerAgent
from loguru import logger

router = APIRouter(prefix="/api/v1", tags=["tasks"])
task_service = TaskService()

# Lazy initialization of agent to avoid import-time errors
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = TaskManagerAgent()
    return _agent

# Cache for frequently accessed data
_response_cache = {}

# ============================================================================
# TASK CRUD ENDPOINTS
# ============================================================================

@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate, response: Response) -> TaskResponse:
    """Create a new task"""
    try:
        result = await task_service.create_task(task)
        if not result:
            logger.error("Task creation returned None")
            raise HTTPException(status_code=500, detail="Task creation failed: No data returned from database")
        
        # Clear cache when new task is created
        _response_cache.clear()
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-cache"
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error creating task: {error_msg}")
        # Only log full traceback in debug mode
        if get_settings().DEBUG:
            logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    response: Response,
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
) -> List[TaskResponse]:
    """List all tasks with optional filtering - optimized with caching"""
    try:
        # Create cache key
        cache_key = f"tasks_{status}_{priority}_{limit}_{offset}"
        
        # Check cache (simple in-memory cache for frequently accessed data)
        # In production, use Redis or similar
        if cache_key in _response_cache:
            cached_data, cached_time = _response_cache[cache_key]
            # Cache for 5 seconds
            if (datetime.now().timestamp() - cached_time) < 5:
                response.headers["X-Cache"] = "HIT"
                return cached_data
        
        results = await task_service.list_tasks(
            status=status.value if status else None,
            priority=priority.value if priority else None,
            limit=limit,
            offset=offset
        )
        
        # Cache the results
        _response_cache[cache_key] = (results, datetime.now().timestamp())
        response.headers["X-Cache"] = "MISS"
        
        # Add cache control headers
        response.headers["Cache-Control"] = "public, max-age=5"
        
        return results
    except Exception as e:
        logger.error(f"Error listing tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    """Get a specific task"""
    result = await task_service.get_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result

@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_update: TaskUpdate) -> TaskResponse:
    """Update a task"""
    try:
        result = await task_service.update_task(task_id, task_update)
        if not result:
            raise HTTPException(status_code=404, detail="Task not found")
        return result
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: str, response: Response):
    """Delete a task"""
    success = await task_service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Clear cache when task is deleted
    _response_cache.clear()
    response.headers["Cache-Control"] = "no-cache"
    
    return None

# ============================================================================
# AI AGENT ENDPOINTS
# ============================================================================

@router.post("/agent/chat")
async def agent_chat(request: dict = Body(...)):
    """Chat with the AI Task Manager Agent"""
    try:
        message = request.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Get conversation history if provided
        conversation_history = request.get("history", [])
        
        agent = get_agent()
        result = await agent.process_user_input(message, conversation_history=conversation_history)
        
        # Ensure we always return a proper response
        if result.get("status") == "error":
            logger.error(f"Agent error: {result.get('error')}")
            # Still return the result, but with proper status code
            return result
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in agent chat endpoint: {error_msg}")
        logger.exception("Full traceback:")
        return {
            "status": "error",
            "error": error_msg,
            "output": f"I encountered an error processing your request: {error_msg}",
            "timestamp": datetime.now().isoformat()
        }

@router.get("/agent/summary")
async def get_summary():
    """Get AI-generated task summary"""
    agent = get_agent()
    result = await agent.get_task_summary()
    return result

@router.get("/agent/next-task")
async def get_next_task():
    """Get AI recommendation for next task"""
    agent = get_agent()
    result = await agent.suggest_next_task()
    return result

@router.get("/agent/prompt-version")
async def get_prompt_version():
    """Get current agent prompt version and available versions"""
    from backend.agents.prompts.registry import PromptRegistry
    agent = get_agent()
    return {
        "active_version": agent.prompt_version,
        "available_versions": PromptRegistry.list_versions(),
        "orchestration": "LangGraph StateGraph"
    }

@router.get("/agent/eval-summary")
async def get_eval_summary():
    """Get prompt version score history and latest benchmark metrics"""
    import os
    import json
    eval_log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evals", "prompt_version_log.json")
    if os.path.exists(eval_log_path):
        try:
            with open(eval_log_path, "r", encoding="utf-8") as f:
                return {"eval_history": json.load(f)}
        except Exception as e:
            return {"eval_history": [], "error": str(e)}
    return {"eval_history": []}

# ============================================================================
# SEARCH ENDPOINT
# ============================================================================

@router.get("/search")
async def search_tasks(q: str = Query(..., min_length=1)):
    """Semantic search for tasks"""
    results = task_service.search_tasks(q)
    return {"results": results}

# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }