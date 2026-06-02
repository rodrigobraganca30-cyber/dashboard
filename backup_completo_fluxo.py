import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

ts = time.strftime('%Y%m%d_%H%M%S')
backup_dir = f'/docker/backup_completo_{ts}'
local_dir = r'C:\Users\SVOBODA\Desktop\DASHBOARD\BACKUP_COMPLETO'
os.makedirs(local_dir, exist_ok=True)

print(f'=== BACKUP COMPLETO COM FLUXO - {ts} ===\n')

# 1. Redis dump completo (agenda)
print('[1] Redis agenda - dump completo (RDB)...')
i, o, e = c.exec_command(f'mkdir -p {backup_dir}')
e.read()
i, o, e = c.exec_command('docker exec redis-agenda redis-cli BGSAVE')
time.sleep(3)
print(f'    {o.read().decode().strip()}')
i, o, e = c.exec_command(f'docker cp redis-agenda:/data/dump.rdb {backup_dir}/redis-agenda-dump.rdb')
time.sleep(2)
print('    RDB copiado')

# 2. Redis agenda - export de todas as keys para texto
print('\n[2] Redis agenda - export keys...')
i, o, e = c.exec_command(f'docker exec redis-agenda redis-cli --no-auth-warning KEYS "*" > {backup_dir}/redis-keys.txt')
time.sleep(2)
i, o, e = c.exec_command(f'wc -l {backup_dir}/redis-keys.txt')
time.sleep(1)
print(f'    {o.read().decode().strip()} keys')

# 3. Blacklist
print('\n[3] Blacklist...')
i, o, e = c.exec_command(f'docker exec redis-agenda redis-cli SMEMBERS agenda:blacklist > {backup_dir}/blacklist.txt')
time.sleep(1)
print('    OK')

# 4. Flow config do Redis
print('\n[4] Flow config...')
i, o, e = c.exec_command(f'docker exec redis-agenda redis-cli GET agenda:flow-config > {backup_dir}/flow-config.json')
time.sleep(1)
print('    OK')

# 5. n8n data
print('\n[5] n8n workflows...')
i, o, e = c.exec_command('ls -d /docker/n8n*/ 2>/dev/null')
time.sleep(1)
n8n_dirs = o.read().decode().strip()
print(f'    Diretórios: {n8n_dirs}')
if n8n_dirs:
    first_dir = n8n_dirs.split('\n')[0].strip()
    i, o, e = c.exec_command(f'cd /docker && tar czf {backup_dir}/n8n-data.tar.gz {first_dir.replace("/docker/","")}')
    time.sleep(10)
    print('    Compactado')

# 6. Evolution API
print('\n[6] Evolution API...')
i, o, e = c.exec_command(f'ls -d /docker/evolution*/ 2>/dev/null')
time.sleep(1)
evo_dirs = o.read().decode().strip()
print(f'    Diretórios: {evo_dirs}')
if evo_dirs:
    first_dir = evo_dirs.split('\n')[0].strip()
    i, o, e = c.exec_command(f'cd /docker && tar czf {backup_dir}/evolution-api.tar.gz {first_dir.replace("/docker/","")}')
    time.sleep(10)
    print('    Compactado')

# 7. Dashboard completo
print('\n[7] Dashboard...')
i, o, e = c.exec_command(f'cp /docker/dashboard/html/index.html {backup_dir}/dashboard-index.html')
time.sleep(2)
print('    OK')
i, o, e = c.exec_command(f'cp /docker/dashboard/whatsapp_agenda_gen.py {backup_dir}/whatsapp_agenda_gen.py')
e.read()
print('    OK')
i, o, e = c.exec_command(f'cp /docker/dashboard/gerar_dashboard_v2.py {backup_dir}/gerar_dashboard_v2.py')
e.read()
print('    OK')

# 8. Backend
print('\n[8] Backend (container)...')
i, o, e = c.exec_command(f'docker cp backend-agenda:/app/index.js {backup_dir}/index.js')
time.sleep(2)
print('    OK')

# 9. Listar tudo
print(f'\n[9] Conteúdo do backup:')
i, o, e = c.exec_command(f'ls -lh {backup_dir}/')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

i, o, e = c.exec_command(f'du -sh {backup_dir}/')
time.sleep(1)
total_server = o.read().decode().strip()
print(f'\nTotal servidor: {total_server}')

# 10. Baixar para local
print(f'\n[10] Baixando para {local_dir}...')
sftp = c.open_sftp()
i, o, e = c.exec_command(f'ls {backup_dir}/')
time.sleep(1)
files = o.read().decode().strip().split('\n')
for f in files:
    f = f.strip()
    if not f:
        continue
    remote = f'{backup_dir}/{f}'
    local = os.path.join(local_dir, f)
    try:
        sftp.get(remote, local)
        size = os.path.getsize(local)
        print(f'  [OK] {f} ({size:,} bytes)')
    except Exception as ex:
        print(f'  [!] {f}: {ex}')
sftp.close()

c.close()

total = sum(os.path.getsize(os.path.join(local_dir, f)) for f in os.listdir(local_dir))
print(f'\nTotal local: {total:,} bytes ({total/1024/1024:.1f} MB)')
print(f'\n=== BACKUP COMPLETO COM FLUXO CONCLUÍDO ===')
