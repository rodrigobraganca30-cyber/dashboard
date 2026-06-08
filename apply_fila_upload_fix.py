import paramiko, os, sys
sys.stdout.reconfigure(encoding='utf-8')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

sftp = c.open_sftp()
remote_path = '/docker/whatsapp-agenda/backend/index.js'
try:
    with sftp.open(remote_path, 'r') as f:
        js = f.read().decode('utf-8')
except Exception as e:
    print(f"Error reading {remote_path}: {e}")
    sys.exit(1)

old_code = "    const newClients = req.body.clients || [];\n    if (!Array.isArray(newClients)) return res.status(400).json({ error: 'clients deve ser array' });"

new_code = """    const newClients = req.body.clients || [];
    if (!Array.isArray(newClients)) return res.status(400).json({ error: 'clients deve ser array' });
    
    // ATTACH THE FILA
    const globalFila = (req.body.fila || 'CONFIRMACAO').toUpperCase();
    newClients.forEach(c => {
      c.fila = (c.fila || globalFila || 'CONFIRMACAO').toUpperCase();
    });"""

if old_code in js:
    js = js.replace(old_code, new_code, 1)
    with sftp.open(remote_path, 'w') as f:
        f.write(js)
    print("Patch applied to index.js on VPS.")
else:
    if "globalFila" in js:
        print("Patch already applied.")
    else:
        print("ERROR: old_code not found in index.js")

sftp.close()

# Restart backend
print("Restarting backend...")
i, o, e = c.exec_command("cd /docker/whatsapp-agenda && docker compose up -d --force-recreate backend")
print("Docker compose restart result:", o.read().decode())
print("Docker compose error:", e.read().decode())
c.close()
