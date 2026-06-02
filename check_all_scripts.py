import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Verificar TODOS os blocos script do dashboard HTML usando Node.js do host
print('[1] Verificando JS de /docker/dashboard/html/index.html com Node:')
cmd = r"""docker run --rm -v /docker/dashboard/html:/data node:20-alpine node -e "
const fs = require('fs');
const html = fs.readFileSync('/data/index.html', 'utf8');
const regex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match;
let idx = 0;
while ((match = regex.exec(html)) !== null) {
  const code = match[1].trim();
  if (!code) { idx++; continue; }
  try {
    new Function(code);
    console.log('Script ' + idx + ': OK (' + code.length + ' chars)');
  } catch(e) {
    console.log('Script ' + idx + ': ERRO - ' + e.message.substring(0, 200));
    // Show context around error
    const lines = code.split('\n');
    const errMatch = e.message.match(/position (\d+)/);
    if (errMatch) {
      const pos = parseInt(errMatch[1]);
      let charCount = 0;
      for (let li = 0; li < lines.length; li++) {
        charCount += lines[li].length + 1;
        if (charCount >= pos) {
          console.log('  Linha ~' + (li+1) + ': ' + lines[li].substring(0, 120));
          break;
        }
      }
    }
  }
  idx++;
}
console.log('Total scripts: ' + idx);
// Also check if showWaSub is defined
console.log('showWaSub definido:', html.includes('function showWaSub'));
"
"""
i, o, e = c.exec_command(cmd)
time.sleep(15)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'ERR: {err[:500]}')

c.close()
