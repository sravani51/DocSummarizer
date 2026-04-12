#!/usr/bin/env python3
"""Reset vector database to prepare for fresh indexing with improved RAG chunks."""

import shutil
from pathlib import Path

VECTOR_DB_DIR = Path("vector_db")

try:
    if VECTOR_DB_DIR.exists():
        shutil.rmtree(VECTOR_DB_DIR)
        print("✓ Old vector database deleted")
    
    VECTOR_DB_DIR.mkdir(exist_ok=True)
    print("✓ Vector database directory ready for fresh indexing")
    print("\nNow:")
    print("1. Restart the backend: python app.py")
    print("2. Re-upload the PDF in the UI")
    print("3. The PDF will be indexed with improved chunking strategy")
    print("4. Try your query again - it should now work!")
    
except Exception as e:
    print(f"✗ Error: {e}")
