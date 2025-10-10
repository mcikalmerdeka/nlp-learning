# 🚀 Quick Start Guide

Get your RAG Embedding Visualizer running in 5 minutes!

## 📋 Prerequisites

- Python 3.8 or higher
- Git (for cloning)
- 2GB of free disk space (for models)

## 🏃 Super Quick Start (3 Commands)

Using uv (recommended):
```bash
# 1. Clone and enter directory
git clone https://github.com/yourusername/rag-embedding-visualizer.git
cd rag-embedding-visualizer

# 2. Install dependencies
uv add streamlit>=1.28.0 sentence-transformers>=2.2.2 chromadb>=0.4.15 plotly>=5.17.0 numpy>=1.24.0 pandas>=2.0.0 scikit-learn>=1.3.0 umap-learn>=0.5.4 torch>=2.0.0

# 3. Run the app
streamlit run app.py
```

Or using pip:
```bash
# 1. Clone and enter directory
git clone https://github.com/yourusername/rag-embedding-visualizer.git
cd rag-embedding-visualizer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

That's it! Your app will open at `http://localhost:8501` 🎉

## 🎮 First Time Usage

### Step 1: Try a Sample
1. Click "Load Sample" in the sidebar
2. Choose "AI & Machine Learning"
3. Click "🚀 Generate Embeddings"
4. Wait 10-20 seconds (first run downloads the model)

### Step 2: See the Magic
- Watch the 3D visualization appear
- Rotate the plot by dragging
- Hover over points to see chunk details

### Step 3: Try a Query
1. In the "Query & Search" box, type: `"neural networks"`
2. Click "Search Similar Chunks"
3. See the red highlighted points (similar chunks)
4. Yellow diamond shows your query location

## 🎯 Common First-Time Questions

### Q: Why is the first run slow?
**A:** The embedding model (~80MB) is being downloaded. Subsequent runs are instant!

### Q: Can I use my own text?
**A:** Yes! Just paste it in the text area or upload a `.txt` file.

### Q: What do the colors mean?
- **Blue dots**: Your document chunks
- **Red dots**: Retrieved/similar chunks from your query
- **Yellow diamond**: Your query position in vector space

### Q: How do I adjust settings?
**A:** Use the sidebar on the left:
- **Model**: Choose faster (MiniLM) or more accurate (mpnet)
- **Chunk Size**: Larger = more context per chunk
- **Overlap**: Higher = smoother transitions between chunks

### Q: What's the difference between PCA and UMAP?
- **PCA**: Faster, linear, preserves global structure
- **UMAP**: Slower, non-linear, better at showing clusters

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError"
```bash
# Solution: Reinstall dependencies
# Using uv:
uv sync --upgrade

# Or using pip:
pip install -r requirements.txt --upgrade
```

### Issue: "Port 8501 already in use"
```bash
# Solution: Use a different port
streamlit run app.py --server.port 8502
```

### Issue: Model download fails
```bash
# Solution: Set cache directory
export TRANSFORMERS_CACHE="./models"
streamlit run app.py
```

### Issue: Out of memory
- Use the smaller model: "all-MiniLM-L6-v2"
- Reduce chunk size to 50 words
- Process smaller texts (< 5000 words)

## 💡 Pro Tips

1. **Start Small**: Try sample texts before uploading large documents
2. **Experiment**: Change reduction methods and see how the visualization changes
3. **Query Testing**: Try different query phrasings to understand semantic search
4. **Chunk Size**: Experiment with 50, 100, 200 to see what works best
5. **Model Selection**: MiniLM for speed, mpnet for research/accuracy

## 📊 Understanding the Visualization

### What am I looking at?
- Each dot = one chunk of your text
- Position = semantic meaning
- Distance = similarity (closer = more similar)

### How to interpret?
- **Clusters**: Similar topics group together
- **Outliers**: Unique or distinct content
- **Query proximity**: Closer dots = more relevant to your query

## 🎓 Example Workflow

### Analyzing a Research Paper
```bash
1. Upload your paper as .txt
2. Set chunk size to 200 (for longer context)
3. Set overlap to 50 (for smooth transitions)
4. Generate embeddings
5. Query: "methodology" - see research methods sections
6. Query: "results" - see findings sections
7. Query: "limitations" - see discussion sections
```

### Comparing Documents
```bash
1. Process first document - note the cluster patterns
2. Take a screenshot
3. Clear and process second document
4. Compare how different topics cluster differently
```

## 🚀 Next Steps

1. **Customize**: Edit colors and styles in `app.py`
2. **Deploy**: Push to GitHub and deploy to Streamlit Cloud
3. **Share**: Send your deployed URL to colleagues
4. **Extend**: Add new features (see README for ideas)

## 📚 Learn More

- [Sentence Transformers Documentation](https://www.sbert.net/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Understanding RAG](https://www.pinecone.io/learn/retrieval-augmented-generation/)

## 🆘 Still Need Help?

1. Check existing [GitHub Issues](https://github.com/yourusername/rag-embedding-visualizer/issues)
2. Open a new issue with:
   - Your Python version
   - Error message
   - Steps to reproduce
3. Join our [Discussions](https://github.com/yourusername/rag-embedding-visualizer/discussions)

---

Happy Visualizing! 🎨✨