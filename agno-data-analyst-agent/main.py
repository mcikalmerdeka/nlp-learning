from typing import Any
from utils import preprocess_and_save
import streamlit as st
from agno.models.openai import OpenAIChat
from agno.agent import Agent
from agno.tools.pandas import PandasTools

# Streamlit app
st.title("📊 Data Analyst Agent")

# Sidebar for API keys
with st.sidebar:
    st.header("API Keys")
    openai_key = st.text_input("Enter your OpenAI API key:", type="password")
    if openai_key:
        st.session_state.openai_key = openai_key
        st.success("API key saved!")
    else:
        st.warning("Please enter your OpenAI API key to proceed.")

# File upload widget
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None and "openai_key" in st.session_state:
    # Preprocess and save the uploaded file
    temp_path, columns, df = preprocess_and_save(uploaded_file)
    
    if temp_path and columns and df is not None:
        # Display the uploaded data as a table
        st.write("Uploaded Data:")
        st.dataframe(df)  # Use st.dataframe for an interactive table
        
        # Display the columns of the uploaded data
        st.write("Uploaded columns:", columns)
        
        # Initialize PandasTools and pre-load the dataframe
        pandas_tools = PandasTools()
        pandas_tools.dataframes["uploaded_data"] = df
        
        # Initialize the Agent with PandasTools
        data_analyst = Agent(
            model=OpenAIChat(id="gpt-4.1-mini", api_key=st.session_state.openai_key),
            tools=[pandas_tools],
            markdown=True,
            instructions=[
                f"You are an expert data analyst.",
                f"A pandas DataFrame named 'uploaded_data' is already loaded with {len(df)} rows.",
                f"Columns: {', '.join(columns)}",
                f"Column types: {dict[Any, Any](df.dtypes)}",
                f"Sample data:\n{df.head(3).to_string()}",
                "Use the run_dataframe_operation tool to analyze 'uploaded_data'.",
                "Always provide clear insights and explanations with your analysis.",
            ]
        )
        
        # Initialize code storage in session state
        if "generated_code" not in st.session_state:
            st.session_state.generated_code = None
        
        # Main query input widget
        user_query = st.text_area("Ask a query about the data:")
        
        # Add info message about terminal output
        st.info("💡 Check your terminal for a clearer output of the agent's response")
        
        if st.button("Submit Query"):
            if user_query.strip() == "":
                st.warning("Please enter a query.")
            else:
                try:
                    # Show loading spinner while processing
                    with st.spinner('Processing your query...'):
                        # Get the response from the agent
                        response = data_analyst.run(input=user_query)

                        # Extract the content from the RunResponse object
                        if hasattr(response, 'content'):
                            response_content = response.content
                        else:
                            response_content = str(response)
                        
                        # Also print to terminal for better visibility
                        print("\n" + "="*50)
                        print("AGENT RESPONSE:")
                        print("="*50)
                        print(response_content)
                        print("="*50 + "\n")

                    # Display the response in Streamlit
                    st.markdown(response_content)
                
                    
                except Exception as e:
                    st.error(f"Error generating response from the agent: {e}")
                    st.error("Please try rephrasing your query or check if the data format is correct.")