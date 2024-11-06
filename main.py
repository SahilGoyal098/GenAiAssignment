from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.concurrency import run_in_threadpool
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
import chromadb
import os
import uuid
from utils import read_pdf, read_docx
import numpy as np

app = FastAPI()

# Initialize ChromaDB client without explicit Settings
chroma_client = chromadb.Client()

# Load Sentence Transformer model on CPU
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Create or get an existing ChromaDB collection
collection = chroma_client.get_or_create_collection("documents")

# Ensure temp_files directory exists
if not os.path.exists("./temp_files"):
    os.makedirs("./temp_files")

# Utility function to extract text from documents
async def extract_text(file: UploadFile) -> str:
    print(f"Saving file {file.filename} temporarily.")  # Log the file name
    temp_file_path = f"./temp_files/{file.filename}"
    
    # Save the file temporarily
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    try:
        # Extract text based on file type
        if file.content_type == "application/pdf":
            print(f"Extracting text from PDF: {file.filename}")
            text = read_pdf(temp_file_path)
        elif file.content_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            print(f"Extracting text from DOCX: {file.filename}")
            text = read_docx(temp_file_path)
        elif file.content_type == "text/plain":
            print(f"Extracting text from TXT: {file.filename}")
            with open(temp_file_path, "r", encoding="utf-8") as txt_file:
                text = txt_file.read()
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
    finally:
        # Clean up temporary file
        os.remove(temp_file_path)
        print(f"Temporary file {file.filename} deleted.")  # Log file deletion
    
    return text

# Endpoint to ingest documents
@app.post("/ingest/")
async def ingest_document(file: UploadFile = File(...)):
    print(f"Received file for ingestion: {file.filename}")
    text = await extract_text(file)
    print(f"Extracted text: {text[:200]}...")  # Log the first 200 characters of the text for confirmation
    
    # Split text into sections for more granular search results
    sections = [section.strip() for section in text.split("\n") if section.strip()]
    embeddings = await run_in_threadpool(lambda: [embedding_model.encode(section) for section in sections])

    # Create unique ids and add to collection
    ids = [str(uuid.uuid4()) for _ in sections]  # Generating unique UUIDs for each section
    
    # Adding each section to the ChromaDB collection
    for i, (embedding, section) in enumerate(zip(embeddings, sections)):
        collection.add(
            embeddings=[embedding],
            documents=[section],
            metadatas=[{"section": f"Section {i}", "type": file.content_type}],
            ids=[ids[i]]  # Use the corresponding unique ID
        )
        print(f"Section {i+1} added to ChromaDB with ID: {ids[i]}")
    
    return {"message": "Document ingested successfully"}

# Endpoint to query documents
class QueryRequest(BaseModel):
    query: str

@app.post("/query/")
async def query_documents(request: QueryRequest):
    print(f"Received query: {request.query}")  # Log the received query
    
    # Recompute the embedding for the query
    query_embedding = await run_in_threadpool(lambda: embedding_model.encode(request.query))
    print(f"Generated query embedding: {query_embedding[:5]}...")  # Log the query embedding

    # Query ChromaDB for similar documents
    results = collection.query(query_embeddings=[query_embedding], n_results=5)
    print(f"Query results: {results}")  # Log the results
    
    # Calculate similarity scores and filter by threshold
    similarity_threshold = 0.7  # Define a threshold for minimum relevance
    relevant_results = [
        {"document": doc, "similarity": sim[0]}  # Access the first element in each similarity list
        for doc, sim in zip(results["documents"], results["distances"])
        if sim[0] > similarity_threshold  # Compare the first similarity value to the threshold
    ]

    # Return filtered results or handle the case where no results are relevant
    if relevant_results:
        return {"results": relevant_results}
    else:
        return {"message": "No relevant results found"}



# To run this first run this uvicorn main:app --reload in your terminal then search this url http://127.0.0.1:8000/docs

