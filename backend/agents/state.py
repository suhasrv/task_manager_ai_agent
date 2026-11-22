from typing import TypedDict, Annotated, Sequence, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Typed state container for the LangGraph Task Manager Agent.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    current_provider: str
    retry_count: int
    tools_called: List[str]
    tool_results: List[Dict[str, Any]]
    errors: List[str]
    prompt_version: str
    intermediate_steps: List[Any]
