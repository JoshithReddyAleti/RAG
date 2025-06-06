import os
import json
import pdfplumber
import pytesseract
from PIL import Image
import io
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize models and clients
embedder = SentenceTransformer('all-MiniLM-L6-v2')  # Local embedding model
chroma_client = chromadb.PersistentClient(path="./output/chroma_db")
collection = chroma_client.get_or_create_collection(name="rag_collection")

# Text splitter for chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
)

def extract_text_from_pdf(pdf_path):
    """Extract text and metadata from PDF, including image-based text."""
    texts = []
    metadata = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            # Extract text directly
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line_num, line in enumerate(lines, start=1):
                    if line.strip():
                        texts.append(line.strip())
                        metadata.append({
                            "file": os.path.basename(pdf_path),
                            "page": page_num,
                            "line": line_num
                        })
            
            # Extract text from images in the page
            for img in page.images:
                img_obj = page.images[img]
                img_data = img_obj['stream'].get_data()
                img_pil = Image.open(io.BytesIO(img_data))
                img_text = pytesseract.image_to_string(img_pil)
                if img_text.strip():
                    lines = img_text.split('\n')
                    for line_num, line in enumerate(lines, start=1):
                        if line.strip():
                            texts.append(line.strip())
                            metadata.append({
                                "file": os.path.basename(pdf_path),
                                "page": page_num,
                                "line": f"image-{line_num}"
                            })
    return texts, metadata

def process_text_file(file_path):
    """Extract text and metadata from text file."""
    texts = []
    metadata = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line_num, line in enumerate(lines, start=1):
            if line.strip():
                texts.append(line.strip())
                metadata.append({
                    "file": os.path.basename(file_path),
                    "page": 1,
                    "line": line_num
                })
    return texts, metadata

def process_file(file_path):
    """Process a file (PDF or text) and return chunks with metadata."""
    if file_path.endswith('.pdf'):
        texts, metadata = extract_text_from_pdf(file_path)
    elif file_path.endswith('.txt'):
        texts, metadata = process_text_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
    
    # Chunk the text
    chunks = []
    chunk_metadata = []
    for text, meta in zip(texts, metadata):
        split_texts = text_splitter.split_text(text)
        for split_text in split_texts:
            chunks.append(split_text)
            chunk_metadata.append(meta)
    
    return chunks, chunk_metadata

def store_chunks(chunks, metadata, json_path):
    """Store chunks and metadata in JSON and ChromaDB."""
    # Save to JSON
    data = [{"text": chunk, "metadata": meta} for chunk, meta in zip(chunks, metadata)]
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    # Generate embeddings and store in ChromaDB
    embeddings = embedder.encode(chunks)
    collection.add(
        documents=chunks,
        metadatas=metadata,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )

def retrieve_chunks(query, top_k=3):
    """Retrieve top_k relevant chunks for the query."""
    query_embedding = embedder.encode([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results['documents'][0], results['metadatas'][0]

def generate_response(query, is_file_specific=False):
    """Generate response for a query, with citations."""
    documents, metadatas = retrieve_chunks(query)
    
    if not documents:
        if is_file_specific:
            return "No relevant information found in the provided files.", []
        else:
            # Fallback to AI response for general queries
            response = f"Generated response for: {query} (using local model, no external data)"
            citations = [{"source": "AI-generated", "page": None, "line": None}]
            return response, citations
    
    # Construct response from retrieved documents
    response = "\n".join([f"- {doc}" for doc in documents])
    citations = [
        {"source": meta["file"], "page": meta["page"], "line": meta["line"]}
        for meta in metadatas
    ]
    
    return response, citations

def process_uploaded_files(upload_dir="./upload", chunk_dir="./chunks"):
    """Process all files in the upload directory."""
    os.makedirs(chunk_dir, exist_ok=True)
    for file_name in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, file_name)
        json_path = os.path.join(chunk_dir, f"{Path(file_name).stem}.json")
        chunks, metadata = process_file(file_path)
        store_chunks(chunks, metadata, json_path)
        print(f"Processed {file_name} and saved chunks to {json_path}")

def main():
    """Main function to process files and handle queries via terminal."""
    # Process all files in upload directory
    process_uploaded_files()
    
    while True:
        query = input("Enter your query (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        
        # Determine if query is file-specific (e.g., mentions a file name)
        is_file_specific = any(
            fname in query.lower() for fname in os.listdir("./upload")
        )
        
        response, citations = generate_response(query, is_file_specific)
        print("\nResponse:")
        print(response)
        print("\nCitations:")
        for citation in citations:
            print(f"Source: {citation['source']}, Page: {citation['page']}, Line: {citation['line']}")

if __name__ == "__main__":
    main()
