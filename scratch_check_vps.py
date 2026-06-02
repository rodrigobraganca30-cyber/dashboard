import paramiko, os, sys

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

print("--- DOCKER PS ---")
i, o, e = c.exec_command('docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}"')
print(o.read().decode())

print("--- DOCKER COMPOSE FILE ---")
i, o, e = c.exec_command('cat /docker/docker-compose.yml 2>/dev/null || cat /docker/whatsapp-agenda/docker-compose.yml 2>/dev/null')
print(o.read().decode())

c.close()
