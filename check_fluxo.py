import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Listar todos os diretórios em /docker relacionados
print('[1] Diretórios em /docker/:')
i, o, e = c.exec_command('ls -d /docker/*/ 2>/dev/null')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 2. Verificar n8n
print('\n[2] n8n data:')
i, o, e = c.exec_command('ls -la /docker/n8n*/ 2>/dev/null | head -10')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 3. Verificar evolution-api
print('\n[3] Evolution API:')
i, o, e = c.exec_command('ls -la /docker/evolution*/ 2>/dev/null | head -10')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 4. Verificar flow configs no Redis
print('\n[4] Flow configs no Redis:')
i, o, e = c.exec_command('docker exec redis-agenda redis-cli KEYS "*flow*" 2>/dev/null')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

i, o, e = c.exec_command('docker exec redis-agenda redis-cli KEYS "*fluxo*" 2>/dev/null')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 5. Dump completo das keys do Redis
print('\n[5] Todas as keys do Redis agenda:')
i, o, e = c.exec_command('docker exec redis-agenda redis-cli KEYS "*" 2>/dev/null')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 6. Containers rodando
print('\n[6] Containers rodando:')
i, o, e = c.exec_command('docker ps --format "{{.Names}}: {{.Image}}" | sort')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
