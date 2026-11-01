@echo off
title Birthday Wisher setup
echo === Step 1: checking Python ===
python --version >nul 2>&1 || (echo Python is missing. Install it from python.org, tick "Add to PATH", then run this file again. & start https://www.python.org/downloads/ & pause & exit /b 1)
echo === Step 2: checking FFmpeg ===
ffmpeg -version >nul 2>&1 || (echo Installing FFmpeg... & winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements & echo FFmpeg installed. Close this window and run setup_windows.bat again so it is detected. & pause & exit /b 0)
echo === Step 3: creating environment and installing packages ===
if not exist venv python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt || (echo Package install failed & pause & exit /b 1)
echo === Step 4: settings file ===
if not exist .env copy .env.example .env >nul
echo Fill TELEGRAM_BOT_TOKEN and OWNER_TELEGRAM_CHAT_ID in the file that opens, save it, then close Notepad.
notepad .env
echo === Step 5: starting the app (Chrome will open) ===
python run.py
pause
