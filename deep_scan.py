import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Extrair Script 3 completo e testar linha por linha
scan = r"""
const fs = require('fs');
const html = fs.readFileSync('/data/index.html', 'utf8');
const regex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match, idx = 0;
while ((match = regex.exec(html)) !== null) {
  const code = match[1].trim();
  if (!code) { idx++; continue; }
  if (idx === 3) {
    const lines = code.split('\n');
    console.log('Script 3: ' + lines.length + ' linhas');
    
    // Teste incremental: adicionar linhas uma a uma
    let accumulated = '';
    for (let i = 0; i < Math.min(lines.length, 50); i++) {
      accumulated += lines[i] + '\n';
      try {
        // Tentar fechar com } pra não dar erro de "unexpected end"
        new Function(accumulated + '\n}}}}}}}}}}}}}}}}}}}');
      } catch(e) {
        if (e.message.includes('Unexpected string') || e.message.includes('Invalid or unexpected token')) {
          console.log('ERRO na linha ' + (i+1) + ': ' + e.message);
          console.log('  Conteudo: ' + JSON.stringify(lines[i].substring(0, 200)));
          if (i > 0) console.log('  Anterior: ' + JSON.stringify(lines[i-1].substring(0, 200)));
          
          // Verificar caracteres especiais
          const line = lines[i];
          for (let j = 0; j < line.length; j++) {
            const cp = line.codePointAt(j);
            if (cp > 127 && cp < 160) {
              console.log('  Char suspeito pos ' + j + ': U+' + cp.toString(16) + ' = ' + JSON.stringify(line[j]));
            }
          }
          break;
        }
      }
    }
    
    // Também mostrar os primeiros 10 linhas pra contexto
    console.log('\n--- Primeiras 10 linhas ---');
    for (let i = 0; i < Math.min(10, lines.length); i++) {
      console.log('L' + (i+1) + ': ' + JSON.stringify(lines[i].substring(0, 250)));
    }
  }
  idx++;
}
"""

print('[1] Scan profundo do Script 3...')
sftp = c.open_sftp()
with sftp.open('/tmp/scan_script3.js', 'w') as f:
    f.write(scan)
sftp.close()

cmd = 'docker run --rm -v /docker/dashboard/html:/data -v /tmp:/scripts node:20-alpine node /scripts/scan_script3.js'
i, o, e = c.exec_command(cmd)
time.sleep(20)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
