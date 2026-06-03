import paramiko, os

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

print("Uploading index_vps.js to VPS...")
sftp = c.open_sftp()
sftp.put('index_vps.js', '/docker/whatsapp-agenda/backend/index.js')
sftp.close()

print("Restarting container...")
i, o, e = c.exec_command('docker restart backend-agenda')
print(o.read().decode())

c.close()
print("Deploy finished.")
