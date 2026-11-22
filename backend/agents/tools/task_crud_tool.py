from langchain_core.tools import StructuredTool, tool
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio
import re
from backend.database.client import DatabaseManager
from backend.models.schemas import TaskCreate, TaskPriority, TaskUpdate
from backend.services.task_service import TaskService
from loguru import logger

db_manager = DatabaseManager()
task_service = TaskService()

def run_async(coro):
    """Helper to run async code from sync context safely"""
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(coro)
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)

def clean_uuid_str(v: str) -> str:
    """Helper to extract clean UUID from formatted text"""
    if not v:
        return v
    v = v.strip()
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    match = re.search(uuid_pattern, v, re.IGNORECASE)
    return match.group(0) if match else v

# ============================================================================
# PYDANTIC INPUT SCHEMAS
# ============================================================================

class CreateTaskInput(BaseModel):
    """Input schema for create_task tool"""
    title: str = Field(..., min_length=1, max_length=255, description="Task title (required) - concise name of the task")
    description: Optional[str] = Field(None, description="Detailed task description")
    priority: str = Field("medium", description="Priority level: low, medium, high, or urgent")
    due_date: Optional[str] = Field(None, description="Due date in ISO format or relative like 'today', 'tomorrow', 'evening', 'morning'")
    estimated_hours: Optional[float] = Field(None, ge=0, le=24, description="Estimated time in hours (e.g. 0.5 for 30 min, 1.5 for 1h30m)")
    tags: Optional[List[str]] = Field(None, description="List of category tags (e.g. ['work', 'urgent'])")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Task title cannot be empty or whitespace")
        return s

class GetTaskInput(BaseModel):
    """Input schema for get_task tool"""
    task_id: str = Field(..., description="UUID of the task to retrieve")

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        return clean_uuid_str(v)

class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool"""
    status: Optional[str] = Field(None, description="Filter by status: pending, in_progress, completed, archived")
    priority: Optional[str] = Field(None, description="Filter by priority: low, medium, high, urgent")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of tasks to return (default 20)")

class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool"""
    task_id: str = Field(..., description="UUID of the task to update")
    title: Optional[str] = Field(None, description="Updated task title")
    description: Optional[str] = Field(None, description="Updated description")
    status: Optional[str] = Field(None, description="Updated status: pending, in_progress, completed, archived")
    priority: Optional[str] = Field(None, description="Updated priority: low, medium, high, urgent")
    due_date: Optional[str] = Field(None, description="Updated due date in ISO format or relative date")

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        return clean_uuid_str(v)

class DeleteTaskInput(BaseModel):
    """Input schema for delete_task tool"""
    task_id: str = Field(..., description="UUID of the task to delete")

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        return clean_uuid_str(v)

class SearchTasksInput(BaseModel):
    """Input schema for search_tasks tool"""
    query: str = Field(..., min_length=1, description="Natural language search query (e.g., 'tasks about coding', 'client meeting')")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results to return (default 10)")

# ============================================================================
# TOOL IMPLEMENTATIONS WITH RETRIES AND FALLBACKS
# ============================================================================

