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
    """Renders an insight or recommendation in a glass card format."""
    st.markdown(f"""
    <div style="background: rgba(30, 30, 46, 0.6); backdrop-filter: blur(10px); padding: 24px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);">
        <h4 style="margin-top: 0; color: #A78BFA; font-weight: 700;">{icon} {title}</h4>
        <div style="color: #E5E7EB; font-size: 1rem; line-height: 1.6;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_step_indicator(current_step):
    """Renders a progress indicator for the user flow."""
    steps = ["Upload", "Analyze", "EDA", "Insights", "Export"]
    cols = st.columns(len(steps))
    for i, step in enumerate(steps):
        is_active = i <= current_step
        color = "#7C3AED" if is_active else "rgba(255,255,255,0.1)"
        text_color = "#ffffff" if is_active else "#94a3b8"
        with cols[i]:
            st.markdown(f"""
            <div style="text-align: center;">
                <div style="height: 4px; background-color: {color}; margin-bottom: 8px; border-radius: 10px; box-shadow: {'0 0 10px #7C3AED' if is_active else 'none'};"></div>
                <span style="color: {text_color}; font-weight: {'700' if is_active else '400'}; font-size: 0.85rem;">{i+1}. {step}</span>
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
        background: rgba(30, 30, 46, 0.6);
        backdrop-filter: blur(10px);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        margin-bottom: 1.5rem;
    }
    .insight-title {
        color: #A78BFA;
        font-weight: 700;
        font-size: 1.25rem;
        margin-bottom: 0.75rem;
    }
    /* Section Separation */
    hr {
        border: 0;
        height: 1px;
        background: linear-gradient(to right, transparent, rgba(255,255,255,0.1), transparent);
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
