#!/bin/bash
# Quick start script for Manim Web App

set -e

echo "=========================================="
echo "Tiny Manim Web App - Quick Start"
echo "=========================================="
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found"
    echo "Please create a .env file with your ANTHROPIC_API_KEY"
    echo "You can copy .env.example to .env and fill in your API key"
    echo ""
fi

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

echo "✓ Dependencies installed"
echo ""

echo "=========================================="
echo "Starting server..."
echo "=========================================="
echo ""
echo "Server will be available at: http://localhost:8000"
echo ""

python -m app.main
