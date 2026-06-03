import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# 1. Restaurar o bak2 (que era funcional)
print('[1] Restaurando bak2 (funcional)...')
i, o, e = c.exec_command('cp /docker/dashboard/html/index.html.bak2 /docker/dashboard/html/index.html')
err = e.read().decode().strip()
print(f'    {"ERRO: " + err if err else "OK"}')

# 2. Verificar se o bak2 restaurado está OK
print('\n[2] Verificando JS do bak2:')
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
"
"""
i, o, e = c.exec_command(cmd)
time.sleep(10)
print(o.read().decode('utf-8', errors='replace').strip())

# 3. Upload inject_bloqueado.py para o VPS
print('\n[3] Enviando inject_bloqueado.py...')
sftp = c.open_sftp()
sftp.put('C:/Users/SVOBODA/Desktop/DASHBOARD/inject_bloqueado.py', '/tmp/inject_bloqueado.py')
sftp.close()
print('    OK')

# 4. Executar no VPS
print('\n[4] Executando injeção...')
i, o, e = c.exec_command('python3 /tmp/inject_bloqueado.py')
time.sleep(3)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'    ERR: {err[:200]}')

# 5. Verificar JS pós-injeção
print('\n[5] Verificando JS pós-injeção:')
i, o, e = c.exec_command(cmd)
time.sleep(10)
result = o.read().decode('utf-8', errors='replace').strip()
print(result)

if 'TODOS OK' in result:
    print('\n✅ SUCESSO! Botões devem funcionar agora.')
else:
    print('\n❌ Ainda tem erros.')

c.close()
