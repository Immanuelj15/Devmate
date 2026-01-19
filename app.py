import streamlit as st
import os

st.set_page_config(page_title="DevMate", layout="wide")

# Custom CSS for UI Polish
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        color: white;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #00ffcc !important;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        color: white;
    }
    
    /* Chat Bubbles */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 8px;
        border: 1px solid #00c6ff;
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
