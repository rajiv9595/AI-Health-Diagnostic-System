#!/bin/bash

echo "===================================="
echo "AI Health Diagnostic System"
echo "Quick Start Script"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Function to start backend
start_backend() {
    echo ""
    echo "Starting Backend Server..."
    cd backend
    source venv/bin/activate
    python app.py
}

# Function to start frontend
start_frontend() {
    echo ""
    echo "Starting Frontend Server..."
    cd frontend
    npm start
}

# Start backend in background
start_backend &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend in background
start_frontend &
FRONTEND_PID=$!

echo ""
echo "===================================="
echo "Services Started!"
echo "===================================="
echo ""
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait










