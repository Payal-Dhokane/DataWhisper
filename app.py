import streamlit as st
import pandas as pd
from src.data_loader import load_data, get_dataframe_info
from src.eda import generate_summary_stats, plot_missing_values, plot_correlation_matrix, plot_distributions, plot_count_plots
from src.llm_insights import generate_insights
from src.chat import get_pandas_agent, query_agent
from src.recommendations import generate_recommendations
from src.auth import authenticate_user
import os

# Set page config
st.set_page_config(page_title="Smart EDA Assistant", layout="wide", page_icon="📊", initial_sidebar_state="expanded")

def load_css():
    """Loads external CSS for SaaS styling."""
    css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def init_session_state():
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'df' not in st.session_state:
        st.session_state.df = None

def main():
    load_css()
    
    # 1. Enforce Authentication
    is_authenticated, authenticator = authenticate_user()
    if not is_authenticated:
        return
        
    # 2. Render App (Only if logged in)
    init_session_state()
    
    # Add Logout button to top of sidebar
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.divider()
    
    st.sidebar.title("📊 Smart EDA")
    st.sidebar.markdown("Upload your CSV and get AI insights.")
    
    # API Key Input
    api_key = st.sidebar.text_input("OpenAI API Key (Required for AI)", type="password")
    if api_key:
        st.sidebar.success("API Key provided.")
    else:
        st.sidebar.warning("Please enter your OpenAI API Key to unlock AI features.")
        
    # File Uploader
    uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])
    
    # Navigation
    app_mode = st.sidebar.radio("Navigation", [
        "Overview", 
        "EDA", 
        "AI Insights & Recommendations", 
        "Chat with Data", 
        "Report Export"
    ])
    
    if uploaded_file is None and st.session_state.uploaded_file is None:
        st.info("Please upload a CSV file in the sidebar to begin.")
        if st.sidebar.button("Load Sample Data (Titanic)", type="primary"):
            st.session_state.uploaded_file = "sample_data/titanic.csv"
            st.rerun()
        return
    
    file_to_load = uploaded_file if uploaded_file else st.session_state.uploaded_file
    
    if file_to_load:
        df = load_data(file_to_load)
        if df is None:
            st.error("Error reading the CSV file. Please check the format.")
            return
            
        st.session_state.df = df

        if app_mode == "Overview":
            st.header("Dataset Overview")
            info = get_dataframe_info(df)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Rows", info['shape'][0])
            col2.metric("Columns", info['shape'][1])
            col3.metric("Missing Values", sum(info['missing_values'].values()))
            
            st.subheader("Data Preview")
            st.dataframe(df.head(10))
            
            st.subheader("Column Data Types & Missing Values")
            dtypes_df = pd.DataFrame({"Data Type": info['dtypes'], "Missing Values": info['missing_values']})
            st.dataframe(dtypes_df)

        elif app_mode == "EDA":
            st.header("Exploratory Data Analysis")
            
            st.subheader("Summary Statistics")
            st.dataframe(generate_summary_stats(df))
            
            st.subheader("Missing Values")
            fig_missing = plot_missing_values(df)
            if fig_missing:
                st.pyplot(fig_missing)
            else:
                st.success("No missing values found!")
                
            st.subheader("Correlation Matrix")
            fig_corr = plot_correlation_matrix(df)
            if fig_corr:
                st.pyplot(fig_corr)
            else:
                st.info("Not enough numeric columns for correlation matrix.")
                
            st.subheader("Distributions (Numeric)")
            figs_dist = plot_distributions(df)
            if figs_dist:
                cols = st.columns(2)
                for i, (col, fig) in enumerate(figs_dist.items()):
                    cols[i % 2].pyplot(fig)
                
            st.subheader("Categorical Counts")
            figs_count = plot_count_plots(df)
            if figs_count:
                cols = st.columns(2)
                for i, (col, fig) in enumerate(figs_count.items()):
                    cols[i % 2].pyplot(fig)

        elif app_mode == "AI Insights & Recommendations":
            st.header("AI Insights & Recommendations")
            if not api_key:
                st.warning("Please provide your OpenAI API Key in the sidebar.")
                return
                
            stats_str = generate_summary_stats(df).to_string()
            info_str = str(get_dataframe_info(df))
            
            if 'insights' not in st.session_state or st.button("Regenerate Insights"):
                with st.spinner("Generating Insights..."):
                    st.session_state.insights = generate_insights(stats_str, api_key)
            st.subheader("Key Insights")
            st.markdown(st.session_state.insights)
            
            st.divider()
            
            if 'recommendations' not in st.session_state or st.button("Regenerate Recommendations"):
                with st.spinner("Generating Recommendations..."):
                    st.session_state.recommendations = generate_recommendations(info_str, api_key)
            st.subheader("Recommendations for Next Steps")
            st.markdown(st.session_state.recommendations)
                
        elif app_mode == "Chat with Data":
            st.header("Chat with Data")
            if not api_key:
                st.warning("Please provide your OpenAI API Key in the sidebar.")
                return
                
            if "messages" not in st.session_state:
                st.session_state.messages = []
                
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    
            if prompt := st.chat_input("Ask a question about your data..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                    
                agent = get_pandas_agent(df, api_key)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = query_agent(agent, prompt)
                        st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
        elif app_mode == "Report Export":
            st.header("Report Generation")
            st.info("Download a comprehensive HTML report containing your EDA and AI insights.")
            
            if st.button("Generate HTML Report", type="primary"):
                with st.spinner("Compiling report..."):
                    from src.report_generator import generate_html_report
                    stats_df = generate_summary_stats(df)
                    info = get_dataframe_info(df)
                    fig_missing = plot_missing_values(df)
                    fig_corr = plot_correlation_matrix(df)
                    
                    insights = st.session_state.get('insights', '')
                    recommendations = st.session_state.get('recommendations', '')
                    
                    html_report = generate_html_report(info, stats_df, fig_missing, fig_corr, insights, recommendations)
                    
                    st.download_button(
                        label="⬇️ Download Your Report (HTML)",
                        data=html_report,
                        file_name="smart_eda_report.html",
                        mime="text/html"
                    )
                st.success("Report is ready!")

if __name__ == "__main__":
    main()
