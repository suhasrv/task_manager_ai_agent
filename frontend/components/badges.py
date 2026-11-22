from typing import Optional

def priority_badge(priority: Optional[str]) -> str:
    """Return HTML pill for task priority"""
    p = (priority or "medium").lower()
    return f'<span class="badge-pill badge-{p}">{p.upper()}</span>'

def status_pill(status: Optional[str]) -> str:
    """Return HTML pill for task status"""
    s = (status or "pending").lower()
    label = s.replace("_", " ").title()
    return f'<span class="status-pill status-{s}">{label}</span>'

def tag_chip(tag: str) -> str:
    """Return HTML chip for category tag"""
    clean = tag.strip().lstrip("#")
    return f'<span class="tag-chip">#{clean}</span>'

def mono_id_pill(task_id: str) -> str:
    """Return monospace pill for task UUID"""
    short = task_id[:8] if task_id else "unknown"
    return f'<span class="mono-id">{short}...</span>'

def tool_badge(tool_name: str) -> str:
    """Return monospace pill for an AI tool invocation"""
    return f'<span class="mono-id" style="color: #2DD4BF; border-color: rgba(20, 184, 166, 0.4); background: rgba(13, 148, 136, 0.15);">🔧 {tool_name}</span>'
