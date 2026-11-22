import os
import sys
from pathlib import Path

# Ensure project root is at front of sys.path so 'frontend' package is always resolvable
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st

# 1. Page Configuration (Must be first Streamlit call)
st.set_page_config(
    page_title="Task Manager Agent Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject ui-ux-pro-max Design System CSS
def load_css():
    css_path = Path(__file__).parent / "assets" / "theme.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

load_css()

# 3. Imports from new atomic modules
from frontend.api.client import APIClient
from frontend.components.nav import render_sidebar
from frontend.views.dashboard import render_dashboard_view
from frontend.views.task_board import render_task_board_view
from frontend.views.schedule import render_schedule_view
from frontend.views.agent_studio import render_agent_studio_view
from frontend.views.create_task import render_create_task_view
from frontend.views.search import render_search_view
from frontend.views.settings import render_settings_view

def main():
    api_client = APIClient()

    # Pre-fetch tasks
    try:
        tasks = api_client.list_tasks()
    except Exception:
        tasks = []

    # Render Sidebar and retrieve route selection
    active_page = render_sidebar(api_client, tasks)

    # Backend Connection Guard
    if not api_client.check_health():
        st.markdown("""
        <div class="stat-card urgent" style="margin-bottom: 1.5rem;">
            <div style="font-weight: 700; color: #FFFFFF; font-size: 1.05rem;">
                ⚠️ Backend Service Offline or Starting
            </div>
            <div style="color: #FDA4AF; font-size: 0.85rem; margin-top: 0.25rem;">
                Cannot connect to FastAPI backend at <code>http://127.0.0.1:8000/api/v1</code>.
                Please ensure the backend server is running.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Route Dispatcher
    if active_page == "📊 Dashboard":
        render_dashboard_view(api_client, tasks)
    elif active_page == "📋 Task Board":
        render_task_board_view(api_client, tasks)
    elif active_page == "📅 Schedule & Calendar":
        render_schedule_view(api_client, tasks)
    elif active_page == "💬 AI Agent Studio":
        render_agent_studio_view(api_client)
    elif active_page == "✏️ Create Task":
        render_create_task_view(api_client)
    elif active_page == "🔍 Semantic Search":
        render_search_view(api_client)
    elif active_page == "⚙️ Settings":
        render_settings_view(api_client, tasks)
    else:
        render_dashboard_view(api_client, tasks)

if __name__ == "__main__":
    main()
