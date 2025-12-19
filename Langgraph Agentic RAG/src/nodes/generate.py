"""Generate node - produces answers using the generation chain."""

from typing import Any, Dict

from src.chains import generation_chain
from src.core.state import GraphState


def generate_node(state: GraphState) -> Dict[str, Any]:
    """
    Generate an answer using the retrieved documents.

    Args:
        state: Current graph state with question and documents.

    Returns:
        Updated state with generation.
    """
    print("---GENERATE NODE---")

    question = state["question"]
    documents = state["documents"]

    generation = generation_chain.invoke({"question": question, "context": documents})

    return {"generation": generation, "documents": documents}
