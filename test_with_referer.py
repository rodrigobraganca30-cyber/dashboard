import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Testar com referer header (como o frontend faz)
print('[1] GET /agenda/blacklist COM referer:')
cmd = '''docker exec backend-agenda node -e "
const http = require('http');
const options = {
  hostname: 'localhost',
  port: 3001,
  path: '/agenda/blacklist',
  headers: { 'referer': 'http://localhost' }
};
http.get(options, r => {
  let d = '';
  r.on('data', c => d += c);
  r.on('end', () => {
    try {
      const arr = JSON.parse(d);
      if (Array.isArray(arr)) {
        console.log('OK - Array com', arr.length, 'itens');
        console.log('Amostra:', JSON.stringify(arr.slice(0,5)));
      } else {
        console.log('Resposta:', d.substring(0, 200));
      }
    } catch(e) {
      console.log('Resposta raw:', d.substring(0, 200));
    }
  });
});
"'''
i, o, e = c.exec_command(cmd)
time.sleep(5)
out = o.read().decode('utf-8', errors='replace').strip()
err_out = e.read().decode('utf-8', errors='replace').strip()
print(f'    {out}')
if err_out:
    print(f'    ERR: {err_out[:200]}')

c.close()
print('\n=== BACKEND V2 CONFIRMADO ===')
