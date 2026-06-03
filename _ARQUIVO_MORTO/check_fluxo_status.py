import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Verificar se o fluxo está ativo no Redis
print('[1] Config do fluxo no Redis:')
i, o, e = c.exec_command('docker exec redis-agenda redis-cli GET agenda:flow-config')
time.sleep(1)
print(f'    {o.read().decode("utf-8", errors="replace").strip() or "(vazio)"}')

# 2. Verificar rota /api/flow no backend
print('\n[2] Rota /api/flow/flow-config no backend:')
i, o, e = c.exec_command('''docker exec backend-agenda node -e "fetch('http://localhost:3001/api/flow/flow-config',{headers:{'x-api-key':'svoboda-agenda-2025'}}).then(r=>{console.log('Status:',r.status);return r.json()}).then(j=>console.log(JSON.stringify(j,null,2))).catch(e=>console.log('ERR:',e.message))"''')
time.sleep(3)
print(o.read().decode('utf-8', errors='replace').strip())

# 3. Verificar fluxos ativos
print('\n[3] Fluxos ativos:')
i, o, e = c.exec_command('''docker exec backend-agenda node -e "fetch('http://localhost:3001/api/flow/ativos',{headers:{'x-api-key':'svoboda-agenda-2025'}}).then(r=>{console.log('Status:',r.status);return r.text()}).then(t=>console.log(t.substring(0,500))).catch(e=>console.log('ERR:',e.message))"''')
time.sleep(3)
print(o.read().decode('utf-8', errors='replace').strip())

# 4. Verificar se existe a rota de flow no index.js
print('\n[4] Rotas de flow no backend:')
i, o, e = c.exec_command('''docker exec backend-agenda node -e "const fs=require('fs');const c=fs.readFileSync('/app/index.js','utf8');const lines=c.split('\\n');lines.forEach((l,i)=>{if(l.includes('/api/flow')||l.includes('flow-config')||l.includes('fluxo'))console.log('L'+(i+1)+':',l.substring(0,150))})"''')
time.sleep(3)
print(o.read().decode('utf-8', errors='replace').strip() or '    Nenhuma rota de flow encontrada')

# 5. Verificar webhook de respostas
print('\n[5] Webhook de mensagens recebidas:')
i, o, e = c.exec_command('''docker exec backend-agenda node -e "const fs=require('fs');const c=fs.readFileSync('/app/index.js','utf8');const lines=c.split('\\n');lines.forEach((l,i)=>{if(l.includes('webhook')||l.includes('incoming')||l.includes('receive'))console.log('L'+(i+1)+':',l.substring(0,150))})"''')
time.sleep(3)
print(o.read().decode('utf-8', errors='replace').strip() or '    Nenhum webhook encontrado')

# 6. Logs recentes do backend (últimos 30 segundos)
print('\n[6] Últimos logs do backend:')
i, o, e = c.exec_command('docker logs backend-agenda --tail 15 2>&1')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

# 7. Verificar mensagens recentes no Redis (respostas de clientes)
print('\n[7] Keys de unread (mensagens não lidas):')
i, o, e = c.exec_command('docker exec redis-agenda redis-cli KEYS "agenda:unread:*" | wc -l')
time.sleep(1)
print(f'    {o.read().decode().strip()} mensagens não lidas')

c.close()
