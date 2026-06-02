import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

print('=== VERIFICAÇÃO COMPLETA DO FLUXO (SEM EXECUTAR NADA) ===\n')

# 1. Backend rodando?
print('[1] Backend:')
i, o, e = c.exec_command('docker ps --filter name=backend-agenda --format "{{.Status}}"')
time.sleep(1)
print(f'    Container: {o.read().decode().strip()}')

# 2. Rotas de flow existem?
print('\n[2] Rotas de flow no backend:')
routes = [
    ('GET', '/api/flow/flow-config'),
    ('GET', '/api/flow/flows'),
    ('GET', '/api/flow/status'),
]
for method, path in routes:
    i, o, e = c.exec_command(f'''docker exec backend-agenda node -e "fetch('http://localhost:3001{path}').then(r=>console.log('{path}:',r.status)).catch(e=>console.log('ERR:',e.message))"''')
    time.sleep(2)
    print(f'    {o.read().decode().strip()}')

# 3. Config do fluxo
print('\n[3] Configuração do fluxo:')
i, o, e = c.exec_command('''docker exec backend-agenda node -e "fetch('http://localhost:3001/api/flow/flow-config').then(r=>r.json()).then(j=>console.log(JSON.stringify(j,null,2))).catch(e=>console.log('ERR:',e.message))"''')
time.sleep(3)
print(o.read().decode('utf-8', errors='replace').strip())

# 4. Fluxos ativos
print('\n[4] Fluxos ativos:')
i, o, e = c.exec_command('''docker exec backend-agenda node -e "fetch('http://localhost:3001/api/flow/status').then(r=>r.json()).then(j=>console.log(JSON.stringify(j))).catch(e=>console.log('ERR:',e.message))"''')
time.sleep(3)
print(f'    {o.read().decode().strip()}')

# 5. HTML com fluxo + botões + bloqueado?
print('\n[5] Dashboard HTML:')
i, o, e = c.exec_command("grep -c 'waFluxoLoadConfig' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    Fluxo UI: {o.read().decode().strip()} refs')
i, o, e = c.exec_command("grep -c 'function showWaSub' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    showWaSub (botões): {o.read().decode().strip()} refs')
i, o, e = c.exec_command("grep -c 'bloqueado' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    Bloqueado: {o.read().decode().strip()} refs')

# 6. JS sem erros?
print('\n[6] JavaScript:')
cmd = r"""docker run --rm -v /docker/dashboard/html:/data node:20-alpine node -e "
const fs=require('fs'),vm=require('vm');
const html=fs.readFileSync('/data/index.html','utf8');
const re=/<script[^>]*>([\s\S]*?)<\/script>/gi;
let m,i=0,errs=0;
while((m=re.exec(html))!==null){const c=m[1].trim();if(!c){i++;continue;}try{new vm.Script(c)}catch(e){errs++;console.log('Script '+i+': '+e.message.substring(0,80))}i++}
console.log(errs===0?'TODOS OK ('+i+' scripts)':errs+' ERROS');
"
"""
i, o, e = c.exec_command(cmd)
time.sleep(15)
print(f'    {o.read().decode().strip()}')

# 7. Webhook recebendo?
print('\n[7] Últimas mensagens recebidas:')
i, o, e = c.exec_command('docker logs backend-agenda --tail 5 2>&1 | grep webhook')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

# 8. Blacklist
print('\n[8] Blacklist:')
i, o, e = c.exec_command('docker exec redis-agenda redis-cli SCARD agenda:blacklist')
time.sleep(1)
print(f'    {o.read().decode().strip()} números bloqueados')

c.close()
