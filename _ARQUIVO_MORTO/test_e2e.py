import paramiko, os
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Testar se /agenda/ serve o novo HTML
print("=== 1. GET /agenda/ (via NGINX) ===")
i, o, e = c.exec_command("curl -s http://localhost/agenda/ | head -c 300")
print(o.read().decode()[:300])

# 2. Testar se /agenda/style.css serve
print("\n=== 2. GET /agenda/style.css ===")
i, o, e = c.exec_command("curl -s http://localhost/agenda/style.css | head -c 200")
print(o.read().decode()[:200])

# 3. Testar se /agenda/script.js serve  
print("\n=== 3. GET /agenda/script.js ===")
i, o, e = c.exec_command("curl -s http://localhost/agenda/script.js | head -c 200")
print(o.read().decode()[:200])

# 4. Testar se /api/agenda/health funciona
print("\n=== 4. GET /api/agenda/health ===")
i, o, e = c.exec_command("curl -s http://localhost/api/agenda/health")
print(o.read().decode().strip())

# 5. Testar se /api/agenda/agenda/clients funciona (com Referer simulando browser)
print("\n=== 5. GET /api/agenda/agenda/clients (com Referer) ===")
i, o, e = c.exec_command("curl -s -H 'Referer: https://svoboda.rtflowapp.com/agenda/' http://localhost/api/agenda/agenda/clients | head -c 500")
out = o.read().decode().strip()
print(f"({len(out)} chars): {out[:500]}")

c.close()
