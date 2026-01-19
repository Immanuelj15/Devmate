import streamlit as st
import os

st.set_page_config(page_title="DevMate", layout="wide")

# Custom CSS for UI Polish
st.markdown("""
<style>
    /* Global Styles - Modern Dark Theme */
    .stApp {
        background-color: #0e1117; /* Deep Charcoal */
        color: #e6e6e6;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #58a6ff !important; /* GitHub Blue */
    }
    p, div, label {
        color: #e6e6e6;
    }
    
    /* Buttons - Primary Action */
    .stButton>button {
        background-color: #238636; /* Dev Green */
        color: white;
        border: 1px solid rgba(240, 246, 252, 0.1);
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #2ea043;
        border-color: rgba(240, 246, 252, 0.1);
        transform: scale(1.02);
    }
    
    /* Chat Bubbles */
    .stChatMessage {
        background-color: #161b22; /* Sidebar Color */
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
    }
    
    /* Assistant Message specifically */
    .stChatMessage[data-testid="stChatMessage"][data-author="assistant"] {
        border-left: 4px solid #58a6ff; /* Blue Accent */
    }
    
    /* User Message specifically */
    .stChatMessage[data-testid="stChatMessage"][data-author="user"] {
        border-left: 4px solid #238636; /* Green Accent */
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #010409;
        border-right: 1px solid #30363d;
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        background-color: #0d1117;
        color: #e6e6e6;
        border: 1px solid #30363d;
        border-radius: 6px;
    }
    .stTextInput>div>div>input:focus {
        border-color: #58a6ff;
    }
    
    /* Audio Input */
    [data-testid="stAudioInput"] {
        background-color: #161b22;
        border-radius: 12px;
        border: 1px solid #30363d;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #161b22;
        color: #58a6ff;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 DevMate – Developer Onboarding Assistant")
st.write("Welcome to DevMate - Your Developer Onboarding Assistant")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    role = st.selectbox("Your Role", ["Intern", "Fresher", "Junior Dev", "Senior Dev"])
    exp = st.selectbox("Experience Level", ["0-1 years", "1-3 years", "3+ years"])

# Main content area
# Main content area
tabs = st.tabs(["💬 Chat", "📝 Quiz Mode", "💻 Code Explainer"])
tab1, tab2, tab3 = tabs[0], tabs[1], tabs[2]

with tab1:
    col1, col2 = st.columns([2, 1])
    
    # Admin Section
    with col2:
        st.subheader("Your Profile")
        st.write(f"**Role:** {role}")
        st.write(f"**Experience:** {exp}")
        
        st.divider()
        st.subheader("Knowledge Base")
        
        # File Uploader
        uploaded_files = st.file_uploader("Upload Docs (PDF, TXT, MD)", 
                                        type=["pdf", "txt", "md"], 
                                        accept_multiple_files=True)
        
        if uploaded_files:
            if st.button("Submit & Process"):
                save_path = "data/docs"
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                    
                with st.spinner("Saving and indexing..."):
                    count = 0
                    for uploaded_file in uploaded_files:
                        try:
                            file_path = os.path.join(save_path, uploaded_file.name)
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            count += 1
                        except Exception as e:
                            st.error(f"Error saving {uploaded_file.name}: {e}")
                    
                    if count > 0:
                        try:
                            from ingest_docs import ingest_docs
                            ingest_docs()
                            st.success(f"Successfully added {count} documents!")
                        except Exception as e:
                            st.error(f"Ingestion failed: {e}")
                            
        if st.button("🔄 Re-ingest All Custom Data"):
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

        # Voice Input Option
        # Voice Input Option (Native)
        input_audio = st.audio_input("🎙️ Speak to DevMate")
        
        user_input = None
        
        if input_audio:
            # Transcribe audio using speech_recognition
            import speech_recognition as sr
            r = sr.Recognizer()
            try:
                with sr.AudioFile(input_audio) as source:
                    audio_data = r.record(source)
                    text = r.recognize_google(audio_data)
                    user_input = text
            except Exception as e:
                st.warning(f"Could not understand audio: {e}")
        
        # React to user input (text bar overrides voice if both present)
        # We need to handle the case where audio input is present but user also types
        # But st.audio_input persists. 
        # Logic: If audio changed, use audio. If text submitted, use text.
        # Simple logic: If text input is submitted, use it. Else if audio is there, use it.
        
        if prompt := st.chat_input("What would you like to know?"):
             user_input = prompt
             user_input = prompt
             
        if user_input:
            # Display user message in chat message container
            st.chat_message("user").markdown(user_input)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Prepare history string for RAG
            history_str = ""
            for msg in st.session_state.messages[:-1]: 
                role_name = "Human" if msg["role"] == "user" else "Assistant"
                history_str += f"{role_name}: {msg['content']}\n"

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        from rag import ask_devmate
                        # Call RAG with history
                        result = ask_devmate(user_input, role, exp, history_str)
                        
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
                        
                        # Generate and play audio
                        try:
                            from gtts import gTTS
                            from io import BytesIO
                            
                            # Create a BytesIO buffer
                            audio_bytes = BytesIO()
                            
                            # Generate speech
                            tts = gTTS(text=response_text, lang='en')
                            tts.write_to_fp(audio_bytes)
                            
                            # Play audio
                            st.audio(audio_bytes, format='audio/mp3')
                        except Exception as e:
                            st.warning(f"Audio generation failed: {e}")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

with tab2:
    st.header("🎮 Knowledge Check")
    st.write("Test your knowledge about the project!")
    
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = []

    if st.button("🎲 Generate New Quiz"):
        with st.spinner("Creating quiz from documents..."):
            from rag import generate_quiz
            st.session_state.quiz_data = generate_quiz()
            # Clear previous answers
            st.session_state.quiz_answers = {}
            
    if st.session_state.quiz_data:
        if "quiz_answers" not in st.session_state:
            st.session_state.quiz_answers = {}
            
        score = 0
        total = len(st.session_state.quiz_data)
        
        for i, q in enumerate(st.session_state.quiz_data):
            st.subheader(f"Q{i+1}: {q['question']}")
            
            # Radio button for options
            options = q['options']
            # We need a unique key for each question's radio button
            user_answer = st.radio(f"Select logic for Q{i+1}", options, label_visibility="collapsed", key=f"q_{i}")
            
            if user_answer == q['answer']:
                st.success("Correct! ✅")
                score += 1
            else:
                st.write("Pick an answer.")
                
        if st.button("Submit Score"):
             st.balloons()
             st.info(f"You got {score} out of {total} correct!")
    else:
        st.info("Click 'Generate New Quiz' to start!")

tab3 = tabs[2] 
with tab3:
    st.header("💻 Code Explainer")
    st.write("Paste a code snippet below, and DevMate will explain it to you!")
    
    code_input = st.text_area("Paste Code Here", height=200, placeholder="def hello_world():\n    print('Hello')")
    
    if st.button("🧐 Explain Code"):
        if code_input.strip():
            with st.spinner("Analyzing code..."):
                from rag import explain_code
                explanation = explain_code(code_input)
                st.markdown("### Explanation")
                st.markdown(explanation)
        else:
            st.warning("Please paste some code first!")
