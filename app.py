import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from google import genai
from data_loader import load_data
from llm_parser import parse_query_to_intent, generate_nl_response
from query_engine import execute_query

# Load environment variables
load_dotenv()

# Initialize Gemini Client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="AI Customer Data Hybrid", page_icon="📈", layout="wide")

st.title("📈 AI Customer Data Hybrid Tool")
st.markdown("A robust AI-Data Pipeline: LLM Intent Parsing ➡️ Pandas Execution ➡️ NL Response Generation")

# --- Sidebar ---
with st.sidebar:
    st.header("Settings")
    if GEMINI_API_KEY:
        st.success("✅ API Key is securely configured by the host. No need to add it!")
        api_key_input = GEMINI_API_KEY
    else:
        api_key_input = st.text_input("Gemini API Key", type="password")
        
    uploaded_file = st.file_uploader("Upload Customer Data (Excel)", type=["xlsx", "xls"])

if not api_key_input:
    st.warning("Please enter your Gemini API Key in the sidebar.")
    st.stop()
else:
    client = genai.Client(api_key=api_key_input)

if uploaded_file is None:
    st.info("Please upload an Excel file to get started.")
    st.stop()

# --- Load Data Engine ---
try:
    df = load_data(uploaded_file)
    with st.expander("Preview Uploaded Data", expanded=False):
        st.dataframe(df.head(10))
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()

# --- Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "df" in message and message["df"] is not None:
            st.dataframe(message["df"])

# User input
if prompt := st.chat_input("E.g: How many customers have budget > 90 lakhs?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        with st.status("Thinking...", expanded=True) as status:
            try:
                # 1. Parse Intent with Conversation History
                status.update(label="Parsing intent with LLM...", state="running")
                # Exclude the current prompt from history since it's passed directly 
                chat_history_for_llm = st.session_state.messages[:-1] 
                intent = parse_query_to_intent(prompt, chat_history_for_llm, client)
                
                if not intent:
                    st.error("Could not parse query.")
                    st.stop()
                    
                st.write("**Parsed Intent:**", intent.model_dump())
                
                # 2. Strict Pandas Execution
                status.update(label="Executing Pandas Query...", state="running")
                raw_result, filtered_df = execute_query(intent, df)
                
                # Render DataFrames nicely as tables in the UI
                if not filtered_df.empty:
                    st.write("**Extracted Data Records:**")
                    st.dataframe(filtered_df)
                    
                st.write("**Engine Result:**", raw_result)
                nl_engine_input = str(raw_result)
                
                # 3. Generating Response
                status.update(label="Generating final response...", state="running")
                final_answer = generate_nl_response(prompt, nl_engine_input, client)
                
                status.update(label="Done!", state="complete")
                
            except Exception as e:
                status.update(label=f"Pipeline Error: {e}", state="error")
                final_answer = f"Error processing query: {e}"
        
        message_placeholder.markdown(final_answer)
        
        # Save both text and structural table data into the session memory
        save_df = filtered_df if (not filtered_df.empty and isinstance(filtered_df, pd.DataFrame)) else None
        st.session_state.messages.append({
            "role": "assistant", 
            "content": final_answer,
            "df": save_df
        })
