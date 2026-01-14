#!/bin/bash
# Nunchi Dashboard Runner

echo "🚀 Starting Nunchi Analytics Dashboard..."
echo ""

# Check if dependencies are installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the dashboard
streamlit run app.py --server.port 8501 --server.headless true
