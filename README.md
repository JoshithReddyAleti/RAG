# RAG
RAG Chatbot Implementation
This project implements a Retrieval-Augmented Generation (RAG) chatbot that processes text and image-based files (PDFs and text files), stores content in chunks with embeddings, retrieves relevant information for user queries, and provides precise citations (file name, page number, line number). It supports file-specific queries and general queries using a local AI model, designed for a secure Fiserv server environment with no external API dependencies.
Code Structure: XD_RAG.py
The main script (XD_RAG.py) contains the RAG logic. Below is an explanation of its key functions:
Imports and Initialization

Purpose: Imports libraries and initializes the embedding model, ChromaDB client, and text splitter.
Details:
Libraries: os, json, pathlib, dotenv for file operations, JSON storage, paths, and environment variables; pdfplumber for PDF text extraction; pytesseract and PIL for image text extraction; langchain.text_splitter for chunking; sentence_transformers for embeddings (all-MiniLM-L6-v2); chromadb for vector storage.
Initializes SentenceTransformer for embeddings, ChromaDB for storage in output/chroma_db, and RecursiveCharacterTextSplitter (500-char chunks, 50-char overlap).
Loads .env file (empty, as no API keys are needed).



extract_text_from_pdf

Purpose: Extracts text and metadata from PDFs, including text in images.
Details:
Uses pdfplumber to extract text per page, splitting into lines with metadata (file name, page, line number).
Uses pytesseract to extract text from images, marking metadata as image-<line_num>.
Returns text and metadata lists.
Error Handling: Catches exceptions (e.g., corrupt PDFs) and returns empty lists.



process_text_file

Purpose: Extracts text and metadata from text files.
Details:
Reads lines, storing non-empty lines with metadata (file name, page=1, line number).
Returns text and metadata lists.
Error Handling: Catches file read errors and returns empty lists.



process_file

Purpose: Processes a file (PDF or text) and chunks the text.
Details:
Calls extract_text_from_pdf or process_text_file based on file extension.
Chunks text using text_splitter (500 chars, 50-char overlap).
Maintains metadata for each chunk.
Returns chunks and metadata.
Error Handling: Catches general errors and returns empty lists.



store_chunks

Purpose: Saves chunks and metadata to JSON and ChromaDB.
Details:
Saves chunks to JSON files in chunks (e.g., testpdf.json).
Generates embeddings with SentenceTransformer and stores in ChromaDB with unique IDs.
Prints storage confirmation.
Error Handling: Catches errors during JSON writing or ChromaDB storage.



retrieve_chunks

Purpose: Retrieves top-k (default=3) relevant chunks for a query.
Details:
Encodes query with SentenceTransformer.
Queries ChromaDB for matching documents.
Returns documents and metadata.
Error Handling: Catches query errors and returns empty lists.



generate_response

Purpose: Generates a response with citations.
Details:
Uses retrieve_chunks to get relevant documents.
For file-specific queries with no results, returns "No information found."
For general queries with no results, provides a placeholder AI response.
Formats response and citations (source, page, line).
Error Handling: Catches errors and returns an error message.



process_uploaded_files

Purpose: Processes all files in the upload directory.
Details:
Iterates through files in upload (e.g., testAI.txt, testpdf.pdf).
Calls process_file and store_chunks for each file.
Creates chunks directory if needed.
Error Handling: Catches directory processing errors.



main

Purpose: Runs the RAG system via terminal.
Details:
Processes files with process_uploaded_files.
Accepts user queries in a loop, detecting file-specific queries (mentions file names).
Calls generate_response and prints response and citations.
Exits on 'quit' input.
Error Handling: Catches errors in the main loop.



File Enhancements
requirements.txt
Ensure the following libraries are included:

langchain
pdfplumber
pytesseract
pillow
sentence-transformers
chromadb
python-dotenv

.env

No changes needed, as no API keys are used (local models only).

ai.py

If it contains AI logic, integrate SentenceTransformer from XD_RAG.py or leave for future LLM integration (e.g., transformers with distilbert).

Chunks JSON Files

Files in chunks (e.g., testai.json, testpdf.json) are updated by XD_RAG.py with metadata (file, page, line). No manual changes needed.

output/chroma_db

Used for persistent embedding storage. Ensure write permissions on the server.

Output Markdown Files

Files in output (e.g., TestAI.md) can log responses. To enable logging, add to main:with open(fソー

Wrap

Run

Copy
with open(f"output/{Path(citation['source']).stem}.md", '

Wrap

Run

Copy
with open(f"output/{Path(citation['source']).stem}.md", 'a') as f:
    f.write(f"Query: {query}\nResponse: {response}\nCitations: {citations}\n\n")



Setup and Usage
Prerequisites

Install tesseract-ocr on the Fiserv server:apt-get install tesseract-ocr


Install dependencies:pip install -r requirements.txt


Ensure the upload directory contains files (e.g., testAI.txt, testpdf.pdf, xd_pdf_with_images.pdf).

Running the Application

Execute:python XD_RAG.py


The script processes files in upload, saves chunks to chunks/*.json, and embeddings to output/chroma_db.
Enter queries in the terminal:
File-specific: How to fix spark plugs in testpdf.pdf?
General: What are spark plugs?


To quit, enter quit.

Example Output

File-Specific Query:Input: How to fix spark plugs in testpdf.pdf?
Response:
- Replace spark plugs every 30,000 miles...
- Use a spark plug socket to remove...
Citations:
Source: testpdf.pdf, Page: 45, Line: 12
Source: testpdf.pdf, Page: 46, Line: 3


General Query:Input: What are spark plugs?
Response: Generated response for: What are spark plugs? (using local model, no external data)
Citation: Source: AI-generated, Page: None, Line: None



API Integration
To integrate with an existing UI, create a FastAPI endpoint:
from fastapi import FastAPI
app = FastAPI()

@app.get("/query")
async def query_rag(query: str, file_specific: bool = False):
    response, citations = generate_response(query, file_specific)
    return {"response": response, "citations": citations}

Why It Works

No Unused Imports: Removed unnecessary imports (e.g., numpy).
Error Handling: Try-except blocks ensure robustness.
Local Models: Uses all-MiniLM-L6-v2 for embeddings, suitable for secure environments.
Citations: Provides precise metadata (file, page, line).
File Support: Handles text and PDFs (text and image-based) with pdfplumber and pytesseract.
General Queries: Placeholder AI response, upgradable with a local LLM (e.g., distilbert).

Secure Environment Notes

Tesseract: Ensure tesseract-ocr is installed. If unavailable, remove image extraction or request server admin installation.
Permissions: Verify write access to output/chroma_db and chunks.
General Queries: Placeholder response can be enhanced with a local LLM if server resources allow.

Testing

Tested for functionality with dependencies installed.
Handles file processing, chunking, embedding, retrieval, and citation generation.
Supports terminal-based querying, ready for API integration.

For issues or enhancements, contact the developer or refer to the documentation of the libraries used.
