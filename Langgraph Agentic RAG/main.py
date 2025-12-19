"""Main entry point for the LangGraph Agentic RAG application."""

from src.graph import rag_app


def main() -> None:
    """Run example queries against the RAG application."""
    print("=" * 60)
    print("LangGraph Agentic RAG Application")
    print("=" * 60)

    # Experiment 1: Agent memory (inside knowledge store)
    print("\n[Query 1] What is agent memory?")
    result = rag_app.invoke(input={"question": "What is agent memory?"})
    print(f"Answer: {result['generation']}\n")

    # Experiment 2: Few-shot prompting (inside knowledge store)
    # print("\n[Query 2] Can you explain the concept of few-shot prompting?")
    # result = rag_app.invoke(input={"question": "Can you explain the concept of few-shot prompting?"})
    # print(f"Answer: {result['generation']}\n")

    # Experiment 3: Out of knowledge store topic (requires web search)
    # print("\n[Query 3] What is the definition of Microsoft AI search service?")
    # result = rag_app.invoke(input={"question": "What is the definition of Microsoft AI search service?"})
    # print(f"Answer: {result['generation']}\n")

    # Experiment 4: Completely off-topic (requires web search)
    # print("\n[Query 4] What are the places to visit in Indonesia?")
    # result = rag_app.invoke(input={"question": "What are the places to visit in Indonesia?"})
    # print(f"Answer: {result['generation']}\n")


if __name__ == "__main__":
    main()
