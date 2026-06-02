import paramiko, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Verificar onde o arquivo patcheado foi colocado no host
print('[1] Verificando arquivo patcheado no host...')
i, o, e = c.exec_command("ls -la /docker/whatsapp-agenda/backend/index.js 2>/dev/null")
r1 = o.read().decode().strip()
print(f'    /docker/whatsapp-agenda/backend/index.js: {r1 or "NAO EXISTE"}')

i, o, e = c.exec_command("ls -la /root/index.js 2>/dev/null")
r2 = o.read().decode().strip()
print(f'    /root/index.js: {r2 or "NAO EXISTE"}')

# Verificar se "blacklist" está no arquivo do host
for path in ['/docker/whatsapp-agenda/backend/index.js', '/root/index.js']:
    i, o, e = c.exec_command(f"grep -c 'blacklist' {path} 2>/dev/null")
    cnt = o.read().decode().strip()
    if cnt and cnt != '0':
        print(f'\n    ** ENCONTRADO! {path} tem {cnt} ocorrências de "blacklist" **')

# 2. Verificar a estrutura docker
print('\n[2] Estrutura Docker:')
i, o, e = c.exec_command("docker inspect backend-agenda --format='{{.Config.WorkingDir}}'")
workdir = o.read().decode().strip()
print(f'    WorkDir: {workdir}')

i, o, e = c.exec_command("docker inspect backend-agenda --format='{{.Config.Image}}'")
image = o.read().decode().strip()
print(f'    Image: {image}')

# 3. Listar o Dockerfile ou docker-compose para entender como o backend é construído
print('\n[3] docker-compose:')
i, o, e = c.exec_command("cat /docker/whatsapp-agenda/docker-compose.yml 2>/dev/null || cat /docker/whatsapp-agenda/docker-compose.yaml 2>/dev/null")
compose = o.read().decode('utf-8', errors='replace').strip()
print(compose[:1000])

c.close()
