#!/bin/bash
echo "Installing DocSummarizer Backend..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    echo "Please install Python 3.10+ from https://www.python.org/"
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "To run the server:"
echo "  1. Make sure you're in the backend directory"
echo "  2. Run: python app.py"
echo ""
echo "The API will be available at: http://localhost:5000"
echo ""
