import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Verificar portas expostas
print('[1] Portas do container:')
i, o, e = c.exec_command("docker inspect backend-agenda --format='{{json .NetworkSettings.Ports}}'")
print(f'    {o.read().decode().strip()}')

# 2. Verificar IP do container
i, o, e = c.exec_command("docker inspect backend-agenda --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'")
ip = o.read().decode().strip()
print(f'\n[2] IP do container: {ip}')

# 3. Testar com IP do container
if ip:
    print(f'\n[3] Teste via IP do container ({ip}):')
    i, o, e = c.exec_command(f'curl -s http://{ip}:3001/health 2>/dev/null')
    time.sleep(2)
    print(f'    /health: {o.read().decode().strip()}')

    i, o, e = c.exec_command(f'curl -s http://{ip}:3001/agenda/blacklist 2>/dev/null | head -c 200')
    time.sleep(2)
    bl = o.read().decode().strip()
    print(f'    /agenda/blacklist: {bl[:200]}')

# 4. Testar de dentro do container
print('\n[4] Teste de dentro do container:')
i, o, e = c.exec_command("docker exec backend-agenda wget -qO- http://localhost:3001/health 2>/dev/null || docker exec backend-agenda node -e \"const http=require('http');http.get('http://localhost:3001/health',r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>console.log(d))})\"")
time.sleep(3)
print(f'    {o.read().decode().strip()}')

c.close()
