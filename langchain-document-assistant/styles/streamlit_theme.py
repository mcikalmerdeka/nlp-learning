import streamlit as st

def apply_custom_theme():
    """Apply custom CSS theme to the Streamlit app"""
    st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        
        /* Chat Input Styling */
        .stChatInput input {
            background-color: #262730 !important;
            color: #fafafa !important;
            border: 1px solid #4a4a4a !important;
        }
        
        /* User Message Styling */
        .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
            background-color: #1e2130 !important;
            border: 1px solid #3a3f5c !important;
            color: #fafafa !important;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
        
        /* Assistant Message Styling */
        .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
            background-color: #262730 !important;
            border: 1px solid #4a4a4a !important;
            color: #fafafa !important;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
        
        /* Avatar Styling */
        .stChatMessage .avatar {
            background-color: #4b9eff !important;
            color: #ffffff !important;
        }
        
        /* Text Color Fix */
        .stChatMessage p, .stChatMessage div {
            color: #fafafa !important;
        }
        
        .stFileUploader {
            background-color: #262730;
            border: 1px solid #4a4a4a;
            border-radius: 5px;
            padding: 15px;
        }
        
        h1, h2, h3 {
            color: #4b9eff !important;
        }
        </style>
        """, unsafe_allow_html=True) 