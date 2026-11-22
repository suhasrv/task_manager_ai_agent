import streamlit as st
from typing import List, Dict, Any
from datetime import datetime
from frontend.components.cards import render_kpi_card, render_task_card

def render_dashboard_view(api_client, tasks: List[Dict[str, Any]]) -> None:
    """
    Render executive dashboard with high-level KPIs, progress velocity,
    priority breakdown, and active task spotlight.
    """
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="font-size: 2rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.25rem;">
            📊 Executive Dashboard
        </h1>
        <p style="color: #94A3B8; font-size: 0.95rem; margin: 0;">
            Real-time task velocity, priority distribution, and active workload telemetry.
        </p>
    </div>
    """, unsafe_allow_html=True)

    total_tasks = len(tasks)
    in_progress = len([t for t in tasks if t.get("status") == "in_progress"])
    pending = len([t for t in tasks if t.get("status") == "pending"])
    completed = len([t for t in tasks if t.get("status") == "completed"])
    urgent = len([t for t in tasks if (t.get("priority") == "urgent" or t.get("priority") == "high") and t.get("status") != "completed"])

    # 5 KPI cards
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_kpi_card("Total Workload", total_tasks, variant="total")
    with c2:
        render_kpi_card("In Progress", in_progress, variant="progress")
    with c3:
        render_kpi_card("Pending Queue", pending, variant="pending")
    with c4:
        render_kpi_card("Completed", completed, variant="completed")
    with c5:
        render_kpi_card("Urgent Action", urgent, variant="urgent")

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # Velocity and Completion Rate
    completion_rate = int((completed / total_tasks * 100)) if total_tasks > 0 else 0
    st.markdown(f"""
    <div class="glass-panel" style="margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-weight: 700; color: #FFFFFF; font-size: 1rem;">
                🚀 Sprint Completion Velocity
            </span>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; color: #2DD4BF; font-weight: 700;">
                {completed} of {total_tasks} Tasks Finished ({completion_rate}%)
            </span>
        </div>
        <div style="background: rgba(30, 41, 59, 0.7); border-radius: 9999px; height: 12px; width: 100%; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.05);">
            <div style="background: linear-gradient(90deg, #0D9488 0%, #14B8A6 50%, #2DD4BF 100%); height: 100%; width: {completion_rate}%; border-radius: 9999px; transition: width 0.5s ease-in-out;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                <span>🎯 Priority Breakdown</span>
            </div>
        """, unsafe_allow_html=True)

        priorities = {
            "urgent": len([t for t in tasks if t.get("priority") == "urgent"]),
            "high": len([t for t in tasks if t.get("priority") == "high"]),
            "medium": len([t for t in tasks if t.get("priority") == "medium"]),
            "low": len([t for t in tasks if t.get("priority") == "low"]),
        }

        for p_name, count in priorities.items():
            pct = int((count / total_tasks * 100)) if total_tasks > 0 else 0
            color = {
                "urgent": "#F43F5E",
                "high": "#FB923C",
                "medium": "#38BDF8",
                "low": "#94A3B8"
            }.get(p_name, "#94A3B8")

            st.markdown(f"""
            <div style="margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.25rem;">
                    <span style="color: #E2E8F0; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">{p_name}</span>
                    <span style="color: #94A3B8; font-family: 'JetBrains Mono', monospace;">{count} items ({pct}%)</span>
                </div>
                <div style="background: rgba(30, 41, 59, 0.5); border-radius: 9999px; height: 6px; width: 100%; overflow: hidden;">
                    <div style="background: {color}; height: 100%; width: {pct}%; border-radius: 9999px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                <span>🏷️ Taxonomy & Tags</span>
            </div>
        """, unsafe_allow_html=True)

        # Aggregate tags
        tag_counts = {}
        for t in tasks:
            for tag in t.get("tags") or []:
                clean = tag.strip().lower()
                tag_counts[clean] = tag_counts.get(clean, 0) + 1

        if tag_counts:
            sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            chips_html = "".join([
                f'<span class="tag-chip" style="font-size: 0.85rem; padding: 0.35rem 0.65rem; margin: 0.25rem;">#{tag} <strong style="color: #2DD4BF;">({count})</strong></span>'
                for tag, count in sorted_tags
            ])
            st.markdown(f'<div style="display: flex; flex-wrap: wrap; gap: 0.25rem;">{chips_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: #64748B; font-style: italic;'>No tags recorded across tasks yet.</p>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Active Work Spotlight
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
        <h2 style="font-size: 1.3rem; font-weight: 700; color: #FFFFFF; margin: 0;">
            🔥 Active Work Items (Needs Attention)
        </h2>
    </div>
    """, unsafe_allow_html=True)

    active_tasks = [t for t in tasks if t.get("status") != "completed"]
    # Sort by urgent first, then high
    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    active_tasks.sort(key=lambda t: priority_order.get((t.get("priority") or "medium").lower(), 4))

    spotlight = active_tasks[:4]

    if spotlight:
        cols = st.columns(2)
        for i, task in enumerate(spotlight):
            with cols[i % 2]:
                render_task_card(task, api_client=api_client, show_actions=True)
    else:
        st.markdown("""
        <div class="glass-panel" style="text-align: center; padding: 2.5rem 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎉</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #FFFFFF;">Inbox Zero!</div>
            <p style="color: #64748B; font-size: 0.9rem; margin-top: 0.25rem;">All tasks have been completed. Use the sidebar to create new work items or ask the AI agent.</p>
        </div>
        """, unsafe_allow_html=True)
