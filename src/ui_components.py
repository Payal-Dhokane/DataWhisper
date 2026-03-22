import streamlit as st

def render_header(title, subtitle=None, icon=None):
    """Renders a consistent header for app sections."""
    if icon:
        st.title(f"{icon} {title}")
    else:
        st.title(title)
    if subtitle:
        st.markdown(f"*{subtitle}*")
    st.divider()

def render_insight_card(title, content, icon="💡"):
    """Renders an insight or recommendation in a card-like format."""
    st.markdown(f"""
    <div style="background-color: #1e2130; padding: 20px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px;">
        <h4 style="margin-top: 0; color: #818cf8;">{icon} {title}</h4>
        <div style="color: #cbd5e1; font-size: 0.95rem;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_step_indicator(current_step):
    """Renders a progress indicator for the user flow."""
    steps = ["Upload", "Analyze", "EDA", "Insights", "Chat"]
    cols = st.columns(len(steps))
    for i, step in enumerate(steps):
        is_active = i <= current_step
        color = "#6366f1" if is_active else "#334155"
        text_color = "#f8fafc" if is_active else "#94a3b8"
        with cols[i]:
            st.markdown(f"""
            <div style="text-align: center;">
                <div style="height: 4px; background-color: {color}; margin-bottom: 8px; border-radius: 2px;"></div>
                <span style="color: {text_color}; font-weight: {'600' if is_active else '400'}; font-size: 0.8rem;">{i+1}. {step}</span>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

def render_info_box(title, message, type="info"):
    """Renders a styled info/warning/success box."""
    if type == "info":
        st.info(f"**{title}**: {message}")
    elif type == "warning":
        st.warning(f"**{title}**: {message}")
    elif type == "success":
        st.success(f"**{title}**: {message}")
    elif type == "error":
        st.error(f"**{title}**: {message}")

def add_custom_css():
    """Adds additional custom CSS that might not be in the external file."""
    st.markdown("""
    <style>
    .insight-card {
        background-color: #1e2130;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .insight-title {
        color: #818cf8;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
