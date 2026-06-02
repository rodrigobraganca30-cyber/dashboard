import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Encontrar IDs de tabelas na aba frota
cmds = [
    "grep -n 'frota-veiculos\\|frota-manut\\|frota-comb\\|frota-desl' /docker/dashboard/html/index.html | head -20",
    "grep -n 'table.*frota\\|frota.*table\\|frota.*tbody' /docker/dashboard/html/index.html | head -10",
    "grep -c '<table' /docker/dashboard/html/index.html",
    "grep -n 'veiculos-table\\|table-veiculos\\|placa-table\\|oficina-table\\|revisao-table\\|comb-table\\|desl-table' /docker/dashboard/html/index.html | head -10",
    "grep -n 'id=\"frota' /docker/dashboard/html/index.html | head -10",
]

for cmd in cmds:
    i, o, e = c.exec_command(cmd)
    time.sleep(2)
    out = o.read().decode('utf-8', errors='replace').strip()
    print(f'CMD: {cmd.split("/docker")[0]}...')
    print(f'  {out}')
    print()

# Extrair a estrutura das tabelas na aba frota
i, o, e = c.exec_command(r"python3 -c \"import re; h=open('/docker/dashboard/html/index.html').read(); i=h.find('id=\\\"frota\\\"'); print('frota div at:', i); chunk=h[i:i+5000]; tbls=re.findall(r'<table[^>]*>', chunk); print('Tables:', tbls[:5]); tbodies=re.findall(r'<tbody[^>]*>', chunk); print('Tbodies:', tbodies[:5])\"")
time.sleep(3)
print('Structure:')
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
