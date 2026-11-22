import streamlit as st
from typing import List, Dict, Any
from frontend.components.cards import render_task_card

def render_search_view(api_client) -> None:
    """
    Render semantic natural language vector search powered by ChromaDB embeddings.
    """
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="font-size: 2rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.25rem;">
            🔍 Semantic Task Search
        </h1>
        <p style="color: #94A3B8; font-size: 0.95rem; margin: 0;">
            Search across task descriptions, titles, and context using ChromaDB vector embeddings.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Search Bar
    query = st.text_input(
        "Semantic Search Query",
        placeholder="e.g. 'high priority security issues' or 'frontend user interface bugs'",
        label_visibility="collapsed"
    )

    # Quick Search Suggestion Pills
    st.markdown("<p style='font-size: 0.85rem; color: #94A3B8; font-weight: 600; margin-bottom: 0.4rem;'>Suggested Searches:</p>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    quick_q = None
    with s1:
        if st.button("🔐 Authentication & Security", use_container_width=True):
            quick_q = "authentication security login"
    with s2:
        if st.button("🎨 Frontend & UI Styling", use_container_width=True):
            quick_q = "frontend ui styling redesign"
    with s3:
        if st.button("🗄️ Database & Storage", use_container_width=True):
            quick_q = "database storage migration sql"
    with s4:
        if st.button("⚡ High Priority Urgencies", use_container_width=True):
            quick_q = "urgent high priority deadline"

    active_query = quick_q or query

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    if active_query:
        with st.spinner("Searching vector index..."):
            res = api_client.search_tasks(active_query)

        # res has structure: {'results': {'ids': [['id1', 'id2']], 'documents': [...], 'metadatas': [...]}}
        results_data = res.get("results", {})
        ids_nested = results_data.get("ids", [[]])
        matched_ids = ids_nested[0] if ids_nested else []

        st.markdown(f"""
        <div style="font-weight: 600; color: #2DD4BF; font-size: 0.95rem; margin-bottom: 1rem;">
            Found {len(matched_ids)} semantic matches for: <em>"{active_query}"</em>
        </div>
        """, unsafe_allow_html=True)

        if not matched_ids:
            st.markdown("""
            <div class="glass-panel" style="text-align: center; padding: 2rem;">
                <p style="color: #94A3B8; margin: 0;">No matching tasks found in vector space.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Fetch tasks
            cols = st.columns(2)
            for idx, task_id in enumerate(matched_ids):
                task = api_client.get_task(task_id)
                if task:
                    with cols[idx % 2]:
                        render_task_card(task, api_client=api_client, show_actions=True)
    else:
        st.markdown("""
        <div class="glass-panel" style="text-align: center; padding: 3rem 1rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🧠</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #FFFFFF;">Semantic Natural Language Search</div>
            <p style="color: #64748B; font-size: 0.9rem; margin-top: 0.25rem; max-width: 500px; margin-left: auto; margin-right: auto;">
                ChromaDB matches your queries by conceptual similarity rather than simple keyword matching. Try asking for concepts like "cloud infrastructure" or "performance bugs".
            </p>
        </div>
        """, unsafe_allow_html=True)
