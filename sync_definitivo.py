"""
sync_definitivo.py — Sincroniza o index.js do container (com TODOS os patches)
para o source local, garantindo que nada se perde num rebuild.
Também faz backup completo de tudo.
"""
import paramiko, os, sys, time, shutil
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

ts = time.strftime('%Y%m%d_%H%M%S')
local_base = r'C:\Users\SVOBODA\Desktop\DASHBOARD'
backup_dir = os.path.join(local_base, f'BACKUP_DEFINITIVO_{ts}')
os.makedirs(backup_dir, exist_ok=True)

print(f'=== SYNC DEFINITIVO — {ts} ===\n')

# ══════════════════════════════════════════════════
# 1. BAIXAR index.js COMPLETO DO CONTAINER
# ══════════════════════════════════════════════════
print('[1/6] Baixando index.js do container (com TODOS os patches)...')

# Primeiro copiar do container para o VPS
i, o, e = c.exec_command('docker cp backend-agenda:/app/index.js /tmp/index_definitivo.js')
time.sleep(2)

# Baixar via SFTP
sftp = c.open_sftp()

# Backup do local atual
local_index = os.path.join(local_base, 'whatsapp-agenda', 'backend', 'index.js')
if os.path.exists(local_index):
    shutil.copy2(local_index, os.path.join(backup_dir, 'index_local_antigo.js'))
    print(f'    Backup local antigo: {os.path.getsize(local_index):,} bytes')

# Baixar o definitivo
sftp.get('/tmp/index_definitivo.js', local_index)
size = os.path.getsize(local_index)
print(f'    ✅ index.js atualizado: {size:,} bytes')

# Também salvar cópia no backup
shutil.copy2(local_index, os.path.join(backup_dir, 'index_definitivo.js'))

# ══════════════════════════════════════════════════
# 2. BAIXAR index_patched_v2.js (referência)
# ══════════════════════════════════════════════════
print('\n[2/6] Salvando index_patched_v2.js no backup...')
patched = os.path.join(local_base, 'index_patched_v2.js')
if os.path.exists(patched):
    shutil.copy2(patched, os.path.join(backup_dir, 'index_patched_v2.js'))
    print('    ✅ Copiado')

# ══════════════════════════════════════════════════
# 3. BAIXAR DASHBOARD HTML DA VPS
# ══════════════════════════════════════════════════
print('\n[3/6] Baixando dashboard HTML da VPS...')
sftp.get('/docker/dashboard/html/index.html', os.path.join(backup_dir, 'dashboard_index.html'))
size = os.path.getsize(os.path.join(backup_dir, 'dashboard_index.html'))
print(f'    ✅ dashboard HTML: {size:,} bytes')

# ══════════════════════════════════════════════════
# 4. BACKUP REDIS COMPLETO
# ══════════════════════════════════════════════════
print('\n[4/6] Backup Redis...')

# BGSAVE
i, o, e = c.exec_command('docker exec redis-agenda redis-cli BGSAVE')
time.sleep(3)
print(f'    {o.read().decode().strip()}')

# Flow config
i, o, e = c.exec_command('docker exec redis-agenda redis-cli GET agenda:button-config')
time.sleep(1)
btn_cfg = o.read().decode('utf-8', errors='replace').strip()
with open(os.path.join(backup_dir, 'button-config.json'), 'w', encoding='utf-8') as f:
    f.write(btn_cfg)
print(f'    ✅ button-config: {len(btn_cfg)} bytes')

# Blacklist
i, o, e = c.exec_command('docker exec redis-agenda redis-cli SMEMBERS agenda:blacklist')
time.sleep(2)
bl = o.read().decode('utf-8', errors='replace').strip()
with open(os.path.join(backup_dir, 'blacklist.txt'), 'w', encoding='utf-8') as f:
    f.write(bl)
bl_count = len([x for x in bl.split('\n') if x.strip()])
print(f'    ✅ blacklist: {bl_count} números')

# Templates
i, o, e = c.exec_command('docker exec redis-agenda redis-cli GET agenda:templates')
time.sleep(1)
tpls = o.read().decode('utf-8', errors='replace').strip()
with open(os.path.join(backup_dir, 'templates.json'), 'w', encoding='utf-8') as f:
    f.write(tpls)
print(f'    ✅ templates: {len(tpls)} bytes')

