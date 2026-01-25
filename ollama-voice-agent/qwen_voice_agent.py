import os
import torch
import streamlit as st
import soundfile as sf
from faster_whisper import WhisperModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from qwen_tts import Qwen3TTSModel
from st_audiorec import st_audiorec


# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
audios_directory = os.path.join(script_dir, 'audios')

# Voice configurations - Qwen3-TTS speakers
VOICE_CONFIG = {
    "English (US) - Ryan": {
        "language": "English",
        "speaker": "Ryan",
        "instruct": "Speak with enthusiasm and clarity"
    },
    "English (US) - Aiden": {
        "language": "English",
        "speaker": "Aiden",
        "instruct": "Speak naturally with a clear voice"
    },
    "Indonesian": {
        "language": "English",  # Qwen3-TTS doesn't have Indonesian, fallback to English
        "speaker": "Ryan",
        "instruct": "Speak clearly and naturally"
    }
}

# LLM Model configurations
LLM_MODELS = {
    "Qwen3 1.7B": "qwen3:1.7b",
    "Llama 3.2 Latest": "llama3.2:latest"
}

# Assistant template
assistant_template = """
You are a helpful, conversational assistant. Keep replies short and clear.
User: {input}
Assistant:
"""

@st.cache_resource
def load_stt():
    """Load Speech-to-Text model"""
    return WhisperModel("base", device="cpu", compute_type="int8")

@st.cache_resource
def load_tts():
    """Load Text-to-Speech model (Qwen3-TTS)"""
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    attn = "flash_attention_2" if torch.cuda.is_available() else "eager"
    
    return Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
        device_map=device,
        dtype=dtype,
        attn_implementation=attn,
    )

def transcribe_audio(file_path):
    """Transcribe audio using Whisper"""
    stt_model = load_stt()
    segments, _ = stt_model.transcribe(file_path)
    return " ".join([segment.text for segment in segments])

def save_recording(audio_bytes, output_path):
    """Save recorded audio"""
    with open(output_path, "wb") as audio_file:
        audio_file.write(audio_bytes)

def generate_response(text, model_name):
    """Generate LLM response"""
    try:
        model = ChatOllama(model=model_name)
        prompt = ChatPromptTemplate.from_template(assistant_template)
        chain = prompt | model
        response = chain.invoke({"input": text})
        return response.content
    except Exception as e:
        if "ConnectError" in str(type(e).__name__):
            raise ConnectionError("Ollama is not running. Start it with: ollama serve")
        raise

def synthesize_audio(text, output_path, voice_config):
    """Synthesize audio using Qwen3-TTS"""
    tts_model = load_tts()
    
    wavs, sr = tts_model.generate_custom_voice(
        text=text,
        language=voice_config["language"],
        speaker=voice_config["speaker"],
        instruct=voice_config["instruct"]
    )
    
    # Save to file
    sf.write(output_path, wavs[0], sr)

# Page config
st.set_page_config(page_title="Qwen Voice Agent", page_icon="🎙️", layout="wide")

# Header
st.title("🎙️ Qwen Voice Agent")

# Info expander
with st.expander("ℹ️ About this Agent"):
    st.markdown("""
    ### How it works:
    1. **Record** your voice using the microphone button below
    2. **Send** your recording - it will be transcribed using Whisper
    3. **AI responds** using Qwen3-1.7b running locally via Ollama
    4. **Listen** to the AI's response synthesized with Qwen3-TTS
    
    ### Technology Stack:
    - **Speech-to-Text**: Faster Whisper (base model)
    - **LLM**: Qwen3-1.7b (Ollama)
    - **Text-to-Speech**: Qwen3-TTS-12Hz-0.6B-CustomVoice
    
    All processing happens locally on your machine! 🔒
    """)

st.divider()

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")

    # LLM model selection
    selected_llm = st.selectbox(
        "🤖 LLM Model",
        options=list(LLM_MODELS.keys()),
        index=0
    )
    llm_model_name = LLM_MODELS[selected_llm]

    # Voice selection
    voice_selection = st.selectbox(
        "🗣️ Voice Selection",
        options=list(VOICE_CONFIG.keys()),
        index=0
    )
    
    selected_voice = VOICE_CONFIG[voice_selection]
    
    st.divider()
    st.markdown("### 📊 Session Info")
    st.metric("Messages", len(st.session_state.get("messages", [])))
    st.markdown(f"**LLM Model:** {selected_llm}")
    st.markdown(f"**Selected Voice:** {voice_selection}")
    st.markdown(f"**Speaker:** {selected_voice['speaker']}")
    st.markdown(f"**Language:** {selected_voice['language']}")
    st.markdown(f"**Device:** {'GPU (CUDA)' if torch.cuda.is_available() else 'CPU'}")

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
        try:
            with st.spinner("💻 Generating response..."):
                response = generate_response(transcription, llm_model_name)
        except ConnectionError as e:
            st.error(f"❌ {str(e)}")
            st.stop()
        
        # Synthesize audio with Qwen3-TTS
        with st.spinner("🔊 Synthesizing audio with Qwen3-TTS..."):
            response_path = os.path.join(audios_directory, f"response_{len(st.session_state.messages)}.wav")
            synthesize_audio(response, response_path, selected_voice)
        
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
