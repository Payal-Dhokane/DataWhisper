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
    """Plots a heatmap of missing values using Seaborn for 100% reliability."""
    missing_data = df.isnull()
    if missing_data.sum().sum() == 0:
        return None
    
    # Use Matplotlib/Seaborn for reliability on Streamlit Cloud
    plt.figure(figsize=(10, 4))
    sns.heatmap(missing_data.head(1000), cbar=False, yticklabels=False, cmap='viridis')
    plt.title(f"Missing Values Heatmap {'(First 1000 rows)' if len(df) > 1000 else ''}")
    plt.tight_layout()
    fig = plt.gcf()
    plt.close()
    return fig

@st.cache_data(show_spinner="Generating Correlation Matrix...")
def plot_correlation_matrix(df):
    """Plots a correlation matrix using Seaborn for 100% reliability."""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty or numeric_df.shape[1] < 2:
        return None
    
    corr = numeric_df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='RdBu_r', center=0, square=True)
    plt.title("Correlation Matrix")
    plt.tight_layout()
    fig = plt.gcf()
    plt.close()
    return fig

@st.cache_data(show_spinner="Generating Distributions...")
def plot_distributions(df, max_plots=5):
    """Plots histograms/distributions using Matplotlib/Seaborn."""
    plots_dict = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) == 0:
        return plots_dict
        
    for col in numeric_cols[:max_plots]:
        plt.figure(figsize=(8, 4))
        sns.histplot(df[col].dropna(), kde=True, color='#818cf8')
        plt.title(f"Distribution of {col}")
        plt.tight_layout()
        plots_dict[col] = plt.gcf()
        plt.close()
    return plots_dict

@st.cache_data(show_spinner="Generating Categorical Counts...")
def plot_count_plots(df, max_plots=5, max_categories=20):
    """Plots count plots using Matplotlib/Seaborn."""
    cat_plots_dict = {}
    cat_cols = df.select_dtypes(exclude=[np.number]).columns
    
    for col in cat_cols:
        if len(cat_plots_dict) >= max_plots:
            break
        if df[col].nunique() <= max_categories:
            plt.figure(figsize=(8, 4))
            sns.countplot(data=df, x=col, palette='viridis')
            plt.title(f"Count Plot of {col}")
            plt.xticks(rotation=45)
            plt.tight_layout()
            cat_plots_dict[col] = plt.gcf()
            plt.close()
    return cat_plots_dict
