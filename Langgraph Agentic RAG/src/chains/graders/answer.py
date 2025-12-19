"""Answer grader chain - assesses if generation addresses the question."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from pydantic import BaseModel, Field

from src.config.prompts import Prompts
from src.core.llm import get_llm


class AnswerGrader(BaseModel):
    """Binary score for answer quality."""

    binary_score: bool = Field(
        description="Answer addresses/resolves the question: True if yes, False if no"
    )


def _build_answer_grader() -> RunnableSequence:
    """Build the answer grader chain."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(AnswerGrader)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", Prompts.ANSWER_GRADER_SYSTEM),
            ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
        ]
    )

    return prompt | structured_llm


answer_grader = _build_answer_grader()

