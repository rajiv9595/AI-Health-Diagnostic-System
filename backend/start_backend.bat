@echo off
cd /d "%~dp0"
echo Activating virtual environment...
call ..\venv\Scripts\activate.bat

echo Starting backend server...
python app.py

pause










