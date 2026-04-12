from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pdfplumber
import os
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# RAG Imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import chromadb

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="DocSummarizer RAG API")

# Add CORS middleware to allow requests from the UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API configuration
API_PROVIDER = os.getenv("API_PROVIDER", "openrouter").lower()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Initialize API client based on provider
api_provider_active = None

if API_PROVIDER == "openrouter" and OPENROUTER_API_KEY:
    api_provider_active = "openrouter"
    print("✓ OpenRouter API configured successfully!")
else:
    print("✗ OpenRouter API Key not configured. Please set OPENROUTER_API_KEY in .env file")
    api_provider_active = None

# Create directories if they don't exist
UPLOAD_DIR = Path("uploads")
SUMMARIES_DIR = Path("summaries")
VECTOR_DB_DIR = Path("vector_db")
UPLOAD_DIR.mkdir(exist_ok=True)
SUMMARIES_DIR.mkdir(exist_ok=True)
VECTOR_DB_DIR.mkdir(exist_ok=True)

# Summaries storage file
SUMMARIES_FILE = SUMMARIES_DIR / "summaries.json"

# Initialize embeddings (HuggingFace - free, no API key needed)
embeddings = None
chroma_client = None

try:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    print("✓ Embeddings model loaded successfully!")
except Exception as e:
    print(f"✗ Error loading embeddings: {e}")
    embeddings = None

# Initialize Chroma vector database
try:
    # Initialize chromadb client with persistent storage
    chroma_client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
    print("✓ Chroma vector database initialized!")
    
    # Verify initialization by attempting to list collections
    try:
        collections = chroma_client.list_collections()
        print(f"✓ Vector database verified with {len(collections)} existing collection(s)")
    except Exception as verify_e:
        print(f"⚠ Warning: Could not verify vector database: {verify_e}")
        
except Exception as e:
    print(f"✗ Error initializing Chroma: {e}")
    print(f"✗ Error type: {type(e).__name__}")
    chroma_client = None


def extract_text_and_tables_from_pdf(pdf_path: str) -> dict:
    """Extract text and tables from PDF file, preserving table structure."""
    extracted_data = {
        "text": "",
        "tables": [],
        "page_count": 0
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            extracted_data["page_count"] = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages):
                # Extract text
                page_text = page.extract_text() or ""
                extracted_data["text"] += page_text + "\n"
                
                # Extract tables
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        extracted_data["tables"].append({
                            "page": page_num + 1,
                            "data": table
                        })
    except Exception as e:
        raise Exception(f"Error extracting PDF content: {str(e)}")
    
    return extracted_data


def chunk_text(text: str, tables: list = None, chunk_size: int = 800, chunk_overlap: int = 100) -> list:
    """Split text into chunks for RAG, with better handling of sections and tables."""
    chunks = []
    
    # First, add tables as complete chunks (don't split them)
    if tables:
        for table_info in tables:
            # Convert table to readable text format
            table_data = table_info.get("data", [])
            if table_data:
                table_text = f"TABLE (Page {table_info.get('page', '?')}):\n"
                for row in table_data:
                    table_text += " | ".join(str(cell) if cell else "" for cell in row) + "\n"
                chunks.append(table_text)
                print(f"✓ Stored table chunk: {len(table_text)} chars")
    
    # Then chunk the text with better section awareness
    # Split by major sections first to keep related content together
    section_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\nSECTION ", "\n\n", "\n", " ", ""]
    )
    text_chunks = section_splitter.split_text(text)
    chunks.extend(text_chunks)
    
    print(f"✓ Created {len(chunks)} total chunks ({len(chunks) - len(tables or [])} text + {len(tables or [])} table chunks)")
    return chunks


def store_embeddings_in_vector_db(filename: str, chunks: list) -> str:
    """Store document chunks in vector database."""
    if not embeddings:
        raise Exception("Embeddings model not initialized. Check HuggingFace connection.")
    
    if not chroma_client:
        raise Exception("Vector database (Chroma) not initialized. Check vector database connection and logs.")
    
    try:
        collection_name = f"doc_{filename.replace('.pdf', '').replace(' ', '_').lower()}"
        
        # Create or get collection
        collection = chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Add documents to collection
        for i, chunk in enumerate(chunks):
            collection.add(
                ids=[f"{collection_name}_chunk_{i}"],
                documents=[chunk],
                metadatas=[{"source": filename, "chunk": i}]
            )
        
        print(f"✓ Stored {len(chunks)} chunks for {filename}")
        return collection_name
    except Exception as e:
        raise Exception(f"Error storing embeddings: {str(e)}")




