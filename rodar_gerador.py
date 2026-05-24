#!/usr/bin/env python3
"""
1. Adiciona chamada ao post_inject.py no robo_oracle.py após o gerador
2. Roda o gerador agora + post_inject
"""
import subprocess, sys

ORACLE = '/opt/painel_robo/src/robo_oracle.py'
GERADOR = '/docker/dashboard/gerar_dashboard_v2.py'
POST = '/docker/dashboard/post_inject.py'

# ── 1. Patch robo_oracle.py para chamar post_inject após o gerador ─────────
with open(ORACLE, 'r', encoding='utf-8') as f:
    src = f.read()

OLD = (
    '                    resultado = subprocess.run([python_exe, script_dash], capture_output=True, text=True)\n'
    '                    if resultado.returncode == 0:\n'
    '                        print("  [DASHBOARD] Atualizado com sucesso no servidor!")\n'
    '                    else:\n'
    '                        print(f"  [DASHBOARD] ERRO ao atualizar: {resultado.stderr}")'
)

NEW = (
    '                    resultado = subprocess.run([python_exe, script_dash], capture_output=True, text=True)\n'
    '                    if resultado.returncode == 0:\n'
    '                        print("  [DASHBOARD] Atualizado com sucesso no servidor!")\n'
    '                        # Aplica patches (tabs, mapeamento de planilhas, etc.)\n'
    '                        script_pi = "/docker/dashboard/post_inject.py"\n'
    '                        import os as _os\n'
    '                        if _os.path.exists(script_pi):\n'
    '                            res_pi = subprocess.run([python_exe, script_pi], capture_output=True, text=True)\n'
    '                            if res_pi.returncode == 0:\n'
    '                                print("  [POST-INJECT] Patches aplicados com sucesso!")\n'
    '                            else:\n'
    '                                print(f"  [POST-INJECT] AVISO: {res_pi.stderr[:200]}")\n'
    '                    else:\n'
    '                        print(f"  [DASHBOARD] ERRO ao atualizar: {resultado.stderr}")'
)

if OLD in src:
    src = src.replace(OLD, NEW, 1)
    with open(ORACLE, 'w', encoding='utf-8') as f:
        f.write(src)
    print('[OK] robo_oracle.py: post_inject.py adicionado após gerador')
elif 'post_inject' in src:
    print('[OK] post_inject já presente no robo_oracle.py')
else:
    print('[AVISO] Anchor não encontrado no robo_oracle.py — patch manual necessário')

# ── 2. Roda o gerador agora ────────────────────────────────────────────────
print('\n[RUN] Rodando gerar_dashboard_v2.py...')
r1 = subprocess.run([sys.executable, GERADOR], capture_output=True, text=True)
if r1.returncode == 0:
    print('[OK] Gerador concluído!')
    print(r1.stdout[-500:] if r1.stdout else '')
else:
    print('[ERRO] Gerador falhou:')
    print(r1.stderr[-500:])

# ── 3. Roda post_inject ────────────────────────────────────────────────────
print('\n[RUN] Rodando post_inject.py...')
r2 = subprocess.run([sys.executable, POST], capture_output=True, text=True)
print(r2.stdout)
if r2.returncode != 0:
    print('[ERRO]', r2.stderr[-300:])
