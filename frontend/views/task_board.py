import streamlit as st
from typing import List, Dict, Any
from frontend.components.cards import render_task_card
from frontend.components.batch_actions import render_batch_action_bar, get_selection_state

def render_task_board_view(api_client, tasks: List[Dict[str, Any]]) -> None:
    """
    Render Kanban columns or compact filterable list with live status transitions
    and batch deletion/multi-select operations.
    """
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="font-size: 2rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.25rem;">
            📋 Task Management Board
        </h1>
        <p style="color: #94A3B8; font-size: 0.95rem; margin: 0;">
            Interactive Kanban board and granular list view with live status transitions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Filter & View Controls
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1.5, 1.5])

    with ctrl_col1:
        view_mode = st.radio(
            "Display Mode",
            ["Columns (Kanban)", "Compact List"],
            horizontal=True,
            label_visibility="collapsed"
        )

    with ctrl_col2:
        priority_filter = st.selectbox(
            "Filter Priority",
            ["All Priorities", "Urgent", "High", "Medium", "Low"],
            label_visibility="collapsed"
        )

    with ctrl_col3:
        search_filter = st.text_input(
            "Filter by title/tag",
            placeholder="🔍 Filter tasks...",
            label_visibility="collapsed"
        )

    # Filter tasks
    filtered = tasks
    if priority_filter != "All Priorities":
        filtered = [t for t in filtered if (t.get("priority") or "").lower() == priority_filter.lower()]
    
    if search_filter.strip():
        q = search_filter.strip().lower()
        filtered = [
            t for t in filtered
            if q in (t.get("title") or "").lower()
            or q in (t.get("description") or "").lower()
            or any(q in tag.lower() for tag in (t.get("tags") or []))
        ]

    # Batch Operations Bar (Select All, Delete Selected, Delete All)
    select_mode = render_batch_action_bar(filtered, api_client, view_prefix="tb")
    selected_ids = get_selection_state("tb")

    def toggle_select(tid: str, is_checked: bool):
        if is_checked:
            selected_ids.add(tid)
        else:
            selected_ids.discard(tid)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    if view_mode == "Columns (Kanban)":
        pending_tasks = [t for t in filtered if t.get("status") == "pending"]
        in_progress_tasks = [t for t in filtered if t.get("status") == "in_progress"]
        completed_tasks = [t for t in filtered if t.get("status") == "completed"]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div style="border-bottom: 2px solid #F59E0B; padding-bottom: 0.5rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; color: #FFFFFF; font-size: 1.05rem;">🟡 Pending Queue</span>
                <span class="mono-id" style="color: #F59E0B; border-color: rgba(245, 158, 11, 0.4);">{len(pending_tasks)}</span>
            </div>
            """, unsafe_allow_html=True)
            if not pending_tasks:
                st.markdown("<p style='color: #64748B; font-style: italic;'>No pending tasks.</p>", unsafe_allow_html=True)
            for t in pending_tasks:
                tid = t.get("id", "")
                render_task_card(
                    t,
                    api_client=api_client,
                    show_actions=True,
                    selectable=select_mode,
                    is_selected=(tid in selected_ids),
                    checkbox_key=f"tb_chk_{tid}",
                    on_select_toggle=toggle_select
                )

        with col2:
            st.markdown(f"""
            <div style="border-bottom: 2px solid #38BDF8; padding-bottom: 0.5rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; color: #FFFFFF; font-size: 1.05rem;">🔵 In Progress</span>
                <span class="mono-id" style="color: #38BDF8; border-color: rgba(56, 189, 248, 0.4);">{len(in_progress_tasks)}</span>
            </div>
            """, unsafe_allow_html=True)
            if not in_progress_tasks:
                st.markdown("<p style='color: #64748B; font-style: italic;'>No tasks in progress.</p>", unsafe_allow_html=True)
            for t in in_progress_tasks:
                tid = t.get("id", "")
                render_task_card(
                    t,
                    api_client=api_client,
                    show_actions=True,
                    selectable=select_mode,
                    is_selected=(tid in selected_ids),
                    checkbox_key=f"tb_chk_{tid}",
                    on_select_toggle=toggle_select
                )

        with col3:
            st.markdown(f"""
            <div style="border-bottom: 2px solid #10B981; padding-bottom: 0.5rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; color: #FFFFFF; font-size: 1.05rem;">🟢 Completed</span>
                <span class="mono-id" style="color: #10B981; border-color: rgba(16, 185, 129, 0.4);">{len(completed_tasks)}</span>
            </div>
            """, unsafe_allow_html=True)
            if not completed_tasks:
                st.markdown("<p style='color: #64748B; font-style: italic;'>No completed tasks.</p>", unsafe_allow_html=True)
            for t in completed_tasks:
                tid = t.get("id", "")
                render_task_card(
                    t,
                    api_client=api_client,
                    show_actions=True,
                    selectable=select_mode,
                    is_selected=(tid in selected_ids),
                    checkbox_key=f"tb_chk_{tid}",
                    on_select_toggle=toggle_select
                )

    else:
        # Compact List View
        st.markdown(f"""
        <div style="font-weight: 600; color: #94A3B8; font-size: 0.9rem; margin-bottom: 1rem;">
            Showing {len(filtered)} matching tasks:
        </div>
        """, unsafe_allow_html=True)

        if not filtered:
            st.markdown("""
            <div class="glass-panel" style="text-align: center; padding: 2rem;">
                <p style="color: #94A3B8; margin: 0;">No tasks match your selected criteria.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            cols = st.columns(2)
            for i, t in enumerate(filtered):
                tid = t.get("id", "")
                with cols[i % 2]:
                    render_task_card(
                        t,
                        api_client=api_client,
                        show_actions=True,
                        selectable=select_mode,
                        is_selected=(tid in selected_ids),
                        checkbox_key=f"tb_chk_{tid}",
                        on_select_toggle=toggle_select
                    )
