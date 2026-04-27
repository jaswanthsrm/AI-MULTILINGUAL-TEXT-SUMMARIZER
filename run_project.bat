@echo off
echo =======================================================
echo    🚀 AI Multilingual Text Summarizer Setup
echo =======================================================
echo.

echo [1/3] Checking for Python Virtual Environment...
IF NOT EXIST "venv" (
    echo       - Creating a new isolated environment venv...
    python -m venv venv
)

echo [2/3] Activating environment...
call venv\Scripts\activate

echo [3/3] Installing Dependencies...
echo       - Checking requirements.txt (This might take a moment the first time)
pip install -q -r requirements.txt

echo.
echo =======================================================
echo    🌐 Starting the App in your Web Browser...
echo =======================================================
echo.

streamlit run app.py

pause
