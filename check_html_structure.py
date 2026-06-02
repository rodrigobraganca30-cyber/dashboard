import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Buscar a estrutura de sub-abas e onde o btn-cfg foi parar
print('[1] Onde está o btn-cfg-section agora:')
i, o, e = c.exec_command("grep -n 'btn-cfg-section\\|SUB.*Disparo\\|SUB.*Config\\|wa-sub-disparo\\|wa-sub-config\\|TEMPLATES DE MENSAGEM\\|Disparar WhatsApp\\|FIM SEÇÃO\\|wa-subtab' /docker/dashboard/html/index.html | head -40")
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

# Ver o conteúdo ao redor do ponto de inserção
print('\n[2] Estrutura das sub-abas WhatsApp:')
i, o, e = c.exec_command("grep -n 'wa-sub\\|subtab\\|sub-tab\\|SUB:' /docker/dashboard/html/index.html | head -20")
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
