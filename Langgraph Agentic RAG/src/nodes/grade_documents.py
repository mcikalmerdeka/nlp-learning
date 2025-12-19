"""Grade documents node - filters relevant documents."""

from typing import Any, Dict

from src.chains import retrieval_grader
from src.core import logger
from src.core.state import GraphState


def grade_documents_node(state: GraphState) -> Dict[str, Any]:
    """
    Grade retrieved documents for relevance to the question.
    
    Sets web_search flag if any document is not relevant.

    Args:
        state: Current graph state with question and documents.

    Returns:
        Updated state with filtered documents and web_search flag.
    """
    logger.debug("Grading document relevance...")

    question = state["question"]
    documents = state["documents"]

    filtered_docs = []
    web_search = False

    for i, doc in enumerate(documents, 1):
        score = retrieval_grader.invoke(
            {"question": question, "document": doc.page_content}
        )
        grade = score.binary_score

        if grade.lower() == "yes":
            logger.debug(f"Doc {i}: ✓ relevant")
            filtered_docs.append(doc)
        else:
            logger.debug(f"Doc {i}: ✗ not relevant")
            web_search = True

    logger.info(f"Graded {len(documents)} docs → {len(filtered_docs)} relevant")

    return {"documents": filtered_docs, "web_search": web_search}
