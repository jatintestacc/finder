@echo off
REM Job Hunter - Streamlit UI Launcher (Windows)
REM Starts the Streamlit web interface for Job Hunter

echo.
echo ========================================
echo 🎯 Job Hunter - Streamlit UI
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

REM Create venv if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install/update requirements
echo Installing dependencies...
pip install -q -r requirements.txt

REM Check for .env file
if not exist ".env" (
    echo ⚠️  .env file not found
    echo Creating .env from .env.example...
    copy .env.example .env
    echo Please edit .env with your API key
    echo.
)

REM Launch Streamlit
echo.
echo 🚀 Launching Streamlit UI...
echo 📱 Open your browser to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run streamlit_app.py

pause
