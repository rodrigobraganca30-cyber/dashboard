import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

print('=== Backups de ontem 26/05 por volta das 12h ===\n')

# HTMLs de backup
print('[1] HTMLs de backup do dia 26/05:')
i, o, e = c.exec_command('ls -lt --time-style=long-iso /docker/dashboard/html/index.html.bak* | grep "2026-05-26"')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# Diretórios de backup
print('\n[2] Diretórios de backup do dia 26/05:')
i, o, e = c.exec_command('ls -ltd --time-style=long-iso /docker/backup*2026052* /docker/backups/backup*2026052* 2>/dev/null')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# Backup do dashboard
print('\n[3] Backup dashboard:')
i, o, e = c.exec_command('ls -ltd --time-style=long-iso /docker/dashboard/backup* 2>/dev/null')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# Procurar qualquer arquivo criado em 26/05 entre 11h-13h
print('\n[4] Arquivos de backup entre 11h-13h de 26/05:')
i, o, e = c.exec_command("find /docker/ -maxdepth 3 -newer /dev/null -name '*bak*' -o -name '*backup*' 2>/dev/null | while read f; do stat --format='%Y %n' \"$f\" 2>/dev/null; done | awk '$1 >= 1748264400 && $1 <= 1748271600 {print}'")
time.sleep(2)
out = o.read().decode('utf-8', errors='replace').strip()
print(out if out else '    Nenhum encontrado nesse horário')

# Procurar por timestamp 12 no nome
print('\n[5] Backups com "12" no nome:')
i, o, e = c.exec_command("find /docker/ -maxdepth 3 -name '*_12*' 2>/dev/null | head -10")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip() or '    Nenhum')

c.close()
