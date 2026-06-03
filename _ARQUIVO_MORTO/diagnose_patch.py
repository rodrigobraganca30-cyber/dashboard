import paramiko, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Vamos ver se as rotas de blacklist existem no index.js
i, o, e = c.exec_command("docker exec backend-agenda grep -n 'blacklist' /app/index.js")
result = o.read().decode('utf-8', errors='replace').strip()
print('[1] Ocorrências de "blacklist" no index.js do container:')
if result:
    for line in result.split('\n'):
        print(f'    {line}')
else:
    print('    NENHUMA - as rotas NÃO foram injetadas!')

# Verifica se validateAndCleanPhone existe
i, o, e = c.exec_command("docker exec backend-agenda grep -n 'validateAndCleanPhone' /app/index.js")
result2 = o.read().decode('utf-8', errors='replace').strip()
print('\n[2] Ocorrências de "validateAndCleanPhone":')
if result2:
    for line in result2.split('\n'):
        print(f'    {line}')
else:
    print('    NENHUMA - a função NÃO foi injetada!')

# Verifica se o arquivo foi atualizado (data/hora)
i, o, e = c.exec_command("docker exec backend-agenda ls -la /app/index.js")
result3 = o.read().decode('utf-8', errors='replace').strip()
print(f'\n[3] Data do arquivo: {result3}')

# Verifica o método de deploy - se copiou para o lugar certo
i, o, e = c.exec_command("docker inspect backend-agenda --format='{{range .Mounts}}{{.Source}}:{{.Destination}} {{end}}'")
result4 = o.read().decode('utf-8', errors='replace').strip()
print(f'\n[4] Mounts do container: {result4}')

c.close()
