import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Upload processar_dados.py atualizado
print('[1/4] Upload processar_dados.py...')
sftp = c.open_sftp()
sftp.put(r'C:\Users\SVOBODA\Desktop\DASHBOARD\processar_dados.py', '/docker/dashboard/processar_dados.py')
sftp.close()
print('    OK')

# 2. Testar execucao
print('\n[2/4] Testando no servidor...')
i, o, e = c.exec_command('cd /docker/dashboard && python3 processar_dados.py 2>&1')
time.sleep(90)
print(o.read().decode('utf-8', errors='replace').strip())

# 3. Copiar JSONs para html/data/
print('\n[3/4] Copiando para html/data/...')
i, o, e = c.exec_command('mkdir -p /docker/dashboard/html/data && cp /docker/dashboard/data/*.json /docker/dashboard/html/data/ && ls -la /docker/dashboard/html/data/')
time.sleep(3)
print(o.read().decode('utf-8', errors='replace').strip())

# 4. Configurar cron completo
print('\n[4/4] Configurando cron...')
# Criar wrapper que gera JSONs + copia para html/data/
wrapper = '#!/bin/bash\ncd /docker/dashboard\npython3 processar_dados.py >> /var/log/processar_dados.log 2>&1\ncp data/*.json html/data/ 2>/dev/null\n/docker/dashboard/gen_inv_list.sh 2>/dev/null\n'
sftp = c.open_sftp()
with sftp.open('/docker/dashboard/atualizar_dados.sh', 'w') as f:
    f.write(wrapper)
sftp.close()
c.exec_command('chmod +x /docker/dashboard/atualizar_dados.sh')
time.sleep(1)

# Atualizar cron
i, o, e = c.exec_command('crontab -l 2>/dev/null')
time.sleep(1)
cron = o.read().decode('utf-8', errors='replace').strip()

if 'atualizar_dados' not in cron:
    # Remover gen_inv_list antigo (sera chamado dentro do wrapper)
    lines = [l for l in cron.split('\n') if 'gen_inv_list' not in l]
    lines.append('0 */2 * * * /docker/dashboard/atualizar_dados.sh')
    new_cron = '\n'.join(lines) + '\n'
    sftp = c.open_sftp()
    with sftp.open('/tmp/new_cron', 'w') as f:
        f.write(new_cron)
    sftp.close()
    c.exec_command('crontab /tmp/new_cron')
    time.sleep(1)
    print('    Cron configurado: a cada 2 horas')
else:
    print('    Cron ja existe')

i, o, e = c.exec_command('crontab -l 2>/dev/null')
time.sleep(1)
print(f'    {o.read().decode("utf-8", errors="replace").strip()}')

c.close()
print('\nPronto! Dados serao atualizados automaticamente.')
