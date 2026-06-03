import paramiko, os
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

print("=== FULL ERROR LOG ===")
i, o, e = c.exec_command("docker logs backend-agenda --tail 30 2>&1")
print(o.read().decode().strip())

c.close()
