import paramiko, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Criar container temporário com a imagem original para extrair o index.js
print('[1] Extraindo index.js original da imagem Docker...')
i, o, e = c.exec_command('docker run --rm --entrypoint cat whatsapp-agenda-backend /app/index.js > /tmp/index_original.js')
err = e.read().decode().strip()
if err:
    print(f'    Aviso: {err}')

i, o, e = c.exec_command('ls -la /tmp/index_original.js')
r = o.read().decode().strip()
print(f'    {r}')

i, o, e = c.exec_command("grep -c 'blacklist' /tmp/index_original.js 2>/dev/null")
cnt = o.read().decode().strip()
print(f'    Ocorrências de "blacklist" no original: {cnt}')

if cnt == '0' or cnt == '':
    print('\n[2] Restaurando o original no container...')
    i, o, e = c.exec_command('docker cp /tmp/index_original.js backend-agenda:/app/index.js')
    err = e.read().decode().strip()
    if err:
        print(f'    ERRO: {err}')
    else:
        print('    OK - Original copiado para o container.')
    
    # Também salvar como backup
    i, o, e = c.exec_command('cp /tmp/index_original.js /docker/whatsapp-agenda/backend/index.js.bak')
    e.read()
    
    print('\n[3] Reiniciando container...')
    i, o, e = c.exec_command('docker restart backend-agenda')
    import time
    time.sleep(6)
    out = o.read().decode().strip()
    print(f'    {out}')
    
    print('\n[4] Verificando...')
    i, o, e = c.exec_command('docker logs backend-agenda --tail 5 2>&1')
    time.sleep(2)
    logs = o.read().decode('utf-8', errors='replace').strip()
    print(logs)
    
    # Também baixar o original para local
    sftp = c.open_sftp()
    sftp.get('/tmp/index_original.js', 'C:/Users/SVOBODA/Desktop/DASHBOARD/index_original.js')
    sftp.close()
    print('\n[5] Original salvo localmente em index_original.js')
else:
    print('\n    Imagem já está com blacklist — não é o original puro.')

c.close()
print('\n=== FIM ===')
