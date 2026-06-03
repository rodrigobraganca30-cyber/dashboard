"""
inject_bloqueado.py - Script para ser executado NO VPS
Injeta o status 'bloqueado' diretamente no HTML do dashboard.
"""
import sys

HTML_PATH = '/docker/dashboard/html/index.html'

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)
changes = 0

# 1. CSS badge
css_anchor = ".wa-badge.elogio{background:rgba(234,179,8,.15);color:#fbbf24}"
css_new = css_anchor + "\n.wa-badge.bloqueado{background:rgba(239,68,68,.2);color:#ef4444;border:1px solid rgba(239,68,68,.3)}"
if css_anchor in html and 'wa-badge.bloqueado' not in html:
    html = html.replace(css_anchor, css_new, 1)
    changes += 1
    print('[+] CSS bloqueado')

# 2. WA_STATUS_LABELS
labels_anchor = "'solicitou-upgrade':'SOLICITOU UPGRADE'}"
labels_new = "'solicitou-upgrade':'SOLICITOU UPGRADE',bloqueado:'\U0001f6ab Bloqueado'}"
if labels_anchor in html and "bloqueado:'" not in html:
    html = html.replace(labels_anchor, labels_new, 1)
    changes += 1
    print('[+] WA_STATUS_LABELS')

# 3. Filtro dropdown
filter_anchor = 'SOLICITOU UPGRADE</label>'
if filter_anchor in html and 'value="bloqueado"' not in html:
    idx = html.index(filter_anchor) + len(filter_anchor)
    inject = '\n          <label class="wa-dd-item"><input type="checkbox" value="bloqueado" onchange="waFilterTable()"> \U0001f6ab Bloqueado</label>'
    html = html[:idx] + inject + html[idx:]
    changes += 1
    print('[+] Filtro dropdown')

# 4. Chat status dropdowns (ambos)
status_old = "Sem Retorno Supervis\u00e3o</option>';"
status_new = "Sem Retorno Supervis\u00e3o</option><option value=\"bloqueado\">\U0001f6ab Bloqueado</option>';"
cnt = html.count(status_old)
if cnt > 0 and '<option value="bloqueado">' not in html:
    html = html.replace(status_old, status_new)
    changes += 1
    print(f'[+] {cnt} dropdown(s) de status')

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'\nTotal mudancas: {changes}')
print(f'Tamanho: {original_len} -> {len(html)} bytes')
print(f'bloqueado count: {html.count("bloqueado")}')
