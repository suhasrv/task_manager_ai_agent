from typing import Dict, Any, List, Optional
import json
import time
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, START, END
from pydantic import ValidationError
from backend.agents.state import AgentState
from backend.agents.prompts.registry import PromptRegistry
from loguru import logger

class ToolExecutorNode:
    """
    Custom LangGraph execution node that enforces:
    1. Pre-execution Pydantic schema validation
    2. Retry logic with exponential backoff on transient errors
    3. Graceful fallback responses for failed tool executions
    """
    def __init__(self, tools: List[BaseTool], max_retries: int = 2):
        self.tools_map: Dict[str, BaseTool] = {tool.name: tool for tool in tools}
        self.max_retries = max_retries

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        last_message = state["messages"][-1]
        if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
            return {"messages": []}

        tool_messages: List[ToolMessage] = []
        tools_called: List[str] = list(state.get("tools_called") or [])
        tool_results: List[Dict[str, Any]] = list(state.get("tool_results") or [])
        errors: List[str] = list(state.get("errors") or [])

        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"] or {}
            tool_call_id = tool_call["id"]
            tools_called.append(tool_name)

            logger.info(f"LangGraph executing tool '{tool_name}' with args: {tool_args}")
            tool = self.tools_map.get(tool_name)

            if not tool:
                err_msg = f"Error: Tool '{tool_name}' is not recognized. Available tools: {list(self.tools_map.keys())}"
                errors.append(err_msg)
                tool_messages.append(ToolMessage(
                    content=err_msg,
                    tool_call_id=tool_call_id,
                    name=tool_name
                ))
                continue

            # 1. Pydantic Schema Validation
            validation_error = None
            if hasattr(tool, "args_schema") and tool.args_schema:
                try:
                    tool.args_schema.model_validate(tool_args)
                except ValidationError as ve:
                    validation_error = f"Input validation error for tool '{tool_name}': {ve.errors()}"
                    logger.warning(validation_error)

            if validation_error:
                errors.append(validation_error)
                tool_messages.append(ToolMessage(
                    content=f"Schema Validation Error: {validation_error}. Please adjust the arguments and retry.",
                    tool_call_id=tool_call_id,
                    name=tool_name
                ))
                continue

            # 2. Execution with Retries & Fallback
            result = None
            success = False
            for attempt in range(self.max_retries + 1):
                try:
                    result = tool.invoke(tool_args)
                    success = True
                    break
                except Exception as ex:
                    logger.warning(f"Tool '{tool_name}' attempt {attempt + 1}/{self.max_retries + 1} failed: {ex}")
                    if attempt < self.max_retries:
                        time.sleep(0.5 * (attempt + 1))
                    else:
                        errors.append(f"Tool {tool_name} failed: {str(ex)}")
                        result = {
                            "success": False,
                            "error": f"Tool execution failed after {self.max_retries + 1} attempts: {str(ex)}",
                            "fallback_note": "Please inform the user about the error or ask for clarification."
                        }

            # Serialize output to string for ToolMessage
            if isinstance(result, (dict, list)):
                content_str = json.dumps(result, default=str)
            else:
                content_str = str(result)

            tool_results.append({
                "tool": tool_name,
                "args": tool_args,
                "success": success,
                "result": result
            })

            tool_messages.append(ToolMessage(
                content=content_str,
                tool_call_id=tool_call_id,
                name=tool_name
            ))

        return {
            "messages": tool_messages,
            "tools_called": tools_called,
            "tool_results": tool_results,
            "errors": errors
        }

def should_continue(state: AgentState) -> str:
    """Conditional router: check if last message contains tool calls"""
    messages = state.get("messages", [])
    if not messages:
        return END

    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls and len(last_message.tool_calls) > 0:
        return "tools"
    return END

def create_task_manager_graph(
    llm: BaseChatModel,
    tools: List[BaseTool],
    prompt_version: str = "v2.0.0"
):
    """
    Builds and compiles a LangGraph StateGraph for the Task Manager Agent.
    """
    # Bind tools to the model
    bound_llm = llm.bind_tools(tools)
    tool_node = ToolExecutorNode(tools=tools, max_retries=2)

    def agent_node(state: AgentState) -> Dict[str, Any]:
        """Invoke LLM with current messages"""
        response = bound_llm.invoke(state["messages"])
        return {"messages": [response]}

    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    # Add Edges
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    workflow.add_edge("tools", "agent")

    return workflow.compile()
