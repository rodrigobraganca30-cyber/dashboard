import paramiko, os
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

print("=== REDIS-AGENDA (container do WhatsApp) ===")
i, o, e = c.exec_command("docker exec redis-agenda redis-cli DBSIZE")
print("Total keys:", o.read().decode().strip())

i, o, e = c.exec_command("docker exec redis-agenda redis-cli KEYS 'agenda:*'")
keys = o.read().decode().strip()
if keys:
    lines = keys.split('\n')
    print(f"Keys 'agenda:*': {len(lines)} encontradas")
    for line in lines[:15]:
        print(f"  - {line}")
    if len(lines) > 15:
        print(f"  ... e mais {len(lines)-15}")
else:
    print("Keys 'agenda:*': NENHUMA")

# Verificar se a rota /agenda/clients retorna dados do PG
print("\n=== TESTE API /agenda/clients ===")
i, o, e = c.exec_command("curl -s http://localhost:3001/agenda/clients | head -c 500")
out = o.read().decode().strip()
print(f"Resposta (primeiros 500 chars): {out[:500]}")

# Verificar health
print("\n=== HEALTH ===")
i, o, e = c.exec_command("curl -s http://localhost:3001/health")
print(o.read().decode().strip())

# Verificar se o backend tem erros PG
print("\n=== ERROS PG NOS LOGS ===")
i, o, e = c.exec_command("docker logs backend-agenda 2>&1 | grep -i 'pg\\|postgres\\|shadow' | tail -10")
pg_errors = o.read().decode().strip()
print(pg_errors if pg_errors else "(nenhum log de PG encontrado)")

c.close()
