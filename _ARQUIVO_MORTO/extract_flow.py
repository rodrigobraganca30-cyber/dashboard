import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Extrair as rotas de flow do DEFINITIVO (linhas 1231-fim)
print('Extraindo rotas de flow do DEFINITIVO:')
i, o, e = c.exec_command("sed -n '1225,1350p' /docker/backups/backup_20260526_000900_DEFINITIVO/index.js")
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
