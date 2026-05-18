import pandas as pd
import streamlit as st

# Maximum allowed CSV upload size. Raising this risks OOM on cloud instances
# because pandas loads the entire file into RAM. Adjust here if needed.
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

def validate_file_size(uploaded_file) -> bool:
    """
    Returns True if the uploaded file is within the allowed size limit.
    Shows a user-friendly error and returns False if the limit is exceeded.
    Only applies to Streamlit UploadedFile objects (not string paths used
    by the sample-data loader).
    """
    # String paths (e.g. "sample_data/titanic.csv") have no .size attribute
    if not hasattr(uploaded_file, "size"):
        return True

    if uploaded_file.size > MAX_FILE_SIZE_BYTES:
        size_mb = uploaded_file.size / (1024 * 1024)
        st.error(
            f"⚠️ File too large: **{size_mb:.1f} MB** "
            f"(limit is {MAX_FILE_SIZE_MB} MB). "
            "Please upload a smaller CSV file or pre-process your data locally."
        )
        return False

    return True

@st.cache_data(show_spinner="Loading data...")
def load_data(uploaded_file):
    """Loads a CSV file into a pandas DataFrame, with caching and encoding detection."""
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings:
        try:
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=encoding)
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
