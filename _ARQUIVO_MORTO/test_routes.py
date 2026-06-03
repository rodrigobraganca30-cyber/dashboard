import paramiko, os
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# O NGINX faz: /api/agenda/* -> proxy para http://backend-agenda:3001/*
# Então /api/agenda/health -> backend:3001/health
# E /api/agenda/agenda/clients -> backend:3001/agenda/clients
# O script.js usa BACKEND + "/health", BACKEND + "/agenda/clients", etc.
# Então BACKEND = "/api/agenda" está correto!

# Testar as rotas como o browser faria
print("=== /api/agenda/health ===")
i, o, e = c.exec_command("curl -s -H 'Referer: https://svoboda.rtflowapp.com/agenda/' http://172.20.0.2:80/api/agenda/health")
print(o.read().decode()[:300])

print("\n=== /api/agenda/all-status ===")
i, o, e = c.exec_command("curl -s -H 'Referer: https://svoboda.rtflowapp.com/agenda/' http://172.20.0.2:80/api/agenda/all-status | head -c 500")
out = o.read().decode('utf-8', errors='replace')[:500]
print(out)

print("\n=== /api/agenda/agenda/clients ===")
i, o, e = c.exec_command("curl -s -H 'Referer: https://svoboda.rtflowapp.com/agenda/' http://172.20.0.2:80/api/agenda/agenda/clients | head -c 500")
out = o.read().decode('utf-8', errors='replace')[:500]
print(out)

c.close()
