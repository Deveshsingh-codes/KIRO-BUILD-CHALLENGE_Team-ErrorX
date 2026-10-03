#!/bin/bash

# Document Authenticity Verification System - Startup Script

echo "==============================================="
echo "Document Authenticity Verification System"
echo "==============================================="
echo ""

# Check if MongoDB is running
if ! mongosh --eval "db.version()" --quiet > /dev/null 2>&1; then
    echo "⚠️  MongoDB is not running!"
    echo "Starting MongoDB..."
    brew services start mongodb/brew/mongodb-community@8.0
    sleep 3
fi

echo "✓ MongoDB is running"
echo ""

# Start Backend
echo "Starting Backend (http://localhost:8000)..."
cd backend
source venv/bin/activate
python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

sleep 3

# Check if backend started successfully
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Backend is running (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start. Check backend.log"
    exit 1
fi

echo ""

# Start Frontend
echo "Starting Frontend (http://localhost:5173 or 5174)..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 3

echo "✓ Frontend is running (PID: $FRONTEND_PID)"
echo ""

echo "==============================================="
echo "Application Started Successfully!"
echo "==============================================="
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173 (or check frontend.log for actual port)"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Logs:"
echo "  Backend:  tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo "To stop:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "  or run: ./stop.sh"
echo ""

# Save PIDs for stop script
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid
