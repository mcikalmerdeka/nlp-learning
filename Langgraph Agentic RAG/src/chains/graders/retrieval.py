"""Retrieval grader chain - checks document relevance to question."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from pydantic import BaseModel, Field

from src.config.prompts import Prompts
from src.core.llm import get_llm


class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question: 'yes' if relevant, 'no' if not"
    )


def _build_retrieval_grader() -> RunnableSequence:
    """Build the retrieval grader chain."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(GradeDocuments)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", Prompts.RETRIEVAL_GRADER_SYSTEM),
            ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
        ]
    )

    return prompt | structured_llm


retrieval_grader = _build_retrieval_grader()

