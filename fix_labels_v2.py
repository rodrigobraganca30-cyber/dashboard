import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

fix_script = r'''
import re

with open('/docker/dashboard/html/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Encontrar TODAS as ocorrências de WA_STATUS_LABELS
idx = 0
positions = []
while True:
    pos = html.find('WA_STATUS_LABELS', idx)
    if pos < 0:
        break
    # Pegar contexto: 20 chars antes, 100 depois
    before = html[max(0,pos-20):pos]
    after = html[pos:pos+200]
    # Verificar se tem \n dentro da declaração
    eol = html.find('\n', pos)
    line_content = html[pos:eol] if eol > 0 else html[pos:pos+500]
    is_broken = '};' not in line_content and 'WA_STATUS_LABELS[' not in line_content
    positions.append((pos, is_broken, line_content[:120]))
    print(f'Pos {pos}: broken={is_broken} -> {line_content[:100]}')
    idx = pos + 1

print(f'\nTotal: {len(positions)} ocorrências')

# Encontrar a quebrada (que é uma declaração var mas não tem };)
for pos, is_broken, preview in positions:
    if is_broken and 'var' in html[max(0,pos-10):pos+5]:
        print(f'\n[!] QUEBRADA na pos {pos}')
        
        # Encontrar o início da linha (var WA_STATUS_LABELS)
        line_start = html.rfind('\n', 0, pos) + 1
        # Encontrar onde deveria terminar (};)
        # A declaração está partida em múltiplas linhas
        # Procurar a próxima 'function ' que indica que acabou a declaração
        next_func = html.find('function ', pos)
        # Tudo entre pos e next_func é a declaração quebrada + lixo
        chunk = html[line_start:next_func]
        print(f'Chunk quebrado ({len(chunk)} chars):')
        print(repr(chunk[:300]))
        
        # Agora pegar a versão completa (a que funciona)
        for pos2, is_broken2, preview2 in positions:
            if not is_broken2 and 'var' in html[max(0,pos2-10):pos2+5]:
                # Esta é a versão boa
                good_start = html.rfind('\n', 0, pos2) + 1
                good_end = html.find('\n', html.find('};', pos2))
                good_line = html[good_start:good_end]
                print(f'\n[+] Versão boa na pos {pos2} ({len(good_line)} chars)')
                print(f'Preview: {good_line[:100]}...{good_line[-50:]}')
                
                # Substituir: remover o chunk quebrado e colocar a versão boa
                html = html[:line_start] + good_line + '\n' + html[next_func:]
                
                with open('/docker/dashboard/html/index.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f'\n[+] HTML corrigido! ({len(html)} bytes)')
                break
        break
'''

print('[1] Enviando fix v2...')
sftp = c.open_sftp()
with sftp.open('/tmp/fix_labels_v2.py', 'w') as f:
    f.write(fix_script)
sftp.close()

print('[2] Executando...')
i, o, e = c.exec_command('python3 /tmp/fix_labels_v2.py')
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'ERR: {err[:300]}')

# Verificar
print('\n[3] Verificando JS:')
cmd = r"""docker run --rm -v /docker/dashboard/html:/data node:20-alpine node -e "
const fs = require('fs');
const html = fs.readFileSync('/data/index.html', 'utf8');
const regex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
let match, idx = 0, errors = 0;
while ((match = regex.exec(html)) !== null) {
  const code = match[1].trim();
  if (!code) { idx++; continue; }
  try { new Function(code); }
  catch(e) { errors++; console.log('Script ' + idx + ': ERRO - ' + e.message.substring(0, 80)); }
  idx++;
}
console.log(errors === 0 ? 'TODOS OK (' + idx + ' scripts)' : errors + ' ERROS');
console.log('showWaSub:', html.includes('function showWaSub'));
console.log('fluxo:', html.includes('waFluxoLoadConfig'));
console.log('bloqueado:', html.includes('bloqueado'));
"
"""
i, o, e = c.exec_command(cmd)
time.sleep(15)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
