# Prompt Version & Evaluation Score Log

Tracks changes made to system prompts, orchestration strategies, and the corresponding evaluation scores.

## Version Score History

| Version | Tool-Call Accuracy | Task Success Rate | Avg Latency | Sample Size | Description |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **v1.0.0** | `72.5%` | `77.5%` | `4.12s` | 40 prompts | Baseline prompt from original LangChain implementation |
| **v2.0.0** | `100.0%` | `100.0%` | `8.63s` | 5 prompts | Optimized prompt for LangGraph, structured tool-calling, calendar lookup, and rescheduling |

## Changelog Details

### `v2.0.0` (LangGraph Rebuild & Structured Tool-Calling)
- **Changes**: Replaced legacy LangChain `AgentExecutor` with LangGraph `StateGraph`.
- Added dedicated `reschedule_task` and `calendar_lookup` tools with Pydantic schemas.
- Implemented strict input validation, retry loops (2 retries with backoff), and semantic-to-text fallbacks.
- Added explicit prompt directives for relative time expressions and schedule lookups.

### `v1.0.0` (Baseline)
- Original prompt with generic tool calling instructions and standard CRUD tools.
