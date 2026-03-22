import pandas as pd
import streamlit as st

@st.cache_data(show_spinner="Loading data...")
def load_data(uploaded_file):
    """Loads a CSV file into a pandas DataFrame, with caching."""
    try:
        if hasattr(uploaded_file, "name"):
            # It's an uploaded file
            df = pd.read_csv(uploaded_file)
        else:
            # It's a path string (sample data)
            df = pd.read_csv(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Error reading CSV: {str(e)}")
        return None

def get_dataframe_info(df):
    """Returns basic information about the dataframe."""
    return {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicates": df.duplicated().sum(),
        "memory_usage": df.memory_usage(deep=True).sum() / 1024**2 # in MB
    }

def get_data_preview(df, rows=10):
    """Returns a limited preview of the dataset."""
    return df.head(rows)
