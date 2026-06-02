import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Listar todos os backups que fiz para encontrar o estado correto
print('[1] Backups disponíveis:')
i, o, e = c.exec_command("ls -lt /docker/dashboard/html/index.html.bak* | head -15")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# O estado que funcionava era ANTES de eu restaurar o DEFINITIVO
# Ou seja, index.html.bak.pre_definitivo
print('\n[2] Verificando bak.pre_definitivo:')
i, o, e = c.exec_command("ls -lh /docker/dashboard/html/index.html.bak.pre_definitivo 2>/dev/null")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

print('\n[3] Verificando bak.pre_fix_final:')
i, o, e = c.exec_command("ls -lh /docker/dashboard/html/index.html.bak.pre_fix_final 2>/dev/null")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# Verificar qual era o bom (bak2 com bloqueado injetado)
print('\n[4] Verificando bak.broken_blacklist (era o bak2 + bloqueado):')
i, o, e = c.exec_command("ls -lh /docker/dashboard/html/index.html.bak.broken_blacklist 2>/dev/null")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
