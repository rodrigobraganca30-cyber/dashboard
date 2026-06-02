"""
patch_backend_v2.py
Patch seguro do backend index.js:
  1. Lê o original (index_original.js) — cópia local do VPS
  2. Aplica as mudanças com str.replace() cuidadoso (SEM regex)
  3. Envia para o VPS, docker cp, e restart
"""
import os, sys, shutil, paramiko

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SRC = os.path.join(os.path.dirname(__file__), 'index_original.js')
OUT = os.path.join(os.path.dirname(__file__), 'index_patched_v2.js')

# ── Lê original ──
with open(SRC, 'r', encoding='utf-8') as f:
    code = f.read()

print(f'[OK] Original lido: {len(code)} bytes, {code.count(chr(10))} linhas')

# ════════════════════════════════════════════════════
# PATCH 1: Adicionar constante KEY_BLACKLIST e função validateAndCleanPhone
#           Logo após a linha "const KEY_UNREAD = ..."
# ════════════════════════════════════════════════════

ANCHOR_1 = "const KEY_UNREAD   = (phone) => `agenda:unread:${phone}`;"

INJECT_1 = """const KEY_UNREAD   = (phone) => `agenda:unread:${phone}`;
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
}"""

assert ANCHOR_1 in code, 'ANCHOR_1 não encontrado!'
code = code.replace(ANCHOR_1, INJECT_1, 1)
print('[+] PATCH 1: validateAndCleanPhone + KEY_BLACKLIST injetados.')

# ════════════════════════════════════════════════════
# PATCH 2: Rotas /agenda/blacklist (GET e POST)
#           Logo antes do KEY_CLIENTS
# ════════════════════════════════════════════════════

ANCHOR_2 = """// ──────────────────────────────────────────────
// CLIENTS (GLOBAL AGENDA)
// ──────────────────────────────────────────────
const KEY_CLIENTS = 'agenda:clients';"""

INJECT_2 = """// ──────────────────────────────────────────────
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

// ──────────────────────────────────────────────
// CLIENTS (GLOBAL AGENDA)
// ──────────────────────────────────────────────
const KEY_CLIENTS = 'agenda:clients';"""

assert ANCHOR_2 in code, 'ANCHOR_2 não encontrado!'
code = code.replace(ANCHOR_2, INJECT_2, 1)
print('[+] PATCH 2: Rotas /agenda/blacklist injetadas.')

# ════════════════════════════════════════════════════
# PATCH 3: POST /status/:clientId — sincronizar "bloqueado" com blacklist
# ════════════════════════════════════════════════════

ANCHOR_3 = """// POST /status/:clientId — salva status manualmente
app.post('/status/:clientId', async (req, res) => {
  try {
    const { status, obs } = req.body;
    await setStatus(req.params.clientId, status, obs);
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});"""

INJECT_3 = """// POST /status/:clientId — salva status manualmente
app.post('/status/:clientId', async (req, res) => {
  try {
    const { status, obs } = req.body;
    await setStatus(req.params.clientId, status, obs);

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

    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});"""

assert ANCHOR_3 in code, 'ANCHOR_3 não encontrado!'
code = code.replace(ANCHOR_3, INJECT_3, 1)
print('[+] PATCH 3: POST /status/:clientId patcheado.')

# ════════════════════════════════════════════════════
# PATCH 4: POST /send — checar blacklist antes de enviar
# ════════════════════════════════════════════════════

ANCHOR_4 = """    const { phone, text, clientId } = req.body;
    if (!phone || !text) return res.status(400).json({ error: 'phone e text obrigatórios' });

    const instance = 'Meta_API_Oficial';
    const result = await sendText(phone, text);"""

INJECT_4 = """    const { phone, text, clientId } = req.body;
    if (!phone || !text) return res.status(400).json({ error: 'phone e text obrigatórios' });

    // ── Blacklist check ──
    const vSend = validateAndCleanPhone(phone);
    if (!vSend.valid) return res.status(400).json({ error: 'Número inválido', reason: vSend.reason });
    const isBlocked = await redis.sIsMember(KEY_BLACKLIST, vSend.number);
    if (isBlocked) return res.status(403).json({ error: 'Número bloqueado (blacklist)', phone: vSend.number });

    const instance = 'Meta_API_Oficial';
    const result = await sendText(phone, text);"""

assert ANCHOR_4 in code, 'ANCHOR_4 não encontrado!'
code = code.replace(ANCHOR_4, INJECT_4, 1)
print('[+] PATCH 4: POST /send patcheado com blacklist check.')

