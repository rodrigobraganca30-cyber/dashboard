import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

i, o, e = c.exec_command('docker ps --filter name=backend-agenda --format "{{.Status}}"')
time.sleep(1)
print('Container:', o.read().decode().strip())

i, o, e = c.exec_command('docker exec backend-agenda curl -s http://localhost:3001/health')
time.sleep(3)
print('Health:', o.read().decode().strip())

i, o, e = c.exec_command('docker exec backend-agenda redis-cli -h redis-agenda SCARD agenda:blacklist')
time.sleep(1)
print('Blacklist:', o.read().decode().strip(), 'numeros')

c.close()
