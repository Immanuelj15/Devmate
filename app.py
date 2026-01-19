import streamlit as st
import os

st.set_page_config(page_title="DevMate", layout="wide")

st.title("🤖 DevMate – Developer Onboarding Assistant")
st.write("Welcome to DevMate - Your Developer Onboarding Assistant")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    role = st.selectbox("Your Role", ["Intern", "Fresher", "Junior Dev", "Senior Dev"])
    exp = st.selectbox("Experience Level", ["0-1 years", "1-3 years", "3+ years"])

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Ask DevMate")
    question = st.text_area("What would you like to know?", placeholder="How do I run this project?", height=150)

with col2:
    st.subheader("Your Profile")
    st.write(f"**Role:** {role}")
    st.write(f"**Experience:** {exp}")
    
    st.divider()
    st.subheader("Admin")
    if st.button("🔄 Re-ingest Knowledge Base"):
        with st.spinner("Ingesting documents..."):
            try:
                from ingest_docs import ingest_docs
                ingest_docs()
                st.success("Ingestion complete!")
            except Exception as e:
                st.error(f"Ingestion failed: {e}")

if st.button("🚀 Ask DevMate", use_container_width=True):
    if question.strip():
        with st.spinner("Thinking..."):
            try:
                # Try to load RAG module
                from rag import ask_devmate
                response = ask_devmate(question, role, exp)
                if response:
                    st.success("Response received!")
                    st.write(response)
                else:
                    st.error("Empty response received. Check logs/credentials.")
            except Exception as e:
                st.warning(f"RAG module not available or failed: {str(e)}")
                st.info("Ensure AWS credentials are set in .env and dependencies are installed.")
                # Fallback removed to avoid confusion
    else:
        st.warning("Please enter a question first!")
