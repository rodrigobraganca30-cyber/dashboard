import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

print('Procurando ATIVIDADES...')
i, o, e = c.exec_command('find / -maxdepth 5 -iname "*ATIVIDADE*" -type f 2>/dev/null')
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip() or 'Nada')

print('\nProcurando *.xlsx...')
i, o, e = c.exec_command('find /docker -name "*.xlsx" -type f 2>/dev/null')
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip() or 'Nada')

print('\nProcurando O.S...')
i, o, e = c.exec_command('find / -maxdepth 5 -iname "*O.S*" -name "*.xlsx" -type f 2>/dev/null')
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip() or 'Nada')

c.close()
