import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Extrair o trecho do HTML com a listagem de inventarios
print('Extraindo formato da listagem...')
i, o, e = c.exec_command("grep -n -A2 'inventario_20-05' /docker/dashboard/html/index.html | head -20")
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

print('\n--- Formato das linhas ---')
i, o, e = c.exec_command("grep -n 'inventario_1[2-5]-05' /docker/dashboard/html/index.html | head -10")
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

print('\n--- Contexto ao redor de inventario_20 ---')
i, o, e = c.exec_command("grep -n -B5 -A5 '20-05-2026' /docker/dashboard/html/index.html | head -30")
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

print('\n--- DOWNLOAD DE INVENTARIOS section ---')
i, o, e = c.exec_command("grep -n -i -A30 'download de invent' /docker/dashboard/html/index.html | head -40")
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
