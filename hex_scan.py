import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

hex_script = r'''
const fs = require('fs');
const html = fs.readFileSync('/data/index.html', 'utf8');

// Encontrar a posição exata do truncamento
const marker = "Entregue D-0','en";
const pos = html.indexOf(marker);
if (pos < 0) { console.log('Marker not found'); process.exit(0); }

console.log('Marker encontrado na pos:', pos);

// Mostrar 50 chars depois do marker em formato hex + ascii
const after = html.substring(pos + marker.length - 3, pos + marker.length + 50);
console.log('\nConteúdo após "en":');
for (let i = 0; i < after.length; i++) {
  const cp = after.codePointAt(i);
  const hex = cp.toString(16).padStart(4, '0');
  const ch = cp >= 32 && cp < 127 ? after[i] : (cp === 10 ? '\\n' : cp === 13 ? '\\r' : '?');
  console.log(`  [${i}] U+${hex} = ${ch} (${cp})`);
  if (i > 20 && cp === 102) break; // stop at 'f' of function
}

// Show 200 chars in raw form
console.log('\nRaw 200 chars after marker:');
console.log(JSON.stringify(after.substring(0, 200)));

// Also check: does the WA_STATUS_LABELS end with };
const labelStart = html.lastIndexOf('WA_STATUS_LABELS=', pos);
const labelEnd = html.indexOf('};', labelStart);
const nextNewline = html.indexOf('\n', labelStart);
console.log('\nWA_STATUS_LABELS starts at:', labelStart);
console.log('Next }; at:', labelEnd);
console.log('Next newline at:', nextNewline);
console.log('}; BEFORE newline:', labelEnd < nextNewline);
console.log('Content at newline pos:', JSON.stringify(html.substring(nextNewline - 5, nextNewline + 5)));
'''

print('[1] Analisando bytes...')
sftp = c.open_sftp()
with sftp.open('/tmp/hex_scan.js', 'w') as f:
    f.write(hex_script)
sftp.close()

cmd = 'docker run --rm -v /docker/dashboard/html:/data -v /tmp:/scripts node:20-alpine node /scripts/hex_scan.js'
i, o, e = c.exec_command(cmd)
time.sleep(15)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
