@echo off
title OROM TEXTILE Telegram Bot (24/7 Auto-Restart)
color 0A

echo ========================================================
echo   OROM TEXTILE TELEGRAM BOT - 24/7 AUTO RESTART SKRIPTI
echo ========================================================
echo.

:loop
echo [%date% %time%] Bot ishga tushirilmoqda...
py -3.12 main.py

echo.
echo [%date% %time%] OGOHLANTIRISH: Bot to'xtadi!
echo 5 soniyadan keyin avtomatik qayta ishga tushiriladi...
timeout /t 5 /nobreak >nul
echo.
goto loop
