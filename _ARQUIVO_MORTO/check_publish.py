import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Verificar como o gerar_dashboard_v2.py faz o upload 
print('[1] Verificando configuração de upload no gerar_dashboard_v2.py:')
i, o, e = c.exec_command("grep -A5 'REMOTE_DIR\\|sftp_host\\|SFTP\\|HTML_OUT' /docker/dashboard/gerar_dashboard_v2.py | head -20")
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

# 2. Verificar o nginx ou web server que serve svoboda.rtflowapp.com
print('\n[2] Nginx configs para rtflowapp:')
i, o, e = c.exec_command("grep -rl 'svoboda.rtflowapp' /etc/nginx/ 2>/dev/null || grep -rl 'svoboda' /docker/traefik/ 2>/dev/null || echo 'Nao encontrado em nginx/traefik'")
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

# 3. Verificar se o html/index.html é o que o Nginx serve
print('\n[3] Root do web server:')
i, o, e = c.exec_command("docker ps --filter 'name=nginx' --format '{{.Names}}' 2>/dev/null || docker ps --filter 'name=web' --format '{{.Names}}' 2>/dev/null")
time.sleep(1)
nginx = o.read().decode().strip()
print(f'    Container: {nginx or "Nenhum nginx encontrado"}')

# 4. Verificar containers com volume do dashboard
print('\n[4] Containers com volume /docker/dashboard:')
i, o, e = c.exec_command("docker ps --format '{{.Names}}' | xargs -I{} sh -c \"docker inspect {} --format='{{range .Mounts}}{{.Source}}:{{.Destination}} {{end}}' | grep -l dashboard 2>/dev/null && echo {}\" 2>/dev/null || echo 'Nenhum'")
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

# 5. Verificar se há um Caddy ou Traefik servindo
print('\n[5] Traefik labels com svoboda:')
i, o, e = c.exec_command("docker ps --format '{{.Names}}' | head -20")
time.sleep(1)
containers = o.read().decode().strip()
print(f'    Containers rodando: {containers}')

# 6. Testar se o dashboard público tem showWaSub
print('\n[6] Testando o dashboard público:')
i, o, e = c.exec_command("curl -s https://svoboda.rtflowapp.com/ 2>/dev/null | grep -c 'showWaSub'")
time.sleep(5)
cnt = o.read().decode().strip()
print(f'    showWaSub no público: {cnt}')

i, o, e = c.exec_command("curl -s https://svoboda.rtflowapp.com/ 2>/dev/null | grep -c 'bloqueado'")
time.sleep(3)
bl = o.read().decode().strip()
print(f'    bloqueado no público: {bl}')

c.close()
