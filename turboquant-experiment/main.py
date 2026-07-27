"""Gradio UI for a LangChain + TurboQuant vector search experiment.

This example replaces the usual FAISS-backed in-memory vector store with the
``turbovec`` implementation of Google's TurboQuant algorithm. The index is
built online: no training step, no k-means, and no separate data passes.

Run:
    uv run main.py
or (after installing dependencies yourself):
    python main.py
"""

from __future__ import annotations

import logging
import os
import pathlib
from dataclasses import dataclass

import gradio as gr
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from turbovec.langchain import TurboQuantVectorStore

from logger import setup_logger


def _load_text_file(file_path: pathlib.Path, encoding: str = "utf-8") -> Document:
    """Read a plain-text file into a LangChain Document.

    This replaces ``langchain_community.document_loaders.TextLoader`` to avoid
    the langchain-community deprecation warning. langchain-community was
    sunset in May 2026, and there is no standalone partner package for plain
    .txt file loading.
    """
    text = file_path.read_text(encoding=encoding)
    return Document(
        page_content=text,
        metadata={"source": str(file_path), "source_file": file_path.name},
    )

# Load environment variables (e.g. OPENAI_API_KEY) from the project .env file.
load_dotenv()

# Configure application logging: console + file in logs/app.log.
logger = setup_logger(name="turboquant_experiment", level=logging.INFO)
logger.info("Logging initialized")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
"""OpenAI embedding model used for the TurboQuant vector index."""

DEFAULT_AGENT_MODEL = "gpt-5.4-nano"
"""OpenAI chat model used for the RAG agent."""

DEFAULT_BIT_WIDTH = 4
"""TurboQuant bit width per coordinate. 4 is the paper's sweet spot for recall."""

INDEX_FOLDER = pathlib.Path("./index_storage")
"""Directory where the persisted index and document side-car are stored."""

DATA_FOLDER = pathlib.Path("./data")
"""Directory containing .txt documents that can be loaded into the index."""

SAMPLE_DOCUMENTS = """\
TurboQuant is a data-oblivious vector quantizer that compresses embeddings with near-Shannon-optimal distortion.
FAISS is a popular library from Meta for efficient similarity search and clustering of dense vectors.
LangChain is an AI agent framework that makes it easy to compose LLMs, retrievers, and tools.
Gradio is a Python library that lets you build machine-learning web UIs in minutes.
Vector databases store high-dimensional embeddings and retrieve the nearest neighbors for a query.
Approximate nearest neighbor search trades a small amount of recall for orders of magnitude faster queries.
"""


# ---------------------------------------------------------------------------
# State container
# ---------------------------------------------------------------------------

