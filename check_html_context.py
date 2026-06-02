import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Verificar o conteúdo exato entre linhas 2900-2940 (onde termina o disparo e onde está o btn-cfg)
print('[1] Contexto ao redor do btn-cfg (linhas 2900-2950):')
i, o, e = c.exec_command("sed -n '2900,2950p' /docker/dashboard/html/index.html")
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

print('\n[2] Onde o wa-disparo fecha (</div> antes de SUB: Configuração):')
i, o, e = c.exec_command("sed -n '3020,3040p' /docker/dashboard/html/index.html")
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

# Ver onde exatamente o disparo abre e fecha
print('\n[3] Linhas 2825-2830:')
i, o, e = c.exec_command("sed -n '2825,2835p' /docker/dashboard/html/index.html")
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
