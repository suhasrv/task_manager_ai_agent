from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from backend.config import get_settings
from backend.agents.tools.task_crud_tool import (
    create_task, get_task, list_tasks, update_task, delete_task, search_tasks
)
from backend.agents.tools.reminder_tool import create_reminder, list_reminders
from backend.agents.tools.reschedule_tool import reschedule_task
from backend.agents.tools.calendar_tool import calendar_lookup
from backend.agents.prompts.registry import PromptRegistry
from backend.agents.graph import create_task_manager_graph
from loguru import logger

# Fix for httpx 0.28.0+ compatibility with OpenAI and Anthropic clients
try:
    import httpx
    _orig_client_init = httpx.Client.__init__
    _orig_async_init = httpx.AsyncClient.__init__

    def _patched_client_init(self, *args, **kwargs):
        if "proxies" in kwargs:
            p = kwargs.pop("proxies")
            if p and "proxy" not in kwargs:
                kwargs["proxy"] = p
        return _orig_client_init(self, *args, **kwargs)

    def _patched_async_init(self, *args, **kwargs):
        if "proxies" in kwargs:
            p = kwargs.pop("proxies")
            if p and "proxy" not in kwargs:
                kwargs["proxy"] = p
        return _orig_async_init(self, *args, **kwargs)

    httpx.Client.__init__ = _patched_client_init
    httpx.AsyncClient.__init__ = _patched_async_init

    import openai
    from openai._base_client import SyncHttpxClientWrapper, AsyncHttpxClientWrapper

    orig_sync = SyncHttpxClientWrapper.__init__
    def patched_sync(self, *args, **kwargs):
        kwargs.pop("proxies", None)
        return orig_sync(self, *args, **kwargs)
    SyncHttpxClientWrapper.__init__ = patched_sync

    orig_async = AsyncHttpxClientWrapper.__init__
    def patched_async(self, *args, **kwargs):
        kwargs.pop("proxies", None)
        return orig_async(self, *args, **kwargs)
    AsyncHttpxClientWrapper.__init__ = patched_async

    logger.info("Applied httpx compatibility patch for OpenAI and Anthropic clients")
except Exception as e:
    logger.warning(f"Could not apply httpx compatibility patch: {e}")

