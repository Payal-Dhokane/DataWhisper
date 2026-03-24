import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import streamlit as st

# Set aesthetic styles
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

@st.cache_data(show_spinner="Analyzing data...")
def generate_summary_stats(df):
    """Returns summary statistics for the dataframe."""
    return df.describe(include='all').T

@st.cache_data(show_spinner="Generating Missing Values...")
def plot_missing_values(df):
    """Plots a heatmap of missing values using Seaborn."""
    if df.empty:
        return None
    missing_data = df.isnull()
    if missing_data.sum().sum() == 0:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(missing_data, yticklabels=False, cbar=False, cmap='viridis', ax=ax)
    ax.set_title('Missing Values Heatmap', pad=20)
    return fig

@st.cache_data(show_spinner="Generating Correlation Matrix...")
def plot_correlation_matrix(df):
    """Plots a correlation matrix using Seaborn."""
    if df.empty:
        return None
    numeric_df = df.select_dtypes(include=[np.number])
    # Remove columns that are all NaN or constant
    numeric_df = numeric_df.dropna(axis=1, how='all')
    numeric_df = numeric_df.loc[:, (numeric_df.nunique() > 1)] 
    
    if numeric_df.empty or numeric_df.shape[1] < 2:
        return None
    
    corr = numeric_df.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='RdBu_r', center=0, ax=ax)
    ax.set_title('Correlation Matrix', pad=20)
    return fig

@st.cache_data(show_spinner="Generating Distributions...")
def plot_distributions(df, max_plots=6):
    """Plots histograms for numeric columns using Seaborn."""
    plots_dict = {}
    if df.empty:
        return plots_dict
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols[:max_plots]:
        clean_data = df[col].dropna()
        if clean_data.empty:
            continue
            
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(clean_data, kde=True, color='#818cf8', ax=ax)
        ax.set_title(f'Distribution of {col}')
        plots_dict[col] = fig
    return plots_dict

@st.cache_data(show_spinner="Generating Categorical Counts...")
def plot_count_plots(df, max_plots=6, max_categories=20):
    """Plots count plots for categorical columns using Seaborn."""
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
            fig, ax = plt.subplots(figsize=(8, 4))
            # Sort by count for better visualization
            order = df[col].value_counts().index
            sns.countplot(data=df, x=col, order=order, palette='viridis', ax=ax)
            ax.set_title(f'Count Plot of {col}')
            plt.xticks(rotation=45)
            cat_plots_dict[col] = fig
            plt.tight_layout()
    return cat_plots_dict
