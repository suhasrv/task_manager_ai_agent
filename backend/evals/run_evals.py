"""
Evaluation Runner for Task Manager Agent
Measures Tool-Call Accuracy, Task Success Rate, Latency, and Schema Compliance.
"""
import sys
import os
import json
import time
import asyncio
import argparse
from datetime import datetime
from typing import Dict, Any, List

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.agents.task_agent import TaskManagerAgent
from backend.agents.prompts.registry import PromptRegistry
from loguru import logger

def load_test_prompts(filepath: str) -> List[Dict[str, Any]]:
    """Load test cases from json file"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

async def evaluate_single_prompt(
    agent: TaskManagerAgent,
    test_case: Dict[str, Any],
    prompt_version: str
) -> Dict[str, Any]:
    """Evaluate a single test case through the LangGraph agent"""
    prompt = test_case["prompt"]
    expected_tools = test_case.get("expected_tools", [])
    case_id = test_case.get("id")
    category = test_case.get("category")

    start_time = time.perf_counter()
    try:
        response = await agent.process_user_input(
            user_input=prompt,
            prompt_version=prompt_version
        )
        latency = round(time.perf_counter() - start_time, 2)
    except Exception as e:
        latency = round(time.perf_counter() - start_time, 2)
        return {
            "id": case_id,
            "category": category,
            "prompt": prompt,
            "status": "exception",
            "error": str(e),
            "tools_used": [],
            "expected_tools": expected_tools,
            "tool_accuracy": 0.0,
            "task_success": 0.0,
            "latency": latency
        }

    status = response.get("status", "error")
    tools_used = response.get("tools_used", [])
    output = response.get("output", "")

    # Tool Accuracy: checks if any expected tool was selected
    tool_hit = False
    if expected_tools:
        tool_hit = any(t in tools_used for t in expected_tools)
    else:
        tool_hit = True

    tool_accuracy = 1.0 if tool_hit else 0.0

    # Task Success: success status, no fatal errors, and non-empty output
    has_error = status != "success" or "All AI API Quotas Exceeded" in output or "error" in output.lower() and "failed" in output.lower()
    task_success = 1.0 if (not has_error and len(output.strip()) > 0) else 0.0

    return {
        "id": case_id,
        "category": category,
        "prompt": prompt,
        "status": status,
        "provider": response.get("provider", "unknown"),
        "tools_used": tools_used,
        "expected_tools": expected_tools,
        "tool_accuracy": tool_accuracy,
        "task_success": task_success,
        "latency": latency,
        "output_preview": output[:100].replace("\n", " ")
    }

async def run_evaluation(
    prompt_version: str = "v2.0.0",
    limit: int = None,
    prompts_file: str = None
) -> Dict[str, Any]:
    """Run full evaluation suite across test prompts"""
    if not prompts_file:
        prompts_file = os.path.join(os.path.dirname(__file__), "test_prompts.json")

    test_cases = load_test_prompts(prompts_file)
    if limit and limit > 0:
        test_cases = test_cases[:limit]

    print(f"\n=======================================================")
    print(f"🎯 Starting Evaluation Suite for Prompt [{prompt_version}]")
    print(f"📦 Total Test Cases: {len(test_cases)}")
    print(f"=======================================================\n")

    agent = TaskManagerAgent(prompt_version=prompt_version)
    results = []

    category_stats: Dict[str, Dict[str, float]] = {}

    for idx, tc in enumerate(test_cases, 1):
        cat = tc.get("category", "general")
        if cat not in category_stats:
            category_stats[cat] = {"count": 0, "tool_hits": 0, "success_hits": 0, "total_latency": 0.0}

        print(f"[{idx:02d}/{len(test_cases):02d}] {tc['id']} ({cat}): \"{tc['prompt']}\"...", end="", flush=True)
        res = await evaluate_single_prompt(agent, tc, prompt_version)
        results.append(res)

        tool_ok = "✅" if res["tool_accuracy"] == 1.0 else "❌"
        succ_ok = "✅" if res["task_success"] == 1.0 else "❌"
        print(f" Tool: {tool_ok} ({res['tools_used']}) | Success: {succ_ok} | {res['latency']}s")

        category_stats[cat]["count"] += 1
        category_stats[cat]["tool_hits"] += res["tool_accuracy"]
        category_stats[cat]["success_hits"] += res["task_success"]
        category_stats[cat]["total_latency"] += res["latency"]

    # Compute overall metrics
    total = len(results)
    avg_tool_accuracy = round(sum(r["tool_accuracy"] for r in results) / total * 100, 2) if total else 0
    avg_task_success = round(sum(r["task_success"] for r in results) / total * 100, 2) if total else 0
    avg_latency = round(sum(r["latency"] for r in results) / total, 2) if total else 0

    print(f"\n=======================================================")
    print(f"📊 EVALUATION SUMMARY: [{prompt_version}]")
    print(f"=======================================================")
    print(f"Tool-Call Accuracy : {avg_tool_accuracy}%")
    print(f"Task Success Rate  : {avg_task_success}%")
    print(f"Average Latency    : {avg_latency} seconds")
    print(f"Total Evaluated    : {total} prompts")
    print(f"-------------------------------------------------------")
    print(f"Category Breakdown:")
    for cat, stats in category_stats.items():
        c_count = stats["count"]
        c_tool = round(stats["tool_hits"] / c_count * 100, 1) if c_count else 0
        c_succ = round(stats["success_hits"] / c_count * 100, 1) if c_count else 0
        c_lat = round(stats["total_latency"] / c_count, 2) if c_count else 0
        print(f" - {cat:24s}: Tool Acc: {c_tool:5.1f}% | Task Succ: {c_succ:5.1f}% | Lat: {c_lat}s")
    print(f"=======================================================\n")

    report = {
        "timestamp": datetime.now().isoformat(),
        "prompt_version": prompt_version,
        "total_cases": total,
        "tool_accuracy_pct": avg_tool_accuracy,
        "task_success_rate_pct": avg_task_success,
        "average_latency_sec": avg_latency,
        "category_breakdown": category_stats,
        "results": results
    }

    # Save run report
    results_dir = os.path.join(os.path.dirname(__file__), "runs")
    os.makedirs(results_dir, exist_ok=True)
    report_file = os.path.join(results_dir, f"eval_{prompt_version}_{int(time.time())}.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Append to prompt version log
    update_version_log(prompt_version, avg_tool_accuracy, avg_task_success, avg_latency, total)

    return report

def update_version_log(version: str, tool_acc: float, task_succ: float, latency: float, total: int):
    """Update prompt_version_log.json and PROMPT_VERSION_LOG.md"""
    log_json_path = os.path.join(os.path.dirname(__file__), "prompt_version_log.json")
    log_md_path = os.path.join(os.path.dirname(__file__), "PROMPT_VERSION_LOG.md")

    log_data = []
    if os.path.exists(log_json_path):
        try:
            with open(log_json_path, "r", encoding="utf-8") as f:
                log_data = json.load(f)
        except Exception:
            log_data = []

    entry = {
        "version": version,
        "timestamp": datetime.now().isoformat(),
        "tool_call_accuracy": tool_acc,
        "task_success_rate": task_succ,
        "avg_latency": latency,
        "sample_size": total,
        "description": PromptRegistry.get_version_info(version).get("description", "")
    }

    # Replace or append entry for this version
    log_data = [e for e in log_data if e.get("version") != version]
    log_data.append(entry)

    with open(log_json_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2)

    # Re-render PROMPT_VERSION_LOG.md
    md_content = "# Prompt Version & Evaluation Score Log\n\n"
    md_content += "Tracks changes made to system prompts, orchestration strategies, and the corresponding evaluation scores.\n\n"
    md_content += "## Version Score History\n\n"
    md_content += "| Version | Tool-Call Accuracy | Task Success Rate | Avg Latency | Sample Size | Description |\n"
    md_content += "| :--- | :---: | :---: | :---: | :---: | :--- |\n"

    for e in log_data:
        md_content += f"| **{e['version']}** | `{e['tool_call_accuracy']}%` | `{e['task_success_rate']}%` | `{e['avg_latency']}s` | {e['sample_size']} prompts | {e['description']} |\n"

    md_content += "\n## Changelog Details\n\n"
    md_content += "### `v2.0.0` (LangGraph Rebuild & Structured Tool-Calling)\n"
    md_content += "- **Changes**: Replaced legacy LangChain `AgentExecutor` with LangGraph `StateGraph`.\n"
    md_content += "- Added dedicated `reschedule_task` and `calendar_lookup` tools with Pydantic schemas.\n"
    md_content += "- Implemented strict input validation, retry loops (2 retries with backoff), and semantic-to-text fallbacks.\n"
    md_content += "- Added explicit prompt directives for relative time expressions and schedule lookups.\n\n"
    md_content += "### `v1.0.0` (Baseline)\n"
    md_content += "- Original prompt with generic tool calling instructions and standard CRUD tools.\n"

    with open(log_md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Evaluation Suite for Task Manager Agent")
    parser.add_argument("--version", type=str, default="v2.0.0", help="Prompt version to evaluate (e.g. v1.0.0, v2.0.0)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of test prompts to evaluate")
    parser.add_argument("--prompts-file", type=str, default=None, help="Path to custom test prompts JSON")
    args = parser.parse_args()

    asyncio.run(run_evaluation(
        prompt_version=args.version,
        limit=args.limit,
        prompts_file=args.prompts_file
    ))
