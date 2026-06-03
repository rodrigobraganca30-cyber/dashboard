import paramiko, os
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)
i, o, e = c.exec_command('python3 -c "import psycopg2"')
print("ERR:", e.read().decode())
print("OUT:", o.read().decode())
c.close()
