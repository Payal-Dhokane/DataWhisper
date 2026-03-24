import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data(show_spinner="Analyzing data...")
def generate_summary_stats(df):
    """Returns summary statistics for the dataframe."""
    return df.describe(include='all').T

@st.cache_data(show_spinner="Generating Missing Values...")
def plot_missing_values(df):
    """Plots a heatmap of missing values using Plotly."""
    missing_data = df.isnull().astype(int)
    if missing_data.sum().sum() == 0:
        return None
    
    # Take a sample if dataset is too large to keep it fast
    plot_df = missing_data.head(1000) if len(df) > 1000 else missing_data
    
    fig = px.imshow(
        plot_df, 
        color_continuous_scale='Viridis',
        title=f"Missing Values Heatmap {'(First 1000 rows)' if len(df) > 1000 else ''}",
        labels=dict(x="Columns", y="Rows", color="Missing")
    )
    fig.update_layout(height=400)
    return fig

@st.cache_data(show_spinner="Generating Correlation Matrix...")
def plot_correlation_matrix(df):
    """Plots a correlation matrix using Plotly."""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty or numeric_df.shape[1] < 2:
        return None
    
    corr = numeric_df.corr()
    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale='RdBu_r',
        zmin=-1, zmax=1,
        title="Correlation Matrix"
    )
    fig.update_layout(height=600)
    return fig

@st.cache_data(show_spinner="Generating Distributions...")
def plot_distributions(df, max_plots=6):
    """Plots histograms using Plotly."""
    plots_dict = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols[:max_plots]:
        fig = px.histogram(
            df, x=col, 
            nbins=30, 
            title=f"Distribution of {col}",
            color_discrete_sequence=['#818cf8']
        )
        fig.update_layout(height=350, showlegend=False)
        plots_dict[col] = fig
    return plots_dict

@st.cache_data(show_spinner="Generating Categorical Counts...")
def plot_count_plots(df, max_plots=6, max_categories=20):
    """Plots count plots using Plotly."""
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
                color_discrete_sequence=['#10b981']
            )
            fig.update_layout(height=350, showlegend=False)
            cat_plots_dict[col] = fig
    return cat_plots_dict
