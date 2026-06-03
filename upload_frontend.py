import paramiko, os

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

sftp = c.open_sftp()
base = '/docker/whatsapp-agenda/frontend/'
print("Uploading frontend files to VPS...")
sftp.put('frontend/index.html', base + 'index.html')
sftp.put('frontend/style.css', base + 'style.css')
sftp.put('frontend/script.js', base + 'script.js')
sftp.close()
c.close()
print("Frontend files uploaded successfully!")
