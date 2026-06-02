import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Verificar backup DEFINITIVO
print('[1] Backup DEFINITIVO:')
i, o, e = c.exec_command('ls -lh /docker/backups/backup_20260526_000900_DEFINITIVO/')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 2. Tem HTML?
print('\n[2] HTML no backup DEFINITIVO:')
i, o, e = c.exec_command('ls -lh /docker/backups/backup_20260526_000900_DEFINITIVO/*.html 2>/dev/null || ls -lh /docker/backups/backup_20260526_000900_DEFINITIVO/index* 2>/dev/null')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip() or '    Nenhum HTML')

# 3. Verificar o outro backup de 26/05
print('\n[3] Backup 001552:')
i, o, e = c.exec_command('ls -lh /docker/backups/backup_20260526_001552/')
time.sleep(1)
print(o.read().decode('utf-8', errors='replace').strip())

# 4. Verificar os HTMLs de 22h do dia 26 (que tinham FLUXO)
# index.html.bak.20260526_220224 tem 13MB e foi de 22:02
print('\n[4] Testando bak.20260526_220224 (mais recente com fluxo):')
cmd = r"""docker run --rm -v /docker/dashboard/html:/data node:20-alpine node -e "
const fs = require('fs');
const html = fs.readFileSync('/data/index.html.bak.20260526_220224', 'utf8');
const hasFluxo = html.includes('waFluxoLoadConfig');
const hasBloqueado = html.includes('bloqueado');
console.log('Fluxo:', hasFluxo);
console.log('Bloqueado:', hasBloqueado);
console.log('Tamanho:', html.length);

// Check JS
const regex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match, idx = 0, errors = [];
while ((match = regex.exec(html)) !== null) {
  const code = match[1].trim();
  if (!code) { idx++; continue; }
  try { new Function(code); }
  catch(e) { errors.push('Script ' + idx + ': ' + e.message.substring(0, 80)); }
  idx++;
}
console.log('Total scripts:', idx);
if (errors.length === 0) console.log('JS: TODOS OK');
else errors.forEach(e => console.log(e));
"
"""
i, o, e = c.exec_command(cmd)
time.sleep(15)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
