import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Verificar se o backend DEFINITIVO tinha rotas de flow
print('[1] Rotas flow no backend DEFINITIVO:')
i, o, e = c.exec_command("grep -n 'flow' /docker/backups/backup_20260526_000900_DEFINITIVO/index.js")
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip() or '    NENHUMA')

print('\n[2] Rotas flow no backend ATUAL (container):')
i, o, e = c.exec_command('''docker exec backend-agenda grep -n 'flow' /app/index.js''')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip() or '    NENHUMA')

# Verificar webhook - como ele processa SIM/NAO
print('\n[3] Webhook processing no container:')
i, o, e = c.exec_command('''docker exec backend-agenda grep -n -A5 "SIM\\|confirmo\\|reagend\\|classific" /app/index.js''')
time.sleep(2)
out = o.read().decode('utf-8', errors='replace').strip()
print(out[:1000] if out else '    NENHUMA')

c.close()
