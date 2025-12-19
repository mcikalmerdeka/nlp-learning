"""Generation chain - produces answers from context."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence

from src.config.prompts import Prompts
from src.core.llm import get_llm


def _build_generation_chain() -> RunnableSequence:
    """Build the generation chain."""
    llm = get_llm()

    prompt = ChatPromptTemplate.from_template(Prompts.GENERATION_TEMPLATE)
    prompt = prompt.partial(
        additional_instructions=Prompts.GENERATION_ADDITIONAL_INSTRUCTIONS
    )

    return prompt | llm | StrOutputParser()


generation_chain = _build_generation_chain()
