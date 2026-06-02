@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════╗
echo ║   BACKUP COMPLETO SVOBODA               ║
echo ║   Local + VPS em um clique               ║
echo ╚══════════════════════════════════════════╝
echo.
python "%~dp0backup_completo.py"
echo.
pause
