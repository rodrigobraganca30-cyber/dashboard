import paramiko, os
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

print("Installing pg in backend...")
i, o, e = c.exec_command('docker exec backend-agenda npm install pg')
print("OUT:", o.read().decode())
print("ERR:", e.read().decode())

# Add to package.json on VPS so rebuilds don't lose it
cmd = """docker exec backend-agenda sh -c "sed -i 's/\\\"dependencies\\\": {/\\\"dependencies\\\": { \\\"pg\\\": \\\"^8.11.5\\\",/g' package.json" """
i, o, e = c.exec_command(cmd)

c.close()
