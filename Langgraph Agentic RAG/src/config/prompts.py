"""Centralized prompt templates for all chains."""


class Prompts:
    """All prompt templates used in the application."""

    # Router prompts
    ROUTER_SYSTEM = """You are an expert at routing a user question to a vectorstore or web search.
The vectorstore contains documents related to agents, prompt engineering, and adversarial attacks.
Use the vectorstore for questions on these topics. For all else, use web-search."""

    # Retrieval grader prompts
    RETRIEVAL_GRADER_SYSTEM = """You are a grader assessing relevance of a retrieved document to a user question.
If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant.
Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.
Don't translate the score into 1 or 0, just return the score as a string."""

    # Answer grader prompts
    ANSWER_GRADER_SYSTEM = """You are a grader assessing whether an answer addresses / resolves a question.
Give a binary score 'yes' or 'no'. 'Yes' means that the answer resolves the question.
If the answer does not address / resolve the question, give a score of 'no'."""

    # Hallucination grader prompts
    HALLUCINATION_GRADER_SYSTEM = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts.
Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""

    # Generation prompts
    GENERATION_TEMPLATE = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Additional Instructions:
{additional_instructions}
Answer:"""

    GENERATION_ADDITIONAL_INSTRUCTIONS = """Filter out the irrelevant information from the context.
Exclude the following elements from Tavily search results:
- Image links and URLs (e.g., .jpg, .png, .gif, .svg)
- Code blocks and snippets
- JSON data structures
- HTML markup and CSS
- Navigation elements, headers, footers
- Advertisement content
- Social media buttons and widgets
- Metadata like timestamps, author info, tags
- Cookie notices and privacy policies
Focus only on the main textual content relevant to answering the question."""

