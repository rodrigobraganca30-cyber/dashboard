import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

extract = r'''
const fs = require('fs');
const html = fs.readFileSync('/data/index.html', 'utf8');
const regex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match, idx = 0;
while ((match = regex.exec(html)) !== null) {
  const code = match[1].trim();
  if (!code) { idx++; continue; }
  if (idx === 3) {
    // Save to file
    fs.writeFileSync('/data/script3.js', code);
    console.log('Script 3 saved: ' + code.length + ' chars, ' + code.split('\n').length + ' lines');
    
    // Try to compile with vm module for exact error position
    const vm = require('vm');
    try {
      new vm.Script(code, { filename: 'script3.js' });
      console.log('No error!');
    } catch(e) {
      console.log('ERROR:', e.message);
      // Parse the line number from error
      const match2 = e.stack.match(/script3\.js:(\d+)/);
      if (match2) {
        const errLine = parseInt(match2[1]);
        console.log('Error at line:', errLine);
        const lines = code.split('\n');
        for (let k = Math.max(0, errLine-4); k <= Math.min(lines.length-1, errLine+2); k++) {
          const marker = k === errLine-1 ? '>>>' : '   ';
          console.log(marker + ' L' + (k+1) + ': ' + lines[k].substring(0, 250));
        }
        
        // Show hex of error line
        const errorLine = lines[errLine-1];
        console.log('\nHex dump of error line (first 100 chars):');
        for (let j = 0; j < Math.min(100, errorLine.length); j++) {
          const cp = errorLine.codePointAt(j);
          if (cp > 127) {
            console.log('  pos ' + j + ': U+' + cp.toString(16).toUpperCase() + ' (' + cp + ')');
          }
        }
      }
    }
  }
  idx++;
}
'''

print('[1] Extraindo e compilando Script 3...')
sftp = c.open_sftp()
with sftp.open('/tmp/extract_compile.js', 'w') as f:
    f.write(extract)
sftp.close()

cmd = 'docker run --rm -v /docker/dashboard/html:/data -v /tmp:/scripts node:20-alpine node /scripts/extract_compile.js'
i, o, e = c.exec_command(cmd)
time.sleep(15)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
