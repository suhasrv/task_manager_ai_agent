import streamlit as st
from typing import List, Dict, Any

def render_sidebar(api_client, tasks: List[Dict[str, Any]]) -> str:
    """
    Render custom branded sidebar navigation, connection status, and quick metrics.
    Returns the selected page title.
    """
    # 1. Branding Header
    st.sidebar.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 0.6rem;">
            <span style="font-size: 1.8rem;">⚡</span>
            <div>
                <div style="font-weight: 800; font-size: 1.15rem; background: linear-gradient(135deg, #14B8A6 0%, #38BDF8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">TASK AGENT</div>
                <div style="font-size: 0.72rem; color: #64748B; letter-spacing: 0.05em; text-transform: uppercase;">AI Studio Edition</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Live Connection Health Pill
    is_healthy = api_client.check_health()
    status_color = "#10B981" if is_healthy else "#EF4444"
    status_text = "Backend Online" if is_healthy else "Backend Offline"

    st.sidebar.markdown(f"""
    <div style="display: inline-flex; align-items: center; gap: 0.4rem; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 9999px; padding: 0.2rem 0.65rem; margin-bottom: 1.25rem;">
        <span style="height: 8px; width: 8px; border-radius: 50%; background-color: {status_color}; display: inline-block;"></span>
        <span style="font-size: 0.75rem; font-weight: 600; color: #94A3B8;">{status_text}</span>
    </div>
    """, unsafe_allow_html=True)

    # 3. Navigation
    page = st.sidebar.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "📋 Task Board",
            "📅 Schedule & Calendar",
            "💬 AI Agent Studio",
            "✏️ Create Task",
            "🔍 Semantic Search",
            "⚙️ Settings"
        ],
        label_visibility="collapsed"
    )

    # 4. Quick Metrics Glance
    if tasks:
        st.sidebar.markdown("---")
        st.sidebar.markdown("<div style='font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 0.5rem;'>Workspace Quick Glance</div>", unsafe_allow_html=True)
        pending_cnt = len([t for t in tasks if t.get("status") == "pending"])
        urgent_cnt = len([t for t in tasks if (t.get("priority") == "urgent" and t.get("status") != "completed")])

        st.sidebar.markdown(f"""
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.4rem;">
            <span style="color: #94A3B8;">Pending Tasks:</span>
            <span style="font-weight: 700; color: #F59E0B;">{pending_cnt}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
            <span style="color: #94A3B8;">Urgent Deadlines:</span>
            <span style="font-weight: 700; color: #EF4444;">{urgent_cnt}</span>
        </div>
        """, unsafe_allow_html=True)

    # 5. Sidebar Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="font-size: 0.72rem; color: #64748B; line-height: 1.5;">
        <div>⚡ Engine: <strong>LangGraph StateGraph</strong></div>
        <div>🧠 Provider: <strong>NVIDIA NIM (Nemotron)</strong></div>
        <div>🏷️ Prompt: <strong>v2.0.0 (Structured)</strong></div>
    </div>
    """, unsafe_allow_html=True)

    return page
