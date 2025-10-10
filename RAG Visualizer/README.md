# 🔍 RAG Embedding Visualizer

An interactive tool to visualize text embeddings and understand how Retrieval-Augmented Generation (RAG) systems work under the hood. Built with Streamlit, ChromaDB, and Sentence Transformers.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Features

- **📝 Text Processing**: Upload text files or paste content directly
- **🧩 Smart Chunking**: Configurable chunk size and overlap for optimal processing
- **🤖 Multiple Models**: Choose from various sentence transformer models
- **💾 ChromaDB Integration**: Real vector database storage and retrieval
- **🎨 3D Visualization**: Interactive 3D plots of embedding space using Plotly
- **🔎 Semantic Search**: Query your documents and see similar chunks highlighted
- **📊 Dimensionality Reduction**: PCA and UMAP support for visualization
- **📈 Real-time Stats**: View embedding dimensions, chunk counts, and similarity scores

## 🚀 Quick Start

### Local Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/rag-embedding-visualizer.git
cd rag-embedding-visualizer
```

2. **Install dependencies**

Using uv (recommended):
```bash
uv add streamlit>=1.28.0 sentence-transformers>=2.2.2 chromadb>=0.4.15 plotly>=5.17.0 numpy>=1.24.0 pandas>=2.0.0 scikit-learn>=1.3.0 umap-learn>=0.5.4 torch>=2.0.0
```

Or using pip:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Run the app**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

> **Note**: First run will download the embedding model (~80-400MB depending on model choice)

## ☁️ Deploy to Streamlit Cloud

### Prerequisites
- GitHub repository with your code
- [Streamlit Cloud account](https://share.streamlit.io) (free)

### Deployment Steps

1. **Prepare your repository**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Fill in:
     - **Repository**: `yourusername/rag-embedding-visualizer`
     - **Branch**: `main`
     - **Main file path**: `app.py`
   - Click "Deploy"!

3. **Wait for deployment** (5-10 minutes for first deployment)
   - Streamlit will install dependencies from `requirements.txt`
   - Models will be cached on first use
   - Your app will be live at `https://your-app-name.streamlit.app`

### Important Notes
- **Memory**: Default resources (800MB RAM) work fine for the MiniLM model
- **Cold starts**: First user may experience longer load time as models download
- **Persistence**: Data resets on each session (by design for this demo tool)
- **Custom domain**: Available on paid plans

## 🤗 Deploy to Hugging Face Spaces

1. **Create a Space**
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Select "Streamlit" as the SDK
   - Choose CPU (basic) - Free tier works great

2. **Add your files**
   - Upload entire `src/` folder, `app.py`, `requirements.txt`, and `.streamlit/` folder
   - Or connect your GitHub repository (easier)

3. **Your Space will be live** at `https://huggingface.co/spaces/your-username/your-space`

> **Note**: Make sure to upload the entire folder structure, not just `app.py`

## 📖 How to Use

### 1. Input Text
- **Type or paste** text directly into the text area
- **Upload** a `.txt` file
- **Load sample** - Try pre-loaded texts on AI, Climate, or Space topics

### 2. Configure Settings (Sidebar)
- **Embedding Model**: 
  - `all-MiniLM-L6-v2` - Fast, 384 dimensions (recommended for most use)
  - `all-mpnet-base-v2` - More accurate, 768 dimensions
  - `paraphrase-multilingual` - For non-English text
- **Chunk Size**: Words per chunk (50-500, default: 100)
- **Overlap**: Overlapping words between chunks (0-100, default: 20)
- **Reduction Method**: 
  - `PCA` - Linear, faster, preserves global structure
  - `UMAP` - Non-linear, better clustering

### 3. Generate Embeddings
- Click **"🚀 Generate Embeddings"**
- Wait 10-20 seconds for processing
- View stats: total chunks, embedding dimensions, reduction method

### 4. Query & Search
- Enter a **semantic query** (e.g., "machine learning algorithms")
- Adjust **number of results** (1-10)
- Click **"Search Similar Chunks"**
- View results with chunk numbers and similarity scores

### 5. Explore the Visualization
- **3D Plot**: Rotate (drag), zoom (scroll), pan (right-click drag)
- **Color Coding**: 
  - 🔵 Blue = all document chunks
  - 🔴 Red = retrieved/similar chunks from your query
  - 💎 Yellow diamond = your query point
