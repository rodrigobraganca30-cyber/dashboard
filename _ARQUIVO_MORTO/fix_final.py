import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Restaurar o bak.20260526_220224 (último com tudo)
print('[1] Restaurando bak.20260526_220224...')
i, o, e = c.exec_command('cp /docker/dashboard/html/index.html /docker/dashboard/html/index.html.bak.pre_fix_final')
e.read()
i, o, e = c.exec_command('cp /docker/dashboard/html/index.html.bak.20260526_220224 /docker/dashboard/html/index.html')
err = e.read().decode().strip()
print(f'    {"OK" if not err else "ERRO: " + err}')

# 2. Verificar conteúdo
i, o, e = c.exec_command("grep -c 'waFluxoLoadConfig' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    Fluxo: {o.read().decode().strip()} refs')
i, o, e = c.exec_command("grep -c 'bloqueado' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    Bloqueado: {o.read().decode().strip()} refs')
i, o, e = c.exec_command("grep -c 'waLoadMetaTemplates' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    Templates: {o.read().decode().strip()} refs')

# 3. Verificar a API key no HTML
print('\n[2] API key no HTML:')
i, o, e = c.exec_command("grep -o \"WA_KEY='[^']*'\" /docker/dashboard/html/index.html | head -3")
time.sleep(1)
html_key = o.read().decode('utf-8', errors='replace').strip()
print(f'    {html_key}')

# 4. Verificar a API key no backend
print('\n[3] API key no backend:')
i, o, e = c.exec_command("docker exec backend-agenda env | grep -i api_key || docker exec backend-agenda env | grep -i KEY")
time.sleep(1)
print(f'    {o.read().decode().strip()}')

i, o, e = c.exec_command("grep -o 'API_KEY=[^ ]*' /docker/whatsapp-agenda/backend/.env 2>/dev/null || grep -o 'API_KEY=[^ ]*' /docker/whatsapp-agenda/.env 2>/dev/null")
time.sleep(1)
print(f'    .env: {o.read().decode().strip()}')

i, o, e = c.exec_command("grep 'apiKey\\|API_KEY\\|validKey' /docker/whatsapp-agenda/backend/index.js 2>/dev/null | head -3")
time.sleep(1)
print(f'    index.js: {o.read().decode("utf-8", errors="replace").strip()[:200]}')

# 5. Verificar no container (index.js ativo)
print('\n[4] API key no container:')
i, o, e = c.exec_command('''docker exec backend-agenda node -e "const fs=require('fs');const c=fs.readFileSync('/app/index.js','utf8');const m=c.match(/(?:apiKey|API_KEY|validKey)[^;]*/g);if(m)m.slice(0,3).forEach(l=>console.log(l.substring(0,150)))"''')
time.sleep(3)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
