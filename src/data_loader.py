import pandas as pd
import streamlit as st
from src.validators import RequestValidator, ValidationResult

@st.cache_data(show_spinner="Loading data...")
def load_data(uploaded_file):
    """Loads a CSV file into a pandas DataFrame, with caching and encoding detection."""
    file_validation = RequestValidator.validate_csv_file(uploaded_file)
    if not file_validation.is_valid:
        file_validation.show_error()
        return None
    
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings:
        try:
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=encoding)
            
            df_validation = RequestValidator.validate_dataframe(df)
            if not df_validation.is_valid:
                df_validation.show_error()
                return None
            
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            st.error(f"Error reading CSV with {encoding}: {str(e)}")
            return None
    
    st.error("Could not decode the CSV file. Please ensure it's a valid CSV with standard encoding.")
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
