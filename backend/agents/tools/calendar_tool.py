from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio
import re
from backend.database.client import DatabaseManager
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
            return asyncio.run(coro)
    except RuntimeError:
        return asyncio.run(coro)

class CalendarLookupInput(BaseModel):
    """Input schema for calendar and schedule lookup"""
    start_date: str = Field(
        ...,
        description="Start date for calendar lookup: 'today', 'tomorrow', 'this week', or ISO date 'YYYY-MM-DD'"
    )
    end_date: Optional[str] = Field(
        None,
        description="Optional end date for lookup window. If omitted, defaults to end of start_date (or end of week if 'this week')"
    )
    include_tasks: bool = Field(
        True,
        description="Whether to include tasks with deadlines in this date window (default True)"
    )

def _parse_lookup_window(start_str: str, end_str: Optional[str] = None):
    """Parse start_str and end_str into (start_datetime, end_datetime)"""
    now = datetime.now()
    s_lower = start_str.lower().strip()
    
    if s_lower == "today":
        start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif s_lower == "tomorrow":
        tomorrow = now + timedelta(days=1)
        start_dt = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif "week" in s_lower:
        start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = (now + timedelta(days=7)).replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        # Try parsing ISO/date strings
        try:
            parsed = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            start_dt = parsed.replace(hour=0, minute=0, second=0, microsecond=0)
            end_dt = parsed.replace(hour=23, minute=59, second=59, microsecond=999999)
        except Exception:
            start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_dt = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    if end_str:
        e_lower = end_str.lower().strip()
        if e_lower == "today":
            end_dt = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif e_lower == "tomorrow":
            tomorrow = now + timedelta(days=1)
            end_dt = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            try:
                parsed_end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                end_dt = parsed_end.replace(hour=23, minute=59, second=59, microsecond=999999)
            except Exception:
                pass

    return start_dt, end_dt

def _calendar_lookup_impl(
    start_date: str,
    end_date: Optional[str] = None,
    include_tasks: bool = True
) -> Dict[str, Any]:
    """
    Implementation of calendar_lookup tool.
    Retrieves events from calendar_events table and tasks with deadlines within the window.
    Provides automatic fallback to general task listing if range query encounters issues.
    """
    try:
        start_dt, end_dt = _parse_lookup_window(start_date, end_date)
        start_iso = start_dt.isoformat()
        end_iso = end_dt.isoformat()

        calendar_events = []
        scheduled_tasks = []

        # 1. Query calendar_events table
        try:
            calendar_events = run_async(db_manager.supabase.get_calendar_events(start_iso, end_iso))
        except Exception as e:
            logger.warning(f"Error querying calendar events: {e}")

        # 2. Query tasks table for deadlines in this window
        if include_tasks:
            try:
                scheduled_tasks = run_async(db_manager.supabase.get_tasks_in_range(start_iso, end_iso))
            except Exception as e:
                logger.warning(f"Error querying tasks in range: {e}")
                # Fallback: get all tasks and filter in Python
                try:
                    all_tasks = run_async(db_manager.supabase.list_tasks(limit=50))
                    for t in all_tasks:
                        due = t.get("due_date")
                        if due:
                            try:
                                dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
                                if start_dt.timestamp() <= dt.timestamp() <= end_dt.timestamp():
                                    scheduled_tasks.append(t)
                            except Exception:
                                pass
                except Exception as fb_err:
                    logger.error(f"Fallback task query also failed: {fb_err}")

        # Format items into clear human-readable structure
        items = []
        for ev in calendar_events:
            items.append({
                "type": "calendar_event",
                "id": ev.get("id"),
                "title": ev.get("title", "Untitled Event"),
                "start_time": ev.get("start_time"),
                "end_time": ev.get("end_time"),
                "calendar_id": ev.get("calendar_id", "default")
            })

        for t in scheduled_tasks:
            items.append({
                "type": "task_deadline",
                "id": t.get("id"),
                "title": t.get("title", "Untitled Task"),
                "due_date": t.get("due_date"),
                "priority": t.get("priority", "medium"),
                "status": t.get("status", "pending"),
                "tags": t.get("tags", [])
            })

        window_desc = f"{start_dt.strftime('%b %d, %Y')} to {end_dt.strftime('%b %d, %Y')}" if start_dt.date() != end_dt.date() else start_dt.strftime('%A, %b %d, %Y')

        if not items:
            summary = f"No calendar events or task deadlines found for {window_desc}. Your schedule is clear!"
        else:
            summary = f"Found {len(calendar_events)} calendar event(s) and {len(scheduled_tasks)} task deadline(s) for {window_desc}."

        logger.info(f"Calendar lookup: {summary}")
        return {
            "success": True,
            "window_start": start_iso,
            "window_end": end_iso,
            "window_description": window_desc,
            "events_count": len(calendar_events),
            "tasks_count": len(scheduled_tasks),
            "total_items": len(items),
            "items": items,
            "summary": summary
        }

    except Exception as e:
        logger.error(f"Error in calendar_lookup: {e}")
        return {
            "success": False,
            "error": f"Failed to perform calendar lookup: {str(e)}",
            "items": []
        }

calendar_lookup = StructuredTool.from_function(
    func=_calendar_lookup_impl,
    name="calendar_lookup",
    description="Look up scheduled tasks, deadlines, and calendar events for a specific date or time window (e.g., 'today', 'tomorrow', 'this week', or '2026-11-25'). Use this to check availability or see what is on the schedule.",
    args_schema=CalendarLookupInput,
    return_direct=False
)
