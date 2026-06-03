import paramiko, os

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Upload schema
sftp = c.open_sftp()
sftp.put('schema.sql', '/tmp/schema.sql')
sftp.close()

# Execute schema inside container
print("Executing schema...")
cmd = "docker exec -i agenda-db psql -U agenda_user -d agenda < /tmp/schema.sql"
i, o, e = c.exec_command(cmd)

out = o.read().decode('utf-8')
err = e.read().decode('utf-8')

if out: print("OUT:", out)
if err: print("ERR:", err)

# Validate tables
i, o, e = c.exec_command("docker exec agenda-db psql -U agenda_user -d agenda -c '\\dt'")
print("Tables:", o.read().decode('utf-8'))

c.close()
