import gradio as gr
import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Set static paths for avatar images
gr.set_static_paths(paths=["images/"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Handle user message submission (multimodal)
def user(user_message, history):
    """
    Add user message to chat history.
    Supports both text and file uploads (images).
    """
    if user_message is None:
        return history
    
    # Handle multimodal input (dict with 'text' and 'files' keys)
    if isinstance(user_message, dict):
        text = user_message.get("text", "")
        files = user_message.get("files", [])
        
        # Build content for Gradio display (can include file paths directly)
        if text and files:
            # Both text and files
            content = text + "\n\n" + "\n".join([f"![Image]({f})" for f in files])
        elif text:
            # Text only
            content = text
        elif files:
            # Files only - show as markdown images
            content = "\n".join([f"![Image]({f})" for f in files])
        else:
            return history
        
        # Add message to history (Gradio format)
        return history + [{"role": "user", "content": content}]
    else:
        # Simple text message (backward compatibility)
        return history + [{"role": "user", "content": user_message}]
    
    return history

# Helper function to encode images
def encode_image(image_path):
    """Encode image to base64 for OpenAI API."""
    import base64
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Handle bot response with streaming
def bot(history, system_prompt, model, temperature, max_tokens):
    """
    Stream bot response from OpenAI.
    
    Args:
        history: Chat history in messages format
        system_prompt: System message to set assistant behavior
        model: OpenAI model to use
        temperature: Sampling temperature (0-2)
        max_tokens: Maximum tokens in response
    """
    # Build messages for OpenAI API (need to convert Gradio format to OpenAI format)
    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in history:
        role = msg["role"]
        content = msg["content"]
        
        # Check if content contains images (markdown format)
        if isinstance(content, str) and "![Image]" in content:
            # Extract text and image paths from markdown
            parts = content.split("\n\n")
            text_part = parts[0] if not parts[0].startswith("![Image]") else ""
            
            # Find all image paths
            import re
            image_paths = re.findall(r'!\[Image\]\(([^)]+)\)', content)
            
            # Build multimodal content for OpenAI
            openai_content = []
            if text_part:
                openai_content.append({"type": "text", "text": text_part})
            
            for img_path in image_paths:
                openai_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encode_image(img_path)}"}
                })
            
            messages.append({"role": role, "content": openai_content})
        else:
            # Regular text message
            messages.append({"role": role, "content": content})
    
    # Stream response from OpenAI
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True
    )
    
    # Add empty assistant message to history
    history.append({"role": "assistant", "content": ""})
    
    # Stream bot response character by character
    for chunk in response:
        if chunk.choices[0].delta.content:
            history[-1]["content"] += chunk.choices[0].delta.content
            yield history

