import streamlit as st
from datetime import date, datetime
from frontend.components.badges import priority_badge, status_pill, tag_chip

def render_create_task_view(api_client) -> None:
    """
    Render structured task creation form with live preview.
    """
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="font-size: 2rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.25rem;">
            ✏️ Create New Task
        </h1>
        <p style="color: #94A3B8; font-size: 0.95rem; margin: 0;">
            Add a structured work item with priority weighting, deadlines, and taxonomy tags.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_preview = st.columns([1.3, 1])

    with col_form:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        with st.form("create_task_form", clear_on_submit=True):
            title = st.text_input("Task Title *", placeholder="e.g. Implement OAuth2 login with Google")
            description = st.text_area("Description", placeholder="Detailed steps, constraints, and acceptance criteria...", height=120)

            c1, c2 = st.columns(2)
            with c1:
                priority = st.selectbox("Priority Level", ["low", "medium", "high", "urgent"], index=1)
            with c2:
                due_date_val = st.date_input("Target Due Date", value=date.today())

            c3, c4 = st.columns(2)
            with c3:
                estimated_hours = st.number_input("Estimated Hours", min_value=0.5, max_value=120.0, value=2.0, step=0.5)
            with c4:
                tags_input = st.text_input("Tags (comma separated)", placeholder="frontend, auth, security")

            submitted = st.form_submit_button("🚀 Create Task", use_container_width=True, type="primary")

            if submitted:
                if not title.strip():
                    st.error("Task title is required!")
                else:
                    parsed_tags = [t.strip() for t in tags_input.split(",") if t.strip()]
                    due_iso = due_date_val.isoformat() if due_date_val else None

                    payload = {
                        "title": title.strip(),
                        "description": description.strip(),
                        "priority": priority,
                        "status": "pending",
                        "due_date": due_iso,
                        "estimated_hours": float(estimated_hours),
                        "tags": parsed_tags
                    }

                    try:
                        res = api_client.create_task(payload)
                        st.success(f"Task '{title}' created successfully!")
                        st.toast(f"Task created with ID {res.get('id', '')[:8]}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to create task: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    with col_preview:
        st.markdown("""
        <div style="font-weight: 700; color: #FFFFFF; font-size: 1.05rem; margin-bottom: 0.75rem;">
            👁️ Design Token Preview
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="task-item-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.4rem;">
                <div>
                    {priority_badge('urgent')}
                    {status_pill('pending')}
                </div>
                <span class="mono-id">demo-preview</span>
            </div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-top: 0.35rem; margin-bottom: 0.35rem;">
                Example Preview Card
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 0.6rem; line-height: 1.4;">
                This card reflects the styling of newly created tasks across all views in the workspace.
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: #64748B;">
                <span>📅 Due: {date.today().strftime('%b %d, %Y')}</span>
                <span>⏱️ 2.5h</span>
            </div>
            <div>
                {tag_chip('preview')}
                {tag_chip('ui-ux-pro')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-panel" style="margin-top: 1rem; font-size: 0.85rem; color: #94A3B8;">
            <div style="color: #2DD4BF; font-weight: 700; margin-bottom: 0.25rem;">💡 Pro Tip</div>
            Tasks created here are automatically vectorized into ChromaDB, making them instantly searchable via semantic natural language queries.
        </div>
        """, unsafe_allow_html=True)
