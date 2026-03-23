import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data(show_spinner="Analyzing data...")
def generate_summary_stats(df):
    """Returns summary statistics."""
    return df.describe(include='all').T

@st.cache_data(show_spinner="Generating Plotly Missing Values...")
def plot_missing_values(df):
    """Heatmap of missing values."""
    missing_data = df.isnull()
    if missing_data.sum().sum() == 0:
        return None
    
    # Simple heatmap with explicit labels
    fig = px.imshow(
        missing_data.head(500).astype(int), # Cast to int for clearer rendering
        aspect="auto", 
        color_continuous_scale="RdBu_r",
        title="Missing Values Heatmap (Showing Top 500)",
        labels={"color": "Is Missing?"},
        template="none" # Remove template for now to debug
    )
    fig.update_layout(height=400)
    return fig

@st.cache_data(show_spinner="Generating Correlation Matrix...")
def plot_correlation_matrix(df):
    """Correlation matrix."""
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
        title="Correlation Matrix",
        labels={"color": "Correlation"},
        template="none"
    )
    fig.update_layout(height=600)
    return fig

@st.cache_data(show_spinner="Generating Distributions...")
def plot_distributions(df, max_plots=5):
    """Distributions using Seaborn/Matplotlib as a robust alternative."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    figs = {}
    
    if len(numeric_cols) == 0:
        return figs

    for col in numeric_cols[:max_plots]:
        # Use classic matplotlib for reliability
        plt.figure(figsize=(8, 4))
        sns.histplot(df[col], kde=True, color='#6366f1')
        plt.title(f"Distribution of {col}")
        plt.tight_layout()
        figs[col] = plt.gcf() # Store Figure object
        plt.close() # Close to free memory
    return figs

@st.cache_data(show_spinner="Generating Categorical Counts...")
def plot_count_plots(df, max_plots=5, max_categories=20):
    """Count plots using Matplotlib for reliability."""
    cat_cols = df.select_dtypes(exclude=[np.number]).columns
    figs = {}
    
    for col in cat_cols:
        if len(figs) >= max_plots:
            break
        if df[col].nunique() <= max_categories:
            plt.figure(figsize=(8, 4))
            sns.countplot(data=df, x=col, palette='viridis')
            plt.title(f"Count of {col}")
            plt.xticks(rotation=45)
            plt.tight_layout()
            figs[col] = plt.gcf()
            plt.close()
    return figs
