# Multi-Department Knowledge Base Demo

A demonstration of **metadata-filtering based access control** for a RAG (Retrieval-Augmented Generation) knowledge base.

## Architecture

**Single Collection with Metadata Filtering** (Recommended Approach)

All documents are stored in one Qdrant collection, but each vector chunk is tagged with metadata that controls access. The application enforces a hard filter at query time before the search runs.

## Features

- **Role-based access control**: Users can only search documents matching their `allowed_groups`
- **Cross-department search**: Executives can search across all departments simultaneously
- **Multi-department demo**: Sample documents for HR, Engineering, Sales, and Finance
- **Local Qdrant**: No Docker required — Qdrant runs locally via file-based storage
- **LangChain RAG**: Uses OpenAI embeddings and GPT-4o-mini for Q&A

## Prerequisites

- Python 3.12+
- OpenAI API key (set in `.env` file)
- `uv` package manager (or `pip`)

## Installation

Using `uv`:

```bash
uv sync
```

Or using `pip`:

```bash
pip install -r requirements.txt
```

## Running the Demo

1. Make sure your `.env` file contains:
   ```
   OPENAI_API_KEY=your_key_here
   ```

2. Start the application:
   ```bash
   uv run python main.py
   ```

3. Open the Gradio URL (typically `http://127.0.0.1:7860`)

4. First, go to the **Ingest Sample Data** tab and click "Create / Reset Sample Database"

5. Then go to the **Search Knowledge Base** tab and try searching with different roles!

## Demo Questions to Try

| Question | Expected Behavior |
|----------|-------------------|
| "What are the Q3 plans?" | Engineering sees API migration, Sales sees pricing, Finance sees headcount, Executive sees all |
| "What is the vacation policy?" | HR sees full policy, others see general benefits overview |
| "Tell me about the IPO" | Only Finance and Executive can access |
| "What is our revenue?" | Only Sales and Executive can access |

## Security Principles Demonstrated

1. **Server-side filtering**: The `allowed_groups` filter is injected by the backend
2. **No trust in client**: User roles are resolved server-side, never from request parameters
3. **Defense in depth**: Database-level filtering prevents unauthorized access even if the UI is bypassed
4. **Array-based permissions**: `allowed_groups` arrays support complex multi-department access

## Project Structure

```
.
├── .env                          # API keys (not committed)
├── main.py                       # Gradio application
├── requirements.txt              # Python dependencies
├── pyproject.toml                # Project configuration
├── qdrant_storage_knowledge_base/  # Local Qdrant database (auto-created)
└── qdrant-local-reference/       # Reference implementation
```

## Dependencies

- `gradio` — Web UI framework
- `langchain` — LLM orchestration framework
- `langchain-openai` — OpenAI embeddings and chat models
- `langchain-qdrant` — Qdrant vector store integration
- `qdrant-client` — Qdrant Python client
- `python-dotenv` — Environment variable loading
