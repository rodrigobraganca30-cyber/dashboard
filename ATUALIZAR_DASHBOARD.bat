@echo off
title Atualizando Dashboard SVOBODA...
echo ===========================================
echo   ATUALIZANDO DASHBOARD E SUBINDO PARA WEB
echo ===========================================
echo.
python "C:\Users\SVOBODA\Desktop\DASHBOARD\gerar_dashboard_v2.py"
echo.
echo ===========================================
echo   PROCESSO CONCLUIDO! 
echo   O site https://svoboda.rtflowapp.com foi atualizado.
echo ===========================================
timeout /t 5
