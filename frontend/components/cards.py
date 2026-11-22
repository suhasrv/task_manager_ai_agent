import streamlit as st
from typing import Dict, Any, List, Optional
from frontend.components.badges import priority_badge, status_pill, tag_chip, mono_id_pill

def format_date_str(due_date: Optional[str]) -> str:
    """Helper to format due date string nicely"""
    if not due_date:
        return "📅 No due date"
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        return f"📅 Due: {dt.strftime('%b %d, %Y')}"
    except Exception:
        return f"📅 Due: {str(due_date)[:10]}"

def render_kpi_card(title: str, value: Any, variant: str = "total") -> None:
    """Render a styled KPI metric card"""
    st.markdown(f"""
    <div class="stat-card {variant}">
        <div class="stat-label">{title}</div>
        <div class="stat-number">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def render_task_card(
    task: Dict[str, Any],
    api_client=None,
    show_actions: bool = True,
    selectable: bool = False,
    is_selected: bool = False,
    checkbox_key: Optional[str] = None,
    on_select_toggle: Optional[callable] = None
) -> None:
    """
    Render a single task as a modern glassmorphic card with action triggers and selection support.
    """
    task_id = task.get("id", "")
    title = task.get("title", "Untitled Task")
    description = task.get("description", "")
    priority = task.get("priority", "medium")
    status = task.get("status", "pending")
    due_date = task.get("due_date")
    tags = task.get("tags") or []
    estimated_hours = task.get("estimated_hours")

    tags_html = "".join([tag_chip(t) for t in tags]) if tags else ""
    est_str = f"⏱️ {estimated_hours}h" if estimated_hours else ""

    if selectable and checkbox_key:
        checked = st.checkbox(
            f"Select: {title}",
            value=is_selected,
            key=checkbox_key,
            label_visibility="visible"
        )
        if on_select_toggle and checked != is_selected:
            on_select_toggle(task_id, checked)

    card_cls = "task-item-card task-selected" if is_selected else "task-item-card"

    st.markdown(f"""
    <div class="{card_cls}">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.4rem;">
            <div>
                {priority_badge(priority)}
                {status_pill(status)}
            </div>
            {mono_id_pill(task_id)}
        </div>
        <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-top: 0.35rem; margin-bottom: 0.35rem;">
            {title}
        </div>
        <div style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 0.6rem; line-height: 1.4;">
            {description if description else '<em>No description provided</em>'}
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: #64748B;">
            <span>{format_date_str(due_date)}</span>
            <span>{est_str}</span>
        </div>
        <div>
            {tags_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if show_actions and api_client:
        del_confirm_key = f"del_confirm_{task_id}"

        if st.session_state.get(del_confirm_key, False):
            st.warning(f"⚠️ Confirm deletion of '{title}'?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Confirm Delete", key=f"do_del_{task_id}", type="primary"):
                    try:
                        api_client.delete_task(task_id)
                        st.session_state[del_confirm_key] = False
                        st.success("Task deleted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            with c2:
                if st.button("Cancel", key=f"cancel_del_{task_id}"):
                    st.session_state[del_confirm_key] = False
                    st.rerun()
        else:
            col_a, col_b, col_c = st.columns([1, 1, 1])
            with col_a:
                if status == "pending":
                    if st.button("▶️ Start", key=f"btn_start_{task_id}"):
                        api_client.update_task(task_id, {"status": "in_progress"})
                        st.rerun()
                elif status == "in_progress":
                    if st.button("✅ Complete", key=f"btn_done_{task_id}", type="primary"):
                        api_client.update_task(task_id, {"status": "completed"})
                        st.rerun()
                elif status == "completed":
                    if st.button("↩️ Reopen", key=f"btn_reopen_{task_id}"):
                        api_client.update_task(task_id, {"status": "pending"})
                        st.rerun()

            with col_b:
                if st.button("📋 Copy ID", key=f"btn_copy_{task_id}"):
                    st.toast(f"Copied ID: {task_id}")

            with col_c:
                if st.button("🗑️ Delete", key=f"btn_del_{task_id}"):
                    st.session_state[del_confirm_key] = True
                    st.rerun()