@dataclass
class AppState:
    """In-memory application state."""

    embeddings: OpenAIEmbeddings
    llm: ChatOpenAI
    store: TurboQuantVectorStore
    index_folder: pathlib.Path
    bit_width: int

    def __init__(
        self,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        agent_model: str = DEFAULT_AGENT_MODEL,
        bit_width: int = DEFAULT_BIT_WIDTH,
    ) -> None:
        logger.info(
            "Initializing AppState: embedding_model=%s, agent_model=%s, bit_width=%s",
            embedding_model,
            agent_model,
            bit_width,
        )
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("OPENAI_API_KEY is not set in environment or .env file")
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Make sure it is defined in your .env file."
            )
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self.llm = ChatOpenAI(model=agent_model, temperature=0.2)
        self.index_folder = INDEX_FOLDER
        self.bit_width = bit_width
        # Lazy index: dimension is inferred from the first added batch.
        self.store = TurboQuantVectorStore(
            embedding=self.embeddings,
            bit_width=bit_width,
        )
        logger.info("AppState initialized; vector store ready")

    def add_texts(self, raw_texts: str, metadata_source: str = "user") -> str:
        """Add non-empty lines as documents to the TurboQuant vector store."""
        logger.info("Adding pasted text documents with source=%s", metadata_source)
        texts = [line.strip() for line in raw_texts.splitlines() if line.strip()]
        if not texts:
            logger.warning("No non-empty lines provided; nothing to add")
            return "No non-empty lines found. Nothing was added."

        docs = [
            Document(page_content=text, metadata={"source": metadata_source, "id": i})
            for i, text in enumerate(texts)
        ]
        try:
            self.store.add_documents(docs)
            total = len(self.store._index)
            logger.info("Added %d pasted documents; total indexed=%d", len(docs), total)
            return f"Added {len(docs)} documents. Total indexed: {total}"
        except Exception:
            logger.exception("Failed to add pasted text documents")
            raise

    def search(self, query: str, k: int = 5) -> str:
        """Run similarity search and return a formatted markdown report."""
        logger.info("Search request: query=%r, k=%d", query, k)
        if not query.strip():
            logger.warning("Empty search query received")
            return "Please enter a query."
        if len(self.store._index) == 0:
            logger.warning("Search attempted on empty index")
            return "Index is empty. Add some documents first."

        try:
            docs_with_scores = self.store.similarity_search_with_score(query, k=k)
            logger.info("Search returned %d results for query=%r", len(docs_with_scores), query)
            lines = [f"## Results for: *{query}*\n"]
            for rank, (doc, score) in enumerate(docs_with_scores, start=1):
                # Cosine similarity mapped to [0, 1] by turbovec; higher is better
                lines.append(f"**{rank}.** Score: `{score:.4f}`")
                lines.append(f"> {doc.page_content}\n")
                lines.append(f"_Metadata: {doc.metadata}_\n")
            return "\n".join(lines)
        except Exception:
            logger.exception("Search failed for query=%r", query)
            raise

    def stats(self) -> str:
        """Return a markdown summary of the current index."""
        logger.info("Refreshing index statistics")
        if len(self.store._index) == 0:
            logger.info("Stats requested for empty index")
            return "Index is empty. Add documents to see statistics."
        stats = self.store._index.stats()
        logger.debug("Index stats: %s", stats)
        stats_text = "\n".join(
            f"- **{key}:** `{value}`" for key, value in stats.items()
        )
        return f"""\
## Index statistics
- **Embedding model:** {self.embeddings.model}
- **Agent model:** {self.llm.model_name}
- **Quantization:** TurboQuant (`turbovec`) at {self.bit_width}-bit per coordinate
- **Index folder:** {self.index_folder}

{stats_text}

Use the *Search* tab to query the index.
"""

    def ask_agent(self, question: str, k: int = 5) -> str:
        """Retrieve relevant documents and answer the question with the LLM."""
        logger.info("Agent request: question=%r, k=%d", question, k)
        if not question.strip():
            logger.warning("Empty agent question received")
            return "Please enter a question."
        if len(self.store._index) == 0:
            logger.warning("Agent question attempted on empty index")
            return "Index is empty. Add some documents first."

        try:
            docs_with_scores = self.store.similarity_search_with_score(question, k=k)
            logger.info(
                "Agent retrieved %d documents for question=%r", len(docs_with_scores), question
            )
            if not docs_with_scores:
                return "No relevant documents found to answer the question."

            context = "\n\n".join(
                f"Document (score {score:.4f}):\n{doc.page_content}"
                for doc, score in docs_with_scores
            )

            prompt = (
                "You are a helpful research assistant. Use only the provided context "
                "to answer the question. If the context does not contain enough "
                "information, say so. Cite the source documents briefly.\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {question}\n\n"
                "Answer:"
            )
            answer = self.llm.invoke(prompt).content
            logger.info("Agent produced answer for question=%r", question)
            return f"## Agent answer\n\n{answer}\n\n---\n\n**Retrieved context:**\n\n{context}"
        except Exception:
            logger.exception("Agent failed for question=%r", question)
            raise

    def list_data_files(self) -> list[str]:
        """Return the .txt file names found in the data folder."""
        if not DATA_FOLDER.exists():
            logger.warning("Data folder '%s' not found", DATA_FOLDER)
            return []
        files = sorted(p.name for p in DATA_FOLDER.glob("*.txt"))
        logger.debug("Found %d .txt files in data folder: %s", len(files), files)
        return files

    def load_files_into_index(
        self, selected_files: list[str], recreate: bool = False
    ) -> str:
        """Load selected .txt files from the data folder into the index.

        If ``recreate`` is True, the current index is discarded first.
        """
        logger.info(
            "Loading files into index: selected=%s, recreate=%s", selected_files, recreate
        )
        if not DATA_FOLDER.exists():
            logger.error("Data folder '%s' not found", DATA_FOLDER)
            return f"Data folder '{DATA_FOLDER}' not found."
        if not selected_files:
            logger.warning("No files selected for loading")
            return "No files selected."

        if recreate:
            self._reset_index()

        added_total = 0
        for filename in selected_files:
            file_path = DATA_FOLDER / filename
            if not file_path.exists():
                logger.warning("Selected file not found: %s", file_path)
                continue
            try:
                doc = _load_text_file(file_path)
                self.store.add_documents([doc])
                added_total += 1
                logger.info("Loaded document from %s", filename)
            except Exception:
                logger.exception("Failed to load file %s", filename)
                raise

        total = len(self.store._index)
        action = "Recreated" if recreate else "Added"
        logger.info(
            "%s index complete: %d file(s), %d document(s), total indexed=%d",
            action,
            len(selected_files),
            added_total,
            total,
        )
        return (
            f"{action} index with {len(selected_files)} file(s), "
            f"{added_total} document(s). Total indexed: {total}"
        )

    def delete_index(self) -> str:
        """Discard the current in-memory index and start fresh."""
        logger.info("Deleting current index")
        self._reset_index()
        logger.info("Index deleted")
        return "Index deleted. The vector store is now empty."

    def _reset_index(self) -> None:
        """Create a fresh, empty TurboQuant vector store."""
        logger.debug("Resetting vector store")
        self.store = TurboQuantVectorStore(
            embedding=self.embeddings,
            bit_width=self.bit_width,
        )

    def save(self) -> str:
        """Persist the index plus side-car to disk."""
        logger.info("Saving index to %s", self.index_folder)
        if len(self.store._index) == 0:
            logger.warning("Save attempted on empty index")
            return "Index is empty. Nothing to save."
        try:
            self.index_folder.mkdir(parents=True, exist_ok=True)
            self.store.dump(str(self.index_folder))
            logger.info("Index saved to %s", self.index_folder)
            return f"Saved index to {self.index_folder}"
        except Exception:
            logger.exception("Failed to save index to %s", self.index_folder)
            raise

    def load(self) -> str:
        """Load a persisted index from disk."""
        logger.info("Loading index from %s", self.index_folder)
        if not self.index_folder.exists():
            logger.warning("No persisted index found at %s", self.index_folder)
            return f"No persisted index found at {self.index_folder}."
        try:
            self.store = TurboQuantVectorStore.load(
                str(self.index_folder),
                embedding=self.embeddings,
            )
            total = len(self.store._index)
            logger.info("Loaded index from %s with %d vectors", self.index_folder, total)
            return f"Loaded index from {self.index_folder} with {total} vectors"
        except Exception:
            logger.exception("Failed to load index from %s", self.index_folder)
            raise


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

