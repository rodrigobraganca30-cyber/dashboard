import paramiko, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Testa rota /agenda/blacklist
i, o, e = c.exec_command('curl -s http://localhost:3001/agenda/blacklist 2>/dev/null | wc -c')
size = o.read().decode().strip()
print(f'Tamanho da resposta da API /agenda/blacklist: {size} bytes')

# Verifica se retorna JSON array
i, o, e = c.exec_command('curl -s http://localhost:3001/agenda/blacklist 2>/dev/null | head -c 80')
preview = o.read().decode().strip()
print(f'Preview: {preview}...')

# Verifica erros recentes no log
i, o, e = c.exec_command('docker logs backend-agenda --tail 3 2>&1')
logs = o.read().decode('utf-8', errors='replace').strip()
print(f'\nUltimas 3 linhas do log:\n{logs}')

c.close()
