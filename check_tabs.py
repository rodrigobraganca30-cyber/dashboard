import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Verificar se o HTML gerado tem erros JS - checar a função showWaSub
print('[1] Verificando showWaSub no HTML gerado:')
i, o, e = c.exec_command("grep -n 'showWaSub' /docker/dashboard/index.html | head -10")
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

# Verificar se há erros de chaves no JS (f-string issue)
print('\n[2] Verificando se há chaves soltas ({) no JS:')
i, o, e = c.exec_command("grep -n 'function showWaSub' /docker/dashboard/index.html")
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

# Verificar se o bloqueado tem chaves duplas corretas
print('\n[3] Verificando bloqueado no HTML gerado:')
i, o, e = c.exec_command("grep -c 'bloqueado' /docker/dashboard/index.html")
time.sleep(1)
print(f'    Ocorrências: {o.read().decode().strip()}')

# Verificar se a variável WA_STATUS_LABELS está correta no HTML
print('\n[4] WA_STATUS_LABELS no HTML:')
i, o, e = c.exec_command("grep 'WA_STATUS_LABELS' /docker/dashboard/index.html | head -c 300")
time.sleep(1)
out = o.read().decode('utf-8', errors='replace').strip()
print(f'    {out[:300]}')

# Checar o bloco de JS gerado para ver se tem syntax error
print('\n[5] Verificando últimas linhas antes/depois do bloqueado:')
i, o, e = c.exec_command("grep -n 'Bloqueado' /docker/dashboard/index.html")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
