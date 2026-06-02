"""
deploy_frontend.py
Envia o whatsapp_agenda_gen.py atualizado para o VPS e regenera o dashboard.
"""
import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

LOCAL_FILE = os.path.join(os.path.dirname(__file__), 'whatsapp_agenda_gen.py')
REMOTE_FILE = '/docker/dashboard/whatsapp_agenda_gen.py'

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Backup do arquivo atual no VPS
print('[1] Fazendo backup do arquivo atual...')
i, o, e = c.exec_command(f'cp {REMOTE_FILE} {REMOTE_FILE}.bak_blacklist')
e.read()
print('    OK')

# 2. Upload
print('\n[2] Enviando arquivo atualizado...')
sftp = c.open_sftp()
sftp.put(LOCAL_FILE, REMOTE_FILE)
sftp.close()
print('    OK')

# 3. Verificar que "bloqueado" está no arquivo remoto
print('\n[3] Verificando...')
i, o, e = c.exec_command(f'grep -c "bloqueado" {REMOTE_FILE}')
cnt = o.read().decode().strip()
print(f'    Ocorrências de "bloqueado" no VPS: {cnt}')

# 4. Regenerar o dashboard (se houver script de geração)
print('\n[4] Regenerando dashboard...')
i, o, e = c.exec_command('cd /docker/dashboard && python3 gerar_dashboard_v2.py 2>&1 | tail -5')
time.sleep(10)
out = o.read().decode('utf-8', errors='replace').strip()
err = e.read().decode('utf-8', errors='replace').strip()
if out:
    print(out)
if err:
    print(f'    ERR: {err[:200]}')

c.close()
print('\n=== FRONTEND DEPLOY CONCLUÍDO ===')
