# 🔍 RAG Pipeline Visualizer

An interactive tool to visualize the complete **naive RAG process** from start to finish. This project breaks down the entire RAG (Retrieval-Augmented Generation) pipeline into three transparent sections: **Retrieval → Augmentation → Generation**. Built with Streamlit, ChromaDB, Sentence Transformers, and OpenAI.

🚀 **[Try it live here!](https://rag-pipeline-visualizer.streamlit.app/)** - Deployed on Streamlit Cloud for direct testing.

<div align="center">
  <img src="https://raw.githubusercontent.com/mcikalmerdeka/nlp-learning/refs/heads/main/rag-pipeline-visualizer/assets/Clearest%20RAG%20Diagram.jpg" alt="RAG Pipeline Diagram" width="500"/>
</div>

## 🌟 Features

### 🔎 Section 1: Retrieval

- **Text Processing**: Upload files or paste content directly
- **Smart Chunking**: Configurable chunk size and overlap
- **Multiple Models**: Choose from various sentence transformer models
- **ChromaDB Integration**: Real vector database storage
- **3D Visualization**: Interactive plots with PCA/UMAP
- **Semantic Search**: Query and see similar chunks highlighted

### 🔧 Section 2: Augmentation

- **System Prompt Management**: View and customize prompts
- **Context Display**: See retrieved chunks formatted for LLM
- **Prompt Preview**: View complete augmented message
- **Token Estimation**: Calculate costs before generation
- **LangSmith-style UI**: Professional observability interface

### ✨ Section 3: Generation

- **OpenAI Integration**: GPT-4o-mini response generation
- **Token Usage**: Detailed breakdown of prompt/completion tokens
- **Cost Tracking**: Real-time cost estimation
- **API Inspection**: Full request/response visibility
- **Regenerate**: Easy response regeneration

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip uv pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys).

### 3. Run the App

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

> **Note**: First run downloads the embedding model (~80-400MB)

### 4. Try It Out

1. Click "Load Sample" in sidebar → Choose "AI & Machine Learning"
2. Click "Generate Embeddings" (wait ~10 seconds)
3. Enter query: "What is deep learning?"
4. Click "Search Similar Chunks"
5. Scroll to **Augmentation** section → Review prompt
6. Click "Proceed to Generation"
7. Scroll to **Generation** section → Click "Generate Response"

## 📖 Complete RAG Workflow

```
┌─────────────────┐
│  1. RETRIEVAL   │
│  • Chunk text   │
│  • Generate     │
│    embeddings   │
│  • Store in     │
│    ChromaDB     │
│  • Search       │
└────────┬────────┘
         ↓
┌─────────────────┐
│ 2. AUGMENTATION │
│  • System       │
│    prompt       │
│  • Retrieved    │
│    context      │
│  • User query   │
└────────┬────────┘
         ↓
┌─────────────────┐
│ 3. GENERATION   │
│  • Call OpenAI  │
│  • Get response │
│  • Track tokens │
│  • View cost    │
└─────────────────┘
```

## 🎯 Use Cases

- **Learning RAG**: Understand the complete pipeline visually
- **Prompt Engineering**: See exact prompts sent to LLM
- **Cost Analysis**: Track token usage and costs
- **Model Comparison**: Compare embedding models
- **Document Analysis**: Explore semantic relationships
- **Education**: Teach vector databases and RAG systems
- **Debugging**: Inspect full API calls and responses

## 🛠️ Technical Stack

- **Streamlit**: Web interface and interactivity
- **Sentence Transformers**: State-of-the-art embeddings
- **ChromaDB**: Vector database for semantic search
- **OpenAI**: GPT-4o-mini for generation
- **Plotly**: Interactive 3D visualizations
- **scikit-learn & UMAP**: Dimensionality reduction

## 🧪 Supported Models

### Embedding Models

| Model                   | Speed  | Accuracy   | Dimensions | Best For           |
| ----------------------- | ------ | ---------- | ---------- | ------------------ |
| all-MiniLM-L6-v2        | ⚡⚡⚡ | ⭐⭐⭐     | 384        | General use, fast  |
| all-mpnet-base-v2       | ⚡⚡   | ⭐⭐⭐⭐⭐ | 768        | High accuracy      |
| paraphrase-multilingual | ⚡⚡   | ⭐⭐⭐⭐   | 384        | Multiple languages |

### LLM Model

