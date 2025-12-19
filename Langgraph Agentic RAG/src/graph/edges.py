"""Conditional edge functions for the RAG graph."""

from src.chains import answer_grader, hallucination_grader, question_router, RouterQuery
from src.core.state import GraphState
from src.graph.constants import (
    GENERATE,
    WEB_SEARCH,
    DECISION_USEFUL,
    DECISION_NOT_USEFUL,
    DECISION_NOT_SUPPORTED,
    DECISION_WEBSEARCH,
    DECISION_VECTORSTORE,
)


def route_question(state: GraphState) -> str:
    """
    Route the initial question to vectorstore or web search.

    Args:
        state: Current graph state with question.

    Returns:
        Route decision: 'vectorstore' or 'websearch'.
    """
    print("---ROUTING QUESTION---")

    question = state["question"]
    source: RouterQuery = question_router.invoke({"question": question})

    if source.datasource == "websearch":
        print("---DECISION: ROUTING TO WEB SEARCH---")
        return DECISION_WEBSEARCH
    else:
        print("---DECISION: ROUTING TO VECTORSTORE---")
        return DECISION_VECTORSTORE


def decide_to_generate(state: GraphState) -> str:
    """
    Decide whether to generate or perform web search based on document relevance.

    Args:
        state: Current graph state with web_search flag.

    Returns:
        Next node: WEB_SEARCH or GENERATE.
    """
    print("---ASSESS GRADED DOCUMENTS---")

    if state["web_search"]:
        print("---DECISION: NOT ALL DOCUMENTS RELEVANT, ROUTING TO WEB SEARCH---")
        return WEB_SEARCH
    else:
        print("---DECISION: ALL DOCUMENTS RELEVANT, ROUTING TO GENERATE---")
        return GENERATE


def grade_generation(state: GraphState) -> str:
    """
    Grade the generation for hallucination and answer quality.

    Args:
        state: Current graph state with question, documents, and generation.

    Returns:
        Decision: 'useful', 'not_useful', or 'not_supported'.
    """
    print("---CHECKING HALLUCINATIONS---")

    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    # Check if generation is grounded in documents
    hallucination_score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )

    if hallucination_score.binary_score:
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        print("---GRADING GENERATION vs QUESTION---")

        # Check if generation addresses the question
        answer_score = answer_grader.invoke(
            {"question": question, "generation": generation}
        )

        if answer_score.binary_score:
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return DECISION_USEFUL
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return DECISION_NOT_USEFUL
    else:
        print("---DECISION: GENERATION NOT GROUNDED, RETRYING---")
        return DECISION_NOT_SUPPORTED

