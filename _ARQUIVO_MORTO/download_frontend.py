import paramiko, os

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

sftp = c.open_sftp()
sftp.get('/docker/whatsapp-agenda/frontend/index.html', 'frontend/index.html')
sftp.close()
c.close()
print("Downloaded frontend/index.html")
