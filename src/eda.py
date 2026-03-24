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
    if df.empty:
        return None
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
    if df.empty:
        return None
    numeric_df = df.select_dtypes(include=[np.number])
    # Remove columns that are all NaN or constant (std=0) as they break correlations
    numeric_df = numeric_df.dropna(axis=1, how='all')
    numeric_df = numeric_df.loc[:, (numeric_df.nunique() > 1)] 
    
    if numeric_df.empty or numeric_df.shape[1] < 2:
        return None
    
    corr = numeric_df.corr().fillna(0)
    
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.index,
        colorscale='RdBu_r',
        zmin=-1, zmax=1,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        hoverinfo="z"
    ))
    
    fig.update_layout(
        title="Correlation Matrix",
        height=600,
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        yaxis_autorange='reversed'
    )
    return fig

@st.cache_data(show_spinner="Generating Distributions...")
def plot_distributions(df, max_plots=6):
    """Plots histograms using Plotly graph_objects for better control."""
    plots_dict = {}
    if df.empty:
        return plots_dict
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols[:max_plots]:
        clean_data = df[col].dropna()
        if clean_data.empty:
            continue
            
        fig = go.Figure(data=[go.Histogram(
            x=clean_data,
            nbinsx=30,
            marker_color='#818cf8',
            opacity=0.75
        )])
        
        fig.update_layout(
            title=f"Distribution of {col}",
            height=350,
            xaxis_title=col,
            yaxis_title="Count",
            template="plotly_dark"
        )
        plots_dict[col] = fig
    return plots_dict

@st.cache_data(show_spinner="Generating Categorical Counts...")
def plot_count_plots(df, max_plots=6, max_categories=20):
    """Plots count plots using Plotly."""
    cat_plots_dict = {}
    if df.empty:
        return cat_plots_dict
    cat_cols = df.select_dtypes(exclude=[np.number]).columns
    
    for col in cat_cols:
        if len(cat_plots_dict) >= max_plots:
            break
        if df[col].dropna().empty:
            continue
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
