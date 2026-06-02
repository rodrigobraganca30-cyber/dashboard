import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

ts = '20260526_214412'
remote_dir = f'/docker/backup_{ts}'
local_dir = r'C:\Users\SVOBODA\Desktop\DASHBOARD\BACKUP_20260526'
os.makedirs(local_dir, exist_ok=True)

sftp = c.open_sftp()

files = [
    'index.html',
    'whatsapp_agenda_gen.py',
    'index.js.backend',
    'index.js.container',
    'blacklist.txt',
    'gerar_dashboard_v2.py',
]

print(f'=== BACKUP LOCAL: {local_dir} ===\n')
for f in files:
    remote = f'{remote_dir}/{f}'
    local = os.path.join(local_dir, f)
    try:
        sftp.get(remote, local)
        size = os.path.getsize(local)
        print(f'  [OK] {f} ({size:,} bytes)')
    except Exception as e:
        print(f'  [!] {f}: {e}')

# Também copiar os scripts de patch locais
import shutil
local_scripts = [
    'patch_backend_v2.py',
    'inject_bloqueado.py',
    'importar_blacklist_inicial.py',
    'index_original.js',
    'index_patched_v2.js',
]
print('\n--- Scripts locais ---')
for s in local_scripts:
    src = os.path.join(r'C:\Users\SVOBODA\Desktop\DASHBOARD', s)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(local_dir, s))
        print(f'  [OK] {s}')

sftp.close()
c.close()

# Listar tudo
print(f'\n=== Conteúdo final do backup local ===')
for f in sorted(os.listdir(local_dir)):
    size = os.path.getsize(os.path.join(local_dir, f))
    print(f'  {f:40s} {size:>12,} bytes')

total = sum(os.path.getsize(os.path.join(local_dir, f)) for f in os.listdir(local_dir))
print(f'\n  TOTAL: {total:,} bytes ({total/1024/1024:.1f} MB)')
print(f'\n✅ Backup completo: servidor + local')
