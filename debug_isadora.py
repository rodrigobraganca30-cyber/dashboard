import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# ISADORA - clicou SIM confirmo às 14:20
phone = '5524988590582'
cid = 'wa_24988590582_ISADORA_MORAES_DE_AL'

print(f'=== Verificando cliente ISADORA ({phone}) ===\n')

# 1. Status atual
print('[1] Status no Redis:')
i, o, e = c.exec_command(f'docker exec redis-agenda redis-cli GET agenda:status:{cid}')
time.sleep(1)
print(f'    {o.read().decode("utf-8", errors="replace").strip() or "(vazio)"}')

# 2. Últimas msgs
print('\n[2] Últimas mensagens:')
i, o, e = c.exec_command(f'docker exec redis-agenda redis-cli GET agenda:msgs:{phone}')
time.sleep(1)
msgs_raw = o.read().decode('utf-8', errors='replace').strip()
if msgs_raw and msgs_raw != '(nil)':
    import json
    try:
        msgs = json.loads(msgs_raw)
        for m in msgs[-5:]:
            direction = '→ ENVIADA' if m.get('from') == 'me' else '← RECEBIDA'
            print(f'    {direction}: {m.get("text","")[:80]}')
    except:
        print(f'    (raw): {msgs_raw[:200]}')
else:
    print('    (sem mensagens)')

# 3. Logs do container filtrando por esse phone
print(f'\n[3] Logs com esse phone:')
i, o, e = c.exec_command(f'docker logs backend-agenda 2>&1 | grep {phone} | tail -5')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip() or '    (nenhum)')

# 4. Verificar todos os logs após restart
print(f'\n[4] TODOS os logs após restart (14:11):')
i, o, e = c.exec_command('docker logs backend-agenda --since "2026-05-27T14:11:00Z" 2>&1')
time.sleep(2)
logs = o.read().decode('utf-8', errors='replace').strip()
for line in logs.split('\n'):
    print(f'    {line.strip()}')

c.close()