- **GPT-4o-mini**: Fast, affordable, high-quality responses
- **Pricing**: ~$0.0001-0.0015 per query (very affordable!)

## 📊 Observability Features

Similar to LangSmith, you can see:

- ✅ **Prompt Construction**: Exact system prompt and user message
- ✅ **Context Injection**: How retrieved chunks are formatted
- ✅ **Token Usage**: Detailed breakdown of input/output tokens
- ✅ **Cost Tracking**: Estimated costs per generation
- ✅ **Full Conversation**: Complete API request/response
- ✅ **Similarity Scores**: Which chunks were most relevant
- ✅ **3D Visualization**: Embedding space visualization

## 📁 Project Structure

```
RAG Visualizer/
├── app.py                              # Main application
├── requirements.txt                    # Dependencies
├── .env                               # API keys (create this)
├── src/
│   ├── config/
│   │   └── settings.py               # Model options, samples
│   ├── core/
│   │   ├── models.py                 # Embedding models
│   │   ├── text_processing.py       # Text chunking
│   │   ├── vector_store.py           # ChromaDB operations
│   │   ├── visualization.py          # 3D plotting
│   │   ├── llm.py                    # OpenAI integration
│   │   └── session_state.py          # State management
│   └── ui/
│       ├── styles.py                 # CSS styling
│       └── components/               # UI components
│           ├── input_section.py
│           ├── query_section.py
│           ├── visualization_section.py
│           ├── augmentation_section.py
│           └── generation_section.py
├── README.md                          # This file
└── DEPLOYMENT_GUIDE.md               # Cloud deployment
```

## 💰 Cost Considerations

**GPT-4o-mini Pricing:**

- Input: $0.150 per 1M tokens
- Output: $0.600 per 1M tokens

**Typical Query Cost:**

- Small (3 contexts, 500 tokens): ~$0.0001-0.0003
- Medium (5 contexts, 1500 tokens): ~$0.0003-0.0008
- Large (10 contexts, 3000 tokens): ~$0.0006-0.0015

**Local Operations (Free):**

- Retrieval: Local embeddings (sentence-transformers)
- Augmentation: Client-side prompt construction

## 🐳 Docker Deployment

Quick start with Docker Compose:

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Or build manually:

```bash
docker build -t rag-visualizer .
docker run -p 8501:8501 --env-file .env rag-visualizer
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for cloud deployment options (Google Cloud Run, AWS, Azure).

## 💡 Tips for Best Results

**Chunk Size:**

- Smaller (50-100) = more granular, specific queries
- Larger (200-500) = more context, conceptual queries

**System Prompt:**

- Customize for your use case (technical docs, customer support, research)
- Include instructions for citation and fallback behavior

**Token Management:**

- Reduce retrieved chunks (n_results) to lower costs
- Use smaller chunk sizes for efficiency
- Monitor token usage in the Generation section

**Model Selection:**

- MiniLM for speed and general use
- mpnet for research and accuracy
- multilingual for non-English text

## 🔧 Troubleshooting

**"OPENAI_API_KEY not found"**

- Ensure `.env` file exists in project root
- Verify format: `OPENAI_API_KEY=sk-...`
- Restart Streamlit after creating `.env`

**High token usage**

- Reduce number of retrieved chunks (n_results slider)
- Use smaller chunk sizes
- Shorten the system prompt

**Model download fails**

```bash
export TRANSFORMERS_CACHE="./models"
streamlit run app.py
```

**Port already in use**

```bash
streamlit run app.py --server.port 8502
```

## 🔮 Future Enhancements

- [ ] Support for other LLM providers (Anthropic, local models)
- [ ] Conversation history
- [ ] RAG evaluation metrics (faithfulness, relevance)
- [ ] PDF and DOCX support
- [ ] Streaming responses
- [ ] Prompt template library
- [ ] Advanced RAG techniques (HyDE, multi-query)
- [ ] Export/import functionality

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

MIT License - see [LICENCE](LICENCE) file for details.

## 🙏 Acknowledgments

- [Sentence Transformers](https://www.sbert.net/) - Embedding models
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [OpenAI](https://openai.com/) - LLM API
- [Streamlit](https://streamlit.io/) - Web framework
- [Plotly](https://plotly.com/) - Interactive visualizations
- [scikit-learn](https://scikit-learn.org/) & [UMAP](https://umap-learn.readthedocs.io/) - Dimensionality reduction

---

⭐ If you find this project helpful, please give it a star!
