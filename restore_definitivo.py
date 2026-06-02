import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

DEFINITIVO = '/docker/backups/backup_20260526_000900_DEFINITIVO'

# 1. Testar JS do HTML DEFINITIVO
print('[1] Testando JS do backup DEFINITIVO:')
cmd = r"""docker run --rm -v """ + DEFINITIVO + r""":/data node:20-alpine node -e "
const fs = require('fs');
const html = fs.readFileSync('/data/index.html', 'utf8');
const hasFluxo = html.includes('waFluxoLoadConfig');
const hasBloqueado = html.includes('bloqueado');
console.log('Fluxo:', hasFluxo);
console.log('Bloqueado:', hasBloqueado);

const regex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match, idx = 0, errors = 0;
while ((match = regex.exec(html)) !== null) {
  const code = match[1].trim();
  if (!code) { idx++; continue; }
  try { new Function(code); console.log('Script ' + idx + ': OK'); }
  catch(e) { errors++; console.log('Script ' + idx + ': ERRO - ' + e.message.substring(0, 80)); }
  idx++;
}
console.log(errors === 0 ? 'TODOS OK' : errors + ' ERROS');
"
"""
i, o, e = c.exec_command(cmd)
time.sleep(15)
print(o.read().decode('utf-8', errors='replace').strip())

# Se tiver fluxo E JS OK, restaurar
print('\n[2] Restaurando DEFINITIVO...')
# Backup do atual
i, o, e = c.exec_command('cp /docker/dashboard/html/index.html /docker/dashboard/html/index.html.bak.pre_definitivo')
e.read()
# Copiar o HTML
i, o, e = c.exec_command(f'cp {DEFINITIVO}/index.html /docker/dashboard/html/index.html')
err = e.read().decode().strip()
print(f'    HTML: {"OK" if not err else "ERRO: " + err}')

# 3. Injetar bloqueado
print('\n[3] Injetando bloqueado...')
i, o, e = c.exec_command('python3 /tmp/inject_bloqueado.py')
time.sleep(3)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'    ERR: {err[:200]}')

# 4. Verificação final
print('\n[4] Verificação final:')
cmd2 = r"""docker run --rm -v /docker/dashboard/html:/data node:20-alpine node -e "
const fs = require('fs');
const html = fs.readFileSync('/data/index.html', 'utf8');
console.log('Fluxo:', html.includes('waFluxoLoadConfig'));
console.log('Bloqueado:', html.includes('bloqueado'));
const regex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match, idx = 0, errors = 0;
while ((match = regex.exec(html)) !== null) {
  const code = match[1].trim();
  if (!code) { idx++; continue; }
  try { new Function(code); }
  catch(e) { errors++; console.log('Script ' + idx + ': ERRO - ' + e.message.substring(0, 80)); }
  idx++;
}
console.log(errors === 0 ? 'JS: TODOS OK (' + idx + ' scripts)' : errors + ' ERROS');
"
"""
i, o, e = c.exec_command(cmd2)
time.sleep(15)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
