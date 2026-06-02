import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Script Python no VPS para corrigir a linha quebrada
fix_script = r'''
import re

with open('/docker/dashboard/html/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)

# O problema: a linha WA_STATUS_LABELS está quebrada com \n no meio
# Encontrar o padrão: WA_STATUS_LABELS={... (incompleto) \n (lixo/vazio) \n ... };
# Precisamos juntar tudo em uma única linha

# Encontrar onde começa
start = html.find('var WA_STATUS_LABELS={')
if start < 0:
    start = html.find('WA_STATUS_LABELS={')
if start < 0:
    print('[!] WA_STATUS_LABELS nao encontrado!')
    exit(1)

print(f'[+] WA_STATUS_LABELS encontrado na pos {start}')

# Encontrar o }; que fecha a declaração
# Procurar o próximo }; após o início
end = html.find('};', start)
if end < 0:
    print('[!] Fechamento }; nao encontrado!')
    exit(1)

end += 2  # incluir o };

# Extrair o bloco inteiro
block = html[start:end]
print(f'[+] Bloco original: {len(block)} chars, {block.count(chr(10))} line breaks')

# Remover line breaks internos (manter tudo em uma linha)
fixed_block = block.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
# Remover espaços duplos
while '  ' in fixed_block:
    fixed_block = fixed_block.replace('  ', ' ')

print(f'[+] Bloco corrigido: {len(fixed_block)} chars, {fixed_block.count(chr(10))} line breaks')

# Substituir no HTML
html = html[:start] + fixed_block + html[end:]

with open('/docker/dashboard/html/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'[+] HTML salvo ({original_len} -> {len(html)} bytes)')
print(f'[+] Preview: {fixed_block[:100]}...{fixed_block[-50:]}')
'''

print('[1] Enviando fix...')
sftp = c.open_sftp()
with sftp.open('/tmp/fix_labels.py', 'w') as f:
    f.write(fix_script)
sftp.close()

print('[2] Executando fix...')
i, o, e = c.exec_command('python3 /tmp/fix_labels.py')
time.sleep(3)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'ERR: {err[:200]}')

# Verificar JS
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
