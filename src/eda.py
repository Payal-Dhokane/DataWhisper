import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def generate_summary_stats(df):
    """Returns summary statistics for the dataframe."""
    return df.describe(include='all')

def plot_missing_values(df):
    """Plots a heatmap of missing values if any exist."""
    if df.isnull().sum().sum() == 0:
        return None
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(df.isnull(), cbar=False, cmap='viridis', yticklabels=False, ax=ax)
    ax.set_title("Missing Values Heatmap")
    plt.tight_layout()
    return fig

def plot_correlation_matrix(df):
    """Plots a correlation matrix for numerical columns."""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty or numeric_df.shape[1] < 2:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 8))
    corr = numeric_df.corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5, ax=ax)
    ax.set_title("Correlation Matrix")
    plt.tight_layout()
    return fig

def plot_distributions(df, max_plots=5):
    """Plots histograms/distributions for numerical columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    figs = {}
    # Limit number of plots to avoid clutter
    for col in numeric_cols[:max_plots]:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(df[col].dropna(), kde=True, ax=ax, color='skyblue')
        ax.set_title(f"Distribution of {col}")
        plt.tight_layout()
        figs[col] = fig
    return figs

def plot_count_plots(df, max_plots=5, max_categories=20):
    """Plots count plots for categorical columns."""
    cat_cols = df.select_dtypes(exclude=[np.number]).columns
    figs = {}
    for col in cat_cols:
        if len(figs) >= max_plots:
            break
        # Only plot if number of unique categories is manageable
        if df[col].nunique() <= max_categories:
            fig, ax = plt.subplots(figsize=(6, 4))
            # Sort by counts for better visualization
            order = df[col].value_counts().index
            sns.countplot(y=col, data=df, order=order, ax=ax, palette='Set2')
            ax.set_title(f"Count Plot of {col}")
            plt.tight_layout()
            figs[col] = fig
    return figs
