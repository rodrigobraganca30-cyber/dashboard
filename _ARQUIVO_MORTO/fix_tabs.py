import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Verificar qual backup estava funcionando 
# Usar o backup pre_inject mais recente que estava bom
print('[1] Testando backup pre_inject mais recente:')
cmd = r"""docker run --rm -v /docker/dashboard/html:/data node:20-alpine node -e "
const fs = require('fs');
const file = 'index.html.bak.pre_inject.20260526_000821';
const html = fs.readFileSync('/data/' + file, 'utf8');
const regex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match, idx = 0, allOk = true;
while ((match = regex.exec(html)) !== null) {
  const code = match[1].trim();
  if (!code) { idx++; continue; }
  try { new Function(code); }
  catch(e) { console.log('Script ' + idx + ': ERRO'); allOk = false; }
  idx++;
}
console.log(allOk ? 'TODOS OK (' + idx + ' scripts)' : 'TEM ERROS');
console.log('showWaSub:', html.includes('function showWaSub'));
console.log('bloqueado:', html.includes('bloqueado'));
"
"""
i, o, e = c.exec_command(cmd)
time.sleep(10)
out = o.read().decode('utf-8', errors='replace').strip()
print(out)

# 2. Restaurar o backup que funcionava
print('\n[2] Restaurando backup funcional...')
i, o, e = c.exec_command('cp /docker/dashboard/html/index.html /docker/dashboard/html/index.html.bak.broken_blacklist')
e.read()
i, o, e = c.exec_command('cp /docker/dashboard/html/index.html.bak.pre_inject.20260526_000821 /docker/dashboard/html/index.html')
err = e.read().decode().strip()
if err:
    print(f'    ERRO: {err}')
else:
    print('    OK - Backup restaurado.')

# 3. Agora injetar "bloqueado" diretamente no HTML restaurado
print('\n[3] Injetando "bloqueado" no HTML restaurado...')

# 3a. Adicionar bloqueado ao WA_STATUS_LABELS
i, o, e = c.exec_command(r"""python3 -c "
import re
with open('/docker/dashboard/html/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

changes = 0

# 1. Add bloqueado to WA_STATUS_LABELS
old = \"'solicitou-upgrade':'SOLICITOU UPGRADE'}\"
new_val = \"'solicitou-upgrade':'SOLICITOU UPGRADE',bloqueado:'\U0001f6ab Bloqueado'}\"
if old in html:
    html = html.replace(old, new_val, 1)
    changes += 1
    print('[+] WA_STATUS_LABELS atualizado')
else:
    print('[!] WA_STATUS_LABELS anchor not found')

# 2. Add CSS for .wa-badge.bloqueado
css_anchor = '.wa-badge.elogio{background:rgba(234,179,8,.15);color:#fbbf24}'
css_new = css_anchor + '\n.wa-badge.bloqueado{background:rgba(239,68,68,.2);color:#ef4444;border:1px solid rgba(239,68,68,.3)}'
if css_anchor in html and 'wa-badge.bloqueado' not in html:
    html = html.replace(css_anchor, css_new, 1)
    changes += 1
    print('[+] CSS bloqueado adicionado')
elif 'wa-badge.bloqueado' in html:
    print('[=] CSS bloqueado já existe')
else:
    print('[!] CSS anchor not found')

# 3. Add bloqueado to filter dropdown
filter_anchor = 'SOLICITOU UPGRADE</label>\n        </div>\n      </div>\n      <div class=\"wa-dd-wrap\">\n        <div class=\"wa-dd-btn\" onclick=\"waToggleDD(\\\"dd-city'
# Try a simpler anchor
filter_old = 'value=\"solicitou-upgrade\" onchange=\"waFilterTable()\"> SOLICITOU UPGRADE</label>'
filter_new = filter_old + '\n          <label class=\"wa-dd-item\"><input type=\"checkbox\" value=\"bloqueado\" onchange=\"waFilterTable()\"> \U0001f6ab Bloqueado</label>'
if filter_old in html and 'value=\"bloqueado\"' not in html:
    html = html.replace(filter_old, filter_new, 1)
    changes += 1
    print('[+] Filtro bloqueado adicionado')
elif 'value=\"bloqueado\"' in html:
    print('[=] Filtro bloqueado já existe')
else:
    print('[!] Filter anchor not found - trying alternative')
    # Try without exact whitespace
    if 'SOLICITOU UPGRADE</label>' in html:
        idx = html.index('SOLICITOU UPGRADE</label>')
        # Find the end of this label
        end = idx + len('SOLICITOU UPGRADE</label>')
        inject = '\n          <label class=\"wa-dd-item\"><input type=\"checkbox\" value=\"bloqueado\" onchange=\"waFilterTable()\"> \U0001f6ab Bloqueado</label>'
        html = html[:end] + inject + html[end:]
        changes += 1
        print('[+] Filtro bloqueado adicionado (alt)')

# 4. Add bloqueado to chat status dropdowns
status_old = 'Sem Retorno Supervisão</option>'"'"';'
status_new = 'Sem Retorno Supervisão</option><option value=\"bloqueado\">\U0001f6ab Bloqueado</option>'"'"';'
count_before = html.count('Sem Retorno Supervisão</option>'"'"';')
if count_before > 0 and 'bloqueado\">\U0001f6ab Bloqueado</option>' not in html:
    html = html.replace(status_old, status_new)
    changes += 1
    print(f'[+] {count_before} dropdown(s) de status atualizados')
elif 'bloqueado\">' in html:
    print('[=] Dropdowns já têm bloqueado')

with open('/docker/dashboard/html/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'\nTotal de mudanças: {changes}')
print('bloqueado count:', html.count('bloqueado'))
"
""")
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'ERR: {err[:300]}')

# 4. Verificar que o HTML continua sem erros de JS
print('\n[4] Verificando JS após injeção:')
cmd2 = r"""docker run --rm -v /docker/dashboard/html:/data node:20-alpine node -e "
const fs = require('fs');
const html = fs.readFileSync('/data/index.html', 'utf8');
const regex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match, idx = 0, allOk = true;
while ((match = regex.exec(html)) !== null) {
  const code = match[1].trim();
  if (!code) { idx++; continue; }
  try { new Function(code); console.log('Script ' + idx + ': OK'); }
  catch(e) { console.log('Script ' + idx + ': ERRO - ' + e.message.substring(0, 100)); allOk = false; }
  idx++;
}
console.log(allOk ? 'TODOS OK' : 'TEM ERROS');
console.log('bloqueado:', html.includes('bloqueado'));
"
"""
i, o, e = c.exec_command(cmd2)
time.sleep(10)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
print('\n=== FIX CONCLUÍDO ===')
