@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ===================================================
echo     OROM TEXTILE BOT HOLATINI TEKSHIRISH
echo ===================================================
echo.

tasklist /fi "imagename eq python.exe" 2>nul | findstr /i "python.exe" >nul
if "%ERRORLEVEL%"=="0" (
    echo [STATUS] Bot kompyuteringizda ISHLAYAPTI! (Aktiv)
) else (
    echo [STATUS] Bot hozir ISHLAMAYAPTI (To'xtagan).
    echo Uni ishga tushirish uchun "start_fon_rejimida.bat" ni bosing.
)

echo.
echo ---------------------------------------------------
echo Oxirgi qaydlar (logs/bot.log dan oxirgi 12 qator):
echo ---------------------------------------------------
powershell -Command "if (Test-Path logs\bot.log) { Get-Content logs\bot.log -Tail 12 } else { Write-Host 'Log fayli topilmadi.' }"
echo ---------------------------------------------------
echo.
pause
