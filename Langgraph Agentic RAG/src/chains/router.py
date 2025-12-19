"""Router chain - routes questions to vectorstore or web search."""

from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from pydantic import BaseModel, Field

from src.config.prompts import Prompts
from src.core.llm import get_llm


class RouterQuery(BaseModel):
    """Route user query to the most relevant datasource."""

    datasource: Literal["vectorstore", "websearch"] = Field(
        ...,
        description="Given a user question, route to web search or vectorstore.",
    )


def _build_router() -> RunnableSequence:
    """Build the question router chain."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(RouterQuery)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", Prompts.ROUTER_SYSTEM),
            ("human", "{question}"),
        ]
    )

    return prompt | structured_llm


question_router = _build_router()
