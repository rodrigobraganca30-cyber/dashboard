import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Usar o index.js.container do backup anterior (que funcionava)
print('[1] Copiando index.js funcional...')
i, o, e = c.exec_command('docker cp /docker/backup_20260526_214412/index.js.container backend-agenda:/app/index.js')
time.sleep(2)
print(f'    {"OK" if not e.read().decode().strip() else "ERRO"}')

print('[2] Reiniciando...')
i, o, e = c.exec_command('docker restart backend-agenda')
time.sleep(8)

print('[3] Verificando...')
time.sleep(3)
i, o, e = c.exec_command('docker ps --filter name=backend-agenda --format "{{.Status}}"')
time.sleep(1)
print(f'    Container: {o.read().decode().strip()}')

i, o, e = c.exec_command('''docker exec backend-agenda node -e "fetch('http://localhost:3001/health').then(r=>r.json()).then(j=>console.log(JSON.stringify(j))).catch(e=>console.log('ERR:',e.message))"''')
time.sleep(3)
print(f'    Health: {o.read().decode().strip()}')

c.close()
