"""
patch_monitor_filtro_v4.py
Solução definitiva: oculta .sla-estourado via CSS puro no gerador.
Sem JS, sem botão, sem localStorage. 100% confiável.
"""
import paramiko, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh_key = os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa')
pkey = paramiko.RSAKey.from_private_key_file(ssh_key)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('187.77.240.87', port=22, username='root', pkey=pkey)

# Lê o arquivo atual
stdin, stdout, stderr = client.exec_command('cat /opt/painel_robo/src/gerar_tv_os.py')
src = stdout.read().decode('utf-8', errors='replace')
print(f'[OK] Lido: {len(src)} bytes')

changes = 0

# ── PATCH 1: Adiciona CSS que oculta cards fora do prazo ─────────────────────
# Âncora: logo após a animação do sla-estourado (linha 828)
OLD_PULSE = '  .danger.sla-estourado .timer-box {{ animation:pulse 1.5s infinite; }}'
NEW_PULSE = (
    '  .danger.sla-estourado .timer-box {{ animation:pulse 1.5s infinite; }}\n'
    '  /* FILTRO: oculta OS fora do prazo */\n'
    '  .os-card.sla-estourado {{ display:none !important; }}'
)

if OLD_PULSE in src:
    src = src.replace(OLD_PULSE, NEW_PULSE, 1)
    changes += 1
    print('[OK] PATCH 1 - CSS de ocultação adicionado')
else:
    print('[SKIP] PATCH 1 - âncora não encontrada, tentando alternativa...')
    # Tenta pelo .safe .timer-value
    if '.sla-estourado' in src and 'display:none' not in src:
        # Adiciona ao final do bloco de style, antes de </style>
        OLD_STYLE_END = '  @keyframes pulse'
        NEW_STYLE_END = (
            '  /* FILTRO: oculta OS fora do prazo */\n'
            '  .os-card.sla-estourado {{ display:none !important; }}\n'
            '  @keyframes pulse'
        )
        if OLD_STYLE_END in src:
            src = src.replace(OLD_STYLE_END, NEW_STYLE_END, 1)
            changes += 1
            print('[OK] PATCH 1b - CSS de ocultação adicionado (alternativa)')

# ── Salva no VPS ─────────────────────────────────────────────────────────────
if changes > 0:
    stdin2, stdout2, stderr2 = client.exec_command(
        'cat > /opt/painel_robo/src/gerar_tv_os.py'
    )
    stdin2.write(src.encode('utf-8'))
    stdin2.channel.shutdown_write()
    stdout2.read()
    print(f'[OK] Arquivo salvo ({len(src)} bytes)')
else:
    print('[AVISO] Nenhum patch aplicado!')

# ── Verifica sintaxe e roda ───────────────────────────────────────────────────
print('\n[...] Verificando sintaxe e gerando HTML...')
stdin3, stdout3, stderr3 = client.exec_command(
    'cd /opt/painel_robo/src && '
    'python3 -c "import py_compile; py_compile.compile(\'gerar_tv_os.py\', doraise=True); print(\'SINTAXE OK\')" 2>&1 && '
    'python3 gerar_tv_os.py 2>&1'
)
out = stdout3.read().decode('utf-8', errors='replace')
print(out[-800:] if len(out) > 800 else out)

client.close()
print('\n[CONCLUIDO]')
