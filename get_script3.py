import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

cmd = r"""docker run --rm -v /docker/dashboard/html:/data node:20-alpine node -e "
const fs = require('fs');
const html = fs.readFileSync('/data/index.html', 'utf8');
const regex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match;
let idx = 0;
while ((match = regex.exec(html)) !== null) {
  const code = match[1].trim();
  if (!code) { idx++; continue; }
  if (idx === 3) {
    const lines = code.split('\n');
    // Show first 55 lines to find the problem
    for (let i = 0; i < Math.min(55, lines.length); i++) {
      console.log('L' + (i+1) + ': ' + lines[i].substring(0, 250));
    }
  }
  idx++;
}
"
"""
i, o, e = c.exec_command(cmd)
time.sleep(10)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
