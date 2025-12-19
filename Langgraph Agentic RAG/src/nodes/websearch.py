"""Web search node - searches the web for additional information."""

from typing import Any, Dict

from langchain_core.documents import Document
from langchain_tavily import TavilySearch

from src.config.settings import settings
from src.core.state import GraphState

# Initialize web search tool
_web_search_tool = TavilySearch(
    max_results=settings.TAVILY_MAX_RESULTS,
    api_key=settings.TAVILY_API_KEY,
)


def web_search_node(state: GraphState) -> Dict[str, Any]:
    """
    Search the web for information related to the question.

    Args:
        state: Current graph state with question and optionally documents.

    Returns:
        Updated state with web search results appended to documents.
    """
    print("---WEB SEARCH NODE---")

    question = state["question"]
    documents = state.get("documents") or []

    # Perform web search
    tavily_results = _web_search_tool.invoke({"query": question})["results"]

    # Combine search results into a single document
    joined_content = "\n".join(result["content"] for result in tavily_results)
    web_doc = Document(page_content=joined_content)

    documents.append(web_doc)

    return {"documents": documents}
