@echo off
cd /d "%~dp0"
title OROM_TEXTILE_RUNNER

:loop
py -3.12 main.py
if errorlevel 1 (
    python main.py
)
timeout /t 5 /nobreak >nul
goto loop
