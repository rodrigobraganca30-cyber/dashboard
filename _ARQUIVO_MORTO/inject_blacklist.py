"""
inject_blacklist.py — Injeta sistema completo de blacklist no backend-agenda
Baseado no index_patched_v2.js que já tem a implementação pronta.
"""
import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

ts = time.strftime('%Y%m%d_%H%M%S')

# ══════════════════════════════════════════════════
# BACKUP
# ══════════════════════════════════════════════════
print(f'[1/4] Backup...')
i, o, e = c.exec_command(f'docker cp backend-agenda:/app/index.js /docker/backup_index_{ts}_pre_blacklist.js')
time.sleep(2)
print('    OK')

# ══════════════════════════════════════════════════
# PATCH
# ══════════════════════════════════════════════════
patch_js = r'''
const fs = require('fs');
let code = fs.readFileSync('/app/index.js', 'utf8');

if (code.includes('KEY_BLACKLIST')) {
  console.log('[=] Blacklist já existe. Nada a fazer.');
  process.exit(0);
}

let changes = 0;

// ─────────────────────────────────────────────
// 1. Adicionar KEY_BLACKLIST e validateAndCleanPhone
//    Inserir após KEY_UNREAD
// ─────────────────────────────────────────────
const unreadAnchor = "const KEY_UNREAD   = (phone) => `agenda:unread:${phone}`;";
if (code.includes(unreadAnchor)) {
  const insertAfter = unreadAnchor;
  const blacklistCode = `
const KEY_BLACKLIST = 'agenda:blacklist';

// ── BLACKLIST: Validação de telefone ──
function validateAndCleanPhone(raw) {
  if (!raw) return { valid: false, number: '', reason: 'vazio' };
  const cleaned = String(raw).replace(/\\D/g, '');
  if (cleaned.length < 10) return { valid: false, number: cleaned, reason: 'curto' };
  if (cleaned.length > 13) return { valid: false, number: cleaned, reason: 'longo' };
  let number = cleaned;
  if (!number.startsWith('55')) number = '55' + number;
  if (number.length !== 13) return { valid: false, number, reason: 'len!==13' };
  return { valid: true, number };
}
`;
  code = code.replace(insertAfter, insertAfter + '\n' + blacklistCode);
  console.log('[+] 1/6 KEY_BLACKLIST + validateAndCleanPhone adicionados');
  changes++;
} else {
  console.log('[!] Âncora KEY_UNREAD não encontrada');
}

// ─────────────────────────────────────────────
// 2. Blacklist sync no POST /status/:clientId
//    Quando status = 'bloqueado', adiciona à blacklist
// ─────────────────────────────────────────────
const statusAnchor = "await setStatus(req.params.clientId, status, obs);\n    res.json({ ok: true });";
if (code.includes(statusAnchor)) {
  const newStatusBlock = `await setStatus(req.params.clientId, status, obs);

    // Blacklist sync: se status == "bloqueado", adiciona telefone à blacklist
    if (status === 'bloqueado') {
      const cid = req.params.clientId;
      const phonePart = cid.replace(/^wa_/, '').split('_')[0];
      const v = validateAndCleanPhone(phonePart);
      if (v.valid) {
        await redis.sAdd(KEY_BLACKLIST, v.number);
        log('info', 'Blacklist: número adicionado via status bloqueado', { phone: v.number, clientId: cid });
      }
    }

    res.json({ ok: true });`;
  code = code.replace(statusAnchor, newStatusBlock);
  console.log('[+] 2/6 Blacklist sync no POST /status adicionado');
  changes++;
} else {
  console.log('[!] Âncora POST /status não encontrada');
}

// ─────────────────────────────────────────────
// 3. Blacklist check no POST /send
//    Verificar antes de enviar
// ─────────────────────────────────────────────
const sendAnchor = "const { phone, text, clientId } = req.body;\n    if (!phone || !text) return res.status(400).json({ error: 'phone e text obrigatórios' });\n\n    const instance = 'Meta_API_Oficial';";
if (code.includes(sendAnchor)) {
  const newSendBlock = `const { phone, text, clientId } = req.body;
    if (!phone || !text) return res.status(400).json({ error: 'phone e text obrigatórios' });

    // ── Blacklist check ──
    const vSend = validateAndCleanPhone(phone);
    if (!vSend.valid) return res.status(400).json({ error: 'Número inválido', reason: vSend.reason });
    const isBlocked = await redis.sIsMember(KEY_BLACKLIST, vSend.number);
    if (isBlocked) return res.status(403).json({ error: 'Número bloqueado (blacklist)', phone: vSend.number });

    const instance = 'Meta_API_Oficial';`;
  code = code.replace(sendAnchor, newSendBlock);
  console.log('[+] 3/6 Blacklist check no POST /send adicionado');
  changes++;
} else {
  console.log('[!] Âncora POST /send não encontrada');
}

// ─────────────────────────────────────────────
// 4. Blacklist check no send-bulk (dentro do loop)
//    Validar + checar blacklist antes de cada envio
// ─────────────────────────────────────────────
const bulkLoopAnchor = "const c = clients[idx];\n        // Rodízio de templates\n        const chosenTpl = tpls[idx % tpls.length];";
if (code.includes(bulkLoopAnchor)) {
  const newBulkLoop = `const c = clients[idx];
        // ── Blacklist: validar e pular se bloqueado ──
        const rawPhone = c.phone || c.tel1 || c.tel2 || '';
        const vBulk = validateAndCleanPhone(rawPhone);
        if (!vBulk.valid) {
          log('warn', 'Número inválido, adicionando à blacklist', { nome: c.nome, phone: rawPhone, reason: vBulk.reason });
          if (vBulk.number) await redis.sAdd(KEY_BLACKLIST, vBulk.number);
          await setStatus(c.id, 'bloqueado', 'Número inválido: ' + vBulk.reason);
          failed++;
          continue;
        }
        const isBl = await redis.sIsMember(KEY_BLACKLIST, vBulk.number);
        if (isBl) {
          log('info', 'Número na blacklist, pulando', { nome: c.nome, phone: vBulk.number });
          await setStatus(c.id, 'bloqueado', 'Número na blacklist');
          failed++;
          continue;
        }
        // Rodízio de templates
        const chosenTpl = tpls[idx % tpls.length];`;
  code = code.replace(bulkLoopAnchor, newBulkLoop);
  console.log('[+] 4/6 Blacklist check no send-bulk loop adicionado');
  changes++;
} else {
  console.log('[!] Âncora send-bulk loop não encontrada');
}

// ─────────────────────────────────────────────
// 5. Auto-blacklist por erro Meta (no catch do send-bulk)
//    Erros 131026, 131052, 131049 = número inválido
// ─────────────────────────────────────────────
const catchAnchor = "log('error', 'Falha envio', { nome: c.nome, error: e.response?.data || e.message });";
if (code.includes(catchAnchor)) {
  const newCatch = `// Auto-blacklist: erro 131026 (número inválido na Meta)
          const errData = e.response?.data?.error || {};
          const errCode = errData.code || 0;
          if (errCode === 131026 || errCode === 131052 || errCode === 131049) {
            const ph = (c.phone || c.tel1 || c.tel2 || '').replace(/\\D/g, '');
            let blNum = ph;
            if (!blNum.startsWith('55')) blNum = '55' + blNum;
            await redis.sAdd(KEY_BLACKLIST, blNum);
            await setStatus(c.id, 'bloqueado', 'Erro Meta ' + errCode);
            log('warn', 'Auto-blacklist por erro Meta', { phone: blNum, errCode, nome: c.nome });
          }
          log('error', 'Falha envio', { nome: c.nome, error: e.response?.data || e.message });`;
  code = code.replace(catchAnchor, newCatch);
  console.log('[+] 5/6 Auto-blacklist por erro Meta adicionado');
  changes++;
} else {
  console.log('[!] Âncora catch send-bulk não encontrada');
}

// ─────────────────────────────────────────────
// 6. Rotas de gestão da blacklist
//    GET/POST/DELETE /agenda/blacklist
// ─────────────────────────────────────────────
const healthAnchor = "app.get('/health'";
if (code.includes(healthAnchor) && !code.includes('/agenda/blacklist')) {
  const blacklistRoutes = `
// ──────────────────────────────────────────────
// BLACKLIST ROUTES
// ──────────────────────────────────────────────
app.get('/agenda/blacklist', async (req, res) => {
  try {
    const members = await redis.sMembers(KEY_BLACKLIST);
    res.json(members || []);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/agenda/blacklist', async (req, res) => {
  try {
    const { numbers } = req.body;
    if (!Array.isArray(numbers)) return res.status(400).json({ error: 'numbers deve ser array' });
    let added = 0;
    for (const n of numbers) {
      const r = validateAndCleanPhone(n);
      if (r.valid) { await redis.sAdd(KEY_BLACKLIST, r.number); added++; }
    }
    res.json({ ok: true, added });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.delete('/agenda/blacklist', async (req, res) => {
  try {
    const { numbers } = req.body;
    if (!Array.isArray(numbers)) return res.status(400).json({ error: 'numbers deve ser array' });
    let removed = 0;
    for (const n of numbers) {
      const r = validateAndCleanPhone(n);
      if (r.valid) { await redis.sRem(KEY_BLACKLIST, r.number); removed++; }
    }
    res.json({ ok: true, removed });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

`;
  code = code.replace(healthAnchor, blacklistRoutes + healthAnchor);
  console.log('[+] 6/6 Rotas /agenda/blacklist adicionadas');
  changes++;
} else {
  console.log('[=] Rotas blacklist já existem ou /health não encontrado');
}

// ── Auth bypass para blacklist ──
const authBypass = "req.path === '/health'";
if (code.includes(authBypass) && !code.includes("startsWith('/agenda/blacklist')")) {
  code = code.replace(authBypass, "req.path === '/health' || req.path.startsWith('/agenda/blacklist')");
  console.log('[+] Auth bypass para /agenda/blacklist adicionado');
}

// ── Salvar ──
fs.writeFileSync('/app/index.js', code);
console.log('\n[✓] index.js salvo (' + code.split('\n').length + ' linhas, ' + changes + ' mudanças)');
console.log('[✓] KEY_BLACKLIST:', code.includes('KEY_BLACKLIST'));
console.log('[✓] validateAndCleanPhone:', code.includes('validateAndCleanPhone'));
console.log('[✓] sIsMember(KEY_BLACKLIST):', code.includes('sIsMember(KEY_BLACKLIST'));
console.log('[✓] /agenda/blacklist:', code.includes('/agenda/blacklist'));
console.log('[✓] Auto-blacklist Meta:', code.includes('Auto-blacklist'));
'''

