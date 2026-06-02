import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

fix = r'''
const fs = require('fs');
let html = fs.readFileSync('/data/index.html', 'utf8');

// Fix 1: waFluxoCancelar('' + fl.id + '')  →  waFluxoCancelar(\' + fl.id + \')
const bad = "waFluxoCancelar('' + fl.id + '')";
const good = "waFluxoCancelar(\\'' + fl.id + '\\')";

const count = html.split(bad).length - 1;
console.log('Ocorrências do padrão quebrado:', count);

if (count > 0) {
  html = html.split(bad).join(good);
  console.log('[+] Corrigido!');
}

fs.writeFileSync('/data/index.html', html, 'utf8');

// Verify
const vm = require('vm');
const regex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match, idx = 0, errors = 0;
while ((match = regex.exec(html)) !== null) {
  const code = match[1].trim();
  if (!code) { idx++; continue; }
  try { new vm.Script(code); }
  catch(e) { 
    errors++; 
    console.log('Script ' + idx + ': ERRO - ' + e.message.substring(0, 80));
    // Show error line
    const m = e.stack.match(/evalmachine\.<anonymous>:(\d+)/);
    if (m) {
      const lines = code.split('\n');
      const errLine = parseInt(m[1]);
      console.log('  Linha ' + errLine + ': ' + lines[errLine-1].substring(0, 150));
    }
  }
  idx++;
}
console.log(errors === 0 ? 'TODOS OK (' + idx + ' scripts)' : errors + ' ERROS');
console.log('showWaSub:', html.includes('function showWaSub'));
console.log('fluxo:', html.includes('waFluxoLoadConfig'));
console.log('bloqueado:', html.includes('bloqueado'));
'''

print('[1] Corrigindo aspas do waFluxoCancelar...')
sftp = c.open_sftp()
with sftp.open('/tmp/fix_quotes.js', 'w') as f:
    f.write(fix)
sftp.close()

cmd = 'docker run --rm -v /docker/dashboard/html:/data -v /tmp:/scripts node:20-alpine node /scripts/fix_quotes.js'
i, o, e = c.exec_command(cmd)
time.sleep(15)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
