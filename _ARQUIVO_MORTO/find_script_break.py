import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

backup_file = 'index.html.bak.pre_restore_20260525_195019'

# Ver o que está antes do "WhatsApp Agenda State" no HTML
print('[1] Contexto antes do bloco WhatsApp Agenda:')
cmd = f'grep -n -B5 "WhatsApp Agenda State" /docker/dashboard/html/{backup_file} | head -20'
i, o, e = c.exec_command(cmd)
time.sleep(2)
print(o.read().decode('utf-8', errors='replace').strip())

# Ver o final do Script 6 (que não fecha)
print('\n[2] Verificando tag script antes do bloco WA:')
cmd2 = r"""docker run --rm -v /docker/dashboard/html:/data node:20-alpine node -e "
const fs = require('fs');
const html = fs.readFileSync('/data/""" + backup_file + r"""', 'utf8');
// Find the position of 'WhatsApp Agenda State'
const waPos = html.indexOf('WhatsApp Agenda State');
if (waPos < 0) { console.log('Nao encontrado!'); process.exit(0); }
// Show 500 chars before it
const before = html.substring(Math.max(0, waPos - 500), waPos);
console.log('--- 500 chars antes do WA Agenda State ---');
console.log(before);
console.log('--- Posição:', waPos, '---');

// Check if there's a </script><script> between Script 6 and WA
const lastScript = html.lastIndexOf('<script>', waPos);
const lastEndScript = html.lastIndexOf('</script>', waPos);
console.log('Ultimo <script> antes do WA:', lastScript);
console.log('Ultimo </script> antes do WA:', lastEndScript);
console.log('');
if (lastScript > lastEndScript) {
  console.log('>>> O <script> em pos', lastScript, 'NAO tem </script> antes do WA');
  console.log('>>> Conteúdo entre <script> e WA:');
  console.log(html.substring(lastScript, waPos).substring(0, 300));
}
"
"""
i, o, e = c.exec_command(cmd2)
time.sleep(10)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
