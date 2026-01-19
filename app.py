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

# Admin Section
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
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
with col1:
    st.subheader("Ask DevMate")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What would you like to know?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Prepare history string for RAG
        history_str = ""
        for msg in st.session_state.messages[:-1]: # Exclude current prompt to avoid duplication if handled by RAG internally (though here we manage it manually)
            role_name = "Human" if msg["role"] == "user" else "Assistant"
            history_str += f"{role_name}: {msg['content']}\n"

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    from rag import ask_devmate
                    # Call RAG with history
                    result = ask_devmate(prompt, role, exp, history_str)
                    
                    if isinstance(result, dict):
                        response_text = result.get("answer", "")
                        sources = result.get("sources", [])
                    else:
                        response_text = str(result)
                        sources = []
                    
                    st.markdown(response_text)
                    
                    # specific display for sources
                    if sources:
                        with st.expander("📚 Source Documents"):
                            for source in sources:
                                st.caption(f"📄 {source}")
                                
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
