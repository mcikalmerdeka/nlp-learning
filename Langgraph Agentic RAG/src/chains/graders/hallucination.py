"""Hallucination grader chain - checks if generation is grounded in facts."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from pydantic import BaseModel, Field

from src.config.prompts import Prompts
from src.core.llm import get_llm


class HallucinationGrader(BaseModel):
    """Binary score for hallucination detection."""

    binary_score: bool = Field(
        description="Answer is grounded in the facts: True if yes, False if no"
    )


def _build_hallucination_grader() -> RunnableSequence:
    """Build the hallucination grader chain."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(HallucinationGrader)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", Prompts.HALLUCINATION_GRADER_SYSTEM),
            ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
        ]
    )

    return prompt | structured_llm


hallucination_grader = _build_hallucination_grader()

