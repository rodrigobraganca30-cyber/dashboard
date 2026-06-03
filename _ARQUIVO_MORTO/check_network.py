import paramiko, os
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Verificar IP do container
print("=== IP DO CONTAINER BACKEND ===")
i, o, e = c.exec_command("docker inspect backend-agenda --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'")
ip = o.read().decode().strip()
print("IP:", ip)

# Testar health via IP do container
print("\n=== HEALTH VIA IP DO CONTAINER ===")
i, o, e = c.exec_command(f"curl -s http://{ip}:3001/health")
print(o.read().decode().strip())

# Testar /agenda/clients via IP do container  
print("\n=== /agenda/clients VIA IP DO CONTAINER ===")
i, o, e = c.exec_command(f"curl -s http://{ip}:3001/agenda/clients | head -c 500")
out = o.read().decode().strip()
print(f"Resposta ({len(out)} chars): {out[:500]}")

# Verificar docker-compose ports
print("\n=== DOCKER-COMPOSE PORTS DO BACKEND ===")
i, o, e = c.exec_command("docker port backend-agenda")
print(o.read().decode().strip() or "(nenhuma porta mapeada)")

# Verificar como o nginx frontend chega ao backend
print("\n=== NGINX CONFIG (se existe proxy) ===")
i, o, e = c.exec_command("docker exec dashboard-nginx cat /etc/nginx/conf.d/default.conf 2>/dev/null || echo 'sem config'")
print(o.read().decode().strip()[:2000])

# Verificar se existe um nginx para o WhatsApp
print("\n=== DOCKER NETWORKS ===")
i, o, e = c.exec_command("docker network ls --format='{{.Name}}'")
print(o.read().decode().strip())

# Verificar a rede do backend-agenda
print("\n=== REDES DO BACKEND-AGENDA ===")
i, o, e = c.exec_command("docker inspect backend-agenda --format='{{json .NetworkSettings.Networks}}' | python3 -m json.tool 2>/dev/null || docker inspect backend-agenda --format='{{json .NetworkSettings.Networks}}'")
print(o.read().decode().strip()[:2000])

c.close()
