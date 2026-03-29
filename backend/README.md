# DocSummarizer Backend

A FastAPI backend service that processes PDF documents and generates AI-powered summaries using OpenAI's GPT API.

## Features

- 📄 PDF text extraction using `pdfplumber`
- 🤖 AI summarization using OpenAI GPT-3.5-turbo
- 💾 Persistent storage of summaries in JSON
- 🚀 Fast API with CORS support for the frontend

## Requirements

- Python 3.10+
- FastAPI
- Uvicorn
- pdfplumber
- openai
- python-dotenv
- **OpenAI API Key** (from https://platform.openai.com/api-keys)

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```

## Running the Server

```bash
python app.py
```

The API will start on `http://localhost:5000`

## API Endpoints

### POST /upload
Upload PDF files and generate summaries.

**Request:**
- Content-Type: multipart/form-data
- Body: Files with key 'files'

**Response:**
```json
{
    "message": "Successfully processed X PDF(s) and generated summaries",
    "count": X
}
```

### GET /summaries
Retrieve all stored summaries.

**Response:**
```json
{
    "summaries": [
        {
            "filename": "document.pdf",
            "summary": "Summary text...",
            "upload_time": "2024-01-15T10:30:00",
            "size_mb": 1.25,
            "file_path": "uploads/document.pdf"
        }
    ],
    "count": 1
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
    "status": "ok",
    "message": "DocSummarizer API is running"
}
```

## Project Structure

```
backend/
├── app.py              # Main FastAPI application
├── requirements.txt    # Python dependencies
├── .env               # Your OpenAI API key
├── .env.example       # Example env file
├── setup.bat          # Windows setup script
├── uploads/           # Uploaded PDF files
├── summaries/         # Stored summaries (JSON)
└── README.md          # This file
```

## Notes

- Requires a valid OpenAI API key (paid account or trial credits)
- PDFs are stored in the `uploads/` directory
- Summaries are persisted in `summaries/summaries.json`
- Uses GPT-3.5-turbo for fast and cost-effective summarization
- Large PDFs are processed in chunks to handle token limits
