import paramiko, os

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

i, o, e = c.exec_command('cat /docker/whatsapp-agenda/docker-compose.yml')
content = o.read().decode('utf-8')

with open('docker-compose-remote.yml', 'w', encoding='utf-8') as f:
    f.write(content)

c.close()
print("Downloaded to docker-compose-remote.yml")
