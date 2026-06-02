import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Restaurar o estado que funcionava
print('[1] Restaurando bak.pre_definitivo...')
i, o, e = c.exec_command('cp /docker/dashboard/html/index.html /docker/dashboard/html/index.html.bak.pre_rollback')
e.read()
i, o, e = c.exec_command('cp /docker/dashboard/html/index.html.bak.pre_definitivo /docker/dashboard/html/index.html')
err = e.read().decode().strip()
print(f'    {"OK" if not err else "ERRO: " + err}')

# Verificar
print('\n[2] Verificação:')
i, o, e = c.exec_command("grep -c 'function showWaSub' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    showWaSub: {o.read().decode().strip()}')
i, o, e = c.exec_command("grep -c 'bloqueado' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    bloqueado: {o.read().decode().strip()}')
i, o, e = c.exec_command("grep -c 'Carregar Templates' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    Templates: {o.read().decode().strip()}')

c.close()
print('\n=== RESTAURADO ===')
