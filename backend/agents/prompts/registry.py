from typing import Dict, Any, List
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from backend.agents.prompts.system_prompt_v1 import SYSTEM_PROMPT_V1
from backend.agents.prompts.system_prompt_v2 import SYSTEM_PROMPT_V2
from loguru import logger

class PromptRegistry:
    """
    Registry for managing and versioning Task Manager Agent system prompts.
    """
    _VERSIONS: Dict[str, Dict[str, Any]] = {
        "v1.0.0": {
            "version": "v1.0.0",
            "prompt_text": SYSTEM_PROMPT_V1,
            "description": "Baseline prompt from original LangChain implementation",
            "date": "2026-11-22"
        },
        "v2.0.0": {
            "version": "v2.0.0",
            "prompt_text": SYSTEM_PROMPT_V2,
            "description": "Optimized prompt for LangGraph, structured tool-calling, calendar lookup, and rescheduling",
            "date": "2026-11-22"
        }
    }
    
    DEFAULT_VERSION = "v2.0.0"

    @classmethod
    def get_prompt_text(cls, version: str = "latest") -> str:
        """Get raw prompt text by version string"""
        v = cls.DEFAULT_VERSION if version in ["latest", "default", None] else version
        if v not in cls._VERSIONS:
            logger.warning(f"Prompt version '{version}' not found. Falling back to default '{cls.DEFAULT_VERSION}'")
            v = cls.DEFAULT_VERSION
        return cls._VERSIONS[v]["prompt_text"]

    @classmethod
    def get_prompt_template(cls, version: str = "latest") -> ChatPromptTemplate:
        """Create a LangChain ChatPromptTemplate with current_time and scratchpad placeholders"""
        prompt_text = cls.get_prompt_text(version)
        return ChatPromptTemplate.from_messages([
            ("system", prompt_text),
            MessagesPlaceholder(variable_name="messages")
        ])

    @classmethod
    def list_versions(cls) -> List[str]:
        """List all available prompt versions"""
        return list(cls._VERSIONS.keys())

    @classmethod
    def get_version_info(cls, version: str) -> Dict[str, Any]:
        """Get metadata for a specific version"""
        return cls._VERSIONS.get(version, {})
