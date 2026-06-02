"""
deploy_unificacao.py
Deploy completo das alterações de unificação de conversas com/sem 9° dígito.
1. Envia whatsapp_agenda_gen.py atualizado para o VPS
2. Envia index.js atualizado para o container backend
3. Regenera o dashboard HTML
4. Reinicia o backend
"""
import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = os.path.dirname(__file__)
LOCAL_FRONTEND = os.path.join(BASE, 'whatsapp_agenda_gen.py')
LOCAL_BACKEND = os.path.join(BASE, 'whatsapp-agenda', 'backend', 'index.js')
REMOTE_FRONTEND = '/docker/dashboard/whatsapp_agenda_gen.py'

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# ── ETAPA 1: Backup ──
print('=' * 50)
print('[1/6] Fazendo backup dos arquivos atuais...')
i, o, e = c.exec_command(f'cp {REMOTE_FRONTEND} {REMOTE_FRONTEND}.bak_dedup')
e.read()
i, o, e = c.exec_command('docker exec backend-agenda cp /app/index.js /app/index.js.bak_dedup')
e.read()
print('    OK - backups criados (.bak_dedup)')

# ── ETAPA 2: Upload frontend (whatsapp_agenda_gen.py) ──
print('\n[2/6] Enviando whatsapp_agenda_gen.py...')
sftp = c.open_sftp()
sftp.put(LOCAL_FRONTEND, REMOTE_FRONTEND)
sftp.close()
# Verificar que as funções novas estão no arquivo remoto
i, o, e = c.exec_command(f'grep -c "_chatDeduplicateList" {REMOTE_FRONTEND}')
cnt = o.read().decode().strip()
print(f'    OK - _chatDeduplicateList aparece {cnt}x no VPS (esperado: 3)')

# ── ETAPA 3: Upload backend (index.js) ──
print('\n[3/6] Enviando index.js para o container Docker...')
sftp = c.open_sftp()
sftp.put(LOCAL_BACKEND, '/tmp/index_unified.js')
sftp.close()
i, o, e = c.exec_command('docker cp /tmp/index_unified.js backend-agenda:/app/index.js')
time.sleep(2)
err = e.read().decode().strip()
if err:
    print(f'    ERRO: {err}')
    c.close()
    sys.exit(1)
# Verificar que getPhoneVariant está no arquivo dentro do container
i, o, e = c.exec_command('docker exec backend-agenda grep -c "getPhoneVariant" /app/index.js')
time.sleep(1)
cnt2 = o.read().decode().strip()
print(f'    OK - getPhoneVariant aparece {cnt2}x no container (esperado: 4)')

# ── ETAPA 4: Reiniciar backend ──
print('\n[4/6] Reiniciando container backend...')
i, o, e = c.exec_command('docker restart backend-agenda')
time.sleep(10)
print(f'    {o.read().decode().strip()}')

# Verificar status
i, o, e = c.exec_command('docker ps --filter name=backend-agenda --format "{{.Status}}"')
time.sleep(1)
status = o.read().decode().strip()
print(f'    Container: {status}')

# ── ETAPA 5: Regenerar dashboard HTML ──
print('\n[5/6] Regenerando dashboard HTML...')
i, o, e = c.exec_command('cd /docker/dashboard && python3 gerar_dashboard_v2.py 2>&1 | tail -8')
time.sleep(15)
out = o.read().decode('utf-8', errors='replace').strip()
if out:
    print(out)
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'    ERR: {err[:300]}')

# ── ETAPA 6: Verificação final ──
print('\n[6/6] Verificação final...')
# Testar se o backend responde
i, o, e = c.exec_command('docker exec backend-agenda node -e "fetch(\'http://localhost:3001/health\').then(r=>r.json()).then(d=>console.log(\'Health:\',JSON.stringify(d))).catch(e=>console.log(\'ERR:\',e.message))"')
time.sleep(3)
health = o.read().decode('utf-8', errors='replace').strip()
print(f'    {health}')

c.close()
print('\n' + '=' * 50)
print('=== DEPLOY UNIFICAÇÃO CONCLUÍDO ===')
print('Acesse https://svoboda.rtflowapp.com e verifique a aba Chat')
print('=' * 50)
