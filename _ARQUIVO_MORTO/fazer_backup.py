import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

ts = time.strftime('%Y%m%d_%H%M%S')
backup_dir = f'/docker/backup_{ts}'

print(f'=== BACKUP {ts} ===\n')

# 1. Criar diretório de backup
i, o, e = c.exec_command(f'mkdir -p {backup_dir}')
e.read()

# 2. Dashboard HTML
print('[1] Dashboard HTML...')
i, o, e = c.exec_command(f'cp /docker/dashboard/html/index.html {backup_dir}/index.html')
e.read()
print('    OK')

# 3. whatsapp_agenda_gen.py
print('[2] whatsapp_agenda_gen.py...')
i, o, e = c.exec_command(f'cp /docker/dashboard/whatsapp_agenda_gen.py {backup_dir}/whatsapp_agenda_gen.py')
e.read()
print('    OK')

# 4. Backend index.js (do host)
print('[3] Backend index.js (host)...')
i, o, e = c.exec_command(f'cp /docker/whatsapp-agenda/backend/index.js {backup_dir}/index.js.backend')
e.read()
print('    OK')

# 5. Backend index.js (do container)
print('[4] Backend index.js (container)...')
i, o, e = c.exec_command(f'docker cp backend-agenda:/app/index.js {backup_dir}/index.js.container')
e.read()
print('    OK')

# 6. Redis blacklist dump
print('[5] Redis blacklist...')
i, o, e = c.exec_command(f'docker exec redis-agenda redis-cli SMEMBERS agenda:blacklist > {backup_dir}/blacklist.txt')
e.read()
print('    OK')

# 7. gerar_dashboard_v2.py
print('[6] gerar_dashboard_v2.py...')
i, o, e = c.exec_command(f'cp /docker/dashboard/gerar_dashboard_v2.py {backup_dir}/gerar_dashboard_v2.py')
e.read()
print('    OK')

# Listar backup
print(f'\n[7] Conteúdo do backup:')
i, o, e = c.exec_command(f'ls -lh {backup_dir}/')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# Tamanho total
i, o, e = c.exec_command(f'du -sh {backup_dir}/')
time.sleep(1)
print(f'\nTotal: {o.read().decode().strip()}')

c.close()
print(f'\n=== BACKUP SALVO EM {backup_dir} ===')
