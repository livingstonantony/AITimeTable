#!/bin/bash

echo "🎓 AI TimeTable System - Setup Script"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python is installed"
python3 --version
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

echo ""

# Install dependencies
echo "📚 Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 To run the application, use:"
echo "   source venv/bin/activate  (if not already active)"
echo "   streamlit run app.py"
echo ""
