import pandas as pd
import streamlit as st

@st.cache_data
def load_data(filepath_or_buffer) -> pd.DataFrame:
    """Loads excel data and returns a pandas DataFrame."""
    try:
        df = pd.read_excel(filepath_or_buffer)
        
        # Preprocessing: Ensure 'Contact' is a string so it doesn't get comma-formatting in UI
        if 'Contact' in df.columns:
            # removing trailing .0 if pandas loaded it as float
            df['Contact'] = df['Contact'].astype(str).str.replace(r'\.0$', '', regex=True)
            
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to load data: {e}")
