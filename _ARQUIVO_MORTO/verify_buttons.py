import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

print('[1] Container:')
i, o, e = c.exec_command('docker ps --filter name=backend-agenda --format "{{.Names}}: {{.Status}}"')
time.sleep(1)
print(f'    {o.read().decode().strip()}')

print('\n[2] BUTTON_FLOWS no codigo:')
i, o, e = c.exec_command('docker exec backend-agenda grep -c BUTTON_FLOWS /app/index.js')
time.sleep(1)
print(f'    {o.read().decode().strip()} ocorrencias')

print('\n[3] Ultimos 25 logs:')
i, o, e = c.exec_command('docker logs backend-agenda --tail 25 2>&1')
time.sleep(2)
logs = o.read().decode('utf-8', errors='replace').strip()
for line in logs.split('\n'):
    marker = ''
    if 'Fluxo bot' in line:
        marker = '  >>> 🟢 '
    elif '"type":"button"' in line:
        marker = '  >>> 🔵 '
    else:
        marker = '    '
    print(f'{marker}{line.strip()}')

c.close()
