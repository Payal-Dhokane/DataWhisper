import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data(show_spinner="Analyzing data...")
def generate_summary_stats(df):
    """Returns summary statistics for the dataframe."""
    return df.describe(include='all').T

@st.cache_data(show_spinner="Generating Plotly Missing Values...")
def plot_missing_values(df):
    """Plots a heatmap of missing values if any exist."""
    missing_data = df.isnull()
    if missing_data.sum().sum() == 0:
        return None
    
    # Sample if dataset is too large to prevent Plotly/Memory issues on Streamlit Cloud
    if len(df) > 5000:
        missing_data = missing_data.sample(5000)
    
    fig = px.imshow(
        missing_data, 
        aspect="auto", 
        color_continuous_scale="Viridis",
        title=f"Missing Values Heatmap {'(Sampled 5000 rows)' if len(df) > 5000 else ''}",
        labels={"color": "Missing"},
        template="plotly_dark" # Ensure it matches the theme
    )
    fig.update_layout(height=400)
    return fig

@st.cache_data(show_spinner="Generating Correlation Matrix...")
def plot_correlation_matrix(df):
    """Plots a correlation matrix for numerical columns."""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty or numeric_df.shape[1] < 2:
        return None
    
    corr = numeric_df.corr()
    
    # Explicitly use column names for axes to prevent "0,1,2,3" issue
    fig = px.imshow(
        corr, 
        text_auto=".2f", 
        aspect="auto", 
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        title="Correlation Matrix",
        x=corr.columns,
        y=corr.index,
        template="plotly_dark"
    )
    fig.update_layout(height=600)
    return fig

@st.cache_data(show_spinner="Generating Distributions...")
def plot_distributions(df, max_plots=5):
    """Plots histograms/distributions for numerical columns."""
    plots_dict = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) == 0:
        return plots_dict
        
    # Sample for performance if needed
    plot_df = df if len(df) <= 10000 else df.sample(10000)
    
    for col in numeric_cols[:max_plots]:
        fig = px.histogram(
            plot_df, x=col, 
            marginal="box", 
            title=f"Distribution of {col} {'(Sampled 10k)' if len(df) > 10000 else ''}",
            color_discrete_sequence=['#818cf8'],
            template="plotly_dark"
        )
        fig.update_layout(height=400, showlegend=False)
        plots_dict[col] = fig
    return plots_dict

@st.cache_data(show_spinner="Generating Categorical Counts...")
def plot_count_plots(df, max_plots=5, max_categories=20):
    """Plots count plots for categorical columns."""
    cat_plots_dict = {}
    cat_cols = df.select_dtypes(exclude=[np.number]).columns
    
    for col in cat_cols:
        if len(cat_plots_dict) >= max_plots:
            break
        if df[col].nunique() <= max_categories:
            counts = df[col].value_counts().reset_index()
            counts.columns = [col, 'count']
            fig = px.bar(
                counts, x=col, y='count',
                title=f"Count Plot of {col}",
                color=col,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                template="plotly_dark"
            )
            fig.update_layout(height=400, showlegend=False)
            cat_plots_dict[col] = fig
    return cat_plots_dict
