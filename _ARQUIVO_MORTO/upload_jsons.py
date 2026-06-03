import paramiko, os, sys, glob, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

sftp = c.open_sftp()
rdir = '/docker/dashboard/html/data'
try:
    sftp.stat(rdir)
except IOError:
    sftp.mkdir(rdir)
    print('Pasta data/ criada')

jsons = glob.glob(r'C:\Users\SVOBODA\Desktop\DASHBOARD\data\*.json')
for j in jsons:
    sftp.put(j, rdir + '/' + os.path.basename(j))
    print(f'  {os.path.basename(j)}: {os.path.getsize(j)//1024} KB')

sftp.close()
c.close()
print(f'OK! {len(jsons)} JSONs enviados para VPS')
