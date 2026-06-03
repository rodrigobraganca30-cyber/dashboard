import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

ts = time.strftime('%Y%m%d_%H%M%S')

# 1. Backup
print('[1/4] Backup...')
c.exec_command(f'cp /docker/dashboard/html/index.html /docker/backup_dashboard_{ts}_pre_dynamic.html')
time.sleep(1)
print('    OK')

# 2. Criar gen_inv_list.sh + list.json + cron
print('[2/4] Criando list.json...')
gen_script = '#!/bin/bash\nDIR="/docker/dashboard/html/inventarios"\nOUT="$DIR/list.json"\necho "[" > "$OUT"\nFIRST=1\nfor f in $(ls -1 "$DIR"/inventario_*.xlsx 2>/dev/null | sort -r); do\n  FNAME=$(basename "$f")\n  SIZE=$(stat -c%s "$f" 2>/dev/null || echo 0)\n  SIZE_KB=$((SIZE / 1024))\n  DATE=$(echo "$FNAME" | grep -oP \'\\d{2}-\\d{2}-\\d{4}\')\n  if [ $FIRST -eq 1 ]; then FIRST=0; else echo "," >> "$OUT"; fi\n  printf \'{"date":"%s","file":"%s","size_kb":%d}\' "$DATE" "$FNAME" "$SIZE_KB" >> "$OUT"\ndone\necho "" >> "$OUT"\necho "]" >> "$OUT"\n'

sftp = c.open_sftp()
with sftp.open('/docker/dashboard/gen_inv_list.sh', 'w') as f:
    f.write(gen_script)
sftp.close()

c.exec_command('chmod +x /docker/dashboard/gen_inv_list.sh && /docker/dashboard/gen_inv_list.sh')
time.sleep(2)

i, o, e = c.exec_command('cat /docker/dashboard/html/inventarios/list.json')
time.sleep(1)
data = o.read().decode('utf-8', errors='replace').strip()
print(f'    list.json: {len(data)} bytes')

# Cron
i, o, e = c.exec_command('crontab -l 2>/dev/null')
time.sleep(1)
cron = o.read().decode('utf-8', errors='replace').strip()
if 'gen_inv_list' not in cron:
    new_cron = cron + '\n0 * * * * /docker/dashboard/gen_inv_list.sh\n'
    sftp = c.open_sftp()
    with sftp.open('/tmp/new_cron', 'w') as f:
        f.write(new_cron)
    sftp.close()
    c.exec_command('crontab /tmp/new_cron')
    time.sleep(1)
    print('    Cron: adicionado (a cada hora)')
else:
    print('    Cron: ja existe')

# 3. Upload e executar patch
print('\n[3/4] Aplicando patch dinamico...')
patch_local = os.path.join(os.path.dirname(__file__), 'patch_inv_dynamic_vps.py')
with open(patch_local, 'r', encoding='utf-8') as f:
    patch_code = f.read()

sftp = c.open_sftp()
with sftp.open('/tmp/patch_inv_dynamic.py', 'w') as f:
    f.write(patch_code)
sftp.close()

i, o, e = c.exec_command('python3 /tmp/patch_inv_dynamic.py')
time.sleep(6)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'ERR: {err[:300]}')

# 4. Verificacao
print('\n[4/4] Verificacao...')
i, o, e = c.exec_command("grep -c 'inv-tbody-dynamic' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'  tbody dinamico: {o.read().decode().strip()} refs')

i, o, e = c.exec_command("grep -c 'list.json' /docker/dashboard/html/index.html")
time.sleep(1)
print(f'  list.json fetch: {o.read().decode().strip()} refs')

i, o, e = c.exec_command("crontab -l 2>/dev/null | grep gen_inv")
time.sleep(1)
print(f'  Cron: {o.read().decode().strip()}')

c.close()
print('\nPronto! Ctrl+Shift+R para ver.')
