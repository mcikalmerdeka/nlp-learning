"""Grade documents node - filters relevant documents."""

from typing import Any, Dict

from src.chains import retrieval_grader
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
    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")

    question = state["question"]
    documents = state["documents"]

    filtered_docs = []
    web_search = False

    for doc in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": doc.page_content}
        )
        grade = score.binary_score

        if grade.lower() == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(doc)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            web_search = True

    return {"documents": filtered_docs, "web_search": web_search}
