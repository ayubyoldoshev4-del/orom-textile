@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ===================================================
echo   OROM TEXTILE BOT - FON REJIMIDA ISHGA TUSHIRISH
echo ===================================================
echo.

:: Avval eski nusxalarini to'xtatamiz
taskkill /f /im python.exe /fi "WINDOWTITLE eq OROM_TEXTILE_RUNNER*" >nul 2>&1

:: VBS orqali qora oyna chiqmasdan butunlay yashirin ishga tushirish
start "" wscript.exe "%~dp0start_silent.vbs"

echo [OK] Bot orqa fonda (yashirin rejimda) muvaffaqiyatli ishga tushirildi!
echo.
echo Endi siz Antigravity'dan bemalol chiqib ketsangiz ham bot to'xtamaydi.
echo Kompyuteringiz yoniq ekan, u mustaqil ishlab turaveradi.
echo.
echo Bot holatini tekshirish uchun: tekshirish.bat faylini bosing.
echo Botni to'xtatish uchun: toxtatish.bat faylini bosing.
echo ===================================================
timeout /t 5
