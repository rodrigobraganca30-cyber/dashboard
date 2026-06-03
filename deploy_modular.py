import paramiko, os

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

base = '/docker/whatsapp-agenda/'

# 1. Criar pastas de módulos no servidor
print("[1] Criando pastas de módulos...")
for folder in ['config', 'utils', 'services']:
    i, o, e = c.exec_command(f'mkdir -p {base}{folder}')
    o.read()

# 2. Upload dos módulos
sftp = c.open_sftp()
files = [
    ('config/logger.js', f'{base}config/logger.js'),
    ('config/redis.js',  f'{base}config/redis.js'),
    ('utils/phone.js',   f'{base}utils/phone.js'),
    ('services/metaService.js', f'{base}services/metaService.js'),
    ('index_vps.js',     f'{base}index_vps.js'),
]
print("[2] Uploading arquivos...")
for local, remote in files:
    sftp.put(local, remote)
    print(f"    OK {local} -> {remote}")
sftp.close()

# 3. Copiar tudo para dentro do container
print("\n[3] Copiando para dentro do container...")
for folder in ['config', 'utils', 'services']:
    i, o, e = c.exec_command(f'docker cp {base}{folder}/. backend-agenda:/app/{folder}/')
    o.read()
    print(f"    OK {folder}/ copiado")

i, o, e = c.exec_command(f'docker cp {base}index_vps.js backend-agenda:/app/index.js')
o.read()
print("    OK index_vps.js -> /app/index.js")

# 4. Verificar estrutura dentro do container
print("\n[4] Verificando estrutura...")
i, o, e = c.exec_command('docker exec backend-agenda find /app -maxdepth 2 -name "*.js" -not -path "*/node_modules/*"')
print(o.read().decode().strip())

# 5. Reiniciar
print("\n[5] Reiniciando backend...")
i, o, e = c.exec_command('docker restart backend-agenda')
print(o.read().decode().strip())

import time
time.sleep(3)

# 6. Verificar logs
print("\n[6] Últimos logs...")
i, o, e = c.exec_command('docker logs backend-agenda --tail 8 2>&1')
print(o.read().decode().strip())

c.close()
print("\n=== DEPLOY MODULAR CONCLUÍDO ===")
