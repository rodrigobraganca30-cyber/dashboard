import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Qual arquivo HTML está sendo servido?
print('[1] Arquivos HTML no diretório do dashboard:')
i, o, e = c.exec_command("ls -la /docker/dashboard/*.html 2>/dev/null")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 2. Qual arquivo tem showWaSub?
print('\n[2] Arquivos com showWaSub:')
i, o, e = c.exec_command("grep -rl 'showWaSub' /docker/dashboard/ 2>/dev/null")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 3. Onde é servido o frontend do WhatsApp?
print('\n[3] Frontends no Docker:')
i, o, e = c.exec_command("ls -la /docker/whatsapp-agenda/frontend/*.html 2>/dev/null")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 4. Buscar showWaSub no frontend do container
print('\n[4] showWaSub no frontend do container:')
i, o, e = c.exec_command("grep -rl 'showWaSub' /docker/whatsapp-agenda/frontend/ 2>/dev/null")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 5. Verificar se o index.html do dashboard principal contém a aba WhatsApp
print('\n[5] grep whatsapp-agenda no index.html:')
i, o, e = c.exec_command("grep -c 'whatsapp-agenda\\|wa-painel\\|showWaSub' /docker/dashboard/index.html 2>/dev/null")
time.sleep(1)
out = o.read().decode().strip()
print(f'    Matches: {out}')

# Se 0, ver o sftp_upload path 
print('\n[6] Verificar onde o dashboard publica:')
i, o, e = c.exec_command("grep -r 'sftp\\|upload\\|deploy' /docker/dashboard/gerar_dashboard_v2.py 2>/dev/null | tail -5")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 7. Verificar tamanho do index.html
print('\n[7] Tamanho index.html:')
i, o, e = c.exec_command("wc -l /docker/dashboard/index.html 2>/dev/null")
time.sleep(1)
print(o.read().decode().strip())

c.close()
