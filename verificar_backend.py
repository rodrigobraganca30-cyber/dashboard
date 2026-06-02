"""
verificar_backend.py
Verifica se o backend subiu e se a blacklist está acessível.
"""
import paramiko, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh_key = os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa')
pkey = paramiko.RSAKey.from_private_key_file(ssh_key)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('187.77.240.87', port=22, username='root', pkey=pkey)

# 1. Verifica se o container está rodando
print('[1] Status do container backend-agenda:')
stdin, stdout, stderr = client.exec_command('docker ps --filter name=backend-agenda --format "{{.Status}}"')
status = stdout.read().decode('utf-8').strip()
print(f'    {status}')

# 2. Verifica últimas linhas do log
print('\n[2] Últimas 10 linhas do log:')
stdin, stdout, stderr = client.exec_command('docker logs backend-agenda --tail 10 2>&1')
logs = stdout.read().decode('utf-8', errors='replace').strip()
print(logs)

# 3. Testa a rota /health
print('\n[3] Teste da rota /health:')
stdin, stdout, stderr = client.exec_command('curl -s http://localhost:3001/health 2>/dev/null || echo "FALHA"')
health = stdout.read().decode('utf-8').strip()
print(f'    {health}')

# 4. Testa a rota /agenda/blacklist
print('\n[4] Teste da rota /agenda/blacklist (primeiros 5):')
stdin, stdout, stderr = client.exec_command('curl -s http://localhost:3001/agenda/blacklist 2>/dev/null | head -c 200')
bl = stdout.read().decode('utf-8').strip()
print(f'    {bl[:200]}...')

# 5. Contagem de itens na blacklist
print('\n[5] Contagem da Blacklist no Redis:')
stdin, stdout, stderr = client.exec_command('docker exec redis-agenda redis-cli SCARD agenda:blacklist')
count = stdout.read().decode('utf-8').strip()
print(f'    Total de números na Blacklist: {count}')

client.close()
print('\n=== VERIFICAÇÃO CONCLUÍDA ===')
