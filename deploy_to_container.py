import paramiko, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Copiar o arquivo patcheado para dentro do container
print('[1] Copiando index.js patcheado para dentro do container...')
i, o, e = c.exec_command('docker cp /docker/whatsapp-agenda/backend/index.js backend-agenda:/app/index.js')
err = e.read().decode().strip()
out = o.read().decode().strip()
if err:
    print(f'    ERRO: {err}')
    sys.exit(1)
print('    OK - Arquivo copiado.')

# 2. Verificar se está lá dentro agora
print('\n[2] Verificando conteúdo dentro do container...')
i, o, e = c.exec_command("docker exec backend-agenda grep -c 'blacklist' /app/index.js")
cnt = o.read().decode().strip()
print(f'    Ocorrências de "blacklist": {cnt}')

i, o, e = c.exec_command("docker exec backend-agenda grep -c 'validateAndCleanPhone' /app/index.js")
cnt2 = o.read().decode().strip()
print(f'    Ocorrências de "validateAndCleanPhone": {cnt2}')

# 3. Reiniciar o container
print('\n[3] Reiniciando container...')
i, o, e = c.exec_command('docker restart backend-agenda')
import time
time.sleep(5)
out = o.read().decode().strip()
print(f'    {out}')

# 4. Verificar se subiu
print('\n[4] Verificando status...')
i, o, e = c.exec_command('docker ps --filter name=backend-agenda --format "{{.Status}}"')
status = o.read().decode().strip()
print(f'    Status: {status}')

# 5. Esperar e verificar log
time.sleep(3)
i, o, e = c.exec_command('docker logs backend-agenda --tail 5 2>&1')
logs = o.read().decode('utf-8', errors='replace').strip()
print(f'\n[5] Últimas 5 linhas do log:\n{logs}')

# 6. Testar rota blacklist
time.sleep(2)
print('\n[6] Testando rota /agenda/blacklist...')
i, o, e = c.exec_command('curl -s http://localhost:3001/agenda/blacklist 2>/dev/null | wc -c')
size = o.read().decode().strip()
print(f'    Tamanho da resposta: {size} bytes')

i, o, e = c.exec_command('curl -s http://localhost:3001/agenda/blacklist 2>/dev/null | head -c 120')
preview = o.read().decode().strip()
print(f'    Preview: {preview}')

c.close()
print('\n=== DEPLOY CONCLUÍDO ===')
