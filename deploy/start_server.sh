#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Deployment Script...${NC}"

# 1. Backend Setup
echo -e "${GREEN}📦 Setting up Backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Start Backend in background
echo "Starting FastAPI Backend..."
# Using nohup to keep it running after shell closes, or just & for session
# Adjust host/port if needed. env vars should be set in .env or exported before running script.
nohup python3 main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend running (PID: $BACKEND_PID)"

cd ..

# 2. Frontend Setup
echo -e "${GREEN}🎨 Setting up Frontend...${NC}"
cd frontend

# Install Node dependencies
echo "Installing Node dependencies..."
npm install

# Build Next.js
echo "Building Next.js app..."
npm run build

# Start Next.js
echo "Starting Next.js Frontend..."
nohup npm start > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend running (PID: $FRONTEND_PID)"

cd ..

echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Check backend/backend.log and frontend/frontend.log for output."
