"""Retrieve node - fetches relevant documents from vector store."""

from typing import Any, Dict

from src.core.state import GraphState
from src.ingestion import get_retriever


def retrieve_node(state: GraphState) -> Dict[str, Any]:
    """
    Retrieve relevant documents for the question.

    Args:
        state: Current graph state with question.

    Returns:
        Updated state with retrieved documents.
    """
    print(f"---RETRIEVE NODE: {state['question']}---")

    question = state["question"]
    retriever = get_retriever()
    documents = retriever.invoke(question)

    return {"documents": documents}