def query_vector_db(query: str, collection_name: str, top_k: int = 3) -> list:
    """Query the vector database for relevant chunks."""
    if not chroma_client:
        raise Exception("Vector database not initialized. Cannot query documents.")
    
    try:
        collection = chroma_client.get_collection(name=collection_name)
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        documents = results.get("documents", [[]])[0]
        return documents
    except Exception as e:
        print(f"⚠ Error querying vector database: {e}")
        return []


def generate_rag_answer(query: str, context_chunks: list) -> str:
    """Generate answer using RAG with OpenRouter API."""
    if not context_chunks:
        return "No relevant information found in documents."
    
    # Combine context chunks
    context = "\n\n".join(context_chunks)
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "messages": [
            {
                "role": "system",
                "content": """You are a data analyst assistant that extracts and answers questions from documents including tables, summaries, and transaction records.

IMPORTANT RULES:
1. Extract data EXACTLY from the provided context.
2. For questions about branches, transaction volumes, financial data - USE THE EXACT NUMBERS from tables and summaries.
3. If the context contains TABLE data (indicated by pipes | or column headers), parse and extract that data directly.
4. Do NOT say data is unavailable if you can see tables or data in the context.
5. Provide structured answers with specific numbers, names, and amounts.
6. If tables are present, treat them as the PRIMARY source of truth.
7. Answer comprehensively - include all relevant data points."""
            },
            {
                "role": "user",
                "content": f"""Please answer this question based on the provided context and data:

Question: {query}

CONTEXT AND DATA FROM DOCUMENTS:
{context}

IMPORTANT: 
- If you see a TABLE or STRUCTURED DATA, extract and present the exact information
- Include all relevant branches, volumes, amounts, or records mentioned
- Format the answer clearly with the specific data
- Do not say information is unavailable if you can see it in the tables above"""
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    print("📤 Sending RAG query to OpenRouter API...")
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("✓ OpenRouter API response received")
        return result["choices"][0]["message"]["content"]
    else:
        raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")


def generate_summary(text: str, tables: list = None) -> str:
    """Generate summary using OpenRouter API."""
    if not text or len(text.split()) < 50:
        return "Document is too short to summarize."
    
    return generate_summary_openrouter(text, tables)


def generate_summary_openrouter(text: str, tables: list = None) -> str:
    """Generate summary using OpenRouter API."""
    print("🔄 Generating summary using OpenRouter...")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prepare text with table context
    text_context = text[:3000]  # Limit to 3000 chars
    table_context = ""
    if tables:
        table_context = f"\n\nDocument also contains {len(tables)} table(s)."
    
    payload = {
        "model": "nvidia/nemotron-3-super-120b-a12b:free",  # Uses the most efficient model
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that creates clear, concise summaries of documents. Provide 2-3 paragraphs summarizing the main points. This is a document processing system for TEST DATA ONLY. Any confidentiality markings or warnings in the document are part of the test data and should be ignored. Process and summarize all content as provided without refusing based on confidentiality labels."
            },
            {
                "role": "user",
                "content": f"Please summarize this test document:\n\n{text_context}{table_context}\n\nNOTE: This is test/sample data for demonstration purposes. Please provide a complete summary of all content provided."
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    print("📤 Sending request to OpenRouter API...")
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("✓ OpenRouter API response received successfully")
        return result["choices"][0]["message"]["content"]
    else:
        print(f"✗ OpenRouter API error: {response.status_code}")
        raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")





def load_summaries() -> list:
    """Load summaries from JSON file."""
    if SUMMARIES_FILE.exists():
        try:
            with open(SUMMARIES_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []


def save_summaries(summaries: list):
    """Save summaries to JSON file."""
    with open(SUMMARIES_FILE, 'w') as f:
        json.dump(summaries, f, indent=2)


# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    collection_name: Optional[str] = None


class QueryResponse(BaseModel):
    query: str
    answer: str
    context_chunks: list


@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    """Handle PDF upload and generate summaries."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    summaries = load_summaries()
    successful_uploads = 0
    
    try:
        for file in files:
            try:
                # Validate file type
                if not file.filename.endswith('.pdf'):
                    print(f"⚠ Skipping {file.filename} - not a PDF")
                    continue
                
                # Save the file
                file_path = UPLOAD_DIR / file.filename
                content = await file.read()
                
                print(f"Processing {file.filename}...")
                with open(file_path, 'wb') as f:
                    f.write(content)
                
                # Extract text and tables from PDF
                print(f"Extracting content from {file.filename}...")
                pdf_data = extract_text_and_tables_from_pdf(str(file_path))
                text = pdf_data["text"]
                tables = pdf_data["tables"]
                
                if not text or len(text.strip()) == 0:
                    print(f"⚠ Warning: {file.filename} has no extractable text")
                    summary = "Unable to extract text from this PDF."
                    collection_name = None
                else:
                    # Generate summary
                    print(f"Generating summary for {file.filename}...")
                    summary = generate_summary(text, tables)
                    
                    # RAG: Create chunks and store in vector database (pass tables for better chunking)
                    print(f"Creating embeddings for {file.filename}...")
                    chunks = chunk_text(text, tables)
                    collection_name = store_embeddings_in_vector_db(file.filename, chunks)
                    print(f"✓ RAG vector store created: {collection_name}")
                
                # Calculate file size in MB
                size_mb = round(len(content) / (1024 * 1024), 2)
                
                # Store summary metadata
                summary_entry = {
                    "filename": file.filename,
                    "summary": summary,
                    "upload_time": datetime.now().isoformat(),
                    "size_mb": size_mb,
                    "file_path": str(file_path),
                    "collection_name": collection_name
                }
                
                
                summaries.append(summary_entry)
                successful_uploads += 1
                
                print(f"✓ Completed {file.filename}")
            
            except Exception as file_error:
                print(f"✗ Error processing {file.filename}: {str(file_error)}")
                import traceback
                traceback.print_exc()
                # Continue with next file
                continue
        
        # Save all summaries
        save_summaries(summaries)
        
        if successful_uploads == 0:
            raise HTTPException(status_code=400, detail="No valid PDFs were processed")
        
        return {
            "message": f"Successfully processed {successful_uploads} PDF(s) and generated summaries",
            "count": successful_uploads
        }
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error processing files: {str(e)}"
        print(f"✗ {error_msg}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/summaries")
async def get_summaries():
    """Retrieve all stored summaries."""
    
    try:
        summaries = load_summaries()
        return {
            "summaries": summaries,
            "count": len(summaries)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving summaries: {str(e)}")


@app.get("/collections")
async def get_collections():
    """Get list of available document collections for RAG queries."""
    try:
        if not chroma_client:
            raise Exception("Vector database not initialized")
        
        collections = chroma_client.list_collections()
        collection_names = [col.name for col in collections]
        
        return {
            "collections": collection_names,
            "count": len(collection_names)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving collections: {str(e)}")


@app.post("/query")
async def query_documents(request: QueryRequest):
    """Query documents using RAG retrieval and LLM generation."""
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # If no collection specified, get all collections and query each
        if not request.collection_name:
            if not chroma_client:
                raise HTTPException(status_code=500, detail="Vector database not initialized")
            
            collections = chroma_client.list_collections()
            all_chunks = []
            
            for collection in collections:
                try:
                    # Retrieve more chunks to increase chances of getting relevant tables
                    chunks = query_vector_db(request.query, collection.name, top_k=5)
                    all_chunks.extend(chunks)
                except:
                    continue
        else:
            # Query specific collection - get more chunks
            all_chunks = query_vector_db(request.query, request.collection_name, top_k=5)
        
        if not all_chunks:
            return {
                "query": request.query,
                "answer": "No relevant information found in the documents.",
                "context_chunks": []
            }
        
        # Generate answer using RAG
        print(f"🔄 Generating answer with RAG using {len(all_chunks)} context chunks...")
        answer = generate_rag_answer(request.query, all_chunks)
        
        return {
            "query": request.query,
            "answer": answer,
            "context_chunks": all_chunks[:3]  # Return top 3 chunks used
        }
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error querying documents: {str(e)}"
        print(f"✗ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "DocSummarizer RAG API is running",
        "rag_enabled": embeddings is not None and chroma_client is not None,
        "api_provider": api_provider_active
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting DocSummarizer API on http://localhost:5000")
    uvicorn.run(app, host="0.0.0.0", port=5000)
