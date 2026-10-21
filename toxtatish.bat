@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ===================================================
echo     OROM TEXTILE BOTNI TO'XTATISH
echo ===================================================
echo.

echo Bot jarayonlari qidirilmoqda...
taskkill /f /im python.exe /fi "WINDOWTITLE eq OROM_TEXTILE_RUNNER*" >nul 2>&1
wmic process where "name='python.exe' and CommandLine like '%%main.py%%'" call terminate >nul 2>&1
wmic process where "name='cmd.exe' and CommandLine like '%%run_hidden.bat%%'" call terminate >nul 2>&1

echo [OK] Bot to'xtatildi!
echo.
pause
