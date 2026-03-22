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
    
    fig = px.imshow(
        missing_data, 
        aspect="auto", 
        color_continuous_scale="Viridis",
        title="Missing Values Heatmap",
        labels={"color": "Missing"}
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
    fig = px.imshow(
        corr, 
        text_auto=".2f", 
        aspect="auto", 
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        title="Correlation Matrix"
    )
    fig.update_layout(height=600)
    return fig

@st.cache_data(show_spinner="Generating Distributions...")
def plot_distributions(df, max_plots=5):
    """Plots histograms/distributions for numerical columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    figs = {}
    for col in numeric_cols[:max_plots]:
        fig = px.histogram(
            df, x=col, 
            marginal="box", # or violin, rug
            hover_data=df.columns,
            title=f"Distribution of {col}",
            color_discrete_sequence=['#818cf8']
        )
        fig.update_layout(height=400, showlegend=False)
        figs[col] = fig
    return figs

@st.cache_data(show_spinner="Generating Categorical Counts...")
def plot_count_plots(df, max_plots=5, max_categories=20):
    """Plots count plots for categorical columns."""
    cat_cols = df.select_dtypes(exclude=[np.number]).columns
    figs = {}
    for col in cat_cols:
        if len(figs) >= max_plots:
            break
        if df[col].nunique() <= max_categories:
            counts = df[col].value_counts().reset_index()
            counts.columns = [col, 'count']
            fig = px.bar(
                counts, x=col, y='count',
                title=f"Count Plot of {col}",
                color=col,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(height=400, showlegend=False)
            figs[col] = fig
    return figs
