import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

patch = r'''
import os, re

html = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()

# Formato de cada linha:
# <tr><td style="font-weight:700;color:white;font-size:14px;"><i class="far fa-calendar-alt" style="color:var(--muted);margin-right:8px;"></i>DD-MM-YYYY</td><td><span class="badge" style="background:rgba(255,255,255,0.05)">XX KB</span></td><td><a href="inventarios/inventario_DD-MM-YYYY.xlsx" download="inventario_DD-MM-YYYY.xlsx" class="estoque-btn"><i class="fas fa-file-excel"></i> Baixar Planilha</a></td></tr>

inv_dir = '/docker/dashboard/html/inventarios'
# Pegar todos os inventarios disponiveis
all_inv = []
for f in os.listdir(inv_dir):
    m = re.search(r'inventario_(\d{2}-\d{2}-\d{4})\.xlsx', f)
    if m:
        date = m.group(1)
        size_kb = os.path.getsize(os.path.join(inv_dir, f)) // 1024
        all_inv.append((date, size_kb))

# Verificar quais ja estao no HTML
existing_dates = set(re.findall(r'inventario_(\d{2}-\d{2}-\d{4})\.xlsx.*?Baixar Planilha', html))
print('Datas ja no HTML: %d' % len(existing_dates))

missing = [(d, s) for d, s in all_inv if d not in existing_dates]
missing.sort(key=lambda x: (int(x[0][6:10]), int(x[0][3:5]), int(x[0][0:2])), reverse=True)

if not missing:
    print('Nenhuma data faltando!')
else:
    print('Datas faltando: %s' % ', '.join([m[0] for m in missing]))
    
    # Criar as novas linhas
    new_rows = ''
    for date, size_kb in missing:
        new_rows += '<tr><td style="font-weight:700;color:white;font-size:14px;"><i class="far fa-calendar-alt" style="color:var(--muted);margin-right:8px;"></i>%s</td><td><span class="badge" style="background:rgba(255,255,255,0.05)">%d KB</span></td><td><a href="inventarios/inventario_%s.xlsx" download="inventario_%s.xlsx" class="estoque-btn"><i class="fas fa-file-excel"></i> Baixar Planilha</a></td></tr>\n' % (date, size_kb, date, date)
    
    # Inserir antes da primeira linha de inventario (20-05-2026)
    anchor = '<tr><td style="font-weight:700;color:white;font-size:14px;"><i class="far fa-calendar-alt" style="color:var(--muted);margin-right:8px;"></i>20-05-2026'
    if anchor in html:
        html = html.replace(anchor, new_rows + anchor)
        print('[+] %d linhas inseridas antes de 20-05-2026' % len(missing))
    else:
        print('[!] Ancora 20-05 nao encontrada')

# Atualizar contador
total = len(existing_dates) + len(missing)
# Procurar o numero antigo (pode ser 14 ou 20)
for old_n in [14, 20, len(existing_dates)]:
    old_str = '>%d</div>' % old_n
    new_str = '>%d</div>' % total
    if old_str in html:
        html = html.replace(old_str, new_str, 1)
        print('[+] Contador: %d -> %d' % (old_n, total))
        break

open('/docker/dashboard/html/index.html', 'w', encoding='utf-8').write(html)
print('\n[OK] HTML salvo, total inventarios: %d' % total)
'''

print('Aplicando...')
sftp = c.open_sftp()
with sftp.open('/tmp/patch_inv2.py', 'w') as f:
    f.write(patch)
sftp.close()

i, o, e = c.exec_command('python3 /tmp/patch_inv2.py')
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'ERR: {err[:300]}')

c.close()
print('\nPronto! Ctrl+Shift+R para recarregar.')
