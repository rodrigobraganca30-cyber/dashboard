import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

patch = '''
html = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()

# Encontrar donut-wrap e limpar por contagem de divs
tag = 'class="donut-wrap"'
start = html.find(tag)
if start < 0:
    print('[!] donut-wrap nao encontrado')
    exit(1)

# Voltar ao < do div
div_start = html.rfind('<div', 0, start)
# Agora contar divs aninhados para achar o </div> correto
pos = html.find('>', div_start) + 1  # posicao apos o >
depth = 1
i = pos
while depth > 0 and i < len(html):
    next_open = html.find('<div', i)
    next_close = html.find('</div>', i)
    if next_close < 0:
        break
    if next_open >= 0 and next_open < next_close:
        depth += 1
        i = next_open + 4
    else:
        depth -= 1
        if depth == 0:
            # Encontramos o </div> que fecha donut-wrap
            end = next_close + len('</div>')
            old = html[div_start:end]
            print('[INFO] donut-wrap: %d chars, depth OK' % len(old))
            print('[INFO] Primeiros 100 chars:', old[:100])
            print('[INFO] Ultimos 80 chars:', old[-80:])
            # Substituir por div vazia
            html = html[:div_start] + '<div class="donut-wrap"></div>' + html[end:]
            print('[+] donut-wrap substituido por vazio')
            break
        i = next_close + 6

open('/docker/dashboard/html/index.html', 'w', encoding='utf-8').write(html)
print('[OK] HTML salvo')
'''

print('Limpando donut...')
sftp = c.open_sftp()
with sftp.open('/tmp/patch_donut2.py', 'w') as f:
    f.write(patch)
sftp.close()

i, o, e = c.exec_command('python3 /tmp/patch_donut2.py')
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err: print(f'ERR: {err[:300]}')

c.close()
print('Ctrl+Shift+R para testar.')
