#!/bin/bash

# Quick start script for Jobly development

set -e

echo "=================================="
echo "Jobly - Quick Start Setup"
echo "=================================="
echo ""

# Check if we're in the project root
if [ ! -d "apps/api" ] || [ ! -d "apps/web" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Backend setup
echo "Setting up Backend (FastAPI)..."
cd apps/api

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -q -r requirements.txt

echo "✓ Backend setup complete"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠ Warning: .env file not found in apps/api/"
    echo "  Copying from .env.example..."
    cp .env.example .env
    echo "  Please edit apps/api/.env with your MongoDB connection string"
fi

cd ../..

# Frontend setup
echo "Setting up Frontend (Next.js)..."
cd apps/web

if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
else
    echo "Node modules already installed"
fi

echo "✓ Frontend setup complete"
echo ""

# Check for .env.local file
if [ ! -f ".env.local" ]; then
    echo "⚠ Warning: .env.local file not found in apps/web/"
    echo "  Copying from .env.local.example..."
    cp .env.local.example .env.local
fi

cd ../..

echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd apps/api"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd apps/web"
echo "  npm run dev"
echo ""
echo "Then visit:"
echo "  - Frontend: http://localhost:3000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "To run tests:"
echo "  cd apps/api && source venv/bin/activate && pytest -v"
echo ""
