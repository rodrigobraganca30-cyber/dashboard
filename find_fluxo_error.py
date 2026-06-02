import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Usar o backup pre_restore que tem FLUXO
backup_file = 'index.html.bak.pre_restore_20260525_195019'

print(f'[1] Analisando JS do backup: {backup_file}')
cmd = r"""docker run --rm -v /docker/dashboard/html:/data node:20-alpine node -e "
const fs = require('fs');
const html = fs.readFileSync('/data/""" + backup_file + r"""', 'utf8');
const regex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match, idx = 0;
while ((match = regex.exec(html)) !== null) {
  const code = match[1].trim();
  if (!code) { idx++; continue; }
  try {
    new Function(code);
    console.log('Script ' + idx + ': OK (' + code.length + ' chars)');
  } catch(e) {
    console.log('Script ' + idx + ': ERRO - ' + e.message);
    // Find error line
    const lines = code.split('\n');
    for (let j = 0; j < lines.length; j++) {
      const sub = lines.slice(0, j + 1).join('\n');
      try { new Function(sub + '\n}'); } catch(e2) {
        if (e2.message.includes('Unexpected') || e2.message.includes('Invalid')) {
          console.log('  Linha ~' + (j+1) + ': ' + lines[j].substring(0, 200));
          if (j > 0) console.log('  Anterior: ' + lines[j-1].substring(0, 200));
          if (j+1 < lines.length) console.log('  Seguinte: ' + lines[j+1].substring(0, 200));
          break;
        }
      }
    }
  }
  idx++;
}
"
"""
i, o, e = c.exec_command(cmd)
time.sleep(20)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
