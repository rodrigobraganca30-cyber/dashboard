import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Verificar se ATIVIDADES DAS O.S.xlsx existe no servidor
print('[1/4] Verificando planilhas no servidor...')
cmds = [
    'ls -la /docker/dashboard/*ATIVIDADE* 2>/dev/null',
    'ls -la /docker/dashboard/*.xlsx 2>/dev/null | head -10',
    'ls -la /docker/dashboard/html/*ATIVIDADE* 2>/dev/null',
    'find /docker -maxdepth 3 -name "*ATIVIDADE*" 2>/dev/null',
]
for cmd in cmds:
    i, o, e = c.exec_command(cmd)
    time.sleep(2)
    out = o.read().decode('utf-8', errors='replace').strip()
    if out:
        print(f'  {out}')

# 2. Verificar se processar_dados.py roda no servidor
print('\n[2/4] Testando processar_dados.py no servidor...')
i, o, e = c.exec_command('cd /docker/dashboard && python3 processar_dados.py 2>&1 | tail -20')
time.sleep(60)  # pode demorar com downloads
out = o.read().decode('utf-8', errors='replace').strip()
print(out)

# 3. Verificar se JSONs foram gerados
print('\n[3/4] Verificando JSONs gerados...')
i, o, e = c.exec_command('ls -la /docker/dashboard/data/*.json 2>/dev/null')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

# 4. Copiar JSONs para html/data/
print('\n[4/4] Copiando JSONs para html/data/...')
i, o, e = c.exec_command('cp /docker/dashboard/data/*.json /docker/dashboard/html/data/ 2>&1 && echo OK')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
