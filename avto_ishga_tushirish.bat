@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ===================================================
echo   WINDOWS YOQILGANDA AVTOMATIK ISHGA TUSHIRISH
echo ===================================================
echo.

set "TARGET=%~dp0start_silent.vbs"
set "SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\OromTextileBot.lnk"

powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%');$s.TargetPath='%TARGET%';$s.WorkingDirectory='%~dp0';$s.Save()"

if exist "%SHORTCUT%" (
    echo [MUVAFFAQIYATLI] Bot Windows avto-ishga tushirish (Startup) ro'yxatiga qo'shildi!
    echo.
    echo Endi har safar kompyuterni yoqqaningizda bot o'zi orqa fonda avtomatik ishga tushadi!
    echo Antigravity dasturini ochish ham shart emas.
) else (
    echo [XATOLIK] Avto-ishga tushirishga qo'shishda xatolik yuz berdi.
)

echo.
pause
