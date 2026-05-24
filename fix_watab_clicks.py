#!/usr/bin/env python3
"""Fix wa-tab buttons not clickable - add z-index and pointer-events"""
ARQUIVO = '/docker/dashboard/html/index.html'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# Fix 1: Adiciona z-index e pointer-events ao .wa-tabs e .wa-tab
OLD_TABS_CSS = ".wa-tabs{display:flex;gap:8px;margin-bottom:24px}\n.wa-tab{background:#111520;border:1px solid #1c2237;border-radius:8px;padding:10px 20px;font-size:13px;color:#94a3b8;cursor:pointer;font-family:var(--font-head);font-weight:600;transition:all .2s}"
NEW_TABS_CSS = ".wa-tabs{display:flex;gap:8px;margin-bottom:24px;position:relative;z-index:50}\n.wa-tab{background:#111520;border:1px solid #1c2237;border-radius:8px;padding:10px 20px;font-size:13px;color:#94a3b8;cursor:pointer;font-family:var(--font-head);font-weight:600;transition:all .2s;position:relative;z-index:51;pointer-events:all;user-select:none}"

if OLD_TABS_CSS in content:
    content = content.replace(OLD_TABS_CSS, NEW_TABS_CSS, 1)
    changes += 1
    print('[OK] z-index e pointer-events adicionados ao .wa-tab')
else:
    print('[AVISO] CSS anchor nao encontrado, tentando alternativa...')
    # Tenta só adicionar o z-index ao .wa-tabs
    OLD2 = ".wa-tabs{display:flex;gap:8px;margin-bottom:24px}"
    NEW2 = ".wa-tabs{display:flex;gap:8px;margin-bottom:24px;position:relative;z-index:50}"
    if OLD2 in content:
        content = content.replace(OLD2, NEW2, 1)
        changes += 1
        print('[OK] z-index adicionado ao .wa-tabs')

# Fix 2: Garante que o chat-mode não bloqueia os tabs
OLD_CHAT = "body.chat-mode .wa-tabs{flex-shrink:0;padding:8px 16px;margin-bottom:0}"
NEW_CHAT = "body.chat-mode .wa-tabs{flex-shrink:0;padding:8px 16px;margin-bottom:0;pointer-events:all;z-index:50}"

if OLD_CHAT in content:
    content = content.replace(OLD_CHAT, NEW_CHAT, 1)
    changes += 1
    print('[OK] chat-mode pointer-events corrigido')

# Fix 3: Adiciona event listener de backup via JS para os tabs
BACKUP_LISTENER = """
  // Backup listeners para wa-tabs (garante funcionamento mesmo com z-index issues)
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.wa-tab').forEach(function(btn) {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        var onclick = btn.getAttribute('onclick');
        if (onclick) {
          var match = onclick.match(/showWaSub\\('([^']+)'/);
          if (match) showWaSub(match[1], btn);
        }
      }, true); // capture phase
    });
  });
"""

ANCHOR_JS = "  var waDispMode='fixed';"
if ANCHOR_JS in content:
    content = content.replace(ANCHOR_JS, BACKUP_LISTENER + "\n  " + "var waDispMode='fixed';", 1)
    changes += 1
    print('[OK] Event listener backup adicionado')

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'[DONE] {changes} correcoes aplicadas')
