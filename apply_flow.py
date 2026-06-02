import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

# Upload do script de patch para o VPS
patch_script = r'''
const fs = require('fs');
let code = fs.readFileSync('/app/index.js', 'utf8');

// 1. Adicionar /api/flow ao bypass de auth (linha 23)
const authOld = "req.path === '/health' || req.path === '/webhook'";
const authNew = "req.path === '/health' || req.path === '/webhook' || req.path.startsWith('/api/flow')";
if (!code.includes('/api/flow')) {
  code = code.replace(authOld, authNew);
  console.log('[+] Auth bypass para /api/flow adicionado');
} else {
  console.log('[=] Auth bypass já existe');
}

// 2. Inserir bloco de rotas antes do /health
const flowBlock = `

// ──────────────────────────────────────────────
// FLUXO AUTOMÁTICO DE RESPOSTAS
// ──────────────────────────────────────────────
const FLOW_CONFIG_KEY = 'flow:config';
const FLOW_ITEMS_KEY  = 'flow:items';

app.get('/api/flow/flow-config', async (req, res) => {
  try {
    const raw = await redis.get(FLOW_CONFIG_KEY);
    res.json(raw ? JSON.parse(raw) : {
      ativo: false, delay_segundos: 10,
      msg_sim: 'Que otimo! Ficamos felizes que tudo correu bem.',
      msg_nao: 'Lamentamos o ocorrido! Nossa equipe de suporte sera acionada.',
      msg_outro: 'Obrigado pelo retorno! Em breve um atendente entrara em contato.'
    });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.post('/api/flow/flow-config', async (req, res) => {
  try {
    const existing = await redis.get(FLOW_CONFIG_KEY);
    const current = existing ? JSON.parse(existing) : {};
    const merged = { ...current, ...req.body, updatedAt: new Date().toISOString() };
    await redis.set(FLOW_CONFIG_KEY, JSON.stringify(merged));
    res.json({ ok: true, config: merged });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.get('/api/flow/flows', async (req, res) => {
  try {
    const raw = await redis.get(FLOW_ITEMS_KEY);
    res.json(raw ? JSON.parse(raw) : []);
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.post('/api/flow/flows', async (req, res) => {
  try {
    const raw = await redis.get(FLOW_ITEMS_KEY);
    const items = raw ? JSON.parse(raw) : [];
    const newItems = req.body;
    if (Array.isArray(newItems)) {
      newItems.forEach(item => {
        items.push({
          id: item.phone + '_' + Date.now(),
          phone: item.phone,
          nome: item.nome || '',
          status: 'aguardando',
          enviado_em: item.enviado_em || new Date().toISOString(),
          resposta_recebida: null,
          classificacao: null
        });
      });
      await redis.set(FLOW_ITEMS_KEY, JSON.stringify(items));
    }
    res.json({ ok: true, total: items.length });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.delete('/api/flow/flows', async (req, res) => {
  try {
    const raw = await redis.get(FLOW_ITEMS_KEY);
    const items = raw ? JSON.parse(raw) : [];
    const active = items.filter(i => i.status === 'aguardando');
    await redis.set(FLOW_ITEMS_KEY, JSON.stringify(active));
    res.json({ ok: true, removed: items.length - active.length });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.delete('/api/flow/flows/:id', async (req, res) => {
  try {
    const raw = await redis.get(FLOW_ITEMS_KEY);
    const items = raw ? JSON.parse(raw) : [];
    const updated = items.map(i => i.id === req.params.id ? { ...i, status: 'cancelado' } : i);
    await redis.set(FLOW_ITEMS_KEY, JSON.stringify(updated));
    res.json({ ok: true });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.get('/api/flow/status', async (req, res) => {
  try {
    const raw = await redis.get(FLOW_ITEMS_KEY);
    const items = raw ? JSON.parse(raw) : [];
    res.json({
      aguardando:  items.filter(i => i.status === 'aguardando').length,
      respondidos: items.filter(i => i.status === 'respondido').length,
      cancelados:  items.filter(i => i.status === 'cancelado').length
    });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

`;

const healthAnchor = "app.get('/health'";
if (code.includes('FLOW_ITEMS_KEY')) {
  console.log('[=] Rotas de flow já existem');
} else if (code.includes(healthAnchor)) {
  code = code.replace(healthAnchor, flowBlock + '\n' + healthAnchor);
  console.log('[+] 7 rotas de flow inseridas antes do /health');
} else {
  console.log('[!] Anchor /health não encontrado!');
  process.exit(1);
}

// 3. Salvar
fs.writeFileSync('/app/index.js', code);
console.log('[+] index.js salvo (' + code.split('\\n').length + ' linhas)');
'''

# Salvar script de patch no VPS
print('[1] Enviando patch...')
sftp = c.open_sftp()
with sftp.open('/tmp/patch_flow.js', 'w') as f:
    f.write(patch_script)
sftp.close()
print('    OK')

# Executar patch dentro do container
print('\n[2] Aplicando patch...')
i, o, e = c.exec_command('docker cp /tmp/patch_flow.js backend-agenda:/tmp/patch_flow.js')
time.sleep(1)
i, o, e = c.exec_command('docker exec backend-agenda node /tmp/patch_flow.js')
time.sleep(3)
print(o.read().decode('utf-8', errors='replace').strip())
err = e.read().decode('utf-8', errors='replace').strip()
if err:
    print(f'ERR: {err[:200]}')

# Reiniciar
print('\n[3] Reiniciando container...')
i, o, e = c.exec_command('docker restart backend-agenda')
time.sleep(8)
print(f'    {o.read().decode().strip()}')

# Verificar
print('\n[4] Verificando...')
time.sleep(3)
i, o, e = c.exec_command('docker ps --filter name=backend-agenda --format "{{.Status}}"')
time.sleep(1)
status = o.read().decode().strip()
print(f'    Container: {status}')

# Testar rotas
print('\n[5] Testando rotas de flow:')
routes = [
    ('GET', '/api/flow/flow-config'),
    ('GET', '/api/flow/flows'),
    ('GET', '/api/flow/status'),
]
for method, path in routes:
    i, o, e = c.exec_command(f'''docker exec backend-agenda node -e "fetch('http://localhost:3001{path}').then(r=>{{console.log('{path}:',r.status);return r.text()}}).then(t=>console.log(t.substring(0,150))).catch(e=>console.log('ERR:',e.message))"''')
    time.sleep(3)
    print(o.read().decode('utf-8', errors='replace').strip())

# Testar POST
print('\n[6] Testando POST flow-config:')
i, o, e = c.exec_command('''docker exec backend-agenda node -e "fetch('http://localhost:3001/api/flow/flow-config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ativo:false})}).then(r=>{console.log('POST:',r.status);return r.text()}).then(t=>console.log(t.substring(0,150))).catch(e=>console.log('ERR:',e.message))"''')
time.sleep(3)
print(o.read().decode('utf-8', errors='replace').strip())

c.close()
print('\n=== FLOW RESTAURADO ===')
