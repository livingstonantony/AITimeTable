@echo off
REM AI TimeTable System - Setup Script for Windows

echo.
echo ====================================
echo 🎓 AI TimeTable System - Setup
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org
    pause
    exit /b 1
)

echo ✅ Python is installed
python --version
echo.

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

echo.

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

echo.

REM Install dependencies
echo 📚 Installing dependencies from requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ✅ Installation complete!
echo.
echo 🚀 To run the application, use:
echo    venv\Scripts\activate
echo    streamlit run app.py
echo.
pause
