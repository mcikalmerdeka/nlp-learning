"""Model loading and embedding generation"""

import streamlit as st
from sentence_transformers import SentenceTransformer


@st.cache_resource
def load_model(model_name: str):
    """Load the sentence transformer model"""
    return SentenceTransformer(model_name)