class TaskManagerAgent:
    """
    AI Task Manager Agent orchestrated via LangGraph StateGraph
    with multi-provider failover, structured Pydantic tools, and prompt versioning.
    """

    def __init__(self, prompt_version: str = "v2.0.0"):
        self.settings = get_settings()
        self.prompt_version = prompt_version
        self.tools = self._setup_tools()
        self.graphs: Dict[str, Any] = {}
        self.llm_instances: Dict[str, BaseChatModel] = {}

        # Initialize primary LLM & graph
        self.llm = self._initialize_llm_with_fallback()
        logger.info(f"TaskManagerAgent initialized with LangGraph (prompt: {self.prompt_version})")

    def _setup_tools(self) -> List[Any]:
        """Configure all structured tools available to the LangGraph agent"""
        return [
            create_task,
            get_task,
            list_tasks,
            update_task,
            delete_task,
            search_tasks,
            reschedule_task,
            calendar_lookup,
            create_reminder,
            list_reminders
        ]

    def _get_provider_order(self) -> List[str]:
        """Determine provider try-order based on configured keys and preferred setting"""
        preferred = (self.settings.LLM_PROVIDER or "nvidia").lower()
        if preferred in ["nim"]:
            preferred = "nvidia"

        candidates = []
        if getattr(self.settings, "NVIDIA_API_KEY", None):
            candidates.append("nvidia")
        if self.settings.GOOGLE_GEMINI_API_KEY:
            candidates.append("gemini")
        if self.settings.OPENAI_API_KEY:
            candidates.append("openai")
        if self.settings.ANTHROPIC_API_KEY:
            candidates.append("anthropic")

        if preferred in candidates:
            return [preferred] + [c for c in candidates if c != preferred]
        return candidates

    def _create_llm_for_provider(self, provider: str) -> Optional[BaseChatModel]:
        """Instantiate an LLM model for a given provider"""
        try:
            if provider == "nvidia" and getattr(self.settings, "NVIDIA_API_KEY", None):
                base_url = getattr(self.settings, "NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
                model = getattr(self.settings, "NVIDIA_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")
                logger.info(f"Connecting to NVIDIA API at {base_url} with model {model}")
                return ChatOpenAI(
                    base_url=base_url,
                    api_key=self.settings.NVIDIA_API_KEY,
                    model=model,
                    temperature=self.settings.LLM_TEMPERATURE
                )
            elif provider == "gemini" and self.settings.GOOGLE_GEMINI_API_KEY:
                model = self.settings.LLM_MODEL if "gemini" in self.settings.LLM_MODEL.lower() else "gemini-2.5-flash"
                for m in [model, "gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]:
                    try:
                        return ChatGoogleGenerativeAI(
                            model=m,
                            google_api_key=self.settings.GOOGLE_GEMINI_API_KEY,
                            temperature=self.settings.LLM_TEMPERATURE
                        )
                    except Exception:
                        continue
            elif provider == "openai" and self.settings.OPENAI_API_KEY:
                model = self.settings.LLM_MODEL if "gpt" in self.settings.LLM_MODEL.lower() else "gpt-4o-mini"
                return ChatOpenAI(
                    model=model,
                    openai_api_key=self.settings.OPENAI_API_KEY,
                    temperature=self.settings.LLM_TEMPERATURE
                )
            elif provider == "anthropic" and self.settings.ANTHROPIC_API_KEY:
                model = self.settings.LLM_MODEL if "claude" in self.settings.LLM_MODEL.lower() else "claude-3-5-sonnet-20241022"
                return ChatAnthropic(
                    model=model,
                    anthropic_api_key=self.settings.ANTHROPIC_API_KEY,
                    temperature=self.settings.LLM_TEMPERATURE
                )
        except Exception as e:
            logger.warning(f"Failed to create LLM for provider {provider}: {e}")
        return None

    def _get_graph_for_provider(self, provider: str):
        """Get or create cached LangGraph workflow for a provider"""
        if provider in self.graphs:
            return self.graphs[provider]

        llm = self._create_llm_for_provider(provider)
        if not llm:
            return None

        self.llm_instances[provider] = llm
        graph = create_task_manager_graph(
            llm=llm,
            tools=self.tools,
            prompt_version=self.prompt_version
        )
        self.graphs[provider] = graph
        return graph

    def _initialize_llm_with_fallback(self) -> BaseChatModel:
        """Initialize primary LLM based on provider priority"""
        order = self._get_provider_order()
        for provider in order:
            llm = self._create_llm_for_provider(provider)
            if llm:
                logger.info(f"✅ Initialized primary LLM provider: {provider}")
                return llm

        raise RuntimeError(
            "Failed to initialize any LLM provider. Please ensure at least one API key is configured in .env"
        )

    async def process_user_input(
        self,
        user_input: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        prompt_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user input through the LangGraph StateGraph with runtime failover.
        """
        active_version = prompt_version or self.prompt_version
        logger.info(f"LangGraph processing input: '{user_input}' (prompt: {active_version})")

        # 1. Format system prompt with current time
        system_text = PromptRegistry.get_prompt_text(active_version).format(
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        messages = [SystemMessage(content=system_text)]

        # 2. Append conversation history if provided
        if conversation_history:
            for item in conversation_history[-4:]:
                u_text = item.get("user")
                a_text = item.get("assistant")
                if u_text:
                    messages.append(HumanMessage(content=u_text))
                if a_text:
                    messages.append(AIMessage(content=a_text))

        # 3. Enhanced input handling for quick affirmative follow-ups
        enhanced_input = user_input
        u_lower = user_input.lower().strip()
        if u_lower in ["yes", "y"]:
            if conversation_history:
                for msg in reversed(conversation_history[-3:]):
                    assist = msg.get("assistant", "").lower()
                    if "created successfully" in assist and "id:" in assist:
                        import re
                        match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', msg.get("assistant", ""), re.I)
                        if match:
                            enhanced_input = f"Create a reminder for task {match.group(0)} in 1 hour"
                            break
            if enhanced_input == user_input:
                enhanced_input = f"{user_input} - show me the details of the tasks from the previous search results"

        messages.append(HumanMessage(content=enhanced_input))

        provider_order = self._get_provider_order()
        if not provider_order:
            return {
                "status": "error",
                "error": "No LLM API keys configured",
                "output": "⚠️ **No AI API Keys Configured**. Please check `.env` configuration.",
                "timestamp": datetime.now().isoformat()
            }

        provider_errors = {}

        # 4. Invoke graph with automatic provider failover
        for provider in provider_order:
            try:
                graph = self._get_graph_for_provider(provider)
                if not graph:
                    provider_errors[provider] = "Initialization returned None"
                    continue

                logger.info(f"Executing LangGraph with provider: {provider}")
                initial_state = {
                    "messages": messages,
                    "current_provider": provider,
                    "retry_count": 0,
                    "tools_called": [],
                    "tool_results": [],
                    "errors": [],
                    "prompt_version": active_version,
                    "intermediate_steps": []
                }

                # Run graph
                state_result = graph.invoke(initial_state)

                # Extract final output
                final_messages = state_result.get("messages", [])
                output = ""
                if final_messages:
                    last_msg = final_messages[-1]
                    if isinstance(last_msg, AIMessage):
                        output = last_msg.content or ""

                # If LLM didn't produce text but tools executed, synthesize from tool result
                tools_called = state_result.get("tools_called", [])
                tool_results = state_result.get("tool_results", [])
                if not output and tool_results:
                    last_res = tool_results[-1].get("result")
                    if isinstance(last_res, dict):
                        output = last_res.get("message") or last_res.get("summary") or str(last_res)
                    elif isinstance(last_res, list):
                        output = f"Found {len(last_res)} item(s)."
                    else:
                        output = str(last_res)

                if not output:
                    output = "I have processed your request successfully."

                logger.info(f"✅ LangGraph response generated by provider '{provider}'. Tools called: {tools_called}")
                return {
                    "status": "success",
                    "output": output,
                    "provider": provider,
                    "tools_used": tools_called,
                    "prompt_version": active_version,
                    "timestamp": datetime.now().isoformat()
                }

            except Exception as e:
                err_msg = str(e)
                logger.warning(f"⚠️ Provider '{provider}' encountered error: {err_msg}. Switching to next available API...")
                provider_errors[provider] = err_msg

        # All providers failed
        logger.error(f"All configured providers {provider_order} failed: {provider_errors}")
        provider_display_names = {
            "nvidia": "NVIDIA NIM / Cloud",
            "gemini": "Google Gemini",
            "openai": "OpenAI",
            "anthropic": "Anthropic Claude"
        }
        lines = []
        for p, err in provider_errors.items():
            name = provider_display_names.get(p, p.capitalize())
            lines.append(f"- **{name}**: ❌ {str(err)[:100]}")

        return {
            "status": "error",
            "error": "All AI providers quota exceeded or unavailable",
            "output": (
                "⚠️ **All AI API Quotas Exceeded / Unavailable**\n\n"
                + "\n".join(lines) +
                "\n\n💡 **Tip**: You can still create and manage tasks manually anytime using the **'Create Task'** page!"
            ),
            "provider_errors": provider_errors,
            "timestamp": datetime.now().isoformat()
        }

    async def get_task_summary(self) -> Dict[str, Any]:
        """Get high-level summary of all tasks"""
        summary_prompt = "Analyze all tasks and provide a total count by status and priority, overdue tasks, and workload recommendations."
        return await self.process_user_input(summary_prompt)

    async def suggest_next_task(self) -> Dict[str, Any]:
        """AI recommendation for next task to work on"""
        prompt = "Based on priorities, due dates, and workload, what task should I work on next?"
        return await self.process_user_input(prompt)
