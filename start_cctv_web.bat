@echo off
setlocal
cd /d "%~dp0"

echo [CCTV Live Web Viewer] Starting...

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python was not found in PATH.
    echo Attempting to install Python via winget...
    winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements >nul 2>&1
    where python >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo Error: Python is not installed.
        echo Please download and install Python from https://www.python.org/
        pause
        exit /b 1
    )
)

if not exist "%~dp0bin\go2rtc.exe" (
    echo [Setup] go2rtc.exe not found. Downloading streaming engine...
    python -c "import urllib.request, zipfile, io; from pathlib import Path; p = Path(r'%~dp0bin'); p.mkdir(parents=True, exist_ok=True); u = 'https://github.com/AlexxIT/go2rtc/releases/download/v1.9.15/go2rtc_win64.zip'; r = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}); data = urllib.request.urlopen(r).read(); zipfile.ZipFile(io.BytesIO(data)).extractall(p); print('go2rtc engine ready!')"
)

echo Launching CCTV Web Server at http://localhost:5000 ...
python web_server.py
if %ERRORLEVEL% neq 0 (
    echo [Server Error] Process exited with error code %ERRORLEVEL%.
    pause
)
