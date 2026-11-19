@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "VENV_DIR=%~dp0.venv"
set "REQ_FILE=%~dp0requirements.txt"
set "HASH_FILE=%VENV_DIR%\.requirements.sha256"

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creating local virtual environment in %VENV_DIR%...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo Error: Failed to create virtual environment. Ensure Python 3.10+ is on PATH.
        pause
        exit /b 1
    )
)

call "%VENV_DIR%\Scripts\activate.bat"

REM Hash-gated dependency installation (offline-safe once installed)
if exist "%REQ_FILE%" (
    for /f "usebackq delims=" %%H in (`python -c "import hashlib, pathlib; print(hashlib.sha256(pathlib.Path('requirements.txt').read_bytes()).hexdigest())"`) do set "REQ_HASH=%%H"
    set "OLD_HASH="
    if exist "%HASH_FILE%" set /p OLD_HASH=<"%HASH_FILE%"

    set "NEED_INSTALL=0"
    if not "!REQ_HASH!"=="!OLD_HASH!" set "NEED_INSTALL=1"
    python -c "import streamlit, pandas" >nul 2>&1
    if errorlevel 1 set "NEED_INSTALL=1"

    if "!NEED_INSTALL!"=="1" (
        echo Syncing dependencies from requirements.txt...
        python -m pip install -r "%REQ_FILE%"
        if errorlevel 1 (
            echo Error: Dependency installation failed.
            pause
            exit /b 1
        )
        >"%HASH_FILE%" echo !REQ_HASH!
    )
)

REM Probe for a free port starting at 8502
set "PORT="
for /f "usebackq delims=" %%P in (`python -c "import socket; f=lambda p: (lambda s: (s.connect_ex(('127.0.0.1',p)), s.close())[0])(socket.socket()); ports=[p for p in range(8502,8552) if f(p)!=0]; print(ports[0] if ports else '')"`) do set "PORT=%%P"
if "%PORT%"=="" (
    echo Error: No free port available in range 8502-8551.
    pause
    exit /b 1
)

echo Starting S&P 500 Arbitrage Web Application on http://localhost:%PORT% ...
start "" "http://localhost:%PORT%"
streamlit run app.py --server.port %PORT% --server.headless true
