from typing import Any, Iterator
import streamlit as st
from agno.models.openai import OpenAIChat
from agno.agent import Agent, RunOutputEvent, RunEvent
from agno.tools.pandas import PandasTools
from agno.utils.pprint import pprint_run_response
from utils import preprocess_and_save

# Streamlit app
st.title("📊 Data Analyst Agent")

# Sidebar for API keys and settings
with st.sidebar:
    st.header("API Keys")
    openai_key = st.text_input("Enter your OpenAI API key:", type="password")
    if openai_key:
        st.session_state.openai_key = openai_key
        st.success("API key saved!")
    else:
        st.warning("Please enter your OpenAI API key to proceed.")
    
    st.divider()
    st.header("Settings")
    debug_mode = st.checkbox("Debug Mode", value=False, help="Enable agent debug mode for detailed logging and execution traces")
    st.session_state.debug_mode = debug_mode
    
    show_pretty_print = st.checkbox("Pretty Terminal Output", value=False, help="Show beautifully formatted output in terminal with tool calls and timing")
    st.session_state.show_pretty_print = show_pretty_print

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
            name="Data Analyst Agent",
            model=OpenAIChat(id="gpt-4.1-mini", api_key=st.session_state.openai_key),
            description="You are an expert data analyst.",
            instructions=[
                f"You are an expert data analyst.",
                f"A pandas DataFrame named 'uploaded_data' is already loaded with {len(df)} rows.",
                f"Columns: {', '.join(columns)}",
                f"Column types: {dict[Any, Any](df.dtypes)}",
                f"Sample data:\n{df.head(3).to_string()}",
                "Use the run_dataframe_operation tool to analyze 'uploaded_data'.",
                "Always provide clear insights and explanations with your analysis.",
            ],
            debug_mode=st.session_state.get("debug_mode", False),
            tools=[pandas_tools],
            markdown=True
        )
        
        # Initialize code storage in session state
        if "generated_code" not in st.session_state:
            st.session_state.generated_code = None
        
        # Main query input widget
        user_query = st.text_area("Ask a query about the data:")
        
        # Add info message about terminal output
        info_parts = []
        if st.session_state.get("debug_mode", False):
            info_parts.append("🐛 Agent debug mode enabled")
        if st.session_state.get("show_pretty_print", False):
            info_parts.append("✨ Pretty terminal output enabled")
        
        if info_parts:
            st.info(" | ".join(info_parts))
        else:
            st.info("💡 Check your terminal for the agent's response stream")
        
        if st.button("Submit Query"):
            if user_query.strip() == "":
                st.warning("Please enter a query.")
            else:
                try:
                    # Show loading spinner while processing
                    with st.spinner('Processing your query...'):
                        response_content = ""
                        
                        # Use pretty print mode for terminal output or simple streaming
                        if st.session_state.get("show_pretty_print", False):
                            # Create stream for detailed terminal output with pprint
                            stream: Iterator[RunOutputEvent] = data_analyst.run(
                                input=user_query,
                                stream=True
                            )
                            pprint_run_response(stream, markdown=True)
                            
                            # Get response content with a fresh non-streaming call
                            response = data_analyst.run(input=user_query, stream=False)
                            response_content = response.content
                        else:
                            # Run the agent with streaming enabled
                            stream: Iterator[RunOutputEvent] = data_analyst.run(
                                input=user_query,
                                stream=True
                            )
                            
                            # Simple streaming - just print content as it arrives
                            for chunk in stream:
                                if chunk.event == RunEvent.run_content and chunk.content:
                                    print(chunk.content, end="", flush=True)
                                    response_content += chunk.content
                            
                            print()  # New line after streaming completes
                    
                    # Display the response in Streamlit
                    if response_content:
                        st.markdown(response_content)
                    else:
                        st.info("No response content was generated.")
                
                except Exception as e:
                    st.error(f"Error generating response from the agent: {e}")
                    st.error("Please try rephrasing your query or check if the data format is correct.")