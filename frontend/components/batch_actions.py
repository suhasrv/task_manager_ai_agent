import streamlit as st
from typing import List, Dict, Any, Set

def get_selection_state(view_prefix: str) -> Set[str]:
    """Retrieve or initialize the set of selected task IDs for a given view"""
    key = f"{view_prefix}_selected_task_ids"
    if key not in st.session_state:
        st.session_state[key] = set()
    return st.session_state[key]

def render_batch_action_bar(
    tasks: List[Dict[str, Any]],
    api_client,
    view_prefix: str = "tb"
) -> bool:
    """
    Render SaaS batch operations bar with Select All, Delete Selected,
    and Delete All capabilities with multi-stage confirmation dialogs.
    Returns: bool (whether multi-select mode is active)
    """
    total_count = len(tasks)
    if total_count == 0:
        return False

    prefix = view_prefix
    mode_key = f"{prefix}_select_mode"
    confirm_del_all_key = f"{prefix}_confirm_del_all"
    confirm_del_sel_key = f"{prefix}_confirm_del_sel"

    selected_ids = get_selection_state(view_prefix)
    # Keep only IDs that currently exist in tasks
    current_task_ids = {t.get("id") for t in tasks if t.get("id")}
    selected_ids.intersection_update(current_task_ids)

    # 1. Main Action Bar Container
    st.markdown('<div class="glass-panel" style="padding: 0.85rem 1.25rem; margin-bottom: 1.25rem;">', unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1.6, 2.4])

    with col_left:
        # Toggle selection mode
        is_select_mode = st.toggle("🔘 Multi-Select Mode", key=mode_key, value=st.session_state.get(mode_key, False))
        if is_select_mode:
            sel_count = len(selected_ids)
            st.markdown(
                f'<span class="mono-id" style="color: #2DD4BF; border-color: rgba(45, 212, 191, 0.4);">{sel_count} of {total_count} Selected</span>',
                unsafe_allow_html=True
            )

    with col_right:
        if is_select_mode:
            c1, c2, c3, c4 = st.columns([1.1, 1.1, 1.7, 1.7])
            with c1:
                if st.button("☑️ All", key=f"{prefix}_btn_sel_all", help="Select all displayed tasks"):
                    selected_ids.update(current_task_ids)
                    st.rerun()
            with c2:
                if st.button("⬜ Clear", key=f"{prefix}_btn_clear", help="Clear current selection"):
                    selected_ids.clear()
                    st.rerun()
            with c3:
                sel_count = len(selected_ids)
                btn_label = f"🗑️ Delete ({sel_count})"
                if st.button(btn_label, key=f"{prefix}_btn_del_sel", disabled=(sel_count == 0)):
                    st.session_state[confirm_del_sel_key] = True
                    st.session_state[confirm_del_all_key] = False
                    st.rerun()
            with c4:
                if st.button("🚨 Delete All", key=f"{prefix}_btn_del_all_mode"):
                    st.session_state[confirm_del_all_key] = True
                    st.session_state[confirm_del_sel_key] = False
                    st.rerun()
        else:
            _, c_del_all = st.columns([1.8, 1.8])
            with c_del_all:
                if st.button(f"🚨 Delete All Tasks ({total_count})", key=f"{prefix}_btn_del_all_direct"):
                    st.session_state[confirm_del_all_key] = True
                    st.session_state[confirm_del_sel_key] = False
                    st.rerun()

    # 2. Confirmation Dialogs
    if st.session_state.get(confirm_del_sel_key, False):
        sel_count = len(selected_ids)
        st.markdown(f"""
        <div class="stat-card urgent" style="margin-top: 0.75rem; border: 2px solid #F43F5E;">
            <div style="font-weight: 700; color: #FFFFFF; font-size: 1rem;">
                ⚠️ Confirm Batch Deletion of {sel_count} Selected Tasks?
            </div>
            <div style="color: #FDA4AF; font-size: 0.85rem; margin-top: 0.25rem;">
                This will permanently delete {sel_count} tasks from your workspace. This action cannot be undone.
            </div>
        </div>
        """, unsafe_allow_html=True)
        conf_col1, conf_col2 = st.columns(2)
        with conf_col1:
            if st.button(f"🚨 Yes, Delete {sel_count} Tasks", key=f"{prefix}_confirm_sel_yes", type="primary"):
                with st.spinner("Deleting selected tasks..."):
                    deleted = api_client.delete_tasks(list(selected_ids))
                    st.session_state[confirm_del_sel_key] = False
                    selected_ids.clear()
                    st.toast(f"Successfully deleted {deleted} tasks.")
                    st.rerun()
        with conf_col2:
            if st.button("✖️ Cancel", key=f"{prefix}_confirm_sel_no"):
                st.session_state[confirm_del_sel_key] = False
                st.rerun()

    if st.session_state.get(confirm_del_all_key, False):
        st.markdown(f"""
        <div class="stat-card urgent" style="margin-top: 0.75rem; border: 2px solid #F43F5E;">
            <div style="font-weight: 800; color: #FFFFFF; font-size: 1.1rem;">
                🚨 DANGER ZONE: Confirm Deletion of ALL {total_count} Tasks
            </div>
            <div style="color: #FDA4AF; font-size: 0.85rem; margin-top: 0.25rem;">
                You are about to permanently delete <strong>EVERY task ({total_count} items)</strong> in your workspace.
                This operation is IRREVERSIBLE.
            </div>
        </div>
        """, unsafe_allow_html=True)
        conf_col1, conf_col2 = st.columns(2)
        with conf_col1:
            if st.button("🚨 YES, PERMANENTLY DELETE ALL TASKS", key=f"{prefix}_confirm_all_yes", type="primary"):
                with st.spinner("Deleting all tasks..."):
                    all_ids = list(current_task_ids)
                    deleted = api_client.delete_tasks(all_ids)
                    st.session_state[confirm_del_all_key] = False
                    selected_ids.clear()
                    st.toast(f"Successfully deleted all {deleted} tasks.")
                    st.rerun()
        with conf_col2:
            if st.button("✖️ Cancel", key=f"{prefix}_confirm_all_no"):
                st.session_state[confirm_del_all_key] = False
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    return is_select_mode
