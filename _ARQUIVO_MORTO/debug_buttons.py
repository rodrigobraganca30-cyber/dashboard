import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Telefones que clicaram botão recentemente
phones = [
    '5524988590582',  # SIM confirmo agora (14:20)
    '5524988280174',  # SIM confirmo (13:55)
    '5521992589627',  # Preciso reagendar (13:56)
    '5521975161316',  # SIM confirmo (13:58)
]

print('=== DEBUG: clientId para cada phone ===\n')
for phone in phones:
    # Verificar se phone2id existe
    i, o, e = c.exec_command(f'docker exec redis-agenda redis-cli GET agenda:phone2id:{phone}')
    time.sleep(1)
    cid = o.read().decode().strip()
    print(f'  {phone} → clientId: {cid or "(VAZIO - SEM MAPPING!)"}')

# Verificar o trecho do código no container
print('\n=== Trecho do webhook com BUTTON_FLOWS ===\n')
i, o, e = c.exec_command('docker exec backend-agenda sed -n "/BUTTON_FLOWS/,/FIM FLUXO/p" /app/index.js | head -50')
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

# Verificar se tem erro nos logs
print('\n=== Erros recentes ===')
i, o, e = c.exec_command('docker logs backend-agenda --tail 50 2>&1 | grep -i "error\\|erro\\|falhou\\|fail"')
time.sleep(2)
errs = o.read().decode('utf-8', errors='replace').strip()
print(f'  {errs or "Nenhum erro encontrado"}')

c.close()