- **Hover**: See chunk preview and 3D coordinates
- **Understanding**: Points closer together = more semantically similar

### 6. Chunk Explorer
- Select individual chunks to view full content
- See embedding vector preview (first 10 of 384/768 dimensions)
- Understand that visualization uses ALL dimensions (reduced to 3D)

## 🛠️ Technical Stack

- **Streamlit**: Web interface and interactivity
- **Sentence Transformers**: State-of-the-art text embeddings
- **ChromaDB**: Vector database for semantic search
- **Plotly**: Interactive 3D visualizations
- **scikit-learn**: PCA dimensionality reduction
- **UMAP**: Advanced dimensionality reduction

## 🧪 Supported Embedding Models

| Model | Speed | Accuracy | Dimensions | Best For |
|-------|-------|----------|------------|----------|
| all-MiniLM-L6-v2 | ⚡⚡⚡ | ⭐⭐⭐ | 384 | General use, fast |
| all-mpnet-base-v2 | ⚡⚡ | ⭐⭐⭐⭐⭐ | 768 | High accuracy |
| paraphrase-multilingual | ⚡⚡ | ⭐⭐⭐⭐ | 384 | Multiple languages |

## 📁 Project Structure

```
RAG Visualizer/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .streamlit/
│   └── config.toml                # Streamlit configuration
├── src/                           # Source code
│   ├── config/                    # Configuration & settings
│   │   ├── __init__.py
│   │   └── settings.py           # Model options, sample texts
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── models.py             # Model loading & caching
│   │   ├── text_processing.py   # Text chunking utilities
│   │   ├── vector_store.py       # ChromaDB operations
│   │   ├── visualization.py      # 3D plotting & dimensionality reduction
│   │   └── session_state.py      # Session state management
│   └── ui/                        # User interface
│       ├── __init__.py
│       ├── styles.py             # CSS styling
│       └── components/            # UI components
│           ├── __init__.py
│           ├── sidebar.py
│           ├── input_section.py
│           ├── query_section.py
│           ├── stats_section.py
│           ├── visualization_section.py
│           └── chunk_explorer.py
├── README.md
├── QUICKSTART.md
├── DEPLOYMENT_GUIDE.md
└── LICENSE
```

## 🎯 Use Cases

- **Learning RAG**: Visualize how retrieval-augmented generation systems work
- **Understanding Embeddings**: See how text gets converted to vectors in semantic space
- **Model Comparison**: Compare different embedding models' clustering behavior
- **Document Analysis**: Explore semantic relationships and topic clusters in your documents
- **Query Engineering**: Test how different query phrasings retrieve different chunks
- **Education**: Teach vector databases, embeddings, and dimensionality reduction
- **Research**: Analyze how chunking strategies affect retrieval quality

## 🔮 Future Enhancements

- [ ] Support for PDF and DOCX files
- [ ] Multiple document comparison
- [ ] Reranking visualization
- [ ] Attention score heatmaps
- [ ] LLM generation integration
- [ ] Custom model upload
- [ ] Batch processing
- [ ] Export embeddings

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 💡 Tips for Best Results

- **Chunk Size**: 
  - Smaller (50-100) = more granular, better for specific queries
  - Larger (200-500) = more context, better for conceptual queries
- **Sample Texts**: Use provided samples for quick demo with proper chunk count
- **Model Choice**: Start with MiniLM for speed, switch to mpnet for accuracy
- **Queries**: Use natural language questions or topic keywords
- **Visualization**: Try both PCA and UMAP to see different perspectives

## 📝 License

This project is licensed under the MIT License - see the [LICENCE](LICENCE) file for details.

## 🙏 Acknowledgments

- [Sentence Transformers](https://www.sbert.net/) for state-of-the-art embedding models
- [ChromaDB](https://www.trychroma.com/) for the elegant vector database
- [Streamlit](https://streamlit.io/) for the amazing web framework
- [Plotly](https://plotly.com/) for stunning interactive visualizations
- [scikit-learn](https://scikit-learn.org/) & [UMAP](https://umap-learn.readthedocs.io/) for dimensionality reduction

---

⭐ If you find this project helpful, please give it a star!
