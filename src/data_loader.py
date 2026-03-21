import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def load_data(uploaded_file):
    """Loads a CSV file into a pandas DataFrame, with caching."""
    try:
        # Check if it's a file-like object or a path (for sample data)
        df = pd.read_csv(uploaded_file)
        return df
    except Exception as e:
        return None

def get_dataframe_info(df):
    """Returns basic information about the dataframe."""
    return {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
    }
