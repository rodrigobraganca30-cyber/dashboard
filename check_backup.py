import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Verificar o BACKUP mais recente do HTML
print('[1] Backup mais recente:')
i, o, e = c.exec_command("ls -lt /docker/dashboard/html/index.html.bak* 2>/dev/null | head -3")
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# Verificar se o backup também tem o erro de Script 3
print('\n[2] Testando backup mais recente com Node:')
cmd = r"""docker run --rm -v /docker/dashboard/html:/data node:20-alpine node -e "
const fs = require('fs');
const files = fs.readdirSync('/data').filter(f => f.startsWith('index.html.bak')).sort().reverse();
if (files.length === 0) { console.log('Sem backups'); process.exit(0); }
console.log('Testando:', files[0]);
const html = fs.readFileSync('/data/' + files[0], 'utf8');
const regex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match;
let idx = 0;
while ((match = regex.exec(html)) !== null) {
  const code = match[1].trim();
  if (!code) { idx++; continue; }
  try {
    new Function(code);
    console.log('Script ' + idx + ': OK');
  } catch(e) {
    console.log('Script ' + idx + ': ERRO - ' + e.message.substring(0, 100));
  }
  idx++;
}
"
"""
i, o, e = c.exec_command(cmd)
time.sleep(10)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
