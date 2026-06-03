import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

print('[1] Status do container:')
i, o, e = c.exec_command('docker ps --filter name=backend-agenda --format "{{.Status}}"')
time.sleep(1)
print(f'    {o.read().decode().strip()}')

print('\n[2] Health via Node:')
i, o, e = c.exec_command('''docker exec backend-agenda node -e "fetch('http://localhost:3001/health').then(r=>r.text()).then(t=>console.log(t)).catch(e=>console.log('ERR:',e.message))"''')
time.sleep(3)
print(f'    {o.read().decode().strip()}')

print('\n[3] Blacklist:')
i, o, e = c.exec_command('docker exec redis-agenda redis-cli SCARD agenda:blacklist')
time.sleep(1)
print(f'    {o.read().decode().strip()} números')

print('\n[4] Logs recentes (sem erros):')
i, o, e = c.exec_command('docker logs backend-agenda --tail 5 2>&1')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
