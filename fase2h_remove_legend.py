import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

patch = '''
html = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()

# Encontrar a legenda externa: <div class="donut-legend"> que esta FORA do donut-wrap
# Ela fica logo apos </div> do donut-wrap
marker = '</div><div class="donut-legend">'
pos = html.find(marker)
if pos < 0:
    print('[!] Legenda externa nao encontrada')
    exit(0)

# Encontrar o final dessa div (contando nesting)
legend_start = pos + len('</div>')  # pular o </div> do donut-wrap
i = legend_start
depth = 0
found_end = -1
while i < len(html):
    next_open = html.find('<div', i)
    next_close = html.find('</div>', i)
    if next_close < 0:
        break
    if next_open >= 0 and next_open < next_close:
        depth += 1
        i = next_open + 4
    else:
        if depth == 0:
            found_end = next_close + len('</div>')
            break
        depth -= 1
        i = next_close + 6

if found_end > 0:
    removed = html[legend_start:found_end]
    print('[INFO] Removendo legenda: %d chars' % len(removed))
    print('[INFO] Conteudo:', removed[:150], '...')
    html = html[:legend_start] + html[found_end:]
    print('[+] Legenda externa removida!')
else:
    print('[!] Nao encontrou fim da legenda')

open('/docker/dashboard/html/index.html', 'w', encoding='utf-8').write(html)
print('[OK] HTML salvo')
'''

print('Removendo legenda duplicada...')
sftp = c.open_sftp()
with sftp.open('/tmp/patch_legend.py', 'w') as f:
    f.write(patch)
sftp.close()

i, o, e = c.exec_command('python3 /tmp/patch_legend.py')
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err: print(f'ERR: {err[:300]}')

c.close()
print('Ctrl+Shift+R para testar!')
