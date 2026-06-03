import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Teste blacklist API de dentro do container
print('[1] GET /agenda/blacklist (de dentro do container):')
cmd = """docker exec backend-agenda node -e "
const http = require('http');
http.get('http://localhost:3001/agenda/blacklist', r => {
  let d = '';
  r.on('data', c => d += c);
  r.on('end', () => {
    const arr = JSON.parse(d);
    console.log('Total na blacklist:', arr.length);
    console.log('Primeiros 5:', arr.slice(0,5));
  });
});
" """
i, o, e = c.exec_command(cmd)
time.sleep(5)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'  ERR: {err}')

# Teste health
print('\n[2] GET /health:')
cmd2 = """docker exec backend-agenda node -e "
const http = require('http');
http.get('http://localhost:3001/health', r => {
  let d = '';
  r.on('data', c => d += c);
  r.on('end', () => console.log(d));
});
" """
i, o, e = c.exec_command(cmd2)
time.sleep(3)
print(o.read().decode().strip())

# Verificar Redis blacklist diretamente
print('\n[3] Redis SCARD agenda:blacklist:')
i, o, e = c.exec_command('docker exec redis-agenda redis-cli SCARD agenda:blacklist')
print(f'    {o.read().decode().strip()}')

# Verificar se SMEMBERS retorna dados
print('\n[4] Redis SRANDMEMBER (amostra de 5):')
i, o, e = c.exec_command('docker exec redis-agenda redis-cli SRANDMEMBER agenda:blacklist 5')
print(f'    {o.read().decode().strip()}')

c.close()
print('\n=== TESTES CONCLUÍDOS ===')
