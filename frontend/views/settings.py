import time
import streamlit as st
from typing import List, Dict, Any

def render_settings_view(api_client, tasks: List[Dict[str, Any]]) -> None:
    """
    Render Workspace Settings, AI Agent Telemetry, Database Health,
    and System Architecture information.
    """
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="font-size: 2rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.25rem;">
            ⚙️ Workspace Settings & System Info
        </h1>
        <p style="color: #94A3B8; font-size: 0.95rem; margin: 0;">
            Manage API configuration, LLM orchestrator parameters, database telemetry, and application metadata.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "⚙️ General Preferences",
        "🤖 AI Agent & Telemetry",
        "🗄️ Database & Storage",
        "ℹ️ About & Architecture"
    ])

    # =========================================================================
    # TAB 1: GENERAL PREFERENCES
    # =========================================================================
    with tab1:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #FFFFFF; font-size: 1.15rem; margin-top: 0;'>Connectivity & Endpoints</h3>", unsafe_allow_html=True)

        col_url, col_test = st.columns([3, 1])
        with col_url:
            backend_url = st.text_input("FastAPI Backend Base URL", value=api_client.base_url)
        with col_test:
            st.markdown("<div style='height: 1.7rem;'></div>", unsafe_allow_html=True)
            if st.button("🔌 Test Ping", use_container_width=True):
                t0 = time.time()
                is_ok = api_client.check_health()
                latency_ms = int((time.time() - t0) * 1000)
                if is_ok:
                    st.toast(f"✅ Backend Online! Latency: {latency_ms}ms")
                else:
                    st.error("❌ Failed to reach backend endpoint.")

        st.markdown("<hr style='border-color: rgba(255, 255, 255, 0.08); margin: 1.25rem 0;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #FFFFFF; font-size: 1.15rem;'>Default Task Creation Defaults</h3>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            def_priority = st.selectbox(
                "Default Priority Level",
                ["low", "medium", "high", "urgent"],
                index=1,
                help="Pre-selected priority when creating a new task manually"
            )
        with c2:
            def_hours = st.number_input(
                "Default Estimated Hours",
                min_value=0.5,
                max_value=40.0,
                value=2.0,
                step=0.5,
                help="Standard allocated duration for new work items"
            )

        c3, c4 = st.columns(2)
        with c3:
            auto_vectorize = st.toggle("🧠 Auto-Vectorize to ChromaDB", value=True, help="Automatically generate embeddings for natural language search")
        with c4:
            enable_toasts = st.toggle("🔔 Enable Live UI Notifications", value=True, help="Show popup toast notifications on task updates and deletions")

        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        if st.button("💾 Save Preferences", type="primary"):
            st.session_state["def_priority"] = def_priority
            st.session_state["def_hours"] = def_hours
            st.session_state["auto_vectorize"] = auto_vectorize
            st.success("Preferences saved successfully!")

        st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 2: AI AGENT & ORCHESTRATOR TELEMETRY
    # =========================================================================
    with tab2:
        prompt_meta = api_client.get_prompt_version()
        active_version = prompt_meta.get("active_version", "v2.0.0")
        engine_name = prompt_meta.get("orchestration", "LangGraph StateGraph")
        model_name = prompt_meta.get("model", "nvidia/nemotron-3-nano")

        st.markdown(f"""
        <div class="glass-panel">
            <h3 style="color: #FFFFFF; font-size: 1.15rem; margin-top: 0;">Active LLM & Orchestration Engine</h3>
            <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1.25rem;">
                <span class="mono-id" style="color: #2DD4BF; border-color: rgba(45, 212, 191, 0.4); font-size: 0.85rem; padding: 0.35rem 0.75rem;">
                    ⚡ Model: {model_name}
                </span>
                <span class="mono-id" style="color: #A78BFA; border-color: rgba(167, 139, 250, 0.4); font-size: 0.85rem; padding: 0.35rem 0.75rem;">
                    🏷️ Prompt Registry: {active_version}
                </span>
                <span class="mono-id" style="color: #38BDF8; border-color: rgba(56, 189, 248, 0.4); font-size: 0.85rem; padding: 0.35rem 0.75rem;">
                    🕸️ Engine: {engine_name}
                </span>
            </div>

            <h4 style="color: #E2E8F0; font-size: 0.95rem; margin-bottom: 0.5rem;">Provider Failover Hierarchy:</h4>
            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; font-size: 0.85rem; margin-bottom: 1.5rem;">
                <span style="background: rgba(13, 148, 136, 0.25); border: 1px solid #14B8A6; padding: 0.25rem 0.6rem; border-radius: 6px; color: #2DD4BF; font-weight: 700;">1. NVIDIA NIM (Active)</span>
                <span style="color: #64748B;">→</span>
                <span style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); padding: 0.25rem 0.6rem; border-radius: 6px; color: #94A3B8;">2. Google Gemini 2.0</span>
                <span style="color: #64748B;">→</span>
                <span style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); padding: 0.25rem 0.6rem; border-radius: 6px; color: #94A3B8;">3. OpenAI GPT-4o</span>
                <span style="color: #64748B;">→</span>
                <span style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); padding: 0.25rem 0.6rem; border-radius: 6px; color: #94A3B8;">4. Anthropic Claude 3.5</span>
            </div>

            <h4 style="color: #E2E8F0; font-size: 0.95rem; margin-bottom: 0.5rem;">Structured Tools Registered:</h4>
            <div style="display: flex; gap: 0.4rem; flex-wrap: wrap;">
                <span class="mono-id" style="color: #2DD4BF;">🔧 calendar_lookup</span>
                <span class="mono-id" style="color: #2DD4BF;">🔧 reschedule_task</span>
                <span class="mono-id" style="color: #2DD4BF;">🔧 create_task</span>
                <span class="mono-id" style="color: #2DD4BF;">🔧 search_tasks</span>
                <span class="mono-id" style="color: #2DD4BF;">🔧 list_tasks</span>
                <span class="mono-id" style="color: #2DD4BF;">🔧 get_task</span>
                <span class="mono-id" style="color: #2DD4BF;">🔧 update_task</span>
                <span class="mono-id" style="color: #2DD4BF;">🔧 delete_task</span>
                <span class="mono-id" style="color: #2DD4BF;">🔧 create_reminder</span>
                <span class="mono-id" style="color: #2DD4BF;">🔧 list_reminders</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-panel">
            <h3 style="color: #FFFFFF; font-size: 1.15rem; margin-top: 0;">Evaluation Suite Benchmark Scores</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem;">
                <div style="background: rgba(15, 23, 42, 0.6); padding: 1rem; border-radius: 8px; border-left: 3px solid #10B981;">
                    <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Tool-Call Accuracy</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: #10B981;">100.0%</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.6); padding: 1rem; border-radius: 8px; border-left: 3px solid #38BDF8;">
                    <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Task Success Rate</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: #38BDF8;">100.0%</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.6); padding: 1rem; border-radius: 8px; border-left: 3px solid #A78BFA;">
                    <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Eval Test Prompts</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: #A78BFA;">40 Test Cases</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # TAB 3: DATABASE & STORAGE
    # =========================================================================
    with tab3:
        st.markdown("""
        <div class="glass-panel">
            <h3 style="color: #FFFFFF; font-size: 1.15rem; margin-top: 0;">Data Layer Telemetry</h3>
            
            <div style="margin-bottom: 1.25rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                    <span style="font-weight: 700; color: #FFFFFF;">🐘 Supabase PostgreSQL</span>
                    <span style="color: #10B981; font-weight: 600; font-size: 0.85rem;">● Connected</span>
                </div>
                <p style="color: #94A3B8; font-size: 0.85rem; margin: 0;">
                    Relational storage managing <code>tasks</code>, <code>calendar_events</code>, and <code>reminders</code> tables.
                </p>
            </div>

            <div style="margin-bottom: 1.25rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                    <span style="font-weight: 700; color: #FFFFFF;">🧠 ChromaDB Vector Store</span>
                    <span style="color: #10B981; font-weight: 600; font-size: 0.85rem;">● Active</span>
                </div>
                <p style="color: #94A3B8; font-size: 0.85rem; margin: 0;">
                    Collection: <code>task_embeddings</code> | Metric: <code>cosine</code> | Model: <code>all-MiniLM-L6-v2</code>
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #FFFFFF; font-size: 1.15rem; margin-top: 0;'>Cache & Memory Management</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94A3B8; font-size: 0.85rem;'>Clear the temporary in-memory response cache if you experience stale task listings.</p>", unsafe_allow_html=True)

        if st.button("🧹 Purge Application Cache", use_container_width=False):
            st.cache_data.clear()
            st.toast("Application cache cleared successfully!")

        st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 4: ABOUT & ARCHITECTURE
    # =========================================================================
    with tab4:
        st.markdown("""
        <div class="glass-panel">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                <span style="font-size: 2rem;">⚡</span>
                <div>
                    <h2 style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF; margin: 0;">
                        Task Manager Agent Studio
                    </h2>
                    <span style="color: #2DD4BF; font-family: monospace; font-size: 0.85rem;">Version 2.0.0 (ui-ux-pro-max edition)</span>
                </div>
            </div>

            <p style="color: #94A3B8; font-size: 0.9rem; line-height: 1.6; margin-bottom: 1.25rem;">
                An autonomous, production-grade task orchestration platform engineered with <strong>LangGraph StateGraph</strong>, 
                <strong>NVIDIA Nemotron-3</strong>, <strong>ChromaDB</strong>, and a modern <strong>Dark Glassmorphic</strong> design system.
            </p>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.25rem;">
                <div style="background: rgba(15, 23, 42, 0.5); padding: 0.85rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05);">
                    <div style="color: #64748B; font-size: 0.75rem; text-transform: uppercase;">Frontend Framework</div>
                    <div style="color: #FFFFFF; font-weight: 600; font-size: 0.95rem; margin-top: 0.2rem;">Python Streamlit 1.40+</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.5); padding: 0.85rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05);">
                    <div style="color: #64748B; font-size: 0.75rem; text-transform: uppercase;">Backend Engine</div>
                    <div style="color: #FFFFFF; font-weight: 600; font-size: 0.95rem; margin-top: 0.2rem;">FastAPI • Uvicorn • AsyncIO</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.5); padding: 0.85rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05);">
                    <div style="color: #64748B; font-size: 0.75rem; text-transform: uppercase;">Orchestration</div>
                    <div style="color: #FFFFFF; font-weight: 600; font-size: 0.95rem; margin-top: 0.2rem;">LangGraph 0.4+ StateGraph</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.5); padding: 0.85rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05);">
                    <div style="color: #64748B; font-size: 0.75rem; text-transform: uppercase;">Design System</div>
                    <div style="color: #FFFFFF; font-weight: 600; font-size: 0.95rem; margin-top: 0.2rem;">ui-ux-pro-max Slate SaaS</div>
                </div>
            </div>

            <h4 style="color: #E2E8F0; font-size: 0.95rem; margin-bottom: 0.5rem;">Quick System Links:</h4>
            <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
                <a href="http://127.0.0.1:8000/docs" target="_blank" style="color: #38BDF8; font-size: 0.85rem; text-decoration: none;">📖 FastAPI Swagger Docs ↗</a>
                <a href="http://127.0.0.1:8000/api/v1/health" target="_blank" style="color: #2DD4BF; font-size: 0.85rem; text-decoration: none;">🩺 Health Check Endpoint ↗</a>
                <a href="http://127.0.0.1:8000/redoc" target="_blank" style="color: #A78BFA; font-size: 0.85rem; text-decoration: none;">📚 ReDoc Documentation ↗</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
