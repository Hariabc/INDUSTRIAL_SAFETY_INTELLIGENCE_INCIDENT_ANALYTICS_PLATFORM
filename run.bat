@echo off
setlocal enabledelayedexpansion

echo ===============================================================================
echo   INDUSTRIAL SAFETY INTELLIGENCE & INCIDENT ANALYTICS PLATFORM
echo   Technical Evaluation Submission for YottaFlex.ai
echo ===============================================================================
echo.

:: Check for Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.11+.
    pause
    exit /b 1
)

:: Check for Node.js
node --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH. Please install Node.js 18+.
    pause
    exit /b 1
)

echo [1/4] Checking Python Virtual Environment...
if exist "venv\Scripts\activate.bat" (
    echo Virtual environment found at .\venv
) else (
    echo Creating virtual environment at .\venv...
    python -m venv venv
    call .\venv\Scripts\activate.bat
    pip install -r requirements.txt
)

echo [2/4] Verifying Database and Seed Data...
if not exist "industrial_safety.db" (
    echo Initializing database schema with Alembic...
    call .\venv\Scripts\alembic -c backend\alembic.ini upgrade head
    echo Generating 50,000 synthetic events and seeding database...
    call .\venv\Scripts\python -m generator.generate --seed 20261022 --load-db
) else (
    echo Database industrial_safety.db verified.
)

echo [3/4] Starting FastAPI Backend on http://localhost:8000 ...
start "Industrial Safety API Backend" cmd /k ".\venv\Scripts\uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [4/4] Starting React Frontend on http://localhost:5173 ...
cd frontend
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)
start "Industrial Safety React Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ===============================================================================
echo   SERVICES STARTED SUCCESSFULLY!
echo   - Frontend UI:        http://localhost:5173
echo   - Backend Swagger:    http://localhost:8000/docs
echo   - Health Check API:   http://localhost:8000/api/health
echo ===============================================================================
echo Press any key to open the dashboard in your default browser...
pause >nul
start http://localhost:5173
