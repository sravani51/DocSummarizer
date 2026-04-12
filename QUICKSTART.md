# 🚀 Quick Start Guide

## Your DocSummarizer is now a RAG System!

### What Changed?
- ✅ **Before**: You could only summarize PDFs
- ✅ **Now**: You can summarize PDFs AND ask questions about them using RAG!

---

## Get Started in 3 Steps

### Step 1: Install Dependencies (2 minutes)
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Start the Backend (1 minute)
```bash
python app.py
```

**You should see:**
```
✓ OpenRouter API configured successfully!
✓ Embeddings model loaded successfully!
✓ Chroma vector database initialized!
Starting DocSummarizer API on http://localhost:5000
```

### Step 3: Open the UI (instantly)
Open `UI/file_upload.html` in your browser

---

## Try It Out!

### Test 1: Upload & Summarize
1. Click **📤 Upload** tab
2. Drag a PDF file or click to select
3. Click **Upload & Summarize**
4. Go to **📋 Summaries** to see the summary

### Test 2: Ask Questions (RAG!)
1. After uploading, click **❓ Ask Questions (RAG)** tab
2. Try one of these questions:
   - "What is this document about?"
   - "Summarize the main points"
   - "What are the key findings?"
3. Click **Send** and get an AI answer!

---

## Key Features

### 📄 Upload Documents
- Drag & drop or click to select
- Supports PDF files
- Auto-generates summaries

### 📋 View Summaries
- All documents listed with summaries
- Shows file size and collection info

### ❓ Ask Questions
- Query all documents or specific ones
- Get answers based on document content
- See the context chunks used

---

## Behind the Scenes

### What RAG Does:
1. **Chunks** your documents into pieces
2. **Creates embeddings** (numerical representations) of each chunk
3. **Stores** them in Chroma (local vector database)
4. **When you ask a question:**
   - Finds relevant chunks
   - Sends them to OpenRouter API
   - Gets back an AI-generated answer

### Why It's Better Than Just LLMs:
- ✅ Answers are based on YOUR actual documents
- ✅ No hallucinations (unless docs are wrong!)
- ✅ Cites the sources
- ✅ Much faster than re-reading documents manually

---

## What Are These New Files?

```
backend/
├── app.py              ← Updated with RAG logic
├── requirements.txt    ← Updated with RAG packages
└── vector_db/          ← NEW! Stores document embeddings
    └── (auto-created when you upload files)

UI/
└── file_upload.html    ← Updated with Query tab

RAG_GUIDE.md          ← Detailed documentation
QUICKSTART.md         ← This file!
```

---

## Troubleshooting

**Q: It says "Failed to connect to API"**
- Make sure `python app.py` is running
- Check it's running on `localhost:5000`

**Q: "No relevant information found"**
- Upload a PDF first
- Try asking about content that's actually in the PDF

**Q: Embeddings model is downloading**
- First run lots an embeddings model (~100MB)
- This is normal and one-time only

**Q: How do I clear all data?**
- Delete the `backend/vector_db/` folder
- Delete `backend/summaries/summaries.json`
- Restart and re-upload files

---

## Next Steps

1. ✅ Try uploading a PDF and asking questions
2. ✅ Read [RAG_GUIDE.md](./RAG_GUIDE.md) for detailed docs
3. ✅ Experiment with different question types
4. ✅ Upload multiple documents and query them together

---

## Architecture

```
┌─────────────────────────┐
│   Your Browser (UI)     │
└────────────┬────────────┘
             │ HTTP
┌────────────┼────────────┐
│   FastAPI Server        │
│  - PDF extraction       │
│  - Embeddings creation  │
│  - RAG queries          │
└────────────┼────────────┘
             │
     ┌───────┴──────┐
     │ OpenRouter   │  ← For LLM summarization & QA
     │ (Cloud API)  │
     └──────────────┘
     
     ┌───────────────┐
     │ Chroma VectorDB│  ← Local file storage
     │ (vector_db/)  │
     └───────────────┘
```

---

## Common Questions

**Q: Do I need to pay for embeddings?**
- No! Using HuggingFace's free model

**Q: Do I need to pay for the vector database?**
- No! Chroma is open-source and free

**Q: What do I pay for?**
- Only the OpenRouter API calls (summaries & answers)

**Q: Can I use different LLMs?**
- Yes! Change the `model` in `app.py`

**Q: How many documents can I upload?**
- As many as your disk space allows!

---

## Happy RAG-ing! 🤖

Questions? Check [RAG_GUIDE.md](./RAG_GUIDE.md) for detailed documentation.

**Created**: April 11, 2026
**System**: DocSummarizer RAG
