"""
Tests for the chain modules.

Run from project root:
    pytest -s -v
"""

import pytest

from src.chains import (
    generation_chain,
    hallucination_grader,
    HallucinationGrader,
    question_router,
    retrieval_grader,
    GradeDocuments,
    RouterQuery,
)
from src.ingestion import get_retriever


@pytest.fixture
def retriever():
    """Get retriever instance."""
    return get_retriever()


class TestRetrievalGrader:
    """Tests for the retrieval grader chain."""

    def test_relevant_document(self, retriever):
        """Test that relevant documents are graded as 'yes'."""
        question = "agent memory"
        docs = retriever.invoke(question)
        doc_text = docs[0].page_content

        result: GradeDocuments = retrieval_grader.invoke(
            {"question": question, "document": doc_text}
        )

        assert result.binary_score == "yes"

    def test_irrelevant_document(self, retriever):
        """Test that irrelevant documents are graded as 'no'."""
        question = "agent memory"
        docs = retriever.invoke(question)
        doc_text = docs[0].page_content

        result: GradeDocuments = retrieval_grader.invoke(
            {"question": "how to make a pizza", "document": doc_text}
        )

        assert result.binary_score == "no"


class TestGenerationChain:
    """Tests for the generation chain."""

    def test_generation(self, retriever):
        """Test that generation produces output."""
        question = "agent memory"
        docs = retriever.invoke(question)

        result: str = generation_chain.invoke(
            {"question": question, "context": docs}
        )

        assert isinstance(result, str)
        assert len(result) > 0
        print(f"\nGenerated answer: {result}")


class TestHallucinationGrader:
    """Tests for the hallucination grader chain."""

    def test_grounded_generation(self, retriever):
        """Test that grounded generations pass."""
        question = "agent memory"
        docs = retriever.invoke(question)
        generation = generation_chain.invoke({"question": question, "context": docs})

        result: HallucinationGrader = hallucination_grader.invoke(
            {"documents": docs, "generation": generation}
        )

        assert result.binary_score is True

    def test_hallucinated_generation(self, retriever):
        """Test that hallucinated generations fail."""
        question = "agent memory"
        docs = retriever.invoke(question)

        result: HallucinationGrader = hallucination_grader.invoke(
            {
                "documents": docs,
                "generation": "In order to make pizza we need to first start with the dough",
            }
        )

        assert result.binary_score is False


class TestRouter:
    """Tests for the question router chain."""

    def test_route_to_vectorstore(self):
        """Test routing to vectorstore for relevant questions."""
        question = "agent memory"

        result: RouterQuery = question_router.invoke({"question": question})

        assert result.datasource == "vectorstore"

    def test_route_to_websearch(self):
        """Test routing to web search for off-topic questions."""
        question = "how to make a pizza"

        result: RouterQuery = question_router.invoke({"question": question})

        assert result.datasource == "websearch"

