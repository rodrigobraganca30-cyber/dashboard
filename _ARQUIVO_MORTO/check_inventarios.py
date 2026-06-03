import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Verificar onde ficam os relatorios de inventario
print('[1] Procurando arquivos de inventario...')
i, o, e = c.exec_command('find /docker/dashboard -name "*inventar*" -type f 2>/dev/null | head -30')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip() or '  Nada em /docker/dashboard')

print('\n[2] Procurando pasta de relatorios...')
i, o, e = c.exec_command('find /docker/dashboard -name "*relator*" -type d 2>/dev/null; find /docker/dashboard -name "*report*" -type d 2>/dev/null; find /docker/dashboard -name "*csv*" -type d 2>/dev/null')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip() or '  Nenhuma pasta encontrada')

print('\n[3] Listando pastas em /docker/dashboard...')
i, o, e = c.exec_command('ls -la /docker/dashboard/')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

print('\n[4] Listando pastas em /docker/dashboard/html...')
i, o, e = c.exec_command('ls -la /docker/dashboard/html/')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

print('\n[5] Procurando CSVs de inventario...')
i, o, e = c.exec_command('find /docker -name "*inventar*" -type f 2>/dev/null | sort | tail -30')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip() or '  Nenhum CSV encontrado')

print('\n[6] Procurando por data nos nomes de arquivo...')
i, o, e = c.exec_command('find /docker/dashboard -name "*.csv" -o -name "*.xlsx" -o -name "*.xls" 2>/dev/null | sort | tail -30')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip() or '  Nenhum arquivo')

print('\n[7] Procurando inventarios em qualquer local...')
i, o, e = c.exec_command('find /docker -maxdepth 4 -name "*inventar*" 2>/dev/null | sort')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip() or '  Nenhum')

c.close()