def build_ui(state: AppState) -> gr.Blocks:
    """Build and return the Gradio demo interface."""
    with gr.Blocks(title="TurboQuant Vector Search Experiment") as demo:
        gr.Markdown(
            """\
            # TurboQuant Vector Search Experiment

            This demo uses **LangChain** + **turbovec** (a TurboQuant implementation)
            instead of a FAISS index. TurboQuant compresses embeddings with no
            training step, no k-means, and no data passes.

            - Embeddings: `text-embedding-3-small` (OpenAI)
            - Agent: `gpt-5.4-nano` (OpenAI) for RAG answers
            - Quantization: TurboQuant (`turbovec`) at 4-bit per coordinate
            - Framework: `langchain` + `langchain-openai` + `langchain-community`
            - Sample documents: load `.txt` files from the `data/` folder
            """
        )

        with gr.Tab("Add documents"):
            doc_input = gr.Textbox(
                label="Documents",
                value=SAMPLE_DOCUMENTS,
                lines=10,
                placeholder="Paste one document per line...",
            )
            add_btn = gr.Button("Add to index", variant="primary")
            add_output = gr.Textbox(label="Status", interactive=False)
            add_btn.click(state.add_texts, inputs=doc_input, outputs=add_output)

        with gr.Tab("Load documents"):
            available_files = state.list_data_files()
            file_selector = gr.CheckboxGroup(
                choices=available_files,
                value=available_files,
                label="Select .txt files from data/",
            )
            with gr.Row():
                load_btn = gr.Button("Load selected into index", variant="primary")
                recreate_btn = gr.Button("Recreate index from selected")
                delete_btn = gr.Button("Delete index", variant="stop")
            load_output = gr.Textbox(label="Status", interactive=False)
            load_btn.click(
                state.load_files_into_index,
                inputs=[file_selector, gr.State(value=False)],
                outputs=load_output,
            )
            recreate_btn.click(
                state.load_files_into_index,
                inputs=[file_selector, gr.State(value=True)],
                outputs=load_output,
            )
            delete_btn.click(state.delete_index, outputs=load_output)

        with gr.Tab("Search"):
            query_input = gr.Textbox(
                label="Query",
                placeholder="What is turboquant?",
            )
            k_slider = gr.Slider(
                minimum=1,
                maximum=20,
                value=5,
                step=1,
                label="Number of results (k)",
            )
            search_btn = gr.Button("Search", variant="primary")
            search_output = gr.Markdown(label="Results")
            search_btn.click(
                state.search,
                inputs=[query_input, k_slider],
                outputs=search_output,
            )

        with gr.Tab("Agent (RAG)"):
            agent_question = gr.Textbox(
                label="Question",
                placeholder="What is the difference between TurboQuant and FAISS?",
                lines=2,
            )
            agent_k_slider = gr.Slider(
                minimum=1,
                maximum=20,
                value=5,
                step=1,
                label="Documents to retrieve (k)",
            )
            agent_btn = gr.Button("Ask agent", variant="primary")
            agent_output = gr.Markdown(label="Answer")
            agent_btn.click(
                state.ask_agent,
                inputs=[agent_question, agent_k_slider],
                outputs=agent_output,
            )

        with gr.Tab("Index stats"):
            stats_btn = gr.Button("Refresh stats", variant="primary")
            stats_output = gr.Markdown()
            stats_btn.click(state.stats, outputs=stats_output)

        with gr.Tab("Persistence"):
            with gr.Row():
                save_btn = gr.Button("Save index")
                load_btn = gr.Button("Load index")
            persist_output = gr.Textbox(label="Status", interactive=False)
            save_btn.click(state.save, outputs=persist_output)
            load_btn.click(state.load, outputs=persist_output)

        gr.Markdown(
            "_Note: make sure `OPENAI_API_KEY` is set in your `.env` file. The index lives in RAM; use the Persistence tab to save/load it. Use Load documents to manage which files are indexed._"
        )

    return demo


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    logger.info("Starting TurboQuant Vector Search Experiment")
    try:
        state = AppState()
        demo = build_ui(state)
        logger.info("Launching Gradio UI on http://0.0.0.0:7860")
        demo.launch(server_name="0.0.0.0", server_port=7860)
    except Exception:
        logger.exception("Application failed to start")
        raise


if __name__ == "__main__":
    main()
