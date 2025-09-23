# Knowledge Graph Visualizer

A powerful Python application that leverages LangChain, OpenAI's GPT models, and PyVis to extract structured knowledge graphs from unstructured text and create interactive visualizations.

![Knowledge Graph Visualization](https://raw.githubusercontent.com/mcikalmerdeka/NLP-Learning/refs/heads/main/Knowledge%20Graph%20Visualizer/output/knowledge_graph.png)

*Interactive knowledge graph visualization showing entities and relationships extracted from text data*

## 🚀 Features

- **AI-Powered Graph Extraction**: Uses advanced LLM transformers to automatically identify entities, relationships, and concepts from text
- **Interactive Visualizations**: Beautiful, interactive network graphs with physics-based layouts
- **Web Interface**: Streamlit-based web application for easy use
- **Multiple Input Methods**: Support for both file upload (.txt) and direct text input
- **Customizable Filtering**: Filter nodes and relationships by type for focused analysis
- **Async Processing**: High-performance asynchronous text processing
- **Professional UI**: Dark theme with responsive design and filter controls

## 📋 Requirements

- Python 3.11+
- OpenAI API key
- Internet connection for visualization libraries

## 🛠️ Installation

**Note**: This project uses [uv](https://github.com/astral-sh/uv) as the recommended dependency manager. uv is significantly faster than pip and provides better dependency resolution.

### Option 1: Using uv (Recommended)

1. **Install uv** (if not already installed)
   ```bash
   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd knowledge-graph-visualizer
   ```

3. **Install dependencies with uv**
   ```bash
   uv sync
   ```

4. **Activate the virtual environment**
   ```bash
   # The environment is automatically created and activated
   uv shell
   ```

### Option 2: Traditional pip

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd knowledge-graph-visualizer
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

4. **Set up OpenAI API key**
   ```bash
   # Create .env file in project root
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

## 📦 Dependencies

- **Core ML**: `langchain`, `langchain-experimental`, `langchain-openai`
- **Visualization**: `pyvis` (interactive graphs with auto-managed dependencies), `streamlit` (web interface)
- **Utilities**: `python-dotenv`, `ipykernel`

**Note**: PyVis automatically downloads and manages its visualization dependencies (Vis.js, network libraries) when first used.

## 🎯 Usage

### Method 1: Streamlit Web Application

```bash
# Using uv (recommended)
uv run streamlit run app.py

# Or using pip virtual environment
streamlit run app.py
```

The web interface provides:
- File upload for .txt files
- Direct text input
- Real-time graph generation
- Interactive visualization display

### Method 2: Python Script

```python
from generate_knowledge_graph import generate_knowledge_graph

# Process text
text = "Your text content here..."
net = generate_knowledge_graph(text)

# The function will save an interactive HTML file
```

### Method 3: Jupyter Notebook

```bash
# Using uv (recommended)
uv run jupyter notebook

# Or using pip virtual environment
jupyter notebook
```

Open `knowledge_graph.ipynb` to see:
- Step-by-step processing examples
- Node and relationship filtering
- Sample data processing (Elon Musk profile)

## 📊 Sample Data

The repository includes a comprehensive profile of Elon Musk (`data/elon_musk_profile.txt`) that demonstrates the system's capabilities. This sample shows:

- **Entities Extracted**: People, Organizations, Products, Concepts, Awards, Places, Dates
- **Relationships**: CEO, FOUNDER, PRODUCES, DEVELOPS, ADVOCATES, etc.
- **Complex Structure**: Multi-company analysis with interconnected relationships

## 🔧 Architecture

### Core Components

1. **`generate_knowledge_graph.py`**
   - Main graph extraction logic
   - Async LLM processing with GPT-4.1
   - PyVis visualization engine
   - Error handling and node validation

2. **`app.py`**
   - Streamlit web interface
   - File upload handling
   - User input processing
   - HTML graph embedding

3. **`knowledge_graph.ipynb`**
   - Interactive examples
   - Filtering demonstrations
   - Educational walkthrough

### Data Flow

```
Text Input → LLM Graph Transformer → Node/Relationship Extraction → Validation → PyVis Visualization → Interactive HTML
```

## 🎨 Visualization Features

- **Physics-based Layout**: Force-directed graph with customizable physics
- **Node Grouping**: Color-coded nodes by type (Person, Organization, Product, etc.)
- **Interactive Controls**: Zoom, pan, drag, filter menu
- **Edge Labels**: Relationship types clearly labeled
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Theme**: Professional appearance with white text on dark background

## 🔍 Advanced Features

### Node Filtering
Filter specific entity types:
```python
allowed_nodes = ["Person", "Organization", "Product"]
graph_transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=allowed_nodes
)
```

### Relationship Filtering
Define specific relationship patterns:
```python
allowed_relationships = [
    ("Person", "WORKS_AT", "Organization"),
    ("Person", "FOUNDER", "Organization")
]
```

## 📁 Project Structure

```
knowledge-graph-visualizer/
├── app.py                          # Streamlit web application
├── generate_knowledge_graph.py     # Core graph generation logic
├── knowledge_graph.ipynb           # Jupyter notebook examples
├── data/
│   └── elon_musk_profile.txt       # Sample input data
├── output/
│   └── knowledge_graph.html        # Generated visualization
├── lib/                           # Auto-generated PyVis dependencies (auto-managed)
│   ├── vis-9.1.2/                 # Vis.js network library
│   ├── tom-select/                # Dropdown components
│   └── bindings/                  # Utility scripts
├── pyproject.toml                 # Project configuration
├── .env                           # Environment variables (create this)
└── README.md                      # This file
```

**Note**: The `lib/` directory is automatically generated by PyVis when first importing `Network`. It contains visualization dependencies and should not be manually edited. This folder is ignored by git (.gitignore) since it's auto-managed.

## 🚀 Performance

- **Async Processing**: Non-blocking LLM calls for better performance
- **Smart Caching**: Efficient node lookup and relationship validation
- **Memory Optimization**: Only processes valid, connected nodes
- **CDN Resources**: Fast loading of visualization libraries

## 🔒 Security & Privacy

- API keys stored in environment variables
- No data persistence on server
- Client-side processing for sensitive data
- Local file handling for uploaded documents

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **LangChain** for the graph transformation framework
- **OpenAI** for the GPT models
- **PyVis** for the interactive visualization engine
- **Streamlit** for the web application framework

## 📞 Support

For issues, questions, or contributions, please:
1. Check existing issues in the repository
2. Create a new issue with detailed description
3. Include sample data and error messages when relevant

---

*Transform your text into beautiful, interactive knowledge graphs with AI-powered analysis and professional visualizations.*
