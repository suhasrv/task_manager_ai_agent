"""Reminder scheduler service for checking and sending reminder notifications"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from typing import List, Dict, Any
from backend.database.client import DatabaseManager
from backend.config import get_settings
from loguru import logger
import asyncio

class ReminderScheduler:
    """Service to check and process reminders"""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_manager = DatabaseManager()
        self.scheduler = None
        self._running = False
    
    async def check_and_send_reminders(self):
        """Check for due reminders and send notifications"""
        try:
            # Get all pending reminders that are due
            now = datetime.now()
            
            # Query reminders that are due (reminder_time <= now) and status is pending
            response = self.db_manager.supabase.client.table("reminders").select(
                "id, task_id, reminder_time, notification_type, status"
            ).eq("status", "pending").lte("reminder_time", now.isoformat()).execute()
            
            reminders = response.data or []
            
            if reminders:
                logger.info(f"Found {len(reminders)} due reminder(s)")
                
                for reminder in reminders:
                    await self._send_reminder_notification(reminder)
            else:
                logger.debug("No due reminders found")
                
        except Exception as e:
            logger.error(f"Error checking reminders: {str(e)}")
    
    async def _send_reminder_notification(self, reminder: Dict[str, Any]):
        """Send a reminder notification"""
        try:
            reminder_id = reminder.get("id")
            task_id = reminder.get("task_id")
            
            # Get task details
            task_response = self.db_manager.supabase.client.table("tasks").select(
                "id, title, description, due_date, priority"
            ).eq("id", task_id).execute()
            
            if not task_response.data:
                logger.warning(f"Task {task_id} not found for reminder {reminder_id}")
                # Mark reminder as failed
                self._update_reminder_status(reminder_id, "failed")
                return
            
            task = task_response.data[0]
            task_title = task.get("title", "Untitled Task")
            
            # Send notification based on type
            notification_type = reminder.get("notification_type", "in_app")
            
            if notification_type == "in_app":
                # Store notification in a notifications table or log it
                logger.info(f"🔔 REMINDER: {task_title} (Task ID: {task_id})")
                # In a real app, you'd store this in a notifications table
                # For now, we'll just log it and mark as sent
            
            # Mark reminder as sent
            self._update_reminder_status(reminder_id, "sent")
            
            logger.info(f"Reminder {reminder_id} sent successfully for task: {task_title}")
            
        except Exception as e:
            logger.error(f"Error sending reminder notification: {str(e)}")
            # Mark reminder as failed
            try:
                self._update_reminder_status(reminder.get("id"), "failed")
            except:
                pass
    
    def _update_reminder_status(self, reminder_id: str, status: str):
        """Update reminder status"""
        try:
            self.db_manager.supabase.client.table("reminders").update({
                "status": status
            }).eq("id", reminder_id).execute()
        except Exception as e:
            logger.error(f"Error updating reminder status: {str(e)}")
    
    def start(self):
        """Start the reminder scheduler"""
        if self._running:
            logger.warning("Reminder scheduler is already running")
            return
        
        if not self.settings.SCHEDULER_ENABLED:
            logger.info("Reminder scheduler is disabled in settings")
            return
        
        try:
            self.scheduler = AsyncIOScheduler()
            
            # Schedule reminder check job
            interval_minutes = self.settings.REMINDER_CHECK_INTERVAL_MINUTES
            self.scheduler.add_job(
                self.check_and_send_reminders,
                trigger=IntervalTrigger(minutes=interval_minutes),
                id="check_reminders",
                name="Check and send reminders",
                replace_existing=True
            )
            
            self.scheduler.start()
            self._running = True
            logger.info(f"✅ Reminder scheduler started (checking every {interval_minutes} minutes)")
            
        except Exception as e:
            logger.error(f"Error starting reminder scheduler: {str(e)}")
            self._running = False
    
    def stop(self):
        """Stop the reminder scheduler"""
        if self.scheduler and self._running:
            try:
                self.scheduler.shutdown()
                self._running = False
                logger.info("Reminder scheduler stopped")
            except Exception as e:
                logger.error(f"Error stopping reminder scheduler: {str(e)}")

# Global scheduler instance
_reminder_scheduler = None

def get_reminder_scheduler() -> ReminderScheduler:
    """Get or create the global reminder scheduler instance"""
    global _reminder_scheduler
    if _reminder_scheduler is None:
        _reminder_scheduler = ReminderScheduler()
    return _reminder_scheduler

