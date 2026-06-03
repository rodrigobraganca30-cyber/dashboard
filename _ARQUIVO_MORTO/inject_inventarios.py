import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

ts = time.strftime('%Y%m%d_%H%M%S')

# Backup
print('[1/3] Backup...')
i, o, e = c.exec_command(f'cp /docker/dashboard/html/index.html /docker/backup_dashboard_{ts}_pre_inv.html')
time.sleep(1)

patch = r'''
import os, re

html = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()

# 1. Copiar inventarios faltantes para a pasta inventarios/
inv_dir = '/docker/dashboard/html/inventarios'
html_dir = '/docker/dashboard/html'

# Listar o que ja existe em inventarios/
existing = set()
if os.path.isdir(inv_dir):
    for f in os.listdir(inv_dir):
        if f.startswith('inventario_') and f.endswith('.xlsx'):
            existing.add(f)

# Copiar da raiz para inventarios/ se faltam
copied = 0
for f in os.listdir(html_dir):
    if f.startswith('inventario_') and f.endswith('.xlsx') and f not in existing:
        src = os.path.join(html_dir, f)
        dst = os.path.join(inv_dir, f)
        import shutil
        shutil.copy2(src, dst)
        existing.add(f)
        copied += 1
        print('[+] Copiado para inventarios/: %s' % f)

# 2. Listar todos os inventarios com tamanho
all_inv = []
for f in sorted(os.listdir(inv_dir)):
    if f.startswith('inventario_') and f.endswith('.xlsx'):
        # Extrair data: inventario_DD-MM-YYYY.xlsx
        m = re.search(r'inventario_(\d{2})-(\d{2})-(\d{4})', f)
        if m:
            dd, mm, yyyy = m.group(1), m.group(2), m.group(3)
            date_str = '%s-%s-%s' % (dd, mm, yyyy)
            size_kb = os.path.getsize(os.path.join(inv_dir, f)) // 1024
            all_inv.append((date_str, size_kb, f))

# Ordenar por data decrescente (mais recente primeiro)
def date_sort_key(item):
    parts = item[0].split('-')
    return (int(parts[2]), int(parts[1]), int(parts[0]))
all_inv.sort(key=date_sort_key, reverse=True)

print('\nInventarios encontrados: %d' % len(all_inv))
for inv in all_inv:
    print('  %s  %d KB' % (inv[0], inv[1]))

# 3. Encontrar a secao de inventarios no HTML e substituir
# Procurar o contador "X relatorios diarios"
count_match = re.search(r'<div[^>]*style="[^"]*font-size:\s*48px[^"]*"[^>]*>\s*(\d+)\s*</div>\s*<div[^>]*>\s*relat', html)
if count_match:
    old_count = count_match.group(1)
    html = html.replace('>%s</div>' % old_count + '\n', '>%d</div>\n' % len(all_inv), 1)
    # Try simpler replacement
    html = html.replace('>%s<' % old_count, '>%d<' % len(all_inv), 1)
    print('\n[+] Contador: %s -> %d' % (old_count, len(all_inv)))

# 4. Reconstruir a tabela de inventarios
# Encontrar a tabela existente
table_start = html.find('DOWNLOAD DE INVENT')
if table_start < 0:
    table_start = html.find('download de invent')
if table_start < 0:
    table_start = html.find('Download de Invent')

if table_start > 0:
    # Encontrar o container da tabela (procurar o proximo <table ou grid)
    # Procurar as linhas de inventario existentes
    # Pattern: dd-mm-yyyy ... KB ... Baixar
    
    # Encontrar o bloco que contem as linhas
    # Procurar primeiro inventario listado
    first_inv_match = re.search(r'<tr[^>]*>.*?inventario_\d{2}-\d{2}-\d{4}', html[table_start:], re.DOTALL)
    if not first_inv_match:
        first_inv_match = re.search(r'<div[^>]*>.*?\d{2}-\d{2}-\d{4}.*?KB', html[table_start:table_start+5000], re.DOTALL)
    
    # Abordagem diferente: encontrar todas as linhas de inventario e substituir
    # Procurar o padrao exato das linhas
    inv_pattern = re.compile(r'(<tr[^>]*>\s*<td[^>]*>\s*\d{2}-\d{2}-\d{4}\s*</td>.*?</tr>)', re.DOTALL)
    matches = list(inv_pattern.finditer(html, table_start))
    
    if matches:
        print('\n[+] Encontradas %d linhas na tabela' % len(matches))
        start_pos = matches[0].start()
        end_pos = matches[-1].end()
        
        # Construir novas linhas
        new_rows = ''
        for date_str, size_kb, fname in all_inv:
            new_rows += '              <tr style="border-bottom:1px solid #1c2237">\n'
            new_rows += '                <td style="padding:10px 16px;font-weight:600;color:#e2e8f0">%s</td>\n' % date_str
            new_rows += '                <td style="padding:10px 16px;color:#64748b">%d KB</td>\n' % size_kb
            new_rows += '                <td style="padding:10px 16px;text-align:right"><a href="inventarios/%s" download style="color:#25d366;text-decoration:none;font-weight:600">Baixar Planilha</a></td>\n' % fname
            new_rows += '              </tr>\n'
        
        html = html[:start_pos] + new_rows + html[end_pos:]
        print('[+] Tabela substituida com %d linhas' % len(all_inv))
    else:
        print('[!] Nenhuma linha <tr> encontrada, tentando outro formato...')
        # Tentar formato com divs
        div_pattern = re.compile(r'(<div[^>]*>\s*<span[^>]*>\s*\d{2}-\d{2}-\d{4})', re.DOTALL)
        div_matches = list(div_pattern.finditer(html, table_start))
        if div_matches:
            print('[+] Encontradas %d linhas (div format)' % len(div_matches))
else:
    print('[!] Secao DOWNLOAD DE INVENTARIOS nao encontrada')

# Atualizar contador no topo
old_14 = '>14<'
if old_14 in html:
    html = html.replace(old_14, '>%d<' % len(all_inv), 1)
    print('[+] Contador 14 -> %d' % len(all_inv))

open('/docker/dashboard/html/index.html', 'w', encoding='utf-8').write(html)
print('\n[OK] HTML salvo (%d bytes)' % len(html))

# Verificacao
v = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()
inv_count = len(re.findall(r'inventario_\d{2}-\d{2}-\d{4}\.xlsx', v))
print('[v] Refs a inventarios no HTML: %d' % inv_count)
'''

print('\n[2/3] Aplicando patch...')
sftp = c.open_sftp()
with sftp.open('/tmp/patch_inv.py', 'w') as f:
    f.write(patch)
sftp.close()

i, o, e = c.exec_command('python3 /tmp/patch_inv.py')
time.sleep(8)
out = o.read().decode('utf-8', errors='replace').strip()
err = e.read().decode('utf-8', errors='replace').strip()
print(out)
if err:
    print(f'ERR: {err[:500]}')

c.close()
print('\n[3/3] Recarregue a pagina (Ctrl+Shift+R)')
