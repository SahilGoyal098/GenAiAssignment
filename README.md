# GenAiAssignment
# FastAPI Document Ingestion and Retrieval Server (RAG)

This project is a lightweight FastAPI server for document ingestion and retrieval using Retrieval-Augmented Generation (RAG) principles. The server uses ChromaDB for document storage and retrieval and `sentence-transformers/all-MiniLM-L6-v2` for embedding generation. The API supports the ingestion and querying of documents in PDF, DOC, DOCX, and TXT formats.

## Features

- **Document Ingestion**: Accepts PDF, DOC, DOCX, and TXT files for ingestion. Text is extracted, embedded, and stored in ChromaDB.
- **Querying**: Accepts queries, generates embeddings, and returns the most relevant document sections based on similarity.
- **Persistent Storage**: Uses ChromaDB’s persistent client to ensure data persistence between server restarts.
- **Efficient Concurrency Handling**: Leverages FastAPI’s asynchronous capabilities and thread pooling for CPU-bound tasks, ensuring non-blocking API endpoints.

## Requirements

- Python 3.8+
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/) (ASGI server for FastAPI)
- [Sentence-Transformers](https://www.sbert.net/) (`sentence-transformers/all-MiniLM-L6-v2`)
- [ChromaDB](https://www.trychroma.com/) for document storage and retrieval
- [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) (for PDF processing)
- [python-docx](https://python-docx.readthedocs.io/en/latest/) (for DOCX processing)

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/yourrepository.git
    cd yourrepository
    ```

2. **Install dependencies**:
    ```bash
    pip install fastapi uvicorn sentence-transformers chromadb pymupdf python-docx
    ```

3. **Set up ChromaDB with persistence (optional)**:
   If you need persistent storage, ensure ChromaDB is configured to use a persistent directory in `main.py`:

    ```python
    from chromadb.config import Settings
    chroma_client = chromadb.Client(Settings(persist_directory="./chroma_persist"))
    ```

## Running the Server

To start the server, run the following command:

```bash
uvicorn main:app --reload

Note: This setup provides a foundational way to implement an API server with FastAPI, integrate document storage using ChromaDB, and generate embeddings with sentence-transformers. The server will respond to queries by retrieving the closest document matches based on similarity scores, but results may not always be perfectly accurate or contextually correct. This example is intended to demonstrate an approach to setting up a RAG pipeline with FastAPI and can be customized and fine-tuned for improved performance in specific applications.
