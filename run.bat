@echo off
title AI Express - Track 1
cd /d "%~dp0"
python main.py
if errorlevel 1 (
  echo.
  echo The program stopped because of an error.
  echo Copy the error above and send it to your team lead/ChatGPT.
  pause
)