print(f'\n[2/4] Aplicando patch de blacklist...')
sftp = c.open_sftp()
with sftp.open('/tmp/patch_blacklist.js', 'w') as f:
    f.write(patch_js)
sftp.close()

i, o, e = c.exec_command('docker cp /tmp/patch_blacklist.js backend-agenda:/tmp/patch_blacklist.js')
time.sleep(1)
i, o, e = c.exec_command('docker exec backend-agenda node /tmp/patch_blacklist.js')
time.sleep(5)
out = o.read().decode('utf-8', errors='replace').strip()
err = e.read().decode('utf-8', errors='replace').strip()
print(out)
if err:
    print(f'    STDERR: {err[:300]}')

# ══════════════════════════════════════════════════
# RESTART
# ══════════════════════════════════════════════════
print(f'\n[3/4] Reiniciando backend-agenda...')
i, o, e = c.exec_command('docker restart backend-agenda')
time.sleep(10)
print(f'    {o.read().decode().strip()}')

# ══════════════════════════════════════════════════
# VERIFICAÇÃO
# ══════════════════════════════════════════════════
print(f'\n[4/4] Verificação...')

i, o, e = c.exec_command('docker ps --filter name=backend-agenda --format "{{.Names}}: {{.Status}}"')
time.sleep(1)
print(f'  Container: {o.read().decode().strip()}')

