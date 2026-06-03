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
    try {
      new Function(code);
      console.log('Script 3: OK');
    } catch(e) {
      console.log('ERRO:', e.message);
      // Find error line
      const lines = code.split('\n');
      // Try to find the problematic line by checking each part
      let start = 0;
      let chunkSize = 50;
      for (let i = 0; i < lines.length; i += chunkSize) {
        const chunk = lines.slice(0, i + chunkSize).join('\n');
        try {
          new Function(chunk + '\n}'); // close it to test
        } catch(e2) {
          // Narrow down within this chunk
          for (let j = Math.max(0, i); j < Math.min(lines.length, i + chunkSize); j++) {
            const subChunk = lines.slice(0, j + 1).join('\n');
            try {
              new Function(subChunk + '\n}');
            } catch(e3) {
              if (e3.message.includes('Unexpected string') || e3.message.includes('Unexpected token')) {
                console.log('Linha ~' + (j+1) + ': ' + lines[j].substring(0, 200));
                // Show context
                for (let k = Math.max(0, j-2); k <= Math.min(lines.length-1, j+2); k++) {
                  console.log((k === j ? '>>> ' : '    ') + 'L' + (k+1) + ': ' + lines[k].substring(0, 180));
                }
                console.log('');
                console.log('Total de linhas no script:', lines.length);
                process.exit(0);
              }
            }
          }
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
time.sleep(15)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err and 'Pulling' not in err:
    print(f'ERR: {err[:300]}')

c.close()
