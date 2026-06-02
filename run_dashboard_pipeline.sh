#!/bin/bash
# run_dashboard_pipeline.sh - Gera e injeta dashboard completo (22h diario)
LOG="/var/log/dashboard_pipeline.log"
DASH="/docker/dashboard"
echo "==============================" >> $LOG
echo "[$(date '+%Y-%m-%d %H:%M:%S')] INICIO" >> $LOG
cd $DASH
python3 gerar_dashboard_v2.py >> $LOG 2>&1 || { echo "[ERRO] gerar falhou" >> $LOG; exit 1; }
python3 injetar_auth.py >> $LOG 2>&1
python3 post_inject.py >> $LOG 2>&1
python3 injetar_templates.py >> $LOG 2>&1
python3 inject_estoque.py >> $LOG 2>&1
python3 injetar_melhorias.py >> $LOG 2>&1
echo "[$(date '+%H:%M:%S')] CONCLUIDO" >> $LOG
