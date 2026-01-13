import os
import wave
import streamlit as st
from faster_whisper import WhisperModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from piper.voice import PiperVoice
from st_audiorec import st_audiorec


# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
audios_directory = os.path.join(script_dir, 'audios')
voices_directory = os.path.join(script_dir, 'voices')

# Voice configurations
VOICE_CONFIG = {
    "English (US)": {
        "lang_code": "en",
        "model": "en_US-lessac-medium.onnx"
    },
    "Indonesian": {
        "lang_code": "id",
        "model": "id_ID-news_tts-medium.onnx"
    }
}

# Assistant template
assistant_template = """
You are a helpful, conversational assistant. Keep replies short and clear.
User: {input}
Assistant:
"""

# Load LLM model
model = ChatOllama(model="llama3.2:latest")

@st.cache_resource
# Load Speech-to-Text model
def load_stt():
    return WhisperModel("base", device="cpu", compute_type="int8")

@st.cache_resource
# Load Text-to-Speech model
def load_tts(voice_path, config_path):
    return PiperVoice.load(voice_path, config_path, use_cuda=False)

# Transcribe audio function
def transcribe_audio(file_path):
    stt_model = load_stt()
    segments, _ = stt_model.transcribe(file_path)
    return " ".join([segment.text for segment in segments])

# Save recording function
def save_recording(audio_bytes, output_path):
    with open(output_path, "wb") as audio_file:
        audio_file.write(audio_bytes)

# Generate response function
def generate_response(text):
    prompt = ChatPromptTemplate.from_template(assistant_template)
    chain = prompt | model
    response = chain.invoke({"input": text})
    return response.content

# Synthesize audio function
def synthesize_audio(text, output_path, voice_language):
    voice_info = VOICE_CONFIG[voice_language]
    lang_code = voice_info["lang_code"]
    model_name = voice_info["model"]
    
    piper_voice_path = os.path.join(voices_directory, lang_code, model_name)
    piper_config_path = f"{piper_voice_path}.json"

    tts_model = load_tts(piper_voice_path, piper_config_path)
    with wave.open(output_path, "wb") as wav_file:
        tts_model.synthesize_wav(text, wav_file)

# Page config
st.set_page_config(page_title="Local Voice Agent", page_icon="🎙️", layout="wide")

# Header
st.title("🎙️ Local Voice Agent")

# Info expander
with st.expander("ℹ️ About this Agent"):
    st.markdown("""
    ### How it works:
    1. **Record** your voice using the microphone button below
    2. **Send** your recording - it will be transcribed using Whisper
    3. **AI responds** using Llama 3.2 running locally via Ollama
    4. **Listen** to the AI's response synthesized with Piper TTS
    
    ### Technology Stack:
    - **Speech-to-Text**: Faster Whisper (base model)
    - **LLM**: Llama 3.2 (Ollama)
    - **Text-to-Speech**: Piper TTS (en_US-lessac-medium)
    
    All processing happens locally on your machine! 🔒
    """)

st.divider()

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")

    # Voice language selection
    voice_language = st.selectbox(
        "🗣️ Voice Language",
        options=list(VOICE_CONFIG.keys()),
        index=0
    )
    st.divider()
    st.markdown("### 📊 Session Info")
    st.metric("Messages", len(st.session_state.get("messages", [])))
    st.markdown(f"**Selected Voice:** {voice_language}")
    st.markdown(f"**Model:** {VOICE_CONFIG[voice_language]['model']}")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat container for messages
chat_container = st.container()

with chat_container:
    st.markdown("**💬 Chat History**")
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.markdown(message["content"])
            if "audio_path" in message and os.path.exists(message["audio_path"]):
                st.audio(message["audio_path"])

# Fixed input area at bottom
st.divider()
input_container = st.container()

with input_container:
    col1, col2, col3 = st.columns([5, 1, 1])
    
    with col1:
        st.markdown("**🎙️ Voice Input**")
        audio_bytes = st_audiorec()
    
    with col2:
        st.markdown("**Actions**")
        send_button = st.button("📤 Send", use_container_width=True)
    
    with col3:
        st.markdown("**&nbsp;**")
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

if send_button:
    if not audio_bytes:
        st.error("⚠️ Please record audio first!")
    else:
        # Transcribe user audio
        with st.spinner("🎧 Transcribing audio..."):
            audio_path = os.path.join(audios_directory, "recording.wav")
            save_recording(audio_bytes, audio_path)
            transcription = transcribe_audio(audio_path)
        
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "avatar": "👤",
            "content": transcription,
        })
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(transcription)
        
        # Generate AI response
        with st.spinner("💻 Generating response..."):
            response = generate_response(transcription)
        
        # Synthesize audio
        with st.spinner("🔊 Synthesizing audio..."):
            response_path = os.path.join(audios_directory, f"response_{len(st.session_state.messages)}.wav")
            synthesize_audio(response, response_path, voice_language)
        
        # Add AI message to chat
        st.session_state.messages.append({
            "role": "assistant",
            "avatar": "💻",
            "content": response,
            "audio_path": response_path
        })
        
        # Display AI message
        with st.chat_message("assistant", avatar="💻"):
            st.markdown(response)
            st.audio(response_path)
        
        st.rerun()