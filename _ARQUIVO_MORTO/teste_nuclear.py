#!/usr/bin/env python3
"""
Teste nuclear: substitui o onclick do botão Disparo por alert direto
para confirmar se onclick funciona de alguma forma.
Também adiciona alert no início de showWaSub.
"""
ARQUIVO = '/docker/dashboard/html/index.html'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# 1. Troca o botão Disparo para um alert PURO (sem chamar função)
OLD_BTN = "    <div class=\"wa-tab\" onclick=\"showWaSub('wa-disparo',this)\">🚀 Disparo</div>"
NEW_BTN = "    <div class=\"wa-tab\" onclick=\"alert('ONCLICK FUNCIONOU! JS ativo.')\">🚀 Disparo</div>"

if OLD_BTN in content:
    content = content.replace(OLD_BTN, NEW_BTN, 1)
    changes += 1
    print('[OK] Botão Disparo com alert puro')
else:
    print('[ERRO] Botão Disparo não encontrado!')

# 2. Adiciona alerta imediato no início de showWaSub (antes do try)
OLD_FUNC = "  function showWaSub(id,btn){\n    try {"
NEW_FUNC = "  function showWaSub(id,btn){\n    alert('showWaSub chamado: ' + id);\n    try {"

if OLD_FUNC in content:
    content = content.replace(OLD_FUNC, NEW_FUNC, 1)
    changes += 1
    print('[OK] Alert no início de showWaSub')

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'[DONE] {changes} mudancas')
print('Instrução: Ctrl+Shift+R e clicar "Disparo"')
print('- Se aparecer "ONCLICK FUNCIONOU" → onclick funciona mas showWaSub falha')
print('- Se não aparecer NADA → onclick está sendo bloqueado antes de executar')
