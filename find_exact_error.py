import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# O backup 20260526_220224 tinha FLUXO + BLOQUEADO + templates funcionando
# Mas tem JS erro no Script 3. Vou descobrir exatamente o que é.
backup = 'index.html.bak.20260526_220224'

print('[1] Encontrando erro exato no Script 3:')
cmd = r"""docker run --rm -v /docker/dashboard/html:/data node:20-alpine node -e "
const fs = require('fs');
const html = fs.readFileSync('/data/""" + backup + r"""', 'utf8');
const regex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match, idx = 0;
while ((match = regex.exec(html)) !== null) {
  const code = match[1].trim();
  if (!code) { idx++; continue; }
  if (idx === 3) {
    try { new Function(code); console.log('OK!'); }
    catch(e) {
      console.log('ERRO:', e.message);
      
      // Binary search for error line
      const lines = code.split('\n');
      console.log('Total linhas:', lines.length);
      
      let lo = 0, hi = lines.length - 1;
      while (lo < hi) {
        const mid = Math.floor((lo + hi) / 2);
        const chunk = lines.slice(0, mid + 1).join('\n');
        try { new Function(chunk); lo = mid + 1; }
        catch(e2) { hi = mid; }
      }
      
      console.log('Erro na linha:', lo + 1);
      for (let k = Math.max(0, lo-3); k <= Math.min(lines.length-1, lo+3); k++) {
        const marker = k === lo ? '>>>' : '   ';
        console.log(marker + ' L' + (k+1) + ': ' + lines[k].substring(0, 250));
      }
    }
  }
  idx++;
}
"
"""
i, o, e = c.exec_command(cmd)
time.sleep(30)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
