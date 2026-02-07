@echo off
echo ====================================
echo AI Health Diagnostic System
echo Quick Start Script
echo ====================================
echo.

:: Check if virtual environment exists
if not exist "backend\venv" (
    echo Creating virtual environment...
    cd backend
    python -m venv venv
    cd ..
)

:: Start backend
echo.
echo Starting Backend Server...
start "Backend - Flask API" cmd /k "cd backend && venv\Scripts\activate && python app.py"

:: Wait a bit for backend to start
timeout /t 5 /nobreak > nul

:: Start frontend
echo.
echo Starting Frontend Server...
start "Frontend - React" cmd /k "cd frontend && npm start"

echo.
echo ====================================
echo Services Starting...
echo ====================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit this window...
echo (The servers will continue running in separate windows)
pause > nul