# ════════════════════════════════════════════════════
# PATCH 5: POST /send-bulk — checar blacklist no loop + add no catch
# ════════════════════════════════════════════════════

# 5a. No início do loop, antes de "const chosenTpl = ..."
ANCHOR_5A = """        const c = clients[idx];
        // Rodízio de templates
        const chosenTpl = tpls[idx % tpls.length];
        try {"""

INJECT_5A = """        const c = clients[idx];
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
        const chosenTpl = tpls[idx % tpls.length];
        try {"""

assert ANCHOR_5A in code, 'ANCHOR_5A não encontrado!'
code = code.replace(ANCHOR_5A, INJECT_5A, 1)
print('[+] PATCH 5a: Validação + blacklist check no loop send-bulk.')

# 5b. No catch do loop, adicionar auto-blacklist em caso de erro Meta
ANCHOR_5B = """        } catch (e) {
          failed++;
          log('error', 'Falha envio', { nome: c.nome, error: e.response?.data || e.message });
        }"""

INJECT_5B = """        } catch (e) {
          failed++;
          const errData = e.response?.data?.error || {};
          const errCode = errData.code || 0;
          // Auto-blacklist: erro 131026 (número inválido na Meta)
          if (errCode === 131026 || errCode === 131052 || errCode === 131049) {
            const ph = (c.phone || c.tel1 || c.tel2 || '').replace(/\\D/g, '');
            let blNum = ph;
            if (!blNum.startsWith('55')) blNum = '55' + blNum;
            await redis.sAdd(KEY_BLACKLIST, blNum);
            await setStatus(c.id, 'bloqueado', 'Erro Meta ' + errCode);
            log('warn', 'Auto-blacklist por erro Meta', { phone: blNum, errCode, nome: c.nome });
          }
          log('error', 'Falha envio', { nome: c.nome, error: e.response?.data || e.message });
        }"""

assert ANCHOR_5B in code, 'ANCHOR_5B não encontrado!'
code = code.replace(ANCHOR_5B, INJECT_5B, 1)
print('[+] PATCH 5b: Auto-blacklist no catch de erros.')

# ════════════════════════════════════════════════════
# SALVAR
# ════════════════════════════════════════════════════
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(code)

print(f'\n[OK] Arquivo patcheado salvo: {OUT} ({len(code)} bytes)')

# ════════════════════════════════════════════════════
# VALIDAR SINTAXE (verificar se "let number" duplica)
# ════════════════════════════════════════════════════
print('\n[VALIDAÇÃO] Checando possíveis conflitos...')
lines = code.split('\n')
for i, line in enumerate(lines, 1):
    if 'let number' in line or 'const number' in line or 'var number' in line:
        print(f'  L{i}: {line.strip()}')

# ════════════════════════════════════════════════════
# DEPLOY
# ════════════════════════════════════════════════════
print('\n[DEPLOY] Enviando para o VPS...')
ssh_key = os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa')
pkey = paramiko.RSAKey.from_private_key_file(ssh_key)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('187.77.240.87', port=22, username='root', pkey=pkey)

# Upload para o host
sftp = client.open_sftp()
sftp.put(OUT, '/docker/whatsapp-agenda/backend/index_patched_v2.js')
sftp.close()
print('  [OK] Upload concluído.')

# Docker cp + restart
import time
cmds = [
    'docker cp /docker/whatsapp-agenda/backend/index_patched_v2.js backend-agenda:/app/index.js',
    'docker restart backend-agenda',
]
for cmd in cmds:
    print(f'  > {cmd}')
    i, o, e = client.exec_command(cmd)
    out = o.read().decode().strip()
    err = e.read().decode().strip()
    if out: print(f'    {out}')
    if err: print(f'    [!] {err}')
    if 'restart' in cmd:
        time.sleep(6)

# Verificar
print('\n[VERIFICAÇÃO FINAL]')
i, o, e = client.exec_command('docker logs backend-agenda --tail 5 2>&1')
time.sleep(3)
logs = o.read().decode('utf-8', errors='replace').strip()
print(logs)

# Testar blacklist API
print('\n[TESTE API]')
i, o, e = client.exec_command('curl -s http://localhost:3001/agenda/blacklist 2>/dev/null | head -c 150')
time.sleep(2)
preview = o.read().decode().strip()
print(f'  /agenda/blacklist: {preview[:150]}...')

i, o, e = client.exec_command('curl -s http://localhost:3001/health 2>/dev/null')
health = o.read().decode().strip()
print(f'  /health: {health}')

client.close()
print('\n=== PATCH V2 CONCLUÍDO ===')