# Meta config
i, o, e = c.exec_command('docker exec redis-agenda redis-cli GET agenda:meta_token')
time.sleep(1)
token = o.read().decode().strip()
i, o, e = c.exec_command('docker exec redis-agenda redis-cli GET agenda:meta_phone_id')
time.sleep(1)
phone_id = o.read().decode().strip()
i, o, e = c.exec_command('docker exec redis-agenda redis-cli GET agenda:meta_waba_id')
time.sleep(1)
waba_id = o.read().decode().strip()
with open(os.path.join(backup_dir, 'meta_config.txt'), 'w', encoding='utf-8') as f:
    f.write(f'token={token}\nphone_id={phone_id}\nwaba_id={waba_id}\n')
print(f'    ✅ meta config salvo')

# RDB dump
i, o, e = c.exec_command('docker cp redis-agenda:/data/dump.rdb /tmp/redis_dump.rdb')
time.sleep(3)
try:
    sftp.get('/tmp/redis_dump.rdb', os.path.join(backup_dir, 'redis_dump.rdb'))
    rdb_size = os.path.getsize(os.path.join(backup_dir, 'redis_dump.rdb'))
    print(f'    ✅ RDB dump: {rdb_size:,} bytes')
except:
    print('    ⚠️ RDB dump falhou (não crítico)')

# ══════════════════════════════════════════════════
# 5. BACKUP NA VPS (cópia permanente)
# ══════════════════════════════════════════════════
print('\n[5/6] Criando backup permanente na VPS...')
vps_backup = f'/docker/backups/backup_{ts}_DEFINITIVO'
i, o, e = c.exec_command(f'mkdir -p {vps_backup}')
time.sleep(1)
i, o, e = c.exec_command(f'docker cp backend-agenda:/app/index.js {vps_backup}/index.js')
time.sleep(2)
i, o, e = c.exec_command(f'cp /docker/dashboard/html/index.html {vps_backup}/dashboard.html')
time.sleep(1)
i, o, e = c.exec_command(f'docker cp redis-agenda:/data/dump.rdb {vps_backup}/redis_dump.rdb')
time.sleep(2)
i, o, e = c.exec_command(f'ls -lh {vps_backup}/')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# ══════════════════════════════════════════════════
# 6. VERIFICAÇÃO DO INDEX.JS LOCAL
# ══════════════════════════════════════════════════
print('\n[6/6] Verificação do index.js local sincronizado...')
with open(local_index, 'r', encoding='utf-8') as f:
    content = f.read()

checks = {
    'BUTTON_FLOWS/BUTTON_STATUS': 'BUTTON_STATUS' in content,
    'KEY_BLACKLIST': 'KEY_BLACKLIST' in content,
    'validateAndCleanPhone': 'validateAndCleanPhone' in content,
    '/agenda/blacklist': '/agenda/blacklist' in content,
    '/button-config': '/button-config' in content,
    'agenda:button-config': 'agenda:button-config' in content,
    'shouldCallJarvis': 'shouldCallJarvis' in content,
    'isEligibleForJarvis': 'isEligibleForJarvis' in content,
    'JARVIS_COOLDOWN': 'JARVIS_COOLDOWN' in content,
    'sendTemplate': 'sendTemplate' in content,
    'send-bulk': 'send-bulk' in content,
    'Auto-blacklist': 'Auto-blacklist' in content,
}

all_ok = True
for name, ok in checks.items():
    status = '✅' if ok else '❌'
    if not ok: all_ok = False
    print(f'    {status} {name}')

sftp.close()
c.close()

# Listar backup
total = sum(os.path.getsize(os.path.join(backup_dir, f)) for f in os.listdir(backup_dir))
print(f'\n📁 Backup local: {backup_dir}')
for f in sorted(os.listdir(backup_dir)):
    sz = os.path.getsize(os.path.join(backup_dir, f))
    print(f'    {f}: {sz:,} bytes')
print(f'    Total: {total:,} bytes ({total/1024/1024:.1f} MB)')

print(f'\n{"="*60}')
if all_ok:
    print(f'✅ SYNC DEFINITIVO COMPLETO — NADA MAIS SE PERDE')
    print(f'   Local: {local_index}')
    print(f'   Backup local: {backup_dir}')
    print(f'   Backup VPS: {vps_backup}')
else:
    print(f'⚠️ SYNC PARCIAL — Alguns componentes podem estar faltando')
print(f'{"="*60}')
