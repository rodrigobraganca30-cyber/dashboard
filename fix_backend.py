import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# O backup tem o index.js.container que era o que estava rodando
# Vamos usar esse
backup_dir = '/docker/backup_20260526_214412'

print('[1] Verificando logs do container...')
i, o, e = c.exec_command('docker logs backend-agenda --tail 10 2>&1')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

print('\n[2] Copiando index.js do container backup...')
i, o, e = c.exec_command(f'docker cp {backup_dir}/index.js.container backend-agenda:/app/index.js')
time.sleep(2)
err = e.read().decode().strip()
print(f'    {"OK" if not err else "ERRO: " + err}')

print('\n[3] Reiniciando...')
i, o, e = c.exec_command('docker restart backend-agenda')
time.sleep(8)
print(f'    {o.read().decode().strip()}')

print('\n[4] Verificando...')
time.sleep(3)
i, o, e = c.exec_command('docker ps --filter name=backend-agenda --format "{{.Status}}"')
time.sleep(1)
print(f'    Status: {o.read().decode().strip()}')

i, o, e = c.exec_command('docker exec backend-agenda curl -s http://localhost:3001/health')
time.sleep(3)
print(f'    Health: {o.read().decode().strip()}')

c.close()
