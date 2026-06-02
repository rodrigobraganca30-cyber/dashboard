import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', port=22, username='root', password='Rtb121930.')

# 1. Check CSV headers (first CSV)
print("=== HEADERS DO CSV RAW ===")
i, o, e = c.exec_command("head -1 /opt/painel_robo/data/agenda_futura_raw/2026-05-29.csv")
headers = o.read().decode('utf-8', 'replace').strip()
print(headers)

# Show columns with index
print("\n=== COLUNAS NUMERADAS ===")
cols = headers.split(',')
for idx, col in enumerate(cols):
    print(f"  [{idx}] {col}")

# 2. Show first 2 data rows
print("\n=== PRIMEIRAS 2 LINHAS DE DADOS ===")
i, o, e = c.exec_command("sed -n '2,3p' /opt/painel_robo/data/agenda_futura_raw/2026-05-29.csv")
print(o.read().decode('utf-8', 'replace'))

# 3. Show what's in column 5,6,7,24,25 of a few rows
print("=== AMOSTRA DE COLUNAS-CHAVE ===")
i, o, e = c.exec_command("""python3 -c "
import csv
with open('/opt/painel_robo/data/agenda_futura_raw/2026-05-29.csv','r',encoding='utf-8-sig') as f:
    r = csv.reader(f)
    h = next(r)
    print('Header total cols:', len(h))
    print()
    for i, row in enumerate(r):
        if i >= 5: break
        print(f'Row {i}:')
        for c in [0,1,2,3,4,5,6,7,22,23,24]:
            val = row[c] if c < len(row) else 'N/A'
            print(f'  [{c}] {h[c] if c < len(h) else \"?\"} = {val[:50]}')
        print()
" """)
print(o.read().decode('utf-8', 'replace'))

c.close()
