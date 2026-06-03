#!/usr/bin/env python3
"""
Diagnóstico cirúrgico: remove backup listener (pode estar bloqueando),
e adiciona diagnóstico que revela o elemento real que recebe o clique.
"""
ARQUIVO = '/docker/dashboard/html/index.html'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# 1. Remove o backup listener problemático (stopPropagation estava bloqueando o onclick original)
OLD_BACKUP = """
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
if OLD_BACKUP in content:
    content = content.replace(OLD_BACKUP, "\n", 1)
    changes += 1
    print('[OK] Backup listener removido (estava bloqueando onclick)')

# 2. Adiciona diagnóstico: captura clique em qualquer lugar e mostra o elemento real
DIAG_JS = """
  // === DIAGNÓSTICO DE CLIQUES ===
  document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(e) {
      var el = e.target;
      var tag = el.tagName + (el.id ? '#'+el.id : '') + (el.className ? '.'+String(el.className).split(' ')[0] : '');
      console.log('[CLICK] target:', tag, '| z-index:', window.getComputedStyle(el).zIndex, '| pointer-events:', window.getComputedStyle(el).pointerEvents);
      // Se clicou perto de .wa-tabs mas o target NÃO é .wa-tab, revela o bloqueador
      if (el.closest && !el.closest('.wa-tab') && !el.closest('.wa-tabs')) {
        var tabs = document.querySelector('.wa-tabs');
        if (tabs) {
          var r = tabs.getBoundingClientRect();
          if (e.clientX >= r.left && e.clientX <= r.right && e.clientY >= r.top && e.clientY <= r.bottom) {
            alert('BLOQUEADOR DETECTADO: ' + tag + '\\nEsse elemento está cobrindo os botões!\\nID: ' + (el.id||'sem-id') + '\\nClasse: ' + (el.className||'sem-classe'));
          }
        }
      }
    }, true);
  });
  // ==============================
"""

ANCHOR_JS = "  var waDispMode='fixed';"
if ANCHOR_JS in content:
    content = content.replace(ANCHOR_JS, DIAG_JS + "\n  " + "var waDispMode='fixed';", 1)
    changes += 1
    print('[OK] Diagnóstico de cliques injetado')

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'[DONE] {changes} mudancas aplicadas')
print('Instrução: Recarregar com Ctrl+Shift+R e clicar nos botões. Se houver bloqueador, aparece alert.')
