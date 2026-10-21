# OROM TEXTILE Botni xavfsiz to'xtatish va qayta ishga tushirish skripti
Write-Host "Eski bot jarayonlari tekshirilmoqda..." -ForegroundColor Yellow

Get-Process -Name python, py -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*python*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

Write-Host "OROM TEXTILE Bot 24/7 rejimida ishga tushirilmoqda..." -ForegroundColor Green
py -3.12 main.py
