import streamlit as st
from typing import List, Dict, Any
from datetime import datetime, date
from frontend.components.cards import render_task_card
from frontend.components.batch_actions import render_batch_action_bar, get_selection_state

def render_schedule_view(api_client, tasks: List[Dict[str, Any]]) -> None:
    """
    Render calendar & deadlines view with overdue alert cards,
    today's itinerary, upcoming days timeline, and batch deletion operations.
    """
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="font-size: 2rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.25rem;">
            📅 Schedule & Deadlines
        </h1>
        <p style="color: #94A3B8; font-size: 0.95rem; margin: 0;">
            Timeline intelligence, overdue item alerts, and chronological task planning.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Batch Operations Bar (Select All, Delete Selected, Delete All)
    select_mode = render_batch_action_bar(tasks, api_client, view_prefix="sch")
    selected_ids = get_selection_state("sch")

    def toggle_select(tid: str, is_checked: bool):
        if is_checked:
            selected_ids.add(tid)
        else:
            selected_ids.discard(tid)

    today = date.today()
    today_str = today.isoformat()

    # Partition tasks by date status
    overdue = []
    due_today = []
    due_upcoming = []
    unscheduled = []

    for t in tasks:
        due = t.get("due_date")
        status = t.get("status")
        if not due:
            unscheduled.append(t)
            continue
        try:
            d_str = str(due)[:10]
            d_obj = datetime.strptime(d_str, "%Y-%m-%d").date()
            if status != "completed" and d_obj < today:
                overdue.append(t)
            elif d_obj == today:
                due_today.append(t)
            elif d_obj > today:
                due_upcoming.append((d_obj, t))
            else:
                # Completed past tasks
                unscheduled.append(t)
        except Exception:
            unscheduled.append(t)

    # 1. OVERDUE ALERT BANNER
    if overdue:
        st.markdown(f"""
        <div class="stat-card urgent" style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <span style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF;">
                        🚨 Overdue Deadlines ({len(overdue)})
                    </span>
                    <p style="color: #FDA4AF; font-size: 0.85rem; margin: 0.25rem 0 0 0;">
                        These tasks have passed their target completion date and require immediate intervention.
                    </p>
                </div>
                <span class="mono-id" style="color: #F43F5E; border-color: rgba(244, 63, 94, 0.4); font-size: 0.9rem;">
                    ACTION REQUIRED
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(2)
        for i, t in enumerate(overdue):
            tid = t.get("id", "")
            with cols[i % 2]:
                render_task_card(
                    t,
                    api_client=api_client,
                    show_actions=True,
                    selectable=select_mode,
                    is_selected=(tid in selected_ids),
                    checkbox_key=f"sch_ovd_{tid}",
                    on_select_toggle=toggle_select
                )

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 2. DUE TODAY
    st.markdown("""
    <div style="border-bottom: 2px solid #14B8A6; padding-bottom: 0.5rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: 700; color: #FFFFFF; font-size: 1.15rem;">📍 Scheduled for Today</span>
        <span class="mono-id" style="color: #2DD4BF;">Today: """ + today.strftime("%b %d, %Y") + """</span>
    </div>
    """, unsafe_allow_html=True)

    if due_today:
        cols = st.columns(2)
        for i, t in enumerate(due_today):
            tid = t.get("id", "")
            with cols[i % 2]:
                render_task_card(
                    t,
                    api_client=api_client,
                    show_actions=True,
                    selectable=select_mode,
                    is_selected=(tid in selected_ids),
                    checkbox_key=f"sch_tdy_{tid}",
                    on_select_toggle=toggle_select
                )
    else:
        st.markdown("""
        <div class="glass-panel" style="padding: 1.25rem; margin-bottom: 1.5rem; text-align: center;">
            <p style="color: #94A3B8; margin: 0;">No tasks currently scheduled for today.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 3. UPCOMING TIMELINE
    st.markdown("""
    <div style="border-bottom: 2px solid #6366F1; padding-bottom: 0.5rem; margin-bottom: 1rem;">
        <span style="font-weight: 700; color: #FFFFFF; font-size: 1.15rem;">🗓️ Upcoming Days</span>
    </div>
    """, unsafe_allow_html=True)

    if due_upcoming:
        due_upcoming.sort(key=lambda x: x[0])
        cols = st.columns(2)
        for i, (d_obj, t) in enumerate(due_upcoming):
            tid = t.get("id", "")
            delta = (d_obj - today).days
            rel_str = f"in {delta} days" if delta > 1 else "Tomorrow"
            with cols[i % 2]:
                st.caption(f"🗓️ {d_obj.strftime('%A, %b %d')} ({rel_str})")
                render_task_card(
                    t,
                    api_client=api_client,
                    show_actions=True,
                    selectable=select_mode,
                    is_selected=(tid in selected_ids),
                    checkbox_key=f"sch_upc_{tid}",
                    on_select_toggle=toggle_select
                )
    else:
        st.markdown("""
        <div class="glass-panel" style="padding: 1.25rem; margin-bottom: 1.5rem; text-align: center;">
            <p style="color: #94A3B8; margin: 0;">No upcoming scheduled tasks on the calendar.</p>
        </div>
        """, unsafe_allow_html=True)

    # 4. UNSCHEDULED / BACKLOG
    with st.expander(f"📦 Unscheduled Tasks & Archive ({len(unscheduled)})"):
        if unscheduled:
            cols = st.columns(2)
            for i, t in enumerate(unscheduled):
                tid = t.get("id", "")
                with cols[i % 2]:
                    render_task_card(
                        t,
                        api_client=api_client,
                        show_actions=True,
                        selectable=select_mode,
                        is_selected=(tid in selected_ids),
                        checkbox_key=f"sch_uns_{tid}",
                        on_select_toggle=toggle_select
                    )
        else:
            st.write("All tasks have scheduled target dates.")
