#!/usr/bin/env python3
"""
Fix definitivo: inline o tab-switching diretamente nos onclick dos botões.
Não depende de showWaSub estar definida — funciona sempre que onclick funciona.
"""
ARQUIVO = '/docker/dashboard/html/index.html'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

# Snippet inline reutilizável para troca de tab
def make_onclick(target_id):
    return (
        "document.querySelectorAll('.wa-sub').forEach(function(s){s.style.display='none'});"
        "document.querySelectorAll('.wa-tab').forEach(function(b){b.classList.remove('active')});"
        f"var t=document.getElementById('{target_id}');if(t){{t.style.display='block'}};"
        "this.classList.add('active');"
        f"if(typeof showWaSub==='function')showWaSub('{target_id}',null);"
    )

changes = 0

# Restaura botão Disparo (foi trocado pelo teste nuclear)
OLD_DISPARO = "    <div class=\"wa-tab\" onclick=\"alert('ONCLICK FUNCIONOU! JS ativo.')\">🚀 Disparo</div>"
NEW_DISPARO = f"    <div class=\"wa-tab\" onclick=\"{make_onclick('wa-disparo')}\">🚀 Disparo</div>"

if OLD_DISPARO in content:
    content = content.replace(OLD_DISPARO, NEW_DISPARO, 1)
    changes += 1
    print('[OK] Botão Disparo restaurado com inline onclick')

# Substitui todos os wa-tab onclicks por inline
tabs = {
    "onclick=\"showWaSub('wa-painel',this)\"": f"onclick=\"{make_onclick('wa-painel')}\"",
    "onclick=\"showWaSub('wa-config',this)\"": f"onclick=\"{make_onclick('wa-config')}\"",
    "onclick=\"showWaSub('wa-chat',this)\"":   f"onclick=\"{make_onclick('wa-chat')}\"",
}

for old, new in tabs.items():
    if old in content:
        content = content.replace(old, new, 1)
        changes += 1
        print(f'[OK] {old[:40]} → inline')
    else:
        print(f'[AVISO] Nao encontrado: {old[:40]}')

# Remove debug alert do início de showWaSub
OLD_SHOW = "  function showWaSub(id,btn){\n    alert('showWaSub chamado: ' + id);\n    try {"
NEW_SHOW = "  function showWaSub(id,btn){\n    try {"

if OLD_SHOW in content:
    content = content.replace(OLD_SHOW, NEW_SHOW, 1)
    changes += 1
    print('[OK] Alert de debug removido de showWaSub')

# Remove diagnóstico de cliques
OLD_DIAG = "\n  // === DIAGNÓSTICO DE CLIQUES ===\n"
if OLD_DIAG in content:
    # Encontra fim do bloco de diagnóstico
    start = content.find(OLD_DIAG)
    end = content.find("  // ==============================\n", start)
    if end > 0:
        content = content[:start] + "\n" + content[end + len("  // ==============================\n"):]
        changes += 1
        print('[OK] Diagnóstico de cliques removido')

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n[DONE] {changes} mudancas aplicadas')
print('Agora os botões usam inline JS direto — independente de showWaSub')
