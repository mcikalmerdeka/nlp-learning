"""Conditional edge functions for the RAG graph."""

from src.chains import answer_grader, hallucination_grader, question_router, RouterQuery
from src.core import logger
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
    logger.debug("Routing question...")

    question = state["question"]
    source: RouterQuery = question_router.invoke({"question": question})

    if source.datasource == "websearch":
        logger.info("Route → Web Search")
        return DECISION_WEBSEARCH
    else:
        logger.info("Route → Vectorstore")
        return DECISION_VECTORSTORE


def decide_to_generate(state: GraphState) -> str:
    """
    Decide whether to generate or perform web search based on document relevance.

    Args:
        state: Current graph state with web_search flag.

    Returns:
        Next node: WEB_SEARCH or GENERATE.
    """
    logger.debug("Assessing graded documents...")

    if state["web_search"]:
        logger.info("Documents insufficient → Web Search")
        return WEB_SEARCH
    else:
        logger.info("Documents sufficient → Generate")
        return GENERATE


def grade_generation(state: GraphState) -> str:
    """
    Grade the generation for hallucination and answer quality.

    Args:
        state: Current graph state with question, documents, and generation.

    Returns:
        Decision: 'useful', 'not_useful', or 'not_supported'.
    """
    logger.debug("Checking for hallucinations...")

    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    # Check if generation is grounded in documents
    hallucination_score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )

    if hallucination_score.binary_score:
        logger.debug("Generation grounded in documents")

        # Check if generation addresses the question
        answer_score = answer_grader.invoke(
            {"question": question, "generation": generation}
        )

        if answer_score.binary_score:
            logger.info("Generation ✓ Useful")
            return DECISION_USEFUL
        else:
            logger.warning("Generation does not address question → Retry")
            return DECISION_NOT_USEFUL
    else:
        logger.warning("Generation not grounded → Web Search")
        return DECISION_NOT_SUPPORTED
