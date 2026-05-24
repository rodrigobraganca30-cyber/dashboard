#!/usr/bin/env python3
"""
patch_21h50.py - Aplica o bloco de ultima atualizacao (21:50) no robo_oracle.py do servidor.
Executar diretamente no servidor: python3 /tmp/patch_21h50.py
"""
import sys

ARQUIVO = '/opt/painel_robo/src/robo_oracle.py'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

# --- Bloco ANTIGO (exatamente como esta no servidor) ---
OLD = (
    '    HORA_INICIO = 7   # 07:00\n'
    '    HORA_FIM = 19     # 19:00\n'
    '    HORA_CONSOLIDACAO = 22  # 22:00 - horario para consolidar historico\n'
    '    consolidacao_feita = False\n'
    '    while True:\n'
    '        agora = datetime.datetime.now()\n'
    '        hora_atual = agora.hour\n'
    '\n'
    '        if hora_atual < HORA_INICIO or hora_atual >= HORA_FIM:\n'
    '            # Consolidacao diaria as 22h (uma vez por dia)\n'
    '            if hora_atual >= HORA_CONSOLIDACAO and not consolidacao_feita:'
)

# --- Bloco NOVO com a ultima atualizacao das 21:50 ---
NEW = (
    '    HORA_INICIO = 7    # 07:00 - inicio do expediente\n'
    '    HORA_FIM = 19      # 19:00 - fim do expediente normal\n'
    '    HORA_CONSOLIDACAO = 22   # 22:00 - horario para consolidar historico e rodar CDP\n'
    '    HORA_ULTIMA_ATV = 21     # 21:50 - ultima atualizacao antes da consolidacao\n'
    '    MINUTO_ULTIMA_ATV = 50\n'
    '    consolidacao_feita = False\n'
    '    ultima_atualizacao_feita = False\n'
    '    while True:\n'
    '        agora = datetime.datetime.now()\n'
    '        hora_atual = agora.hour\n'
    '        minuto_atual = agora.minute\n'
    '\n'
    '        if hora_atual < HORA_INICIO or hora_atual >= HORA_FIM:\n'
    '\n'
    '            # --- ULTIMA ATUALIZACAO: 21:50 ---\n'
    '            # Entra no Oracle uma ultima vez para garantir que O.S. concluidas\n'
    '            # apos as 19h estejam no historico antes da consolidacao das 22h.\n'
    '            if (hora_atual == HORA_ULTIMA_ATV and minuto_atual >= MINUTO_ULTIMA_ATV\n'
    '                    and not ultima_atualizacao_feita and not consolidacao_feita):\n'
    '                sep = "=" * 50\n'
    '                print(f"\\n{sep}")\n'
    '                print(f" [ULTIMA ATUALIZACAO] {agora.strftime(\'%d/%m/%Y %H:%M:%S\')}")\n'
    '                print(f" Buscando O.S. finalizadas apos as {HORA_FIM}h...")\n'
    '                print(f"{sep}")\n'
    '                try:\n'
    '                    main()\n'
    '                    print("  [ULTIMA ATUALIZACAO] Concluida com sucesso!")\n'
    '                except Exception as e:\n'
    '                    print(f"  [ULTIMA ATUALIZACAO] ERRO: {e}")\n'
    '                ultima_atualizacao_feita = True\n'
    '\n'
    '            # --- CONSOLIDACAO DIARIA: 22:00 ---\n'
    '            if hora_atual >= HORA_CONSOLIDACAO and not consolidacao_feita:'
)

# --- Patch 1: bloco principal ---
if OLD not in content:
    print('[ERRO] Bloco original nao encontrado no arquivo.')
    print('[INFO] Verifique se o arquivo do servidor bate com o esperado.')
    sys.exit(1)

content = content.replace(OLD, NEW, 1)

# --- Patch 2: reset da nova flag ao voltar ao expediente ---
OLD_RESET = (
    '        # Reseta a flag de consolidacao quando volta ao expediente\n'
    '        consolidacao_feita = False'
)
NEW_RESET = (
    '        # Reseta as flags quando volta ao expediente (novo dia)\n'
    '        consolidacao_feita = False\n'
    '        ultima_atualizacao_feita = False'
)

if OLD_RESET in content:
    content = content.replace(OLD_RESET, NEW_RESET, 1)
else:
    print('[AVISO] Bloco de reset nao encontrado, continuando sem ele...')

# --- Salva ---
with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(content)

print('[OK] Patch aplicado com sucesso!')
print(f'[OK] Arquivo salvo: {ARQUIVO}')
