#!/bin/bash
# Quick start script for Phase 1 POC

set -e

echo "🚀 Starting Ignition SCADA Tag Bulk Uploader - Phase 1 POC"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  WARNING: .env has been created with default credentials!"
    echo "   You MUST edit .env and set proper credentials before deployment."
    echo "   Default credentials: admin/password (DO NOT USE IN PRODUCTION)"
    echo ""
    echo "   Edit .env now to configure Ignition Gateway connection"
    echo ""
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Starting FastAPI server..."
echo "API will be available at: http://localhost:8080"
echo "Interactive docs at: http://localhost:8080/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
