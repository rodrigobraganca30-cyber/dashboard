import paramiko, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Ver o log completo de erro
print('[1] Log completo do crash:')
i, o, e = c.exec_command('docker logs backend-agenda 2>&1')
logs = o.read().decode('utf-8', errors='replace').strip()
# Mostrar as últimas 30 linhas (o erro deve estar aí)
lines = logs.split('\n')
for line in lines[-30:]:
    print(line)

c.close()
