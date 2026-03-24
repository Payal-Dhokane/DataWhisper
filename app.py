import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Import custom modules
from src.data_loader import load_data, get_dataframe_info, get_data_preview
from src.eda import (
    generate_summary_stats, 
    plot_missing_values, 
    plot_correlation_matrix, 
    plot_distributions, 
    plot_count_plots
)
from src.llm_insights import generate_insights, explain_chart
from src.chat import get_pandas_agent, query_agent, get_suggested_questions
from src.recommendations import generate_recommendations # Keeping it for now
from src.auth import authenticate_user
from src.ui_components import render_header, render_insight_card, render_step_indicator, render_info_box, add_custom_css

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="DataWhisper | AI-Powered EDA", 
    layout="wide", 
    page_icon="📊", 
    initial_sidebar_state="expanded"
)

def load_css():
    """Loads external CSS for SaaS styling."""
    css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    add_custom_css()

def init_session_state():
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0 # 0: Upload, 1: Analyze, 2: EDA, 3: Insights, 4: Chat
    if 'insights' not in st.session_state:
        st.session_state.insights = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def main():
    load_css()
    init_session_state()
    
    # 1. Enforce Authentication
    is_authenticated, authenticator = authenticate_user()
    if not is_authenticated:
        return
        
    # Sidebar Logout
    if authenticator:
        authenticator.logout('Logout', 'sidebar')
    elif "google_auth" in st.session_state:
        if st.sidebar.button("Logout"):
            del st.session_state["google_auth"]
            st.rerun()
    st.sidebar.divider()
    st.sidebar.title("📊 DataWhisper")
    st.sidebar.markdown("Transform your data into actionable insights.")
    
    # Check for API Key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.sidebar.error("❌ GROQ_API_KEY missing in .env")
        st.sidebar.info("Get one at [console.groq.com](https://console.groq.com/)")
    else:
        st.sidebar.success("✅ AI Engine Ready (Groq)")

    # Sidebar Navigation - Step-by-Step
    st.sidebar.subheader("Navigation")
    steps = ["1. Upload Data", "2. Dataset Overview", "3. Visual EDA", "4. AI Insights", "5. Chat with Data", "6. Export Report"]
    
    # Map steps to st.session_state.current_step
    app_mode = st.sidebar.radio("Go to:", steps, index=st.session_state.current_step)
    st.session_state.current_step = steps.index(app_mode)
    
    render_step_indicator(st.session_state.current_step)

    # 1. Upload Data
    if st.session_state.current_step == 0:
        render_header("Upload Dataset", "Start by uploading your CSV file.", "📤")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
            if uploaded_file:
                st.session_state.uploaded_file = uploaded_file
                df = load_data(uploaded_file)
                if df is not None:
                    st.session_state.df = df
                    st.success(f"Successfully loaded {uploaded_file.name}!")
                    if st.button("Proceed to Overview →", type="primary"):
                        st.session_state.current_step = 1
                        st.rerun()
        
        with col2:
            render_info_box("Instructions", "Upload a CSV file with headers. Ensure numeric columns are properly formatted for correlation analysis.")
            if st.button("Load Sample Data (Titanic)", use_container_width=True):
                st.session_state.uploaded_file = "sample_data/titanic.csv"
                df = load_data("sample_data/titanic.csv")
                st.session_state.df = df
                st.session_state.current_step = 1
                st.rerun()

    # If no data is loaded, stop here
    if st.session_state.df is None and st.session_state.current_step > 0:
        st.warning("Please upload a dataset first.")
        st.session_state.current_step = 0
        st.rerun()
        return

    df = st.session_state.df

    # 2. Dataset Overview
    if st.session_state.current_step == 1:
        render_header("Dataset Overview", "A quick look at your data structure.", "📋")
        info = get_dataframe_info(df)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Rows", info['shape'][0])
        col2.metric("Columns", info['shape'][1])
        col3.metric("Missing Values", sum(info['missing_values'].values()))
        col4.metric("Duplicates", info['duplicates'])
        
        st.subheader("Data Preview (Top 10)")
        st.dataframe(get_data_preview(df), use_container_width=True)
        
        with st.expander("Show Column Details"):
            dtypes_df = pd.DataFrame({
                "Column": info['columns'],
                "Type": [info['dtypes'][c] for c in info['columns']],
                "Missing": [info['missing_values'][c] for c in info['columns']]
            })
            st.table(dtypes_df)
        
        if st.button("Proceed to EDA →", type="primary"):
            st.session_state.current_step = 2
            st.rerun()

    # 3. Visual EDA
    elif st.session_state.current_step == 2:
        render_header("Visual Exploratory Data Analysis", "Interactive visualizations powered by Plotly.", "📈")
        
        tab1, tab2, tab3 = st.tabs(["Summary & Missing", "Correlations", "Distributions"])
        
        with tab1:
            st.subheader("Summary Statistics")
            st.dataframe(generate_summary_stats(df), use_container_width=True)
            
            st.subheader("Missing Values")
            fig_missing = plot_missing_values(df)
            if fig_missing:
                st.plotly_chart(fig_missing, use_container_width=True)
                if st.button("Ask AI to explain this chart"):
                    explanation = explain_chart({"type": "Heatmap", "columns": "Missing values across all columns"})
                    st.info(explanation)
            else:
                st.success("No missing values found!")

        with tab2:
            st.subheader("Correlation Analysis")
            fig_corr = plot_correlation_matrix(df)
            if fig_corr:
                st.plotly_chart(fig_corr, use_container_width=True)
                if st.button("Explain Correlations"):
                    explanation = explain_chart({"type": "Correlation Matrix", "columns": "Numerical column relationships"})
                    st.info(explanation)
            else:
                st.info("Not enough numeric columns for correlation matrix.")

        with tab3:
            st.subheader("Numerical & Categorical Distributions")
            figs_dist = plot_distributions(df)
            figs_count = plot_count_plots(df)
            
            if figs_dist or figs_count:
                all_figs = {**figs_dist, **figs_count}
                cols = st.columns(2)
                for i, (col_name, fig) in enumerate(all_figs.items()):
                    with cols[i % 2]:
                        st.plotly_chart(fig, use_container_width=True)
                        if st.button(f"Explain {col_name} chart", key=f"btn_{col_name}"):
                            explanation = explain_chart({"type": "Distribution/Count Plot", "columns": col_name})
                            st.write(explanation)
            else:
                st.info("No visualizations could be generated.")

        if st.button("Generate AI Insights →", type="primary"):
            st.session_state.current_step = 3
            st.rerun()

    # 4. AI Insights
    elif st.session_state.current_step == 3:
        render_header("AI Powered Insights", "Smart analysis generated by Llama 3.", "🧠")
        
        if st.session_state.insights is None or st.button("Regenerate Insights"):
            with st.spinner("🤖 Analyzing dataset and thinking..."):
                info = get_dataframe_info(df)
                summary = generate_summary_stats(df).to_string()
                insights = generate_insights(
                    df_summary=summary,
                    column_names=str(info['columns']),
                    dtypes=str(info['dtypes']),
                    missing_values=str(info['missing_values']),
                    correlations="Calculated from numeric columns"
                )
                st.session_state.insights = insights
        
        st.markdown(st.session_state.insights)
        
        st.divider()
        
        if st.checkbox("Show Data Preprocessing Recommendations"):
            if 'recommendations' not in st.session_state or st.button("Regenerate Recommendations"):
                with st.spinner("🔍 Analyzing for recommendations..."):
                    info_str = str(get_dataframe_info(df))
                    st.session_state.recommendations = generate_recommendations(info_str)
            st.subheader("Actionable Recommendations")
            st.markdown(st.session_state.recommendations)
        
        if st.button("Start Chatting with Data →", type="primary"):
            st.session_state.current_step = 4
            st.rerun()

    # 5. Chat with Data
    elif st.session_state.current_step == 4:
        render_header("Chat with Data", "Ask natural language questions about your dataset.", "💬")
        
        # Suggested questions
        cols = st.columns(4)
        suggestions = get_suggested_questions()
        for i, ques in enumerate(suggestions):
            if cols[i].button(ques, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": ques})
                # Trigger agent execution...
                
        # Chat Interface
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        if prompt := st.chat_input("Ex: What is the average age of passengers who survived?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            agent = get_pandas_agent(df)
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    info = str(get_dataframe_info(df))
                    response = query_agent(agent, prompt, df_context=info)
                    st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # 6. Export Report
    elif st.session_state.current_step == 5:
        render_header("Export Report", "Download your analysis as a document.", "📄")
        st.info("Download a comprehensive report containing your dataset info, summary, and AI insights.")
        
        if st.button("Generate HTML Report", type="primary"):
            with st.spinner("Brewing your report..."):
                from src.report_generator import generate_html_report
                stats_df = generate_summary_stats(df)
                info = get_dataframe_info(df)
                # Note: Currently passing None for figs because generating them for report needs care 
                # (Plotly figs to HTML works differently than Matplotlib)
                # For now, keeping it simple as per original report_generator's expectation of figs
                # I might need to update report_generator later to support Plotly.
                
                html_report = generate_html_report(
                    info, 
                    stats_df, 
                    None, # fig_missing - need to handle plotly
                    None, # fig_corr - need to handle plotly
                    st.session_state.get('insights', 'No insights generated.'), 
                    "" # recommendations
                )
                
                st.download_button(
                    label="⬇️ Download Report (HTML)",
                    data=html_report,
                    file_name="datawhisper_report.html",
                    mime="text/html"
                )

if __name__ == "__main__":
    main()
