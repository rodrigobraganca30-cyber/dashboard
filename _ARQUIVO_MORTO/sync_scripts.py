import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

sftp = c.open_sftp()

# 1. Upload gerar_dashboard_v2.py
local_gen = r'C:\Users\SVOBODA\Desktop\DASHBOARD\gerar_dashboard_v2.py'
remote_gen = '/docker/dashboard/gerar_dashboard_v2.py'
print('[1/2] Uploading gerar_dashboard_v2.py...')
sftp.put(local_gen, remote_gen)
print(f'    OK ({os.path.getsize(local_gen):,} bytes)')

# 2. Upload processar_dados.py
local_proc = r'C:\Users\SVOBODA\Desktop\DASHBOARD\processar_dados.py'
remote_proc = '/docker/dashboard/processar_dados.py'
print('[2/2] Uploading processar_dados.py...')
sftp.put(local_proc, remote_proc)
print(f'    OK ({os.path.getsize(local_proc):,} bytes)')

sftp.close()
c.close()
print('\nPronto! Ambos sincronizados com a VPS.')
