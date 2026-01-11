# DocuChat AI: Intelligent Document Assistant

![Project Header](./assets/Project%20Header.jpg)

A powerful LLM-powered document assistant that extracts information from various documents, supporting files containing both text and image components. This application enables seamless data retrieval and analysis from your content library with **enhanced external search capabilities** for comprehensive answers.

## 🌐 Try the Live Demo

**🚀 [Launch DocuChat AI](https://docu-chat-ai.streamlit.app/)**

Experience the power of AI-driven document analysis instantly! No setup required - just upload your PDF and start asking questions.

### Cloud vs Local Deployment

| Feature | **Cloud Version** (Streamlit Community Cloud) | **Local Version** (`app.py`) |
|---------|-----------------------------------------------|------------------------------------------|
| **Setup** | Zero setup - ready to use | Requires local installation & API keys |
| **Storage** | InMemoryVectorStore (session-based) | ChromaDB (persistent) |
| **File Persistence** | Documents reset on app restart | Documents saved permanently |
| **Performance** | Shared resources, 1GB memory limit | Full local resources |
| **Concurrent Users** | 3-5 users on free tier | Single user (your machine) |
| **External Search** | Limited without Tavily API key | Full capability with API keys |
| **Privacy** | Documents processed on Streamlit servers | Complete local privacy |
| **Best For** | Quick testing, sharing, demos | Production use, large documents, privacy |

## 🚀 Features

- **Multiple LLM Support**: Integrates with GPT-4o, GPT-4.1, Claude Sonnet 4, and DeepSeek-R1 models
- **Document Processing**: Efficiently processes PDF documents, extracting and indexing their content
- **Semantic Search**: Uses vector embeddings to find the most relevant information from your documents
- **🔍 External Search Integration**: Automatically searches external sources when document context is insufficient
- **Conversational Interface**: Clean, intuitive chat interface to ask questions about your documents
- **Custom Styling**: Dark mode interface with responsive design
- **Multiple Vector Store Options**: Supports both ChromaDB (current approach) and InMemoryVectorStore (legacy approach)
- **Intelligent Search Modes**: Toggle between document-only mode and enhanced mode with external search

## 🛠️ Implementation Details

- Built with **LangChain** framework for document processing and retrieval augmented generation (RAG)
- Utilizes **Streamlit** for the web interface
- **Professional Architecture**: Modular structure with separated config, core logic, and UI components
- Implements chunking with `RecursiveCharacterTextSplitter` for optimal document segmentation
- **External Search**: Powered by **Tavily Search API** for up-to-date external information
- **Intelligent Agent System**: Uses LangChain agents (v1 API) with modern `create_agent` pattern
- Supports two vector store implementations:
  - **ChromaDB**: Persistent vector database for better scalability and performance
  - **InMemoryVectorStore**: Simple in-memory storage for lightweight applications
- Supports semantic search with both cloud and local embedding models
- Handles PDF documents using `PyMuPDFLoader` (cloud models) and `PDFPlumberLoader` (DeepSeek version)
- Includes chat history management for continuous conversations

## 🔍 External Search Integration

### How It Works

1. **Document Analysis First**: When you ask a question, the AI first tries to answer using your uploaded document
2. **Automatic External Search**: If the document doesn't contain sufficient information, the AI automatically searches external sources via Tavily
3. **Combined Response**: You get a comprehensive answer that combines both document content and external search results
4. **Toggle Control**: Enable/disable external search via the sidebar toggle

### Search Modes

- **🔍 External Search Enabled**: AI will search external sources when document context is insufficient
- **📚 Document Only Mode**: AI will only use information from your uploaded documents

### Example Use Cases

**Questions that trigger external search:**

- "What are the latest developments in [topic not in your document]?"
- "What happened after [date mentioned in document]?"
- "How does this compare to recent industry trends?"
- "What are the current market conditions for [topic]?"

**Questions that use document only:**

- Direct questions about content explicitly mentioned in your uploaded PDF
- Summaries of document sections
- Analysis of data/charts within the document

## 📋 Requirements

- Python 3.11+
- Required packages (from pyproject.toml):
  ```
  langchain-anthropic>=0.3.13
  langchain-chroma>=0.2.3
  langchain-community>=0.3.24
  langchain-core>=0.3.59
  langchain-ollama>=0.3.2
  langchain-openai>=0.3.16
  langchain-tavily>=0.2.4
  langchain-text-splitters>=0.3.8
  pymupdf>=1.25.5
  protobuf<=3.20.3
  python-dotenv>=1.1.0
  streamlit>=1.45.1
  ```
- API keys for OpenAI and Anthropic (for cloud models)
- **Tavily API key** (for external search functionality)
- Ollama installation (for local models)

## 🔧 Setup

1. Clone this repository
2. Install the required packages using uv package manager:
   ```
   uv pip install .
   ```
3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```
4. Get a **Tavily API key** from [https://tavily.com/](https://tavily.com/) for external search functionality
5. For local models, install Ollama and pull the DeepSeek models:
   ```
   ollama pull deepseek-r1:1.5b
   ```
6. Create a directory for document storage:
   ```
   mkdir -p document_store/pdfs
   ```

## 🚀 Usage

### Cloud Version (No Setup Required)

Simply visit **[https://docu-chat-ai.streamlit.app/](https://docu-chat-ai.streamlit.app/)** to start using the application immediately!

### Local Installation

#### Production Version (ChromaDB Persistent Storage)

```bash
streamlit run app.py
```
**Best for**: Production use, persistent document storage, multiple documents

#### Development Version (InMemory Storage)

```bash
streamlit run app_inmemory.py
```
**Best for**: Testing, development, temporary document analysis

#### Local LLM Version (DeepSeek R1 with Ollama)

```bash
streamlit run app_deepseek.py
```
**Best for**: Privacy-focused use, offline processing, local LLM experimentation

#### Cloud Deployment Version

```bash
streamlit run streamlit_cloud.py
```
**Best for**: Deploying to Streamlit Community Cloud or similar platforms

### How to Use

1. Upload a PDF document using the file uploader
2. **Choose your search mode**: Toggle external search ON/OFF in the sidebar
3. Wait for the document to be processed, chunked, and indexed
4. Ask questions about the document content using the chat interface
5. **Enhanced Responses**: Get AI-generated responses that combine document content with external search results (when enabled)
6. Use the "Clear Chat History" button in the sidebar to start a new conversation

## 🌐 Cloud Deployment

### Streamlit Community Cloud

The application is deployed on **Streamlit Community Cloud** and accessible at:
**🔗 [https://docu-chat-ai.streamlit.app/](https://docu-chat-ai.streamlit.app/)**

#### Key Features for Cloud Deployment

✅ **InMemoryVectorStore** - No persistence issues on cloud platforms  
✅ **Temporary file handling** - Cloud-compatible PDF processing  
✅ **Session state tracking** - Remembers processed files during your session  
✅ **Cached resources** - Optimized performance  
✅ **Error handling** - Robust cloud deployment with graceful fallbacks  
✅ **Graceful fallbacks** - Works even without external search API keys  

#### Cloud Limitations

⚠️ **File persistence:** Documents reset when app restarts (session-based storage)  
⚠️ **Concurrent users:** ~3-5 users simultaneously on free tier  
⚠️ **Resource limits:** 1GB memory limit on Streamlit Community Cloud  
⚠️ **External search:** Limited functionality without Tavily API key  

#### Deploy Your Own Instance

1. **Fork this repository** on GitHub
2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io/new](https://share.streamlit.io/new)
   - Select your forked repository
   - **Main file path:** `streamlit_cloud.py`
3. **Set environment variables:**
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here (optional)
   ```

**Note:** External search will work with limited functionality without the Tavily API key. Get a free API key at [tavily.com](https://tavily.com) for full external search capability.

## 📊 Comparison of Available Models

| Model           | Type  | Best For                                       | Required Setup      | Implementation                            | External Search |
| --------------- | ----- | ---------------------------------------------- | ------------------- | ----------------------------------------- | --------------- |
| GPT-4o          | Cloud | High accuracy, complex queries                 | OpenAI API key      | ChatOpenAI with temperature=0             | ✅              |
| GPT-4.1         | Cloud | Latest OpenAI model with improved reasoning    | OpenAI API key      | ChatOpenAI with temperature=0             | ✅              |
| Claude Sonnet 4 | Cloud | Latest Claude model with enhanced capabilities | Anthropic API key   | ChatAnthropic with temperature=0          | ✅              |
| DeepSeek R1     | Local | Privacy, offline use, faster responses         | Ollama installation | OllamaLLM with the deepseek-r1:1.5b model | ✅              |

## 🔍 Embedding Models

The application uses different embedding models based on the version:

- **Cloud Version**: OpenAI's `text-embedding-3-large` model for high-quality embeddings
- **Local Version**: Can use either OpenAI embeddings or local Ollama embeddings with DeepSeek models

## 🔒 Privacy

### Cloud Deployment (Streamlit Community Cloud)
- **Document processing**: Files are temporarily processed on Streamlit servers
- **No persistence**: Documents are deleted when session ends or app restarts
- **API calls**: Document content sent to OpenAI/Anthropic APIs for processing
- **External search**: Search queries sent to Tavily API when enabled

### Local Deployment
- **Complete privacy**: All document processing happens on your machine
- **Local storage**: Documents stored in local ChromaDB (persistent)
- **API calls**: Only model responses sent to external APIs (OpenAI/Anthropic)
- **DeepSeek R1**: Fully local processing with no external API calls

### Model Privacy Levels
- **Cloud models** (GPT-4o, GPT-4.1, Claude Sonnet 4): Document content sent to external APIs
- **Local models** (DeepSeek R1): All processing happens locally with no data leaving your machine
- **External Search**: When enabled, search queries are sent to Tavily API for external information

## 🗄️ Vector Storage Options

### ChromaDB (Production)

- **Persistent Storage**: Document embeddings are saved to disk
- **Better Scalability**: Can handle larger document collections
- **Improved Performance**: Optimized for efficient retrieval
- **Implementation**: Used in `app.py`

### InMemoryVectorStore (Development)

- **Lightweight**: Simple in-memory storage with no persistence
- **Fast for Small Datasets**: Efficient for smaller document collections
- **Implementation**: Used in `app_inmemory.py`, `app_deepseek.py`, and `streamlit_cloud.py`

## 🤖 External Search Agent Architecture

The application uses an intelligent agent system for external search:

- **Agent Framework**: LangChain v1 `create_agent` (modern API)
- **Tools**: Tavily Search API integration using `@tool` decorator
- **Orchestration**: Automatic fallback when document context is insufficient
- **Response Enhancement**: Combines document and external contexts intelligently

### Example Workflow

1. Upload a research paper about AI from 2023
2. Ask: "What are the latest AI developments in 2024?"
3. Watch as the AI:
   - Recognizes the document doesn't contain 2024 information
   - Automatically searches external sources via Tavily
   - Provides a comprehensive answer combining both sources

## 🎯 Benefits of Enhanced Integration

- **No more "I don't know" responses**: AI can find relevant information beyond your documents
- **Always current information**: Get the most up-to-date data from external sources
- **Seamless integration**: No manual switching between modes
- **Clear source indication**: Know what information comes from documents vs. external sources
- **Intelligent fallback**: External search only triggers when needed

## 📁 Project Structure

```
langchain-document-assistant/
├── config/                      # Configuration & Settings
│   ├── settings.py              # Constants, paths, model configs
│   ├── models.py                # LLM initialization
│   └── prompts/                 # Prompt templates
├── core/                        # Core Business Logic
│   ├── document_processor.py    # PDF loading, chunking
│   ├── vector_store.py          # Vector store wrappers
│   └── rag_chain.py             # RAG chain & answer generation
├── agents/                      # Agent implementations
├── tools/                       # Tool implementations
├── components/                  # UI components
├── styles/                      # Styling
├── app.py                       # Main app (ChromaDB)
├── app_inmemory.py              # Development version
├── app_deepseek.py              # DeepSeek local LLM version
└── streamlit_cloud.py           # Cloud deployment version
```

This modular architecture provides:
- **Separation of Concerns**: Config, core logic, and UI are separated
- **Reusability**: Core modules can be imported and reused
- **Maintainability**: Easy to find and modify specific functionality
- **Scalability**: Simple to add new features without bloating main files

## Project Screenshots

In this demo I used the BPS Palu City data of [population and employment](https://github.com/mcikalmerdeka/NLP-Learning/blob/main/Langchain%20Document%20Assistant%20with%20Deepseek%20R1%20-%20GPT4o%20-%20Claude%203.5%20Sonnet/document_store/pdfs/Statistik%20Penduduk%20dan%20Ketenagakerjaan%20Kota%20Palu%202025.pdf) from the official report of "Kota Palu Dalam Angka 2025" which you can access in this `document_store` folder in this repo. You may use several example files that I stored there or use your own PDFs.

### Document Upload Interface

![Upload Document](./assets/Project%20Screenshot%201.png)

*The document upload interface allows users to select and upload PDF files for analysis. The system processes the document and prepares it for question answering with optional external search capabilities.*

### Initial Question and Answer

![Document Chat](./assets/Project%20Screenshot%202.png)

*After document processing, users can ask specific questions about the content. The AI assistant retrieves relevant information from the document and provides comprehensive answers based on the document context, with the option to enhance responses using external search.*

### Follow-up Question Capabilities

![Follow-up Questions](./assets/Project%20Screenshot%203.png)

*The system supports follow-up questions, maintaining context from previous interactions. This allows for a natural conversation flow while exploring document content in greater depth, with intelligent external search integration when document context is insufficient.*
