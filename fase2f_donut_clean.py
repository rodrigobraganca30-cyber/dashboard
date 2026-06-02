import paramiko, os, sys, time, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

patch = r'''
import re
html = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()

# 1. Limpar o conteudo inline do donut-wrap (SVG + legenda antiga)
# Substituir tudo entre <div class="donut-wrap"> e </div> seguinte
pattern = r'(<div class="donut-wrap">)(.*?)(</div>)'
match = re.search(pattern, html, re.DOTALL)
if match:
    old_content = match.group(2)
    # Substituir com div vazia - runFilter vai recriar
    html = html[:match.start()] + '<div class="donut-wrap"></div>' + html[match.end():]
    print('[+] donut-wrap limpo: %d chars removidos' % len(old_content))
else:
    print('[!] donut-wrap nao encontrado')

# 2. Remover scripts duplicados antigos
for old_id in ['dynamicDonutFix', 'dynamicFrotaKPI']:
    while old_id in html:
        s = html.find('<script id="' + old_id + '">')
        if s < 0: break
        e = html.find('</script>', s)
        if e < 0: break
        html = html[:s] + html[e+len('</script>'):]
        print('[+] Removido script antigo: ' + old_id)

open('/docker/dashboard/html/index.html', 'w', encoding='utf-8').write(html)
print('[OK] HTML salvo (%d bytes)' % len(html))
'''

print('Limpando donut inline...')
sftp = c.open_sftp()
with sftp.open('/tmp/patch_donut_clean.py', 'w') as f:
    f.write(patch)
sftp.close()

i, o, e = c.exec_command('python3 /tmp/patch_donut_clean.py')
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err: print(f'ERR: {err[:300]}')

c.close()
print('Ctrl+Shift+R para testar.')
