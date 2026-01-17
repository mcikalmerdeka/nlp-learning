"""
Multi-table database chat application (Basic - without RAG)
"""

import os
import sys
import streamlit as st

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME_WRS,
    MODEL_OPTIONS, SHOW_DEBUG_INFO
)
from config.prompts import SQL_GENERATION_SYSTEM_PROMPT, RESPONSE_GENERATION_SYSTEM_PROMPT
from core import DatabaseConnection, execute_sql_query, LLMClient, load_schema_description

# Configure Streamlit
st.set_page_config(page_title="Chat with your database through LLMs")
st.header("Chat with your database through LLMs")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# App info
st.expander("ℹ️ About Multi-Table Database Chat").markdown(
    """
    - This app allows you to ask questions about a complex database with multiple related tables.
    - The AI assistant will convert your question into SQL, query the database, and provide a detailed analysis.
    - The system loads the full database schema to understand table relationships.
    - Choose an AI model from the sidebar and connect to your database to get started!
    - The chat has memory, so you can ask follow-up questions.
    """
)

# Sidebar
with st.sidebar:
    # Model settings
    st.subheader("Model Settings")
    model_choice = st.selectbox(
        "Select a model",
        list(MODEL_OPTIONS.keys()),
        key="model_choice"
    )
    
    # Database settings
    st.subheader("Database Settings")
    st.text_input("Host", value=DB_HOST, key="Host")
    st.text_input("Port", value=DB_PORT, key="Port")
    st.text_input("User", value=DB_USER, key="User")
    st.text_input("Password", type="password", value=DB_PASSWORD, key="Password")
    st.text_input("Database", value=DB_NAME_WRS, key="Database")
    
    if st.button("Test Connection"):
        with st.spinner("Testing database connection..."):
            db_conn = DatabaseConnection(
                host=st.session_state["Host"],
                database=st.session_state["Database"],
                user=st.session_state["User"],
                password=st.session_state["Password"],
                port=st.session_state["Port"]
            )
            db_conn.test_connection()
    
    # Chat controls
    st.subheader("Chat Controls")
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.success("Chat history cleared!")

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])

# User input
question = st.chat_input("Ask a question about your database")

if question:
    # Display user message
    st.chat_message("user").write(question)
    st.session_state.chat_history.append({"role": "user", "content": question})
    
    with st.spinner("Processing your query..."):
        # Initialize LLM client and database connection
        llm_client = LLMClient(st.session_state.model_choice)
        db_conn = DatabaseConnection(
            host=st.session_state["Host"],
            database=st.session_state["Database"],
            user=st.session_state["User"],
            password=st.session_state["Password"],
            port=st.session_state["Port"]
        )
        
        # Get conversation history
        model_history = st.session_state.chat_history[:-1] if len(st.session_state.chat_history) > 1 else None
        
        # Load schema and generate SQL
        schema = load_schema_description()
        sql_query = llm_client.generate_response(
            question=question,
            system_prompt=SQL_GENERATION_SYSTEM_PROMPT.format(database_schema_description=schema),
            history=model_history
        )
        
        if sql_query:
            if SHOW_DEBUG_INFO:
                st.subheader("Generated SQL Query:")
                st.code(sql_query, language="sql")
            
            # Execute query
            result = execute_sql_query(db_conn, sql_query)
            
            if result:
                if SHOW_DEBUG_INFO:
                    st.subheader("Query Results:")
                    for row in result:
                        st.write(row)
                
                # Generate human-friendly response
                humane_response = llm_client.generate_response(
                    question=question,
                    system_prompt=RESPONSE_GENERATION_SYSTEM_PROMPT.format(
                        question=question,
                        result=result
                    ),
                    history=model_history
                )
                
                st.chat_message("assistant").write(humane_response)
                st.session_state.chat_history.append({"role": "assistant", "content": humane_response})
            else:
                error_message = "No results returned from the query."
                st.error(error_message)
                st.session_state.chat_history.append({"role": "assistant", "content": error_message})
        else:
            error_message = "Failed to generate SQL query."
            st.error(error_message)
            st.session_state.chat_history.append({"role": "assistant", "content": error_message})

# Footer
st.markdown(
    """
    <style>
    .footer {position: fixed;left: 0;bottom: 0;width: 100%;background-color: #000;color: white;text-align: center;}
    </style>
    <div class='footer'>
        <p>mcikalmerdeka@gmail.com</p>
    </div>
    """,
    unsafe_allow_html=True,
)
