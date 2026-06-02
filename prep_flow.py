import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Backup do index.js atual
print('[1] Backup do index.js atual...')
i, o, e = c.exec_command('docker cp backend-agenda:/app/index.js /docker/backup_index_pre_flow.js')
time.sleep(2)
print('    OK')

# 2. Encontrar a linha do /health para inserir antes
print('\n[2] Procurando ponto de inserção...')
i, o, e = c.exec_command('''docker exec backend-agenda node -e "
const fs = require('fs');
const c = fs.readFileSync('/app/index.js', 'utf8');
const lines = c.split('\\n');
lines.forEach((l, i) => {
  if (l.includes('/health') || l.includes('app.listen'))
    console.log('L' + (i+1) + ':', l.substring(0, 100));
});
console.log('Total:', lines.length, 'linhas');
"''')
time.sleep(3)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
