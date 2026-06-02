#!/bin/bash
# setup_cron_agenda_futura.sh
# Execute no VPS como root ou com sudo:
#   bash /opt/painel_robo/src/setup_cron_agenda_futura.sh
# ─────────────────────────────────────────────────────────────

SCRIPT="/opt/painel_robo/src/robo_agenda_futura.py"
PYTHON="/opt/painel_robo/venv/bin/python3"
LOG="/opt/painel_robo/src/log_agenda_futura.txt"
RAW_DIR="/opt/painel_robo/data/agenda_futura_raw"
CRON_JOB="0 5 * * * $PYTHON $SCRIPT >> $LOG 2>&1"

echo "=== Setup Robô Agenda Futura ==="

# 1. Cria pasta de dados brutos
mkdir -p "$RAW_DIR"
chmod 755 "$RAW_DIR"
echo "[OK] Pasta criada: $RAW_DIR"

# 2. Cria arquivo de log se não existir
touch "$LOG"
echo "[OK] Log: $LOG"

# 3. Instala dependências extras se necessário
if "$PYTHON" -c "import pyotp" 2>/dev/null; then
    echo "[OK] pyotp já instalado"
else
    echo "[...] Instalando pyotp..."
    "$PYTHON" -m pip install pyotp --quiet
fi

# 4. Adiciona cron job (se não existir ainda)
if crontab -l 2>/dev/null | grep -q "robo_agenda_futura"; then
    echo "[OK] Cron job já existe, pulando."
else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "[OK] Cron adicionado: $CRON_JOB"
fi

echo ""
echo "=== Cron jobs ativos ==="
crontab -l

echo ""
echo "=== Teste de sintaxe do robô ==="
"$PYTHON" -m py_compile "$SCRIPT" && echo "[OK] Sem erros de sintaxe" || echo "[ERRO] Verifique o script!"

echo ""
echo "✅ Setup concluído! O robô rodará todos os dias às 05:00 AM."
echo "   Para rodar agora manualmente:"
echo "   $PYTHON $SCRIPT"
