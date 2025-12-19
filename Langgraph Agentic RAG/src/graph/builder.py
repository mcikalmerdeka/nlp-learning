"""Graph builder - constructs the RAG workflow graph."""

from langgraph.graph import END, START, StateGraph

from src.config.settings import settings
from src.core import logger
from src.core.state import GraphState
from src.graph.constants import (
    GENERATE,
    GRADE_DOCUMENTS,
    RETRIEVE,
    WEB_SEARCH,
    DECISION_USEFUL,
    DECISION_NOT_USEFUL,
    DECISION_NOT_SUPPORTED,
    DECISION_WEBSEARCH,
    DECISION_VECTORSTORE,
)
from src.graph.edges import decide_to_generate, grade_generation, route_question
from src.nodes import generate_node, grade_documents_node, retrieve_node, web_search_node


def build_graph() -> StateGraph:
    """
    Build the RAG workflow graph.

    Returns:
        Compiled StateGraph ready for execution.
    """
    graph = StateGraph(GraphState)

    # Add nodes
    graph.add_node(RETRIEVE, retrieve_node)
    graph.add_node(GRADE_DOCUMENTS, grade_documents_node)
    graph.add_node(GENERATE, generate_node)
    graph.add_node(WEB_SEARCH, web_search_node)

    # Set conditional entry point (router)
    graph.set_conditional_entry_point(
        path=route_question,
        path_map={
            DECISION_WEBSEARCH: WEB_SEARCH,
            DECISION_VECTORSTORE: RETRIEVE,
        },
    )

    # Add edges
    graph.add_edge(RETRIEVE, GRADE_DOCUMENTS)
    graph.add_edge(WEB_SEARCH, GENERATE)

    # Conditional edge: grade documents -> generate or web search
    graph.add_conditional_edges(
        source=GRADE_DOCUMENTS,
        path=decide_to_generate,
        path_map={
            WEB_SEARCH: WEB_SEARCH,
            GENERATE: GENERATE,
        },
    )

    # Conditional edge: generate -> end, retry, or web search
    graph.add_conditional_edges(
        source=GENERATE,
        path=grade_generation,
        path_map={
            DECISION_USEFUL: END,
            DECISION_NOT_USEFUL: GENERATE,
            DECISION_NOT_SUPPORTED: WEB_SEARCH,
        },
    )

    return graph.compile()


# Pre-built graph instance
rag_app = build_graph()


def save_graph_visualization(output_path: str | None = None) -> None:
    """Save the graph visualization to a PNG file."""
    path = output_path or settings.GRAPH_OUTPUT_PATH
    rag_app.get_graph().draw_mermaid_png(output_file_path=path)
    logger.info(f"Graph saved to: {path}")
