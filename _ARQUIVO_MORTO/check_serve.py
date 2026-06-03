import paramiko, os
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Verificar onde o NGINX do dashboard serve os arquivos
print("=== CONTEÚDO de /usr/share/nginx/html/ no dashboard-nginx ===")
i, o, e = c.exec_command("docker exec dashboard-nginx ls -la /usr/share/nginx/html/")
print(o.read().decode().strip())

print("\n=== CONTEÚDO de /usr/share/nginx/html/agenda/ no dashboard-nginx ===")
i, o, e = c.exec_command("docker exec dashboard-nginx ls -la /usr/share/nginx/html/agenda/ 2>&1")
print(o.read().decode().strip())

# Verificar onde o frontend do backend-agenda é servido
print("\n=== CONTEÚDO de /app/public/ no backend-agenda ===")
i, o, e = c.exec_command("docker exec backend-agenda ls -la /app/public/ 2>&1")
print(o.read().decode().strip())

# Verificar volumes do dashboard-nginx
print("\n=== VOLUMES DO DASHBOARD-NGINX ===")
i, o, e = c.exec_command("docker inspect dashboard-nginx --format='{{range .Mounts}}{{.Source}} -> {{.Destination}}\n{{end}}'")
print(o.read().decode().strip())

# Verificar volumes do backend-agenda
print("\n=== VOLUMES DO BACKEND-AGENDA ===")
i, o, e = c.exec_command("docker inspect backend-agenda --format='{{range .Mounts}}{{.Source}} -> {{.Destination}}\n{{end}}'")
print(o.read().decode().strip())

c.close()
