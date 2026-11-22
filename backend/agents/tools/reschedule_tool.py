from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import re
from backend.services.task_service import TaskService
from backend.database.client import DatabaseManager
from loguru import logger

task_service = TaskService()
db_manager = DatabaseManager()

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
            return asyncio.run(coro)
    except RuntimeError:
        return asyncio.run(coro)

class RescheduleTaskInput(BaseModel):
    """Input schema for rescheduling a task"""
    task_id: str = Field(..., description="UUID or title identifier of the task to reschedule")
    new_due_date: str = Field(
        ...,
        description="New due date/time: relative string like 'tomorrow', 'today at 8pm', 'next Monday 9am', or ISO format '2026-11-25T18:00:00'"
    )
    reason: Optional[str] = Field(None, description="Optional reason for rescheduling the task")

    @field_validator("task_id")
    @classmethod
    def clean_task_id(cls, v: str) -> str:
        """Extract clean UUID if embedded in formatted strings like '[task_id: xxx]'"""
        if not v:
            raise ValueError("task_id cannot be empty")
        v = v.strip()
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        match = re.search(uuid_pattern, v, re.IGNORECASE)
        return match.group(0) if match else v

def _parse_relative_date(date_str: str) -> Optional[datetime]:
    """Parse relative date expressions into a timezone-aware or naive datetime"""
    if not date_str:
        return None
    now = datetime.now()
    d_lower = date_str.lower().strip()
    
    # Common relative phrases
    if d_lower in ["today", "this evening", "tonight"]:
        hour = 20 if ("evening" in d_lower or "tonight" in d_lower) else 18
        return now.replace(hour=hour, minute=0, second=0, microsecond=0)
    elif d_lower == "tomorrow":
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=18, minute=0, second=0, microsecond=0)
    elif "tomorrow morning" in d_lower:
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
    elif "tomorrow evening" in d_lower:
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=20, minute=0, second=0, microsecond=0)
    elif "in " in d_lower:
        # e.g., 'in 2 days', 'in 3 hours', 'in 1 week'
        num_match = re.search(r'\d+', d_lower)
        num = int(num_match.group(0)) if num_match else 1
        if "hour" in d_lower:
            return now + timedelta(hours=num)
        elif "day" in d_lower:
            return (now + timedelta(days=num)).replace(hour=18, minute=0, second=0, microsecond=0)
        elif "week" in d_lower:
            return (now + timedelta(weeks=num)).replace(hour=18, minute=0, second=0, microsecond=0)
    elif "next " in d_lower:
        # e.g., 'next monday', 'next friday'
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for idx, day in enumerate(weekdays):
            if day in d_lower:
                days_ahead = (idx - now.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7
                target_date = now + timedelta(days=days_ahead)
                return target_date.replace(hour=9, minute=0, second=0, microsecond=0)

    # ISO or standard date parsing fallback
    for fmt in [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y"
    ]:
        try:
            return datetime.strptime(date_str.replace("Z", "+0000"), fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        pass
    
    return None

def _reschedule_task_impl(
    task_id: str,
    new_due_date: str,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Implementation of reschedule_task tool.
    Validates task existence, parses new due date, and updates the task.
    Includes fallback search by title if task_id UUID is not found directly.
    """
    try:
        parsed_dt = _parse_relative_date(new_due_date)
        if not parsed_dt:
            return {
                "success": False,
                "error": f"Could not parse new due date '{new_due_date}'. Please provide a valid relative format like 'tomorrow at 5pm' or ISO format."
            }

        iso_due_date = parsed_dt.isoformat()

        # 1. Fetch current task to verify existence
        task = run_async(task_service.get_task(task_id))
        
        # Fallback: If not found by exact ID, attempt title search
        if not task:
            logger.info(f"Task ID '{task_id}' not found directly. Attempting fallback title search...")
            search_results = task_service.search_tasks(task_id)
            ids = search_results.get("ids", [[]])[0] if search_results else []
            if ids:
                task = run_async(task_service.get_task(ids[0]))
                if task:
                    task_id = task["id"]
                    logger.info(f"Fallback located task ID: {task_id} ('{task.get('title')}')")

        if not task:
            return {
                "success": False,
                "error": f"Task '{task_id}' not found. Please list tasks first to obtain a valid task ID."
            }

        old_due_date = task.get("due_date", "No previous due date")

        # 2. Update task with new due date
        from backend.models.schemas import TaskUpdate
        update_data = TaskUpdate(due_date=parsed_dt)
        result = run_async(task_service.update_task(task_id, update_data))

        if not result:
            return {
                "success": False,
                "error": f"Failed to update task {task_id} in database."
            }

        reason_str = f" Reason: {reason}." if reason else ""
        formatted_display = parsed_dt.strftime("%A, %b %d %Y at %I:%M %p")
        
        logger.info(f"✅ Successfully rescheduled task '{task.get('title')}' (ID: {task_id}) to {formatted_display}")
        return {
            "success": True,
            "task_id": task_id,
            "title": task.get("title"),
            "old_due_date": str(old_due_date),
            "new_due_date": iso_due_date,
            "new_due_date_formatted": formatted_display,
            "message": f"✅ Rescheduled task '{task.get('title')}' (ID: {task_id}) to {formatted_display}.{reason_str}"
        }

    except Exception as e:
        logger.error(f"Error in reschedule_task tool: {e}")
        return {
            "success": False,
            "error": f"Failed to reschedule task: {str(e)}"
        }

reschedule_task = StructuredTool.from_function(
    func=_reschedule_task_impl,
    name="reschedule_task",
    description="Reschedule an existing task to a new due date/time. Use this whenever a user wants to move, postpone, delay, change deadline, or reschedule a task.",
    args_schema=RescheduleTaskInput,
    return_direct=False
)
