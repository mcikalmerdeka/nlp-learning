"""Main entry point for the LangGraph Agentic RAG application."""

from src.core import setup_logging
from src.graph import rag_app

# Configure logging level: DEBUG, INFO, WARNING, ERROR
setup_logging("INFO")


def main() -> None:
    """Run example queries against the RAG application."""
    print("=" * 60)
    print("LangGraph Agentic RAG Application")
    print("=" * 60)

    # # Experiment 1: Agent memory (inside knowledge store)
    # print("\n[Query 1] What is agent memory?")
    # result = rag_app.invoke(input={"question": "What is agent memory?"})
    # print(f"Answer: {result['generation']}\n")

    # # Experiment 2: Few-shot prompting (inside knowledge store)
    # print("\n[Query 2] Can you explain the concept of few-shot prompting?")
    # result = rag_app.invoke(input={"question": "Can you explain the concept of few-shot prompting?"})
    # print(f"Answer: {result['generation']}\n")

    # # Experiment 3: Out of knowledge store topic (requires web search)
    # print("\n[Query 3] What is the definition of Context Engineering and when did it get popular?")
    # result = rag_app.invoke(input={"question": "What is the definition of Context Engineering and when did it get popular?"})
    # print(f"Answer: {result['generation']}\n")

    # # Experiment 4: Completely off-topic (requires web search)
    # print("\n[Query 4] What are the best places to visit in Indonesia?")
    # result = rag_app.invoke(input={"question": "What are the best places to visit in Indonesia?"})
    # print(f"Answer: {result['generation']}\n")

    # Experiment 5: Streaming response (node-by-node updates)
    print("\n[Query 5] Can you explain the concept of few-shot prompting?\n")
    for chunk in rag_app.stream(
        input={"question": "Can you explain the concept of few-shot prompting?"}
    ):
        for node, update in chunk.items():
            print(f"{'=' * 50}")
            print(f"Update from node: {node}")
            print(f"{'=' * 50}")

            if "documents" in update:
                docs = update["documents"]
                print(f"📄 Documents: {len(docs)} retrieved")
                if docs:
                    # Show first doc source as preview
                    source = docs[0].metadata.get("source", "unknown")
                    print(f"   Source: {source}")

            if "web_search" in update:
                status = "🔍 Yes" if update["web_search"] else "✅ No"
                print(f"Web search needed: {status}")

            if "generation" in update:
                print(f"\n💬 Generated Answer:")
                print(f"{'─' * 40}")
                print(update["generation"])
                print(f"{'─' * 40}")

            print()

if __name__ == "__main__":
    main()
