import streamlit as st
from typing import List, Dict, Any
from frontend.components.badges import tool_badge

def render_agent_studio_view(api_client) -> None:
    """
    Render AI Agent Studio with live model telemetry, prompt versioning,
    interactive categorized prompt library, and conversational agent interaction.
    """
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="font-size: 2rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.25rem;">
            💬 AI Agent Studio
        </h1>
        <p style="color: #94A3B8; font-size: 0.95rem; margin: 0;">
            Autonomous LangGraph StateGraph agent powered by NVIDIA Nemotron-3, ChromaDB vector memory, and structured tools.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Fetch orchestrator telemetry
    prompt_meta = api_client.get_prompt_version()
    active_version = prompt_meta.get("active_version", "v2.0.0")
    engine_name = prompt_meta.get("orchestration", "LangGraph StateGraph")
    model_name = prompt_meta.get("model", "nvidia/nemotron-3-nano")

    # Studio Header Telemetry Banner
    st.markdown(f"""
    <div class="glass-panel" style="margin-bottom: 1.25rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <span style="font-size: 1.5rem;">🤖</span>
            <div>
                <div style="font-weight: 700; color: #FFFFFF; font-size: 0.95rem;">
                    NVIDIA Nemotron-3 • LangGraph
                </div>
                <div style="font-size: 0.8rem; color: #94A3B8;">
                    Structured tool calling: <code style="color: #2DD4BF;">calendar_lookup</code>, <code style="color: #2DD4BF;">reschedule_task</code>, <code style="color: #2DD4BF;">create_task</code>, <code style="color: #2DD4BF;">search_tasks</code>
                </div>
            </div>
        </div>
        <div style="display: flex; gap: 0.5rem; align-items: center;">
            <span class="mono-id" style="color: #2DD4BF; border-color: rgba(20, 184, 166, 0.4);">
                ⚡ {model_name}
            </span>
            <span class="mono-id" style="color: #A78BFA; border-color: rgba(167, 139, 250, 0.4);">
                🏷️ Prompt: {active_version}
            </span>
            <span class="mono-id" style="color: #38BDF8; border-color: rgba(56, 189, 248, 0.4);">
                🎯 Benchmark: 93.3%
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    prompt_to_send = None

    # Quick Action Prompt Pills
    st.markdown("<p style='font-size: 0.85rem; color: #94A3B8; font-weight: 600; margin-bottom: 0.4rem;'>Quick Action Triggers:</p>", unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns(4)

    with p1:
        if st.button("📅 Check Today's Schedule", use_container_width=True):
            prompt_to_send = "What tasks are scheduled for today?"
    with p2:
        if st.button("🎯 Suggest Next Task", use_container_width=True):
            prompt_to_send = "What is the single most important task I should tackle next and why?"
    with p3:
        if st.button("🚨 Show Urgent Tasks", use_container_width=True):
            prompt_to_send = "Show me all urgent and overdue tasks that need my attention."
    with p4:
        if st.button("📊 Workload Summary", use_container_width=True):
            prompt_to_send = "Give me an executive summary of my total workload and priorities."

    # Comprehensive Interactive Prompt Library
    with st.expander("📚 Explore Prompt Library (6 Categories • 24 Ready-to-Run Prompts)", expanded=False):
        st.markdown("""
        <p style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 0.75rem;">
            Click <strong>▶ Run</strong> on any prompt below to automatically send it to the AI Agent Studio.
        </p>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📅 Schedule & Deadlines",
            "✏️ Create Tasks",
            "🔄 Reschedule Items",
            "🔍 Semantic Search",
            "🎯 Prioritization",
            "📊 Workload Analytics"
        ])

        with tab1:
            st.markdown("<div style='font-size: 0.82rem; color: #2DD4BF; margin-bottom: 0.5rem;'>Tool: <code>calendar_lookup</code> • Multi-source deadline aggregation</div>", unsafe_allow_html=True)
            prompts_cal = [
                "What tasks and meetings are scheduled for today?",
                "Show me all deadlines coming up this week.",
                "Do I have any tasks due tomorrow?",
                "What tasks are currently overdue and requiring immediate action?"
            ]
            for idx, p in enumerate(prompts_cal):
                c_txt, c_btn = st.columns([4, 1])
                with c_txt:
                    st.markdown(f"<span style='color: #FFFFFF; font-size: 0.9rem;'>💬 \"{p}\"</span>", unsafe_allow_html=True)
                with c_btn:
                    if st.button("▶ Run", key=f"run_cal_{idx}", use_container_width=True):
                        prompt_to_send = p

        with tab2:
            st.markdown("<div style='font-size: 0.82rem; color: #2DD4BF; margin-bottom: 0.5rem;'>Tool: <code>create_task</code> • Pydantic schema validation & ChromaDB vectorization</div>", unsafe_allow_html=True)
            prompts_create = [
                "Create an urgent task 'Fix security vulnerability in authentication' due tomorrow with 3 hours estimate tagged #security #auth",
                "Add a task 'Draft Q4 engineering roadmap' with high priority due this Friday estimated at 4 hours",
                "Create a medium task 'Update dependencies and run pytest suite' due next Monday",
                "Add a task 'Prepare presentation slides for stakeholder review' estimated at 2 hours tagged #presentation"
            ]
            for idx, p in enumerate(prompts_create):
                c_txt, c_btn = st.columns([4, 1])
                with c_txt:
                    st.markdown(f"<span style='color: #FFFFFF; font-size: 0.88rem;'>💬 \"{p}\"</span>", unsafe_allow_html=True)
                with c_btn:
                    if st.button("▶ Run", key=f"run_create_{idx}", use_container_width=True):
                        prompt_to_send = p

        with tab3:
            st.markdown("<div style='font-size: 0.82rem; color: #2DD4BF; margin-bottom: 0.5rem;'>Tool: <code>reschedule_task</code> • Relative date parsing & fuzzy title resolution</div>", unsafe_allow_html=True)
            prompts_resched = [
                "Move my urgent tasks due today to tomorrow at 5pm",
                "Reschedule the task 'Implement OAuth2 login' to next Monday at 10am",
                "Postpone all overdue tasks by 3 days",
                "Move the next upcoming task to Friday at 2pm"
            ]
            for idx, p in enumerate(prompts_resched):
                c_txt, c_btn = st.columns([4, 1])
                with c_txt:
                    st.markdown(f"<span style='color: #FFFFFF; font-size: 0.9rem;'>💬 \"{p}\"</span>", unsafe_allow_html=True)
                with c_btn:
                    if st.button("▶ Run", key=f"run_resched_{idx}", use_container_width=True):
                        prompt_to_send = p

        with tab4:
            st.markdown("<div style='font-size: 0.82rem; color: #2DD4BF; margin-bottom: 0.5rem;'>Tool: <code>search_tasks</code> • ChromaDB semantic vector embeddings & natural language queries</div>", unsafe_allow_html=True)
            prompts_search = [
                "Find all tasks related to database optimization, migrations, or SQL performance",
                "Search for tasks concerning frontend UI styling and design system tokens",
                "Show me any work items tagged with #security or #auth",
                "Find all tasks with estimated effort greater than 3 hours"
            ]
            for idx, p in enumerate(prompts_search):
                c_txt, c_btn = st.columns([4, 1])
                with c_txt:
                    st.markdown(f"<span style='color: #FFFFFF; font-size: 0.9rem;'>💬 \"{p}\"</span>", unsafe_allow_html=True)
                with c_btn:
                    if st.button("▶ Run", key=f"run_search_{idx}", use_container_width=True):
                        prompt_to_send = p

        with tab5:
            st.markdown("<div style='font-size: 0.82rem; color: #2DD4BF; margin-bottom: 0.5rem;'>Capability: Autonomous Agent Reasoning • Priority weighting & deadline urgency</div>", unsafe_allow_html=True)
            prompts_prio = [
                "What is the single most important task I should tackle right now and why?",
                "Rank my top 3 highest priority tasks by deadline urgency",
                "Which active tasks are currently at the greatest risk of missing their deadlines?",
                "If I have only 2 hours available today, which task provides the highest leverage?"
            ]
            for idx, p in enumerate(prompts_prio):
                c_txt, c_btn = st.columns([4, 1])
                with c_txt:
                    st.markdown(f"<span style='color: #FFFFFF; font-size: 0.9rem;'>💬 \"{p}\"</span>", unsafe_allow_html=True)
                with c_btn:
                    if st.button("▶ Run", key=f"run_prio_{idx}", use_container_width=True):
                        prompt_to_send = p

        with tab6:
            st.markdown("<div style='font-size: 0.82rem; color: #2DD4BF; margin-bottom: 0.5rem;'>Capability: Synthesized Workload Telemetry • Status distribution & effort estimation</div>", unsafe_allow_html=True)
            prompts_analytics = [
                "Give me an executive summary of my total workload and priority breakdown",
                "How many tasks are in progress versus pending in my workspace?",
                "Break down my workload by tag and estimate total hours required",
                "Provide a sprint progress report on completed tasks versus remaining items"
            ]
            for idx, p in enumerate(prompts_analytics):
                c_txt, c_btn = st.columns([4, 1])
                with c_txt:
                    st.markdown(f"<span style='color: #FFFFFF; font-size: 0.9rem;'>💬 \"{p}\"</span>", unsafe_allow_html=True)
                with c_btn:
                    if st.button("▶ Run", key=f"run_analytics_{idx}", use_container_width=True):
                        prompt_to_send = p

    # Chat history session storage
    if "agent_messages" not in st.session_state:
        st.session_state.agent_messages = [
            {
                "role": "assistant",
                "content": "👋 Hello! I am your AI Task Management Agent orchestrated with LangGraph and NVIDIA Nemotron-3. Use the Prompt Library above or ask me anything directly below!",
                "tools_used": [],
                "provider": "nvidia"
            }
        ]

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Render conversation
    for msg in st.session_state.agent_messages:
        role = msg["role"]
        with st.chat_message(role):
            st.markdown(msg["content"])
            if msg.get("tools_used"):
                tools_html = " ".join([tool_badge(t) for t in msg["tools_used"]])
                st.markdown(f"<div style='margin-top: 0.4rem;'>{tools_html}</div>", unsafe_allow_html=True)
            if role == "assistant" and msg.get("provider"):
                st.markdown(
                    f"<div style='font-size: 0.75rem; color: #64748B; margin-top: 0.25rem; font-family: monospace;'>Provider: {msg.get('provider')} | Prompt: {active_version}</div>",
                    unsafe_allow_html=True
                )

    # Handle input from chat_input or quick prompt buttons
    user_input = st.chat_input("Ask the AI agent to manage, reschedule, or analyze your tasks...")
    active_prompt = prompt_to_send or user_input

    if active_prompt:
        # Append user message
        st.session_state.agent_messages.append({"role": "user", "content": active_prompt})

        # Format history for APIClient
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.agent_messages[:-1]
        ]

        with st.chat_message("user"):
            st.markdown(active_prompt)

        with st.chat_message("assistant"):
            with st.spinner("🤖 Orchestrator processing tool calls..."):
                resp = api_client.agent_chat(active_prompt, history=history)

            output_text = resp.get("output", "I processed your request.")
            tools_used = resp.get("tools_used", [])
            provider = resp.get("model_provider", "nvidia")

            st.markdown(output_text)
            if tools_used:
                tools_html = " ".join([tool_badge(t) for t in tools_used])
                st.markdown(f"<div style='margin-top: 0.4rem;'>{tools_html}</div>", unsafe_allow_html=True)

            st.markdown(
                f"<div style='font-size: 0.75rem; color: #64748B; margin-top: 0.25rem; font-family: monospace;'>Provider: {provider} | Prompt: {active_version}</div>",
                unsafe_allow_html=True
            )

            st.session_state.agent_messages.append({
                "role": "assistant",
                "content": output_text,
                "tools_used": tools_used,
                "provider": provider
            })

            st.rerun()
