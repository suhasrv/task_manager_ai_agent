import os
import httpx
from typing import List, Dict, Any, Optional
from loguru import logger

class APIClient:
    """
    Robust HTTP API Client connecting the Streamlit frontend to the FastAPI backend.
    Includes connection pooling, error resilience, and standardized return formats.
    """
    _instance = None

    def __new__(cls, base_url: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, base_url: Optional[str] = None):
        if getattr(self, "_initialized", False):
            return
        
        env_url = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1")
        self.base_url = (base_url or env_url).rstrip("/")
        
        # Connection pooled client
        self._client = httpx.Client(
            timeout=15.0,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
        self._initialized = True
        logger.info(f"Frontend APIClient initialized pointing to: {self.base_url}")

    def check_health(self) -> bool:
        """Check if backend is healthy and responding"""
        try:
            res = self._client.get(f"{self.base_url}/health", timeout=3.0)
            return res.status_code == 200
        except Exception:
            return False

    def list_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List tasks with optional status and priority filtering"""
        params = {"limit": limit, "offset": offset}
        if status and status.lower() != "all":
            params["status"] = status.lower()
        if priority and priority.lower() != "all":
            params["priority"] = priority.lower()

        try:
            res = self._client.get(f"{self.base_url}/tasks", params=params)
            res.raise_for_status()
            return res.json() if res.text else []
        except Exception as e:
            logger.error(f"Error in list_tasks: {e}")
            return []

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a single task by ID"""
        try:
            res = self._client.get(f"{self.base_url}/tasks/{task_id}")
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {e}")
            return None

    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        res = self._client.post(f"{self.base_url}/tasks", json=task_data)
        res.raise_for_status()
        return res.json()

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update task fields"""
        try:
            res = self._client.patch(f"{self.base_url}/tasks/{task_id}", json=updates)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            return None

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID"""
        try:
            res = self._client.delete(f"{self.base_url}/tasks/{task_id}")
            return res.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            return False

    def delete_tasks(self, task_ids: List[str]) -> int:
        """Batch delete multiple tasks by ID. Returns count of successfully deleted tasks."""
        deleted_count = 0
        for tid in task_ids:
            if self.delete_task(tid):
                deleted_count += 1
        return deleted_count

    def agent_chat(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Chat with the LangGraph AI Task Manager Agent"""
        payload = {"message": message}
        if history:
            payload["history"] = history
        try:
            res = self._client.post(f"{self.base_url}/agent/chat", json=payload, timeout=60.0)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Agent chat error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "output": f"Could not reach AI Agent: {str(e)}"
            }

    def search_tasks(self, query: str) -> Dict[str, Any]:
        """Semantic search for tasks using vector embeddings"""
        try:
            res = self._client.get(f"{self.base_url}/search", params={"q": query})
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Search tasks error: {e}")
            return {"results": {"ids": [[]]}}

    def get_summary(self) -> Dict[str, Any]:
        """Get AI-generated task workload summary"""
        try:
            res = self._client.get(f"{self.base_url}/agent/summary", timeout=30.0)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            return {"status": "error", "output": str(e)}

    def get_next_task(self) -> Dict[str, Any]:
        """Get AI recommendation for next priority item"""
        try:
            res = self._client.get(f"{self.base_url}/agent/next-task", timeout=30.0)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            return {"status": "error", "output": str(e)}

    def get_prompt_version(self) -> Dict[str, Any]:
        """Get active prompt version and orchestration metadata"""
        try:
            res = self._client.get(f"{self.base_url}/agent/prompt-version", timeout=5.0)
            res.raise_for_status()
            return res.json()
        except Exception:
            return {"active_version": "v2.0.0", "orchestration": "LangGraph StateGraph"}

    def get_eval_summary(self) -> Dict[str, Any]:
        """Get benchmark evaluation scores history"""
        try:
            res = self._client.get(f"{self.base_url}/agent/eval-summary", timeout=5.0)
            res.raise_for_status()
            return res.json()
        except Exception:
            return {"eval_history": []}
