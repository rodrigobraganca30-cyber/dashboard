import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

i, o, e = c.exec_command("grep -n 'Baixar Planilha' /docker/dashboard/html/index.html | head -5")
time.sleep(2)
print('Baixar Planilha lines:')
print(o.read().decode('utf-8', errors='replace').strip())

i, o, e = c.exec_command("grep -n '20-05-2026' /docker/dashboard/html/index.html | head -5")
time.sleep(2)
print('\n20-05-2026 lines:')
print(o.read().decode('utf-8', errors='replace').strip())

i, o, e = c.exec_command("grep -n '07-05-2026' /docker/dashboard/html/index.html | head -3")
time.sleep(2)
print('\n07-05-2026 lines:')
print(o.read().decode('utf-8', errors='replace').strip())

# Get the actual line content around Baixar
i, o, e = c.exec_command("grep -n 'Baixar' /docker/dashboard/html/index.html | head -3")
time.sleep(2)
print('\nBaixar refs:')
print(o.read().decode('utf-8', errors='replace').strip())

# Get actual format - extract 200 chars around first inventory link
i, o, e = c.exec_command(r"python3 -c \"h=open('/docker/dashboard/html/index.html').read(); i=h.find('inventario_20-05'); print(h[max(0,i-200):i+200]) if i>0 else print('NOT FOUND')\"")
time.sleep(3)
print('\nContext around inventario_20-05:')
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
