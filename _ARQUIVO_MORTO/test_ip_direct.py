import paramiko, os
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Verificar porta do nginx
print("=== Porta do dashboard-nginx ===")
i, o, e = c.exec_command("docker port dashboard-nginx")
print(o.read().decode().strip())

# Verificar o compose original
print("\n=== Docker compose labels ===")
i, o, e = c.exec_command("docker inspect dashboard-nginx --format='{{json .Config.Labels}}' | python3 -m json.tool 2>/dev/null | head -30")
print(o.read().decode()[:1500])

# O nginx escuta na 80 mas pode estar atrás do Traefik
# Testar diretamente pelo IP do container na rede correta
print("\n=== Teste via IP direto do container na porta 80 ===")
i, o, e = c.exec_command("curl -s http://172.20.0.2:80/agenda/ | head -c 300")
print(o.read().decode()[:300])

print("\n=== Teste via IP direto /agenda/script.js ===")
i, o, e = c.exec_command("curl -s http://172.20.0.2:80/agenda/script.js | head -c 200")
print(o.read().decode()[:200])

print("\n=== Teste via IP direto /api/agenda/health ===")
i, o, e = c.exec_command("curl -s http://172.20.0.2:80/api/agenda/health")
print(o.read().decode()[:300])

print("\n=== Teste via IP direto /api/agenda/agenda/clients (com Referer) ===")
i, o, e = c.exec_command("curl -s -H 'Referer: https://svoboda.rtflowapp.com/' http://172.20.0.2:80/api/agenda/agenda/clients | head -c 500")
print(o.read().decode()[:500])

c.close()
