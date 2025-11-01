from typing import Any
import streamlit as st
from agno.models.openai import OpenAIChat
from agno.agent import Agent
from agno.tools.pandas import PandasTools
from utils import preprocess_and_save

# Import necessary modules for terminal display
from typing import get_args
from rich.console import Console, Group
from rich.live import Live
from rich.status import Status
from rich.text import Text
from agno.utils.response import create_panel, format_tool_calls
from agno.run.agent import RunEvent, RunOutputEvent
from agno.utils.timer import Timer

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
                        # Set up terminal display
                        console = Console()
                        accumulated_tool_calls = []
                        response_content = ""
                        
                        with Live(console=console) as live_log:
                            status = Status("Thinking...", spinner="aesthetic", speed=0.4, refresh_per_second=10)
                            response_timer = Timer()
                            response_timer.start()
                            panels = [status]
                            
                            # Display user query
                            message_panel = create_panel(
                                content=Text(user_query, style="green"),
                                title="Message",
                                border_style="cyan",
                            )
                            panels.append(message_panel)
                            live_log.update(Group(*panels))
                            
                            # Run the agent with streaming enabled
                            for response_event in data_analyst.run(
                                input=user_query,
                                stream=True,
                                stream_events=True
                            ):
                                # Handle events
                                if isinstance(response_event, tuple(get_args(RunOutputEvent))):
                                    # Capture tool calls
                                    if (response_event.event == RunEvent.tool_call_started and 
                                        hasattr(response_event, "tool") and 
                                        response_event.tool is not None):
                                        accumulated_tool_calls.append(response_event.tool)
                                    
                                    # Capture response content
                                    if response_event.event == RunEvent.run_content:
                                        if hasattr(response_event, "content") and isinstance(response_event.content, str):
                                            response_content += response_event.content
                                
                                # Update display with tool calls
                                panels = [status, message_panel]
                                
                                if accumulated_tool_calls:
                                    tool_calls_content = Text()
                                    formatted_tool_calls = format_tool_calls(accumulated_tool_calls)
                                    for formatted_tool_call in formatted_tool_calls:
                                        tool_calls_content.append(f"• {formatted_tool_call}\n")
                                    
                                    tool_calls_panel = create_panel(
                                        content=tool_calls_content.plain.rstrip(),
                                        title="Tool Calls",
                                        border_style="yellow",
                                    )
                                    panels.append(tool_calls_panel)
                                
                                if response_content:
                                    response_panel = create_panel(
                                        content=response_content,
                                        title=f"Response ({response_timer.elapsed:.1f}s)",
                                        border_style="blue",
                                    )
                                    panels.append(response_panel)
                                
                                live_log.update(Group(*panels))
                            
                            response_timer.stop()
                            # Remove thinking status
                            panels = [p for p in panels if not isinstance(p, Status)]
                            live_log.update(Group(*panels))

                    # Display the response in Streamlit
                    st.markdown(response_content)
                
                    
                except Exception as e:
                    st.error(f"Error generating response from the agent: {e}")
                    st.error("Please try rephrasing your query or check if the data format is correct.")