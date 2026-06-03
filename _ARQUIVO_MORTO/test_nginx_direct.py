import paramiko, os
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Testar diretamente no container nginx
print("=== 1. GET /agenda/ direto no container NGINX ===")
i, o, e = c.exec_command("docker exec dashboard-nginx wget -qO- http://localhost/agenda/ 2>&1 | head -c 300")
print(o.read().decode()[:300])

print("\n=== 2. GET /agenda/script.js direto no container ===")
i, o, e = c.exec_command("docker exec dashboard-nginx wget -qO- http://localhost/agenda/script.js 2>&1 | head -c 200")
print(o.read().decode()[:200])

print("\n=== 3. GET /api/agenda/health direto no container ===")
i, o, e = c.exec_command("docker exec dashboard-nginx wget -qO- http://localhost/api/agenda/health 2>&1")
print(o.read().decode()[:300])

print("\n=== 4. GET /api/agenda/agenda/clients com Referer ===")
i, o, e = c.exec_command("docker exec dashboard-nginx wget -qO- --header='Referer: https://svoboda.rtflowapp.com/' http://localhost/api/agenda/agenda/clients 2>&1 | head -c 500")
print(o.read().decode()[:500])

# Verificar se dashboard-nginx tem curl
print("\n=== 5. Network: dashboard-nginx networks ===")
i, o, e = c.exec_command("docker inspect dashboard-nginx --format='{{range .NetworkSettings.Networks}}{{.NetworkID | printf \"%.12s\"}} {{.IPAddress}}\n{{end}}'")
print(o.read().decode().strip())

# Verificar se backend-agenda está na mesma rede do nginx
print("\n=== 6. Dashboard networks ===")
i, o, e = c.exec_command("docker network inspect dashboard_default --format='{{range .Containers}}{{.Name}} {{.IPv4Address}}\n{{end}}'")
print(o.read().decode().strip())

c.close()
