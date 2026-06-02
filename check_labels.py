import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Buscar a linha WA_STATUS_LABELS no HTML real
print('[1] Linha WA_STATUS_LABELS no HTML:')
i, o, e = c.exec_command("grep -n 'WA_STATUS_LABELS' /docker/dashboard/html/index.html")
time.sleep(2)
raw = o.read()
line = raw.decode('utf-8', errors='replace').strip()
print(f'    Tamanho: {len(line)} chars')
print(f'    Começo: {line[:200]}...')
print(f'    ...Final: ...{line[-100:]}')

# Verificar se a linha contém o fechamento };
if line.endswith('};'):
    print('    ✅ Termina com };')
elif '};' in line:
    print(f'    ⚠️ Contém }}; mas não termina com ele')
else:
    print('    ❌ NÃO contém }; — LINHA TRUNCADA!')

# Verificar se "bloqueado" está na mesma linha
if 'bloqueado' in line:
    print('    ✅ Contém "bloqueado"')
else:
    print('    ❌ NÃO contém "bloqueado" — TRUNCADA ANTES!')

# Verificar a linha seguinte
print('\n[2] Linha seguinte no HTML:')
i, o, e = c.exec_command("grep -n -A1 'WA_STATUS_LABELS' /docker/dashboard/html/index.html | tail -1")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# Verificar se o Python source tem o problema
print('\n[3] Verificar source no VPS:')
i, o, e = c.exec_command("grep 'WA_STATUS_LABELS' /docker/dashboard/whatsapp_agenda_gen.py | wc -c")
time.sleep(1)
print(f'    Tamanho da linha no source: {o.read().decode().strip()} bytes')

c.close()
