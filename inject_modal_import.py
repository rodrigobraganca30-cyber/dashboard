"""
inject_modal_import.py — Injeta modal de importacao no HTML live da VPS
"""
import paramiko, os, sys, time, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

ts = time.strftime('%Y%m%d_%H%M%S')

# Backup
print('[1/3] Backup...')
i, o, e = c.exec_command(f'cp /docker/dashboard/html/index.html /docker/backup_dashboard_{ts}_pre_modal.html')
time.sleep(1)
print('    OK')

# Upload o patch Python para VPS
print('\n[2/3] Uploading e aplicando patch...')

# Ler o patch do arquivo separado
patch_path = os.path.join(os.path.dirname(__file__), 'patch_modal_vps.py')
with open(patch_path, 'r', encoding='utf-8') as f:
    patch_code = f.read()

sftp = c.open_sftp()
with sftp.open('/tmp/patch_modal.py', 'w') as f:
    f.write(patch_code)
sftp.close()

i, o, e = c.exec_command('python3 /tmp/patch_modal.py')
time.sleep(10)
out = o.read().decode('utf-8', errors='replace').strip()
err = e.read().decode('utf-8', errors='replace').strip()
print(out)
if err:
    print(f'ERR: {err[:500]}')

c.close()
print(f'\n[3/3] Pronto! Recarregue a pagina (Ctrl+Shift+R)')
