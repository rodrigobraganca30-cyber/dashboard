import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

ts_backup = '20260526_214739'

print('=== RESTAURANDO BACKUP ===\n')

# 1. Restaurar dashboard
print('[1] Restaurando /docker/dashboard/...')
i, o, e = c.exec_command(f'cd /docker && tar xzf /docker/backup_dashboard_completo_{ts_backup}.tar.gz')
time.sleep(15)
err = e.read().decode('utf-8', errors='replace').strip()
print(f'    {"OK" if not err else "Avisos: " + err[:200]}')

# 2. Restaurar whatsapp-agenda (backend)
print('\n[2] Restaurando /docker/whatsapp-agenda/...')
i, o, e = c.exec_command(f'cd /docker && tar xzf /docker/backup_whatsapp_agenda_{ts_backup}.tar.gz')
time.sleep(5)
err = e.read().decode('utf-8', errors='replace').strip()
print(f'    {"OK" if not err else "Avisos: " + err[:200]}')

# 3. Copiar o index.js patchado de volta para o container
print('\n[3] Atualizando backend no container...')
i, o, e = c.exec_command('docker cp /docker/whatsapp-agenda/backend/index.js backend-agenda:/app/index.js')
time.sleep(2)
err = e.read().decode('utf-8', errors='replace').strip()
print(f'    {"OK" if not err else "ERRO: " + err[:200]}')

# 4. Restart do container
print('\n[4] Reiniciando backend-agenda...')
i, o, e = c.exec_command('docker restart backend-agenda')
time.sleep(5)
print(f'    {o.read().decode().strip()}')

# 5. Verificar que o HTML está OK
print('\n[5] Verificando dashboard HTML...')
i, o, e = c.exec_command("grep -c 'showWaSub' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    showWaSub: {o.read().decode().strip()} ocorrências')

i, o, e = c.exec_command("grep -c 'bloqueado' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    bloqueado: {o.read().decode().strip()} ocorrências')

# 6. Verificar backend
print('\n[6] Verificando backend...')
i, o, e = c.exec_command('docker exec backend-agenda node -e "console.log(\'OK\')"')
time.sleep(3)
out = o.read().decode().strip()
print(f'    Node: {out}')

# 7. Verificar health
i, o, e = c.exec_command('docker exec backend-agenda curl -s http://localhost:3001/health')
time.sleep(3)
print(f'    Health: {o.read().decode().strip()}')

c.close()
print('\n=== RESTAURAÇÃO CONCLUÍDA ===')
