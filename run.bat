@echo off
setlocal enabledelayedexpansion

echo ======================================================================
echo  Explainable Organizational Memory-Driven SCM Framework
echo  Team Members:
echo    1. YOGALAKSHMI S (23MIS0383)
echo    2. PAVITHRA L (23MIS0160)
echo    3. YUVARAJ G (24MIS0403)
echo ======================================================================
echo.

:: 1. Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your system PATH.
    echo Please install Python 3.10 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Python installation detected:
python --version
echo.

:: 2. Setup Virtual Environment if not present
if not exist "venv\Scripts\activate.bat" (
    echo [2/5] Creating Python virtual environment (venv)...
    python -m venv venv
    if errorlevel 1 (
        echo [WARNING] Could not create virtual environment. Using global Python.
        set "PY_CMD=python"
    ) else (
        echo Virtual environment created successfully.
        call venv\Scripts\activate.bat
        set "PY_CMD=python"
    )
) else (
    echo [2/5] Activating existing virtual environment...
    call venv\Scripts\activate.bat
    set "PY_CMD=python"
)
echo.

:: 3. Install/verify dependencies
echo [3/5] Verifying dependencies from requirements.txt...
%PY_CMD% -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [WARNING] Package installation had warnings. Continuing...
)
echo Dependencies verified.
echo.

:: 4. Initialize Database if not already seeded
echo [4/5] Checking SQLite database status...
if not exist "scm_framework.db" (
    echo Database not found. Initializing schema and seeding demonstration scenario...
    %PY_CMD% init_db.py
) else (
    echo Existing database detected (scm_framework.db). Preserving user data.
)
echo.

:: 5. Launch Application
echo [5/5] Starting Flask development server...
echo.
echo ======================================================================
echo  APPLICATION IS RUNNING!
echo  Open your web browser at:
echo      http://127.0.0.1:5000
echo.
echo  Demo Accounts:
echo    - Project Manager:        pm_user      (password123)
echo    - Configuration Manager:  cm_user      (password123)
echo    - Developer:              dev_user     (password123)
echo    - QA Engineer:            qa_user      (password123)
echo    - DevOps Engineer:        devops_user  (password123)
echo    - ML/Trust Analyst:       analyst_user (password123)
echo.
echo  Student Accounts:
echo    - YOGALAKSHMI S:          yogalakshmi  (password123)
echo    - PAVITHRA L:             pavithra     (password123)
echo    - YUVARAJ G:              yuvaraj      (password123)
echo ======================================================================
echo Press CTRL+C to terminate the application.
echo.

%PY_CMD% app.py

pause
