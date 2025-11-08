from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.chunking.recursive import RecursiveChunking

# Read the PDF file
pdf_reader = PDFReader(
    chunking=RecursiveChunking(
        chunk_size=500,
        overlap=200
    )
)
documents = pdf_reader.read(r"E:\NLP Learning\NLP-Learning\agno-rag-agent\data\Resume_Muhammad Cikal Merdeka_AI.pdf")

print(documents)