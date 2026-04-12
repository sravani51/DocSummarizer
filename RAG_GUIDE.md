# 🤖 DocSummarizer RAG System Guide

## What is RAG?

**Retrieval-Augmented Generation (RAG)** is an AI technique that:
1. **Retrieves** relevant information from your documents using vector embeddings
2. **Augments** the AI model with that context
3. **Generates** accurate answers based on your document content

## New Features

### ✨ Features Added

1. **📄 Document Summarization** (Original)
   - Upload PDFs and get AI-powered summaries
   - Summaries stored with metadata

2. **❓ RAG Query System** (NEW!)
   - Ask questions about your uploaded documents
   - Get answers based on relevant document chunks
   - Query specific documents or all documents at once
   - Shows context sources used for the answer

3. **🗂️ Vector Database**
   - Automatic document chunking
   - Embeddings created using HuggingFace's all-MiniLM-L6-v2 model
   - Persistent storage in Chroma vector database
   - No additional API keys needed for embeddings

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**New packages added:**
- `langchain` - RAG orchestration
- `langchain-community` - Community integrations
- `chromadb` - Vector database (open-source, free)
- `sentence-transformers` - Embeddings (HuggingFace)

### 2. Environment Setup

Create a `.env` file in the `backend` directory:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
API_PROVIDER=openrouter
```

### 3. Run the Backend

```bash
cd backend
python app.py
```

Expected output:
```
✓ OpenRouter API configured successfully!
✓ Embeddings model loaded successfully!
✓ Chroma vector database initialized!
Starting DocSummarizer API on http://localhost:5000
```

### 4. Open the UI

Navigate to `UI/file_upload.html` in your browser (or serve it via a simple HTTP server)

## How to Use

### Upload Documents

1. Go to **📤 Upload** tab
2. Drag & drop or click to select PDF files
3. Click **Upload & Summarize**
4. The backend will:
   - Extract text from PDFs
   - Generate AI summaries
   - Create text chunks
   - Generate embeddings for each chunk
   - Store in Chroma vector database

### View Summaries

1. Go to **📋 Summaries** tab
2. See all uploaded documents with their summaries
3. Metadata includes file size and collection name

### Ask Questions (RAG)

1. Go to **❓ Ask Questions** tab
2. (Optional) Select a specific document from the dropdown
3. Type your question about the documents
4. Click **Send** or press Enter
5. The system will:
   - Retrieve relevant document chunks
   - Generate an answer using those chunks
   - Show the context used

## System Architecture

```
┌─────────────────────────────────────────┐
│          Web UI (HTML/CSS/JS)           │
└────────────────┬────────────────────────┘
                 │ HTTP
┌────────────────┼────────────────────────┐
│         FastAPI Backend (Python)        │
├──────────┬──────────┬──────────┬────────┤
│ PDF      │ Text     │ Embeddings│ OpenRouter│
│ Extractor│ Chunker  │ (HF)     │ API    │
└──────────┼──────────┼──────────┴────────┘
           │
      ┌────┴──────┐
      │   Chroma   │
      │  Vector DB │
      │ (Persistent)
      └────────────┘
```

## API Endpoints

### Upload Documents
```
POST /upload
- Accepts multiple PDF files
- Extracts text and tables
- Generates AI summaries
- Creates embeddings and stores in vector DB
- Returns: { message, count, summaries_with_collection_names }
```

### Get Summaries
```
GET /summaries
- Returns all uploaded documents with summaries
- Includes collection names for RAG querying
```

### Get Available Collections
```
GET /collections
- Returns list of all document collections in vector DB
- Used to populate dropdown in query UI
```

### Query Documents (RAG)
```
POST /query
- Body: { "query": "Your question", "collection_name": "optional" }
- Retrieves relevant chunks from vector DB
- Generates answer using OpenRouter API
- Returns: { query, answer, context_chunks }
```

### Health Check
```
GET /health
- Returns: { status, message, rag_enabled, api_provider }
```

## Vector Database Details

### Chroma
- **Type**: Persistent vector database
- **Location**: `vector_db/` folder
- **Capacity**: Unlimited (scalable)
- **Access**: Open-source, free to use
- **Collections**: One per uploaded document

### Embeddings
- **Model**: `all-MiniLM-L6-v2` (HuggingFace)
- **Dimensions**: 384-dimensional vectors
- **Speed**: Fast, CPU-friendly
- **Cost**: FREE (no API key needed!)

### Chunking Strategy
- **Chunk Size**: 500 characters
- **Overlap**: 50 characters
- **Separator**: Preserves structure (paragraphs > sentences > words)

## Troubleshooting

### Issue: "Vector database not initialized"
- Check if embeddings loaded: Look for "✓ Embeddings model loaded" in logs
- Try reinstalling: `pip install sentence-transformers --upgrade`

### Issue: "No API key configured"
- Ensure `.env` file exists in `backend/` directory
- Check: `OPENROUTER_API_KEY=your_key_here`

### Issue: Query returns "No relevant information"
- Upload more documents
- Try rephrasing your question
- Ask about content that's actually in the documents

### Issue: Upload is slow
- First upload may load embeddings model (~100MB)
- Subsequent uploads are faster
- Large PDFs take longer to process

## What's Next?

### Potential Enhancements
1. **Different Embedding Models** - Try larger models for better accuracy
2. **Hybrid Search** - Combine keyword and semantic search
3. **Answer Confidence Scores** - Show how confident the answer is
4. **Document Citations** - Show which documents the answer came from
5. **Multi-language Support** - Support PDFs in different languages
6. **Filtering** - Query by date range, document type, etc.

## Performance Tips

1. **Batch Uploads** - Upload multiple documents at once
2. **Document Size** - Optimal PDFs are 10-100 pages
3. **Query Specificity** - More specific questions get better answers
4. **Collection Selection** - Querying one collection is faster than all

## Terminology

- **Embedding**: A numerical representation of text (384 numbers for our model)
- **Vector DB**: Database that stores and searches embeddings
- **Chunk**: A piece of the document (usually a few sentences)
- **Collection**: All chunks from one document, grouped together
- **Retrieval**: Finding relevant chunks for a query
- **Augmentation**: Adding retrieved content to the LLM prompt
- **Generation**: AI model creating the final answer

## Architecture Benefits

✅ **Fast** - Vector DB queries are sub-millisecond  
✅ **Accurate** - AI answers based on your actual documents  
✅ **Scalable** - Can handle hundreds of documents  
✅ **Free** - No embedding API costs  
✅ **Persistent** - Data saved between sessions  
✅ **Privacy** - Vector DB runs locally  

---

**Created**: 2026-04-11  
**System**: DocSummarizer with RAG
