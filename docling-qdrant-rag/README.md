# Docling and Qdrant RAG

A quick repo for me to play with Docling and Qdrant. The repo used the [Docling paper](https://arxiv.org/pdf/2408.09869) as the example document.

Several example questions to try (example from chatgpt generated):

Here are **RAG-oriented, practical questions** you can ask _about the Docling paper_ to both **evaluate Docling** and **design better retrieval pipelines**. I’ve grouped them by intent so you can pick what fits your use case.

---

## 1. Document Understanding & Conversion Quality (Core for RAG)

- How does Docling infer **reading order**, and how reliable is it for multi-column academic papers?
- What document structures does Docling preserve explicitly in JSON (e.g., sections, subsections, lists)?
- How does Docling differentiate between **paragraph text, captions, and references**, and how accurate is this separation?
- How are **figures and their captions** linked in the final document object?
- How robust is Docling when handling PDFs with **non-standard layouts** (e.g., slides, reports, brochures)?

---

## 2. Chunking & Embedding Strategy (Very RAG-specific)

- How does Docling’s structured output improve **semantic chunking** compared to raw PDF text extraction?
- What advantages does Docling provide for **table-aware chunking** in RAG pipelines?
- How does Docling output enable **hierarchical chunking** (document → section → paragraph)?
- What metadata fields extracted by Docling are most useful as **retrieval filters** (e.g., section title, page number, document language)?
- How does Docling’s output compare to naïve chunking when used with vector databases?

---

## 3. Tables in RAG (Critical Differentiator)

- How does TableFormer represent table structure in the JSON output?
- How are table headers, row headers, and body cells encoded for downstream consumption?
- What are the best practices for embedding **tables as structured data vs text flattening** when using Docling?
- How reliable is Docling for tables with merged cells or missing borders?
- How can Docling tables be indexed to support **cell-level retrieval** in RAG?

---

## 4. OCR & Scanned Documents

- When OCR is enabled, how are OCR-derived tokens distinguished from native PDF text?
- How does OCR affect retrieval accuracy and hallucination risk in RAG?
- What are the performance trade-offs of enabling OCR in large-scale ingestion pipelines?
- How does Docling handle mixed documents (partially scanned, partially digital)?

---

## 5. Performance & Scalability for Production RAG

- What configuration settings are most important when running Docling in **batch ingestion pipelines**?
- How does the choice of PDF backend affect downstream RAG quality?
- What are the memory and throughput implications when processing thousands of PDFs?
- How predictable is Docling’s runtime for heterogeneous document collections?
- How does Docling compare to cloud-based document parsers in cost–performance for RAG?

---

## 6. Extensibility & Custom RAG Enhancements

- How can a custom model pipeline be added to enrich documents with **domain-specific annotations**?
- Can Docling be extended to tag content for **retrieval intents** (e.g., definitions, methods, results)?
- How easy is it to integrate Docling with custom chunkers instead of quackling?
- What parts of the pipeline are most suitable for injecting **LLM-based post-processing**?

---

## 7. Evaluation & Failure Modes

- What are the most common failure cases of Docling that affect RAG answer quality?
- How does Docling behave when document metadata (title, authors) is missing or malformed?
- What quality regressions occur when switching from docling-parse to pypdfium?
- How can errors in layout detection propagate into retrieval mistakes?

---

## 8. Comparison & Positioning

- In which RAG scenarios does Docling outperform generic PDF loaders (e.g., LangChain loaders)?
- What types of documents should **not** be processed with Docling for RAG?
- How does Docling compare to multimodal VLM-based parsers for knowledge extraction?
- Why does Docling favor specialized models over end-to-end vision-language models for RAG?

---

## 9. Future-Proofing Your RAG System

- How will upcoming models (equation, code, figure classification) change RAG design?
- How might GPU acceleration affect ingestion pipeline architecture?
- How stable is the Docling output schema across versions for long-lived vector stores?

---
