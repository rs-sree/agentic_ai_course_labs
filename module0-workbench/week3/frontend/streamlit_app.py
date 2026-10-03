"""
AI Workbench — Streamlit Frontend
Connects to the FastAPI backend via HTTP.
Architecture: Browser → Streamlit → FastAPI → LLM
"""

import streamlit as st
import requests
import os

st.set_page_config(page_title="AI Workbench", page_icon="🤖", layout="centered")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("AI Workbench")
st.caption("Powered by LLM — Select a task, paste your text, get results.")

task = st.selectbox(
    "Choose a task:",
    options=["summarize", "rewrite", "keypoints", "explain"],
    format_func=lambda x: x.replace("keypoints", "Key Points").title(),
)

text = st.text_area(
    "Input text:",
    height=200,
    placeholder="Paste the text you want to process...",
)

if st.button("Run AI", type="primary", disabled=not text.strip()):
    with st.spinner("Processing..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/{task}",
                json={"text": text},
                timeout=60,
            )
            if response.status_code == 200:
                data = response.json()
                st.success(f"Task: {data['task']} | Model: {data['model']}")
                st.markdown(data["result"])
                if data.get("tokens_used"):
                    st.caption(f"Tokens used: {data['tokens_used']}")
            else:
                st.error(f"Error {response.status_code}: {response.json().get('detail', 'Unknown error')}")
        except requests.ConnectionError:
            st.error(f"Cannot connect to backend at {BACKEND_URL}. Is it running?")
        except requests.Timeout:
            st.error("Request timed out. The LLM may be overloaded.")
