import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Encontrar o backup 20260526_120555
print('[1] Procurando backup 20260526_120555...')
i, o, e = c.exec_command('find /docker/ -name "*20260526_120555*" -o -name "*20260526*" 2>/dev/null | grep -i backup | head -20')
time.sleep(3)
print(o.read().decode('utf-8', errors='replace').strip())

# 2. Listar backups de 26/05
print('\n[2] Todos os backups de 26/05:')
i, o, e = c.exec_command('ls -lh /docker/backup_20260526*/ 2>/dev/null')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

i, o, e = c.exec_command('ls -d /docker/backup_20260526* 2>/dev/null')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 3. Procurar no /docker/dashboard/backup*
print('\n[3] Backups no dashboard:')
i, o, e = c.exec_command('ls -d /docker/dashboard/backup* 2>/dev/null')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 4. Verificar se existe como tar.gz
print('\n[4] Tar.gz backups:')
i, o, e = c.exec_command('ls -lh /docker/backup*tar.gz 2>/dev/null')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 5. Procurar com find
print('\n[5] Find completo:')
i, o, e = c.exec_command('find /docker/ -maxdepth 2 -name "*120555*" 2>/dev/null')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip() or '    Nenhum resultado')

# 6. Backups do HTML por data 25-26 maio
print('\n[6] HTMLs de backup de 25-26/05:')
i, o, e = c.exec_command('ls -lt /docker/dashboard/html/index.html.bak*20260526* /docker/dashboard/html/index.html.bak*20260525* 2>/dev/null | head -10')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
