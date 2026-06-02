import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

ts = time.strftime('%Y%m%d_%H%M%S')

# 1. Backup
print('[1/3] Backup...')
c.exec_command(f'cp /docker/dashboard/html/index.html /docker/backup_dashboard_{ts}_pre_fase2_v2.html')
time.sleep(1)

# 2. Upload dynamic_loader.js como arquivo externo
print('[2/3] Upload dynamic_loader.js...')
sftp = c.open_sftp()
sftp.put(r'C:\Users\SVOBODA\Desktop\DASHBOARD\dynamic_loader.js', '/docker/dashboard/html/dynamic_loader.js')
size = os.path.getsize(r'C:\Users\SVOBODA\Desktop\DASHBOARD\dynamic_loader.js')
print(f'    OK ({size:,} bytes)')
sftp.close()

# 3. Injetar UMA tag <script> antes de </body>
print('[3/3] Injetando tag script...')
patch = '''
html = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()

# Verificar se ja existe
if 'dynamic_loader.js' in html:
    print('[!] Tag ja existe')
    exit(0)

# Adicionar script antes de </body>
tag = '<script src="dynamic_loader.js"></script>'
body_end = html.rfind('</body>')
if body_end > 0:
    html = html[:body_end] + tag + '\\n' + html[body_end:]
    print('[+] Tag adicionada')

open('/docker/dashboard/html/index.html', 'w', encoding='utf-8').write(html)
print('[OK] HTML salvo')
'''

sftp = c.open_sftp()
with sftp.open('/tmp/inject_loader.py', 'w') as f:
    f.write(patch)
sftp.close()

i, o, e = c.exec_command('python3 /tmp/inject_loader.py')
time.sleep(3)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err: print(f'ERR: {err[:200]}')

# Verificar
i, o, e = c.exec_command("grep -c 'dynamic_loader' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'Refs: {o.read().decode().strip()}')

c.close()
print('\nFase 2 v2 aplicada! Ctrl+Shift+R para testar.')
print('F12 > Console > procure [DynLoader]')
