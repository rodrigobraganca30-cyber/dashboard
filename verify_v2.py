import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Container status
i, o, e = c.exec_command('docker ps --filter name=backend-agenda --format "{{.Status}}"')
print(f'[1] Container: {o.read().decode().strip()}')

# 2. Últimas linhas do log (verificar se não crashou)
i, o, e = c.exec_command('docker logs backend-agenda --tail 8 2>&1')
time.sleep(1)
print(f'[2] Log:\n{o.read().decode("utf-8", errors="replace").strip()}')

# 3. Verificar se blacklist existe no código
i, o, e = c.exec_command("docker exec backend-agenda grep -c 'blacklist' /app/index.js")
print(f'\n[3] Blacklist ocorrências: {o.read().decode().strip()}')

i, o, e = c.exec_command("docker exec backend-agenda grep -c 'validateAndCleanPhone' /app/index.js")
print(f'[3] validateAndCleanPhone: {o.read().decode().strip()}')

# 4. Testar com curl -v para ver headers
print('\n[4] Teste /health:')
i, o, e = c.exec_command('curl -v http://localhost:3001/health 2>&1')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

print('\n[5] Teste /agenda/blacklist:')
i, o, e = c.exec_command('curl -v http://localhost:3001/agenda/blacklist 2>&1')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