def _create_task_impl(
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    due_date: Optional[str] = None,
    estimated_hours: Optional[float] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Internal implementation of create_task with date parsing and retry"""
    last_err = None
    for attempt in range(2):
        try:
            parsed_due_date = due_date
            if due_date:
                due_date_lower = due_date.lower().strip()
                now = datetime.now()
                if due_date_lower == "today":
                    parsed_due_date = now.replace(hour=18, minute=0, second=0, microsecond=0).isoformat()
                elif due_date_lower == "tomorrow":
                    tomorrow = now + timedelta(days=1)
                    parsed_due_date = tomorrow.replace(hour=18, minute=0, second=0, microsecond=0).isoformat()
                elif "evening" in due_date_lower or "tonight" in due_date_lower:
                    parsed_due_date = now.replace(hour=20, minute=0, second=0, microsecond=0).isoformat()
                elif "morning" in due_date_lower:
                    tomorrow = now + timedelta(days=1) if now.hour >= 12 else now
                    parsed_due_date = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0).isoformat()

            task_priority = TaskPriority.MEDIUM
            p_lower = priority.lower().strip()
            if p_lower == "high":
                task_priority = TaskPriority.HIGH
            elif p_lower == "urgent":
                task_priority = TaskPriority.URGENT
            elif p_lower == "low":
                task_priority = TaskPriority.LOW

            due_date_obj = None
            if parsed_due_date:
                try:
                    if 'Z' in parsed_due_date:
                        due_date_obj = datetime.fromisoformat(parsed_due_date.replace('Z', '+00:00'))
                    else:
                        due_date_obj = datetime.fromisoformat(parsed_due_date)
                except Exception as e:
                    logger.warning(f"Could not parse due_date '{parsed_due_date}': {e}")
                    due_date_obj = None

            task_create = TaskCreate(
                title=title,
                description=description,
                priority=task_priority,
                due_date=due_date_obj,
                estimated_hours=estimated_hours,
                tags=tags or [],
                created_by=None
            )

            result = run_async(task_service.create_task(task_create))
            if result and result.get("id"):
                logger.info(f"Task created: ID={result['id']}, Title={result.get('title')}")
                return {
                    "success": True,
                    "task_id": result["id"],
                    "title": result.get("title"),
                    "status": result.get("status", "pending"),
                    "priority": result.get("priority", "medium"),
                    "due_date": result.get("due_date"),
                    "message": f"✅ Task '{title}' created successfully! ID: {result['id']}. Status: {result.get('status', 'pending')}, Priority: {result.get('priority', 'medium')}"
                }
        except Exception as e:
            last_err = e
            logger.warning(f"create_task attempt {attempt+1} failed: {e}")

    logger.error(f"Error in create_task after retries: {last_err}")
    return {
        "success": False,
        "error": f"Failed to create task: {str(last_err)}"
    }

def _get_task_impl(task_id: str) -> Dict[str, Any]:
    """Get a specific task by ID with fallback title search"""
    try:
        clean_id = clean_uuid_str(task_id)
        result = run_async(db_manager.supabase.get_task(clean_id))
        if result:
            return result
        # Fallback: search tasks by query
        search_res = db_manager.chroma.search_tasks(task_id, 1)
        if search_res and search_res.get("ids") and search_res["ids"][0]:
            fb_task = run_async(db_manager.supabase.get_task(search_res["ids"][0][0]))
            if fb_task:
                return fb_task
        return {"error": f"Task '{task_id}' not found"}
    except Exception as e:
        logger.error(f"Error in get_task tool: {e}")
        return {"error": f"Failed to get task: {str(e)}"}

def _list_tasks_impl(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """List tasks with optional filters"""
    try:
        normalized_priority = priority.lower() if priority else None
        normalized_status = status.lower() if status else None
        results = run_async(db_manager.supabase.list_tasks(
            status=normalized_status,
            priority=normalized_priority,
            limit=limit
        ))
        return results or []
    except Exception as e:
        logger.error(f"Error in list_tasks tool: {e}")
        return []

def _update_task_impl(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """Update task fields"""
    try:
        clean_id = clean_uuid_str(task_id)
        updates = {}
        if title: updates["title"] = title
        if description is not None: updates["description"] = description
        if status: updates["status"] = status
        if priority: updates["priority"] = priority
        if due_date: updates["due_date"] = due_date

        task_update = TaskUpdate(**updates)
        result = run_async(task_service.update_task(clean_id, task_update))
        if result:
            return {
                "success": True,
                "message": "Task updated successfully",
                "task": result
            }
        return {"error": f"Failed to update task: Task {clean_id} not found"}
    except Exception as e:
        logger.error(f"Error in update_task tool: {e}")
        return {"error": f"Failed to update task: {str(e)}"}

def _delete_task_impl(task_id: str) -> Dict[str, Any]:
    """Delete a task by ID"""
    try:
        clean_id = clean_uuid_str(task_id)
        result = run_async(task_service.delete_task(clean_id))
        return {
            "success": result,
            "message": "Task deleted successfully" if result else f"Failed to delete task {clean_id}",
            "task_id": clean_id
        }
    except Exception as e:
        logger.error(f"Error in delete_task tool: {e}")
        return {"success": False, "error": f"Failed to delete task: {str(e)}"}

def _search_tasks_impl(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search tasks with semantic search and automatic keyword fallback"""
    try:
        expanded_query = query
        if len(query.split()) <= 2:
            expanded_query = f"tasks related to {query} or about {query}"

        # 1. Semantic search via ChromaDB
        task_ids = []
        try:
            chroma_results = db_manager.chroma.search_tasks(expanded_query, max_results)
            task_ids = chroma_results.get("ids", [[]])[0] if chroma_results else []
        except Exception as chroma_err:
            logger.warning(f"ChromaDB search failed, falling back to database text search: {chroma_err}")

        # 2. Fetch full tasks for ChromaDB results
        tasks = []
        if task_ids:
            for tid in task_ids:
                try:
                    t = run_async(db_manager.supabase.get_task(tid))
                    if t:
                        tasks.append(t)
                except Exception:
                    continue

        # 3. Fallback: text search in Supabase if semantic returned no tasks
        if not tasks:
            logger.info(f"Semantic search returned 0 items, executing text search fallback for '{query}'")
            all_tasks = run_async(db_manager.supabase.list_tasks(limit=100))
            q_lower = query.lower()
            for task in all_tasks:
                title = (task.get("title") or "").lower()
                desc = (task.get("description") or "").lower()
                tags = [tag.lower() for tag in (task.get("tags") or [])]
                if q_lower in title or q_lower in desc or any(q_lower in tag for tag in tags):
                    tasks.append(task)
                    if len(tasks) >= max_results:
                        break

        logger.info(f"Search for '{query}' returned {len(tasks)} tasks")
        return tasks
    except Exception as e:
        logger.error(f"Error in search_tasks tool: {e}")
        return []

# ============================================================================
# STRUCTURED TOOLS EXPORT
# ============================================================================

create_task = StructuredTool.from_function(
    func=_create_task_impl,
    name="create_task",
    description="Create a new task in the database. Provide title (required), description, priority (low/medium/high/urgent), due_date (ISO format or 'today'/'tomorrow'), estimated_hours, and tags.",
    args_schema=CreateTaskInput,
    return_direct=False
)

get_task = StructuredTool.from_function(
    func=_get_task_impl,
    name="get_task",
    description="Get full details of a specific task by its UUID ID.",
    args_schema=GetTaskInput,
    return_direct=False
)

list_tasks = StructuredTool.from_function(
    func=_list_tasks_impl,
    name="list_tasks",
    description="List all tasks with optional filtering by status (pending, in_progress, completed, archived) and priority (low, medium, high, urgent). Use this to view or filter existing tasks.",
    args_schema=ListTasksInput,
    return_direct=False
)

update_task = StructuredTool.from_function(
    func=_update_task_impl,
    name="update_task",
    description="Update an existing task's fields like title, description, priority, or status (e.g. mark completed).",
    args_schema=UpdateTaskInput,
    return_direct=False
)

delete_task = StructuredTool.from_function(
    func=_delete_task_impl,
    name="delete_task",
    description="Delete a task from the database by its UUID ID.",
    args_schema=DeleteTaskInput,
    return_direct=False
)

search_tasks = StructuredTool.from_function(
    func=_search_tasks_impl,
    name="search_tasks",
    description="Search tasks by semantic meaning or natural language topic. Returns full task details including IDs and statuses.",
    args_schema=SearchTasksInput,
    return_direct=False
)
