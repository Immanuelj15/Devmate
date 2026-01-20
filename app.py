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
    st.subheader("👤 Profile")
    role = st.selectbox("Your Role", ["Intern", "Fresher", "Junior Dev", "Senior Dev"])
    exp = st.selectbox("Experience", ["0-1 years", "1-3 years", "3+ years"])
    
    st.divider()
    st.subheader("🧠 Knowledge Base")
    
    # 1. Stats
    docs_path = "data/docs"
    if os.path.exists(docs_path):
        files = os.listdir(docs_path)
        num_files = len(files)
        st.info(f"📚 **{num_files}** Documents Indexed")
        with st.expander("View Index"):
            for f in files:
                st.caption(f"📄 {f}")
    else:
            st.info("0 Documents Indexed")
    
    # 2. Add Data (Tabs for cleaner UI)
    st.markdown("---")
    st.write("📥 **Add to Knowledge Base**")
    
    ingest_tabs = st.tabs(["📄 Upload", "🐙 GitHub"])
    
    with ingest_tabs[0]:
        uploaded_files = st.file_uploader("Drop PDF/TXT/MD here", 
                                        type=["pdf", "txt", "md"], 
                                        accept_multiple_files=True,
                                        label_visibility="collapsed")
        
        if uploaded_files:
            if st.button("✅ Process Files", use_container_width=True):
                save_path = "data/docs"
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                    
                with st.spinner("Saving..."):
                    count = 0
                    for uploaded_file in uploaded_files:
                        try:
                            file_path = os.path.join(save_path, uploaded_file.name)
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            count += 1
                        except Exception as e:
                            st.error(f"Error: {e}")
                    
                    if count > 0:
                        try:
                            from ingest_docs import ingest_docs
                            ingest_docs()
                            st.success(f"Added {count} files!")
                        except Exception as e:
                            st.error(f"Ingest failed: {e}")

    with ingest_tabs[1]:
        repo_url = st.text_input("Repo URL", placeholder="https://github.com/...", label_visibility="collapsed")
        
        if st.button("⬇️ Clone Repo", use_container_width=True):
            if repo_url:
                try:
                    import git
                    import shutil
                    
                    repo_name = repo_url.split("/")[-1].replace(".git", "")
                    clone_path = os.path.join("data", "repos", repo_name)
                    
                    if os.path.exists(clone_path):
                        # Helper to remove read-only files (common in git repos on Windows)
                        def on_rm_error(func, path, exc_info):
                            import stat
                            os.chmod(path, stat.S_IWRITE)
                            func(path)
                            
                        shutil.rmtree(clone_path, onerror=on_rm_error)
                    
                    with st.spinner(f"Cloning {repo_name}..."):
                        git.Repo.clone_from(repo_url, clone_path)
                        st.success(f"Cloned {repo_name}!")
                    
                    with st.spinner("Learning code..."):
                        from ingest_docs import ingest_docs
                        ingest_docs()
                        st.success("Brain Updated!")
                        
                except Exception as e:
                    st.error(f"Error: {e}")

    # 4. Actions
    st.divider()
    st.subheader("⚙️ Actions")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 Refresh", use_container_width=True):
             with st.spinner("Refreshing..."):
                try:
                    from ingest_docs import ingest_docs
                    ingest_docs()
                    st.success("Done!")
                except Exception as e:
                    st.error(f"{e}")
    with col_b:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# Main content area
# Main content area
tabs = st.tabs(["💬 Chat", "📝 Quiz Mode", "💻 Code Explainer"])
tab1, tab2, tab3 = tabs[0], tabs[1], tabs[2]

with tab1:
    st.subheader("Ask DevMate")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Container for all chat messages (History + New)
    chat_container = st.container()

    # Display chat messages from history on app rerun
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Custom CSS for Bottom Bar
    from streamlit_float import float_init
    from streamlit_mic_recorder import mic_recorder
    import io
    
    # Initialize float
    float_init()

    # Chat Logic Container
    # We use a container for the footer to hold inputs
    footer_container = st.container()
    
    # Logic variables
    user_input = None
    
    # Footer Content (Floating)
    with footer_container:
        # Style the container to look like a bar
        st.markdown("""
        <style>
            div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
                background-color: #0e1117;
                padding: 10px;
                border-top: 1px solid #30363d;
                border-radius: 10px;
                align-items: center;
            }
        </style>
        """, unsafe_allow_html=True)
        
        cols = st.columns([12, 1, 1])
        
        with cols[0]:
            # Text Input
            def submit():
                st.session_state.user_submitted = st.session_state.widget_input
                st.session_state.widget_input = "" # Clear input
            
            st.text_input("Message", placeholder="Message DevMate...", key="widget_input", on_change=submit, label_visibility="collapsed")
            
        with cols[1]:
            # Mic Button
            audio = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='recorder', format="wav")
            
        with cols[2]:
            # Send Button (Manual Trigger)
            # Use on_click callback to safely clear state
            st.button("➤", key="send_btn", on_click=submit)

    # Float the footer
    footer_container.float("bottom: 0rem; background-color: #0e1117; z-index: 1000;")

    # Handle Inputs (Text or Audio)
    if "user_submitted" in st.session_state and st.session_state.user_submitted:
        user_input = st.session_state.user_submitted
        st.session_state.user_submitted = None # Reset
        
    if audio:
        # Transcribe audio using speech_recognition
        import speech_recognition as sr
        r = sr.Recognizer()
        try:
             # mic_recorder returns dict with 'bytes'
             audio_bytes = audio['bytes']
             # SpeechRecognition needs a file-like object
             audio_file = io.BytesIO(audio_bytes)
             
             with sr.AudioFile(audio_file) as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data)
                user_input = text
        except Exception as e:
            st.warning(f"Audio Error: {e}")
            
    if user_input:
        # Append new messages to the SAME container
        with chat_container:
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
