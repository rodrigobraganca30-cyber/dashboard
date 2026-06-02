"""
backup_vps.py - Backup completo dos arquivos críticos do VPS
"""
import paramiko, os, sys, datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh_key = os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa')
pkey = paramiko.RSAKey.from_private_key_file(ssh_key)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('187.77.240.87', port=22, username='root', pkey=pkey)

ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

# 1. Backup do /opt/painel_robo (robô oracle + gerar_tv_os)
print('[...] Fazendo backup de /opt/painel_robo ...')
stdin, stdout, stderr = client.exec_command(
    f'tar -czf /root/backup_painel_robo_{ts}.tar.gz /opt/painel_robo/ 2>&1 && echo OK'
)
out = stdout.read().decode('utf-8', errors='replace')
print(f'  painel_robo: {out.strip()}')

# 2. Backup do /docker/dashboard (scripts Python + HTML gerado)
print('[...] Fazendo backup de /docker/dashboard ...')
stdin, stdout, stderr = client.exec_command(
    f'tar -czf /root/backup_docker_dashboard_{ts}.tar.gz /docker/dashboard/ 2>&1 && echo OK'
)
out = stdout.read().decode('utf-8', errors='replace')
print(f'  docker/dashboard: {out.strip()}')

# 3. Lista os backups criados no VPS
print('\n[...] Backups no VPS (/root/):')
stdin, stdout, stderr = client.exec_command('ls -lh /root/backup_*.tar.gz 2>/dev/null')
print(stdout.read().decode('utf-8', errors='replace'))

# 4. Baixa os backups para o PC local
print('[...] Baixando backups para o PC...')
sftp = client.open_sftp()

backup_dir = r'C:\Users\SVOBODA\Desktop\BACKUPS_VPS'
os.makedirs(backup_dir, exist_ok=True)

for nome in [f'backup_painel_robo_{ts}.tar.gz', f'backup_docker_dashboard_{ts}.tar.gz']:
    remote = f'/root/{nome}'
    local  = os.path.join(backup_dir, nome)
    try:
        sftp.get(remote, local)
        size = os.path.getsize(local) / (1024*1024)
        print(f'  [OK] {nome} -> {size:.1f} MB')
    except Exception as e:
        print(f'  [ERRO] {nome}: {e}')

sftp.close()
client.close()

print(f'\n[CONCLUIDO] Backups salvos em: {backup_dir}')
print(f'  Timestamp: {ts}')
