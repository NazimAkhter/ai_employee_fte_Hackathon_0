@echo off
REM Kill any existing Chrome/Chromium processes
taskkill /F /IM chrome.exe 2>nul
taskkill /F /IM chromium.exe 2>nul
taskkill /F /IM msedge.exe 2>nul

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Run the LinkedIn poster
python linkedin_poster.py %1 %2 %3