# Create Gradio interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:

    # Title
    gr.Markdown(
        """
        # 💬 OpenAI Chatbot with Component Showcase
        This demo showcases various Gradio components while providing a functional chatbot.
        """
    )
    
    # Tabs - organize content into different sections
    with gr.Tabs():

        # Add Chat tab
        with gr.Tab("💬 Chat"):
            with gr.Row():
                # Column - organize components vertically (left side - main chat)
                with gr.Column(scale=2):
                    # Chatbot - displays conversation history with streaming support
                    chatbot = gr.Chatbot(
                        height=500,
                        show_copy_button=True,  # Allows copying messages
                        avatar_images=("images/nkhco2.jpg", "images/qkomor.jpg"),  # User and Bot avatars
                        label="Conversation",
                        type="messages"
                    )
                    
                    # MultimodalTextbox - supports text + file uploads (images, audio, etc.)
                    msg = gr.MultimodalTextbox(
                        interactive=True,
                        file_count="multiple",  # Allow multiple file uploads
                        placeholder="Type a message or upload images...",
                        show_label=False,
                        submit_btn=True,  # Show built-in submit button
                        stop_btn=True,  # Show stop button for streaming
                    )
                    
                    # ClearButton - specialized button to clear component values
                    clear = gr.ClearButton([msg, chatbot], value="🗑️ Clear Chat")
                
                # Right sidebar - settings panel
                with gr.Column(scale=1):
                    # Accordion for Model Settings
                    with gr.Accordion("⚙️ Model Settings", open=True):
                        # Dropdown - select from predefined options
                        model = gr.Dropdown(
                            choices=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
                            value="gpt-4o-mini",
                            label="Model",
                            info="Choose the OpenAI model (gpt-4o models support vision)"
                        )
                        
                        # Slider - select numeric value within a range
                        temperature = gr.Slider(
                            minimum=0,
                            maximum=2,
                            value=0.7,
                            step=0.1,
                            label="Temperature",
                            info="Controls randomness: 0=focused, 2=creative"
                        )
                        
                        max_tokens = gr.Slider(
                            minimum=50,
                            maximum=4096,
                            value=1000,
                            step=50,
                            label="Max Tokens",
                            info="Maximum length of response"
                        )
                    
                    # Accordion - collapsible section to save space
                    with gr.Accordion("🎭 System Prompt", open=True):
                        # TextArea - multi-line text input
                        system_prompt = gr.TextArea(
                            value="You are a helpful assistant.",
                            label="System Message",
                            info="Define the assistant's behavior and personality",
                            lines=4,
                            max_lines=10
                        )
                    
                    # HTML - render custom HTML content
                    gr.HTML(
                        """
                        <div style="padding: 12px; background: var(--block-background-fill); border: 1px solid var(--border-color-primary); border-radius: 8px; margin-top: 10px;">
                            <strong>💡 Tips:</strong>
                            <ul style="margin: 5px 0; padding-left: 20px; font-size: 0.9em;">
                                <li>Higher temperature = more creative</li>
                                <li>Lower temperature = more focused</li>
                                <li>Adjust max tokens for longer responses</li>
                            </ul>
                        </div>
                        """
                    )
        
        # Add Examples tab
        with gr.Tab("📚 Examples"):
            gr.Markdown("### Pre-configured Example Prompts")
            
            # Examples - provide quick-access example inputs
            examples = gr.Examples(
                examples=[
                    ["Explain quantum computing in simple terms"],
                    ["Write a haiku about programming"],
                    ["What are the benefits of Python?"],
                    ["Help me debug a recursive function"],
                ],
                inputs=msg,
                label="Click to use these examples"
            )
        
        # Add About tab
        with gr.Tab("ℹ️ About"):
            gr.Markdown(
                """
                ## Component Guide
                
                This interface demonstrates these Gradio components:
                
                - **Chatbot**: Displays conversation with streaming support
                - **MultimodalTextbox**: Text input with file upload support (images, audio, video)
                - **Textbox**: Single/multi-line text input
                - **Button**: Clickable action trigger (variant="primary" makes it blue)
                - **ClearButton**: Specialized button that clears specified components
                - **Dropdown**: Select from predefined options
                - **Slider**: Numeric value selection with visual feedback
                - **Accordion**: Collapsible section to organize UI
                - **Tabs**: Organize content into separate views
                - **Row/Column**: Layout containers (Row=horizontal, Column=vertical)
                - **Markdown**: Render formatted text with markdown syntax
                - **HTML**: Embed custom HTML for advanced styling
                - **Examples**: Quick-access example inputs
                
                ### Other useful components not shown here:
                - **Checkbox**: Boolean toggle
                - **Radio**: Single selection from options
                - **CheckboxGroup**: Multiple selection
                - **Image/Audio/Video/File**: Media upload/display
                - **Dataframe**: Display/edit tabular data
                - **Plot**: Display matplotlib/plotly charts
                - **JSON**: Display formatted JSON
                - **Code**: Display syntax-highlighted code
                """
            )
    
    # Event handlers - connect user interactions to functions
    # Submit event on multimodal textbox (triggered by Enter key or submit button)
    msg.submit(
        user, 
        [msg, chatbot], 
        [chatbot], 
        queue=False
    ).then(
        bot, 
        [chatbot, system_prompt, model, temperature, max_tokens], 
        chatbot
    )

# Run the demo
if __name__ == "__main__":
    demo.launch()