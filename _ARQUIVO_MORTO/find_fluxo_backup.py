import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Listar backups por data (mais recentes primeiro) e verificar quais têm o fluxo
print('[1] Backups disponíveis com fluxo:')
cmd = r"""docker run --rm -v /docker/dashboard/html:/data node:20-alpine node -e "
const fs = require('fs');
const files = fs.readdirSync('/data')
  .filter(f => f.startsWith('index.html.bak'))
  .sort()
  .reverse()
  .slice(0, 15);

for (const file of files) {
  try {
    const html = fs.readFileSync('/data/' + file, 'utf8');
    const hasFluxo = html.includes('waFluxoLoadConfig') || html.includes('FLUXO AUTOMÁTICO');
    const hasBloqueado = html.includes('bloqueado');
    
    // Check JS errors
    const regex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
    let match, idx = 0, jsOk = true;
    while ((match = regex.exec(html)) !== null) {
      const code = match[1].trim();
      if (!code) { idx++; continue; }
      try { new Function(code); }
      catch(e) { jsOk = false; }
      idx++;
    }
    
    const status = [];
    if (hasFluxo) status.push('FLUXO');
    if (hasBloqueado) status.push('BLOQ');
    if (jsOk) status.push('JS-OK');
    else status.push('JS-ERRO');
    
    console.log(file.padEnd(55) + ' ' + status.join(' | '));
  } catch(e) {
    console.log(file.padEnd(55) + ' ERRO: ' + e.message.substring(0, 50));
  }
}
"
"""
i, o, e = c.exec_command(cmd)
time.sleep(30)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err and 'Pulling' not in err and 'Downloaded' not in err:
    print(f'ERR: {err[:200]}')

c.close()
