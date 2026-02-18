#!/bin/bash

# GPT-OSS Chat Interface Launcher Script

echo "🤖 Starting GPT-OSS 20B Chat Interface"
echo "======================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python -c "import gradio, requests, tiktoken, json" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
fi

# Start the application
echo "🚀 Launching application..."
echo "   - Open your browser to: http://localhost:7860"
echo "   - Press Ctrl+C to stop the server"
echo ""

python main.py