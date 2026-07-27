# TurboQuant Vector Search Experiment

A small, self-contained Gradio demo that replaces the usual FAISS in-memory
vector store with a **TurboQuant**-powered index via
[`turbovec`](https://github.com/RyanCodrai/turbovec), orchestrated with
**LangChain** and **OpenAI** models (embeddings + agent).

> You asked to do the research and structure the repo; you will install the
dependencies and run the code yourself.

## Why TurboQuant instead of FAISS?

| Feature | FAISS PQ | ScaNN | **TurboQuant (turbovec)** |
|---|---|---|---|
| Preprocessing | K-means (minutes) | Tree building (minutes) | **None (instant)** |
| Recall@10 | ~60% | ~85% | **~95%** |
| Compression | 8x | 4x | **5-8x** |
| Dependencies | C++/CUDA | C++/TensorFlow | **Rust + Python bindings** |
| Training data needed | Yes | Yes | **No (data-oblivious)** |
| Query complexity | O(N) brute-force | O(log N) | **O(sqrt(N)) with IVF** |

Key takeaways from the research:

- TurboQuant is a **data-oblivious quantizer** from Google's ICLR 2026 paper
  ([arXiv:2504.19874](https://arxiv.org/abs/2504.19874)).
- It compresses embeddings **per-vector** with random rotations and Lloyd-Max
  codebooks, so there is **no training phase**, no k-means, and no batch
  preprocessing.
- `turbovec` is a Rust implementation with Python bindings and a first-class
  **LangChain** `VectorStore` integration, making it a near drop-in replacement
  for `langchain_core.vectorstores.in_memory.InMemoryVectorStore` and FAISS
  based stores.
- For a quick, ready-to-run example, `turbovec[langchain]` is the easiest path
  because it already wires the quantizer into LangChain's retriever API.

See `docs/what_is_turboquant.md` for a deeper explanation of TurboQuant and how
it compares to FAISS and dedicated vector databases.

## What this demo does

1. **Add documents** — paste text (one document per line) and index it with
   TurboQuant compression.
2. **Load documents** — select `.txt` files from the `data/` folder and load
   them with a small native file reader that creates LangChain `Document`
   objects. You can also recreate the index from a fresh selection or delete the
   index entirely.
3. **Search** — query the index and get top-k ranked results with cosine
   similarity scores.
4. **Agent (RAG)** — ask a question; the app retrieves relevant documents and
   answers with `gpt-5.4-nano`.
5. **Index stats** — see how many vectors are stored and which model is used.
6. **Persistence** — save/load the compressed index to `./index_storage/`.

## Project structure

```
.
├── data/             # Sample .txt documents for RAG demos
│   ├── nebula_station_incident.txt
│   ├── evergreen_corp_q3_review.txt
│   ├── asteria_colony_charter.txt
│   └── lumina_tech_product_spec.txt
├── docs/             # Example prompts and explanatory docs
│   ├── example_queries.md
│   └── what_is_turboquant.md
├── logger.py         # Centralized logging configuration
├── logs/             # Created at runtime; contains app.log
├── main.py           # Gradio UI + LangChain + TurboQuant integration
├── pyproject.toml    # Dependencies (pinned to latest stable versions)
├── README.md         # This file
└── index_storage/    # Created at runtime when you save/load the index
```

## Dependencies

The latest stable versions used in this repo (as of July 2026):

| Package | Version | Why |
|---|---|---|
| `turbovec[langchain]` | `>=0.8.0` | TurboQuant vector index + LangChain `VectorStore` |
| `langchain` | `>=1.3.14` | Agent/retriever framework |
| `langchain-openai` | `>=1.4.1` | OpenAI embeddings + chat model wrapper |
| `gradio` | `>=6.20.0` | Web UI |
| `python-dotenv` | `>=1.2.2` | Loads `OPENAI_API_KEY` from `.env` |
| `numpy` | `>=2.0.0` | Array operations required by turbovec |

Optional dev dependencies are listed under `[project.optional-dependencies]dev`.

## How to run

1. **Install dependencies** (you said you will do this yourself):

   ```bash
   # Using uv (recommended for this project)
   uv sync

   # Or plain pip
   pip install -e .
   ```

2. **Run the Gradio app**:

   ```bash
   uv run main.py
   # or
   python main.py
   ```

3. **Open the UI** in your browser at `http://localhost:7860`.

4. **Try it**:
   - Go to the **Load documents** tab, select the sample files in `data/`,
     and click *Load selected into index* or *Recreate index from selected*.
   - Switch to the **Search** tab and ask something specific to the files, e.g.
     `"What happened on Nebula Station in March 2147?"` or
     `"What is the target price of Project Firewheel?"`.
   - Switch to the **Agent (RAG)** tab and ask a question such as
     `"What are the main risks in Evergreen's Q3 review?"`.
   - See `docs/example_queries.md` for many more ready-to-use search queries
     and agent questions for every document.
   - Use the **Persistence** tab to save the index to disk.
   - Use **Delete index** in the **Load documents** tab to start over.

## Implementation notes

- **Embedding model**: `text-embedding-3-small` from OpenAI.
- **Agent model**: `gpt-5.4-nano` from OpenAI for RAG answers.
- **Environment**: `python-dotenv` loads variables from the project `.env` file.
  The app checks that `OPENAI_API_KEY` is present before starting.
- **TurboQuant bit width**: `4` bits per coordinate. This is the paper's
  practical sweet spot for recall vs. compression.
- **Vector store**: `turbovec.langchain.TurboQuantVectorStore`, which wraps an
  `IdMapIndex` so stable external IDs survive saves/loads.
- **Normalization**: `turbovec` L2-normalizes embeddings on insert, so the raw
  scores reported by `similarity_search_with_score` are cosine-like inner
  products in `[-1, 1]`.
- **File loading**: a small native helper reads each selected `.txt` file into
  a `langchain_core.documents.Document`. This avoids importing from
  `langchain_community`, which was sunset in May 2026. The file name is stored
  in the document metadata as `source_file`.
- **Index management**: *Load selected into index* appends to the existing index;
  *Recreate index from selected* clears the index and rebuilds it from the chosen
  files; *Delete index* discards the in-memory index and starts fresh.
- **Persistence**: uses the public `TurboQuantVectorStore.dump()` / `.load()`
  methods, which write both the binary quantized index (`index.tvim`) and a
  JSON document side-car (`docstore.json`) into `./index_storage/`.
- **Stats**: the demo reads `store._index` to display the index length and
  `IdMapIndex.stats()`. This touches the private backing index because the
  LangChain `VectorStore` surface does not expose size/statistics directly.

## Logging

`logger.py` provides centralized logging that mirrors the style used in the
project's `logging_example.py`:

- **Console output** (stdout): `INFO` level and above with timestamp, logger
  name, level, and message.
- **File output**: `logs/app.log` with `DEBUG` level and above, including
  function name and line number.
- Handlers are cleared on setup to avoid duplicate messages, and propagation is
disabled.

The app logs key events such as startup, document loading, index resets, search
and agent requests, persistence operations, and any exceptions. If something
fails in the UI, check the terminal output and `logs/app.log` for details.

## References

- [`turbovec` on PyPI](https://pypi.org/project/turbovec/)
- [`turbovec` GitHub](https://github.com/RyanCodrai/turbovec)
- [TurboQuant paper (arXiv:2504.19874)](https://arxiv.org/abs/2504.19874)
- [LangChain VectorStore docs](https://python.langchain.com/docs/integrations/vectorstores/)
- [Gradio docs](https://www.gradio.app/docs)

## License

This experiment is unlicensed boilerplate; add your own license as needed.
