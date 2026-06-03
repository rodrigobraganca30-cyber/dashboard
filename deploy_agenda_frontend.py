import paramiko, os
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

sftp = c.open_sftp()
base = '/docker/dashboard/html/agenda/'

# Backup do antigo index.html da agenda
print("1. Fazendo backup do index.html antigo...")
i, o, e = c.exec_command(f"cp {base}index.html {base}index.html.bak.pre_fase9")
print(o.read().decode().strip())

# Upload dos novos arquivos
print("2. Uploading novos arquivos para /docker/dashboard/html/agenda/ ...")
sftp.put('frontend/index.html', base + 'index.html')
sftp.put('frontend/style.css', base + 'style.css')
sftp.put('frontend/script.js', base + 'script.js')
sftp.close()

# Verificar
print("3. Verificando...")
i, o, e = c.exec_command(f"ls -la {base}")
print(o.read().decode().strip())

# Reload nginx
print("\n4. Recarregando NGINX...")
i, o, e = c.exec_command("docker exec dashboard-nginx nginx -s reload 2>&1")
print(o.read().decode().strip())
print(e.read().decode().strip())

c.close()
print("\nDeploy da Agenda concluído!")
