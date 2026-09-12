@echo off
REM ============================================
REM CropMind - Full Stack Startup Script (Windows)
REM Double-click this file to launch backend + frontend + browser
REM Place this file in the PROJECT ROOT (next to backend/ and frontend/)
REM ============================================

setlocal
cd /d "%~dp0"

echo ============================================
echo   CropMind - Starting full stack...
echo ============================================
echo.

REM ============================================
REM Step 1: Backend - create venv if missing
REM ============================================
if not exist "backend\venv" (
    echo [Backend] Creating Python virtual environment...
    python -m venv backend\venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv. Is Python installed and on PATH?
        pause
        exit /b 1
    )
)

REM ============================================
REM Step 2: Backend - install dependencies
REM ============================================
echo [Backend] Checking dependencies (this may take a few minutes on first run)...
call backend\venv\Scripts\activate.bat
pip install -r backend\requirements.txt --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo [ERROR] pip install failed. See the error above.
    call backend\venv\Scripts\deactivate.bat
    pause
    exit /b 1
)
call backend\venv\Scripts\deactivate.bat
echo [Backend] Dependencies OK.

REM ============================================
REM Step 3: Frontend - install dependencies if missing
REM ============================================
if not exist "frontend\node_modules" (
    echo [Frontend] Installing npm dependencies, first run, this may take a few minutes...
    pushd frontend
    call npm install
    popd
    if errorlevel 1 (
        echo [ERROR] npm install failed. Is Node.js installed and on PATH?
        pause
        exit /b 1
    )
)

REM ============================================
REM Step 4: Launch backend in its own window
REM   --app-dir backend adds backend/ to sys.path so "app.main:app" resolves,
REM   while the working directory stays at project root so that
REM   ml_models/... relative paths (used in model_registry.py) resolve too.
REM ============================================
echo [Backend] Launching FastAPI server on http://localhost:8000 ...
start "CropMind Backend" cmd /k "%~dp0run_backend.bat"

REM ============================================
REM Step 5: Launch frontend in its own window
REM ============================================
echo [Frontend] Launching Vite dev server on http://localhost:5173 ...
start "CropMind Frontend" cmd /k "%~dp0run_frontend.bat"

REM ============================================
REM Step 6: Wait for both servers to warm up, then open Chrome
REM ============================================
echo.
echo Waiting for servers to start...
timeout /t 8 /nobreak >nul

start chrome "http://localhost:5173"
if errorlevel 1 (
    echo [INFO] Could not launch Chrome directly, opening with default browser instead...
    start "" "http://localhost:5173"
)

echo.
echo ============================================
echo   CropMind is starting up in two windows:
echo   - Backend  (FastAPI) : http://localhost:8000/docs
echo   - Frontend (Vite)    : http://localhost:5173
echo   Close those windows to stop the servers.
echo ============================================
echo.
echo Press any key to close this window (the Backend and Frontend
echo windows will keep running separately).
pause >nul

endlocal