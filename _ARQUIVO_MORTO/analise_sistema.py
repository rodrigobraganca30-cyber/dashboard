import paramiko, os

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

def run(cmd):
    i, o, e = c.exec_command(cmd)
    out = o.read().decode().strip()
    err = e.read().decode().strip()
    return out, err

print("=" * 60)
print("  ANÁLISE COMPLETA DO SISTEMA - SVOBODA")
print("=" * 60)

# 1. Containers
print("\n[1] CONTAINERS RODANDO")
out, _ = run("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'")
print(out)

# 2. Backend logs
print("\n[2] BACKEND LOGS (últimas 15 linhas)")
out, _ = run("docker logs backend-agenda --tail 15 2>&1")
print(out)

# 3. PostgreSQL tabelas
print("\n[3] POSTGRESQL - TABELAS")
out, _ = run("""docker exec agenda-db psql -U agenda_user -d agenda -c "SELECT tablename FROM pg_tables WHERE schemaname='public';" """)
print(out)

# 4. PostgreSQL contagens
print("\n[4] POSTGRESQL - CONTAGENS")
out, _ = run("""docker exec agenda-db psql -U agenda_user -d agenda -c "SELECT 'clientes' as tabela, count(*) FROM clientes UNION ALL SELECT 'mensagens', count(*) FROM mensagens UNION ALL SELECT 'blacklist', count(*) FROM blacklist UNION ALL SELECT 'logs', count(*) FROM logs;" """)
print(out)

# 5. Amostra de clientes
print("\n[5] AMOSTRA DE CLIENTES (5 primeiros)")
out, _ = run("""docker exec agenda-db psql -U agenda_user -d agenda -c "SELECT id, nome, telefone, cidade, status_atual FROM clientes LIMIT 5;" """)
print(out)

# 6. Amostra de mensagens
print("\n[6] AMOSTRA DE MENSAGENS (5 últimas)")
out, _ = run("""docker exec agenda-db psql -U agenda_user -d agenda -c "SELECT telefone, remetente, LEFT(texto,40) as texto, timestamp FROM mensagens ORDER BY id DESC LIMIT 5;" """)
print(out)

# 7. Frontend files no servidor
print("\n[7] FRONTEND FILES NO SERVIDOR")
out, _ = run("ls -la /docker/whatsapp-agenda/frontend/")
print(out)

# 8. DATABASE_URL configurada?
print("\n[8] DATABASE_URL NO CONTAINER BACKEND")
out, _ = run("docker exec backend-agenda printenv DATABASE_URL")
print(out if out else "*** NÃO CONFIGURADA! ***")

# 9. Health check
print("\n[9] HEALTH CHECK DO BACKEND")
out, _ = run("curl -s http://localhost:3001/health")
print(out)

# 10. Redis keys count
print("\n[10] REDIS - TOTAL DE CHAVES")
out, _ = run("docker exec redis redis-cli DBSIZE")
print(out)

# 11. Verificar se pg está instalado no backend
print("\n[11] MÓDULO PG NO BACKEND")
out, _ = run("docker exec backend-agenda npm list pg 2>&1")
print(out)

# 12. Schema do PostgreSQL  
print("\n[12] SCHEMA DAS TABELAS")
out, _ = run("""docker exec agenda-db psql -U agenda_user -d agenda -c "\\d clientes" """)
print(out)

print("\n" + "=" * 60)
print("  FIM DA ANÁLISE")
print("=" * 60)

c.close()
