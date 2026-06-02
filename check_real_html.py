import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Verificar showWaSub no html/index.html
print('[1] showWaSub em html/index.html:')
i, o, e = c.exec_command("grep -c 'showWaSub' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    Matches: {o.read().decode().strip()}')

# 2. Verificar bloqueado
print('\n[2] bloqueado em html/index.html:')
i, o, e = c.exec_command("grep -c 'bloqueado' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    Matches: {o.read().decode().strip()}')

# 3. Verificar tamanho
print('\n[3] Tamanho html/index.html:')
i, o, e = c.exec_command("wc -l /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    {o.read().decode().strip()}')

# 4. Data de modificação
print('\n[4] Data de modificação:')
i, o, e = c.exec_command("ls -la /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    {o.read().decode().strip()}')

# 5. Verificar se showWaSub tem o JS correto (sem corrupção de f-string)
print('\n[5] Primeiras linhas do showWaSub:')
i, o, e = c.exec_command("grep -A2 'function showWaSub' /docker/dashboard/html/index.html | head -5")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 6. Verificar se a aba WhatsApp existe
print('\n[6] Aba whatsapp-agenda:')
i, o, e = c.exec_command("grep -c 'wa-painel\\|wa-disparo\\|wa-config\\|wa-chat' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    Matches: {o.read().decode().strip()}')

c.close()
