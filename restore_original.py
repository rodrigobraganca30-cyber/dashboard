import paramiko, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Restaurar o backup do index.js original
print('[1] Verificando se existe backup...')
i, o, e = c.exec_command('ls -la /docker/whatsapp-agenda/backend/index.js.bak 2>/dev/null')
bak = o.read().decode().strip()
print(f'    {bak or "NAO EXISTE"}')

if bak:
    print('\n[2] Restaurando backup...')
    i, o, e = c.exec_command('cp /docker/whatsapp-agenda/backend/index.js.bak /docker/whatsapp-agenda/backend/index_PATCHEADO.js')
    e.read()
    # Copiar backup como index.js
    i, o, e = c.exec_command('cp /docker/whatsapp-agenda/backend/index.js.bak /docker/whatsapp-agenda/backend/index.js')
    err = e.read().decode().strip()
    if err:
        print(f'    ERRO: {err}')
    else:
        print('    OK - Backup restaurado no host.')

    print('\n[3] Copiando original para dentro do container...')
    i, o, e = c.exec_command('docker cp /docker/whatsapp-agenda/backend/index.js backend-agenda:/app/index.js')
    err = e.read().decode().strip()
    if err:
        print(f'    ERRO: {err}')
    else:
        print('    OK.')

    print('\n[4] Reiniciando container...')
    i, o, e = c.exec_command('docker restart backend-agenda')
    import time
    time.sleep(5)
    out = o.read().decode().strip()
    print(f'    {out}')

    print('\n[5] Verificando se subiu...')
    i, o, e = c.exec_command('docker logs backend-agenda --tail 5 2>&1')
    time.sleep(3)
    logs = o.read().decode('utf-8', errors='replace').strip()
    print(logs)
else:
    print('\n    SEM BACKUP! Preciso recuperar de outra forma.')
    # Tenta baixar o index_vps.js local (era o original antes do patch)
    print('    Verificando index_vps.js local (cópia pre-patch)...')

c.close()
print('\n=== FIM ===')
