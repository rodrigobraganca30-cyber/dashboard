import paramiko, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', port=22, username='root', password='Rtb121930.')

sftp = c.open_sftp()
remote = "/opt/painel_robo/data/csv/ATIVIDADES DAS O.S.xlsx"
local = r"C:\Users\SVOBODA\Desktop\DASHBOARD\ATIVIDADES DAS O.S.xlsx"

# Verificar tamanho remoto
stat = sftp.stat(remote)
print(f"Servidor: {stat.st_size:,} bytes")
print(f"Local:    {os.path.getsize(local):,} bytes")

# Download
sftp.get(remote, local)
print(f"✅ Download concluído: {os.path.getsize(local):,} bytes")
sftp.close()
c.close()
