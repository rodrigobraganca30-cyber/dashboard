import paramiko, os, sys

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

sftp = c.open_sftp()
sftp.put('docker-compose-remote.yml', '/docker/whatsapp-agenda/docker-compose.yml')
sftp.close()
print("Uploaded docker-compose.yml")

print("Starting PostgreSQL and updating backend...")
i, o, e = c.exec_command('cd /docker/whatsapp-agenda && docker compose up -d')
err = e.read().decode('utf-8')
out = o.read().decode('utf-8')

if out: print("OUT:", out)
if err: print("ERR:", err)

print("Checking db status...")
i, o, e = c.exec_command('docker ps --filter name=agenda-db')
print(o.read().decode('utf-8'))

c.close()
