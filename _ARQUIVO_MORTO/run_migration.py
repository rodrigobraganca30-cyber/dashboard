import paramiko, os

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

sftp = c.open_sftp()
sftp.put('migrate.js', '/docker/whatsapp-agenda/backend/migrate.js')
sftp.close()

print("Copying to container and running migration...")
cmd = """
docker cp /docker/whatsapp-agenda/backend/migrate.js backend-agenda:/app/migrate.js
docker exec backend-agenda node migrate.js
"""
i, o, e = c.exec_command(cmd)
print("OUT:", o.read().decode())
print("ERR:", e.read().decode())

c.close()