i, o, e = c.exec_command('docker exec backend-agenda grep -c "KEY_BLACKLIST" /app/index.js')
time.sleep(1)
print(f'  KEY_BLACKLIST: {o.read().decode().strip()} refs')

i, o, e = c.exec_command('docker exec backend-agenda grep -c "validateAndCleanPhone" /app/index.js')
time.sleep(1)
print(f'  validateAndCleanPhone: {o.read().decode().strip()} refs')

i, o, e = c.exec_command('docker exec backend-agenda grep -c "agenda/blacklist" /app/index.js')
time.sleep(1)
print(f'  /agenda/blacklist: {o.read().decode().strip()} refs')

i, o, e = c.exec_command('docker exec backend-agenda grep -c "BUTTON_FLOWS\\|BUTTON_STATUS" /app/index.js')
time.sleep(1)
print(f'  BUTTON_FLOWS: {o.read().decode().strip()} refs (preservado)')

i, o, e = c.exec_command('docker exec backend-agenda wget -q -O- http://localhost:3001/health')
time.sleep(2)
print(f'  Health: {o.read().decode().strip()}')

# Blacklist atual
i, o, e = c.exec_command('docker exec redis-agenda redis-cli SCARD agenda:blacklist')
time.sleep(1)
print(f'  Blacklist atual: {o.read().decode().strip()} números bloqueados')

i, o, e = c.exec_command('docker logs backend-agenda --tail 3 2>&1')
time.sleep(1)
print(f'  Logs: {o.read().decode("utf-8", errors="replace").strip()}')

c.close()
print(f'\n{"="*50}')
print(f'✅ BLACKLIST ATIVADA COM SUCESSO')
print(f'   Backup: /docker/backup_index_{ts}_pre_blacklist.js')
print(f'{"="*50}')
