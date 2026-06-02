import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Ver quantas vezes "template" aparece no HTML atual vs no backup que funcionava
print('[1] Templates no HTML atual:')
i, o, e = c.exec_command("grep -c 'Carregar Templates\\|waLoadTemplates\\|loadTemplates\\|templates_meta\\|TEMPLATES CADASTRADOS' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'    Matches: {o.read().decode().strip()}')

# 2. Verificar no backup mais recente (20260526_220224) que tinha o fluxo + bloqueado
print('\n[2] Templates no bak.20260526_220224:')
i, o, e = c.exec_command("grep -c 'Carregar Templates\\|waLoadTemplates\\|loadTemplates\\|templates_meta\\|TEMPLATES CADASTRADOS' /docker/dashboard/html/index.html.bak.20260526_220224")
time.sleep(1)
print(f'    Matches: {o.read().decode().strip()}')

# 3. Verificar seção de templates no HTML atual
print('\n[3] Seção de templates no HTML atual:')
i, o, e = c.exec_command("grep -n 'Carregar Templates\\|waLoadTemplates\\|loadTemplates\\|fetchTemplates\\|/templates' /docker/dashboard/html/index.html | head -10")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 4. Mesmo no backup recente
print('\n[4] Seção de templates no backup recente:')
i, o, e = c.exec_command("grep -n 'Carregar Templates\\|waLoadTemplates\\|loadTemplates\\|fetchTemplates\\|/templates' /docker/dashboard/html/index.html.bak.20260526_220224 | head -10")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 5. Diferença de tamanho
print('\n[5] Tamanhos:')
i, o, e = c.exec_command("wc -c /docker/dashboard/html/index.html /docker/dashboard/html/index.html.bak.20260526_220224")
time.sleep(1)
print(o.read().decode().strip())

c.close()
