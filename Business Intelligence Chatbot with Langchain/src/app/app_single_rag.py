"""
Single-table database chat application (with RAG)
Note: For single table approach, RAG provides minimal benefit as schema is simple.
This is included for completeness but the basic version is recommended.
"""

import os
import sys
import streamlit as st

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from config import (
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME_SINGLE,
    MODEL_OPTIONS, SHOW_DEBUG_INFO, EMBEDDING_MODEL
)
from config.prompts import RESPONSE_GENERATION_SYSTEM_PROMPT
from core import DatabaseConnection, execute_sql_query, LLMClient

# Configure Streamlit
st.set_page_config(page_title="Chat with your database through LLMs")
st.header("Chat with your database through LLMs")

# Schema descriptions for single table
SCHEMA_DESCRIPTIONS = [
    "Table: sales, Column: ORDERNUMBER, Description: Unique identifier for sales order",
    "Table: sales, Column: QUANTITYORDERED, Description: Number of quantity of products sold in units",
    "Table: sales, Column: SALES, Description: Amount of sales or revenue in USD",
    "Table: sales, Column: PRODUCTLINE, Description: Line of products",
    "Table: sales, Column: ORDERDATE, Description: Date of the order",
    "Table: sales, Column: STATUS, Description: Current status of the order",
    "Table: sales, Column: QTR_ID, Description: Quarter of the year (1-4)",
    "Table: sales, Column: MONTH_ID, Description: Month of the year (1-12)",
    "Table: sales, Column: YEAR_ID, Description: Year when the order was placed",
    "Table: sales, Column: MSRP, Description: Manufacturer's suggested retail price",
    "Table: sales, Column: PRODUCTCODE, Description: Unique code identifying the product",
    "Table: sales, Column: CUSTOMERNAME, Description: Name of the customer",
    "Table: sales, Column: PHONE, Description: Customer's phone number",
    "Table: sales, Column: ADDRESSLINE1, Description: First line of customer's address",
    "Table: sales, Column: CITY, Description: Customer's city",
    "Table: sales, Column: STATE, Description: Customer's state or province",
    "Table: sales, Column: COUNTRY, Description: Customer's country",
    "Table: sales, Column: TERRITORY, Description: Sales territory",
    "Table: sales, Column: DEALSIZE, Description: Size of the deal (Small, Medium, Large)"
]

SQL_GENERATION_PROMPT = """
You are an expert in converting English questions to PostgreSQL query!

Based on the following database schema information:
{retrieved_schema}

Format your SQL query with proper indentation and line breaks.
The output should not include ``` or the word "sql".
Only return the SQL query, no other text.
Remember previous questions and context when generating SQL for follow-up questions.
"""

# Initialize vector store
if "vector_store" not in st.session_state:
    embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    st.session_state.vector_store = FAISS.from_texts(SCHEMA_DESCRIPTIONS, embedding=embedding_model)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# App info
st.expander("ℹ️ About Single-Table Database Chat with RAG").markdown(
    """
    - This version uses RAG to retrieve relevant schema information for each query.
    - Note: For single table databases, the basic version may be sufficient.
    - The AI assistant will convert your question into SQL and provide analysis.
    - Choose an AI model from the sidebar and connect to your database to get started!
    """
)

# Sidebar
with st.sidebar:
    st.subheader("Model Settings")
    model_choice = st.selectbox("Select a model", list(MODEL_OPTIONS.keys()), key="model_choice")
    
    st.subheader("Database Settings")
    st.text_input("Host", value=DB_HOST, key="Host")
    st.text_input("Port", value=DB_PORT, key="Port")
    st.text_input("User", value=DB_USER, key="User")
    st.text_input("Password", type="password", value=DB_PASSWORD, key="Password")
    st.text_input("Database", value=DB_NAME_SINGLE, key="Database")
    
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
    
    st.subheader("Chat Controls")
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.success("Chat history cleared!")

# Display chat history
for message in st.session_state.chat_history:
    st.chat_message(message["role"]).write(message["content"])

# User input
question = st.chat_input("Ask a question about your sales data")

if question:
    st.chat_message("user").write(question)
    st.session_state.chat_history.append({"role": "user", "content": question})
    
    with st.spinner("Processing your query..."):
        llm_client = LLMClient(st.session_state.model_choice)
        db_conn = DatabaseConnection(
            host=st.session_state["Host"],
            database=st.session_state["Database"],
            user=st.session_state["User"],
            password=st.session_state["Password"],
            port=st.session_state["Port"]
        )
        
        model_history = st.session_state.chat_history[:-1] if len(st.session_state.chat_history) > 1 else None
        
        # Retrieve relevant schema
        docs = st.session_state.vector_store.similarity_search(question, k=5)
        retrieved_schema = "\n".join([doc.page_content for doc in docs])
        
        if SHOW_DEBUG_INFO:
            with st.expander("Retrieved Schema"):
                st.text(retrieved_schema)
        
        # Generate SQL
        sql_query = llm_client.generate_response(
            question=question,
            system_prompt=SQL_GENERATION_PROMPT.format(retrieved_schema=retrieved_schema),
            history=model_history
        )
        
        if sql_query:
            if SHOW_DEBUG_INFO:
                st.subheader("Generated SQL Query:")
                st.code(sql_query, language="sql")
            
            result = execute_sql_query(db_conn, sql_query)
            
            if result:
                if SHOW_DEBUG_INFO:
                    st.subheader("Query Results:")
                    for row in result:
                        st.write(row)
                
                humane_response = llm_client.generate_response(
                    question=question,
                    system_prompt=RESPONSE_GENERATION_SYSTEM_PROMPT.format(question=question, result=result),
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
    <div class='footer'><p>mcikalmerdeka@gmail.com</p></div>
    """,
    unsafe_allow_html=True,
)
