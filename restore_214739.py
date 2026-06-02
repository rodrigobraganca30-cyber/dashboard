import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

print('=== RESTAURANDO backup_dashboard_completo_20260526_214739 ===\n')

# 1. Backup do estado atual antes de restaurar
print('[1] Backup do estado atual...')
i, o, e = c.exec_command('cp /docker/dashboard/html/index.html /docker/dashboard/html/index.html.bak.pre_restore_214739')
e.read()
print('    OK')

# 2. Restaurar o tar.gz
print('\n[2] Restaurando dashboard completo...')
i, o, e = c.exec_command('cd /docker && tar xzf /docker/backup_dashboard_completo_20260526_214739.tar.gz')
time.sleep(15)
err = e.read().decode('utf-8', errors='replace').strip()
print(f'    {"OK" if not err else "Avisos: " + err[:200]}')

# 3. Restaurar o backend também
print('\n[3] Restaurando backend...')
i, o, e = c.exec_command('cd /docker && tar xzf /docker/backup_whatsapp_agenda_20260526_214739.tar.gz')
time.sleep(5)
err = e.read().decode('utf-8', errors='replace').strip()
print(f'    {"OK" if not err else "Avisos: " + err[:200]}')

# 4. Copiar index.js para o container
print('\n[4] Atualizando backend no container...')
i, o, e = c.exec_command('docker cp /docker/whatsapp-agenda/backend/index.js backend-agenda:/app/index.js')
time.sleep(2)
print(f'    {"OK" if not e.read().decode().strip() else "ERRO"}')

# 5. Reiniciar backend
print('\n[5] Reiniciando backend...')
i, o, e = c.exec_command('docker restart backend-agenda')
time.sleep(8)
print(f'    {o.read().decode().strip()}')

# 6. Verificar
print('\n[6] Verificação:')
time.sleep(3)
i, o, e = c.exec_command('docker ps --filter name=backend-agenda --format "{{.Status}}"')
time.sleep(1)
print(f'    Container: {o.read().decode().strip()}')

i, o, e = c.exec_command('''docker exec backend-agenda node -e "fetch('http://localhost:3001/health').then(r=>r.json()).then(j=>console.log('Health:',JSON.stringify(j))).catch(e=>console.log('ERR:',e.message))"''')
time.sleep(3)
print(f'    {o.read().decode().strip()}')

i, o, e = c.exec_command("grep -c 'bloqueado' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    Bloqueado: {o.read().decode().strip()} refs')

i, o, e = c.exec_command("grep -c 'function showWaSub' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    showWaSub: {o.read().decode().strip()} refs')

c.close()
print('\n=== RESTAURADO ===')
