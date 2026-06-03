import paramiko, os
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

print("=== CONTAINER STATE ===")
i, o, e = c.exec_command('docker inspect backend-agenda --format="{{.State.Status}}"')
print("Status:", o.read().decode().strip())

print("\n=== HEALTH CHECK VERBOSE ===")
i, o, e = c.exec_command("curl -sv http://localhost:3001/health 2>&1")
print(o.read().decode()[:1000])

print("\n=== ÚLTIMAS 30 LINHAS DO LOG ===")
i, o, e = c.exec_command("docker logs backend-agenda --tail 30 2>&1")
print(o.read().decode())

print("\n=== TESTE /agenda/clients VERBOSE ===")
i, o, e = c.exec_command("curl -sv http://localhost:3001/agenda/clients 2>&1 | head -30")
print(o.read().decode()[:1500])

c.close()
