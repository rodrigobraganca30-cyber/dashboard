require('dotenv').config();
const express = require('express');
const axios   = require('axios');
const cors    = require('cors');
const { createClient } = require('redis');
const fs = require('fs');
const path    = require('path');
const { Pool } = require('pg');

const app  = express();
app.use(cors());
app.use(express.json({ limit: '50mb' }));

// ──────────────────────────────────────────────
// POSTGRESQL POOL (Shadow Write)
// ──────────────────────────────────────────────
const pgPool = new Pool({
  connectionString: process.env.DATABASE_URL
});
pgPool.on('error', (err) => {
  log('error', 'PostgreSQL error', { error: err.message });
});

// ──────────────────────────────────────────────
// SERVE FRONTEND STATIC (index.html)
// ──────────────────────────────────────────────
app.use(express.static(path.join(__dirname, '..', 'frontend')));

// ──────────────────────────────────────────────
// AUTH MIDDLEWARE — API Key
// ──────────────────────────────────────────────
const API_KEY = process.env.AGENDA_API_KEY;
function authMiddleware(req, res, next) {
  // Skip auth for health, webhook, static files, and frontend requests (same-origin)
  if (req.path === '/health' || req.path === '/webhook' || req.path === '/' || req.path.endsWith('.html') || req.path.endsWith('.js') || req.path.endsWith('.css') || req.path.endsWith('.ico') || req.headers.referer) {
    return next();
  }
  const key = req.headers['x-api-key'] || req.query.apikey;
  if (key === API_KEY) return next();
  res.status(401).json({ error: 'API Key inválida' });
}
app.use(authMiddleware);

// ──────────────────────────────────────────────
// RATE LIMITING (simple in-memory)
// ──────────────────────────────────────────────
const rateLimits = {};
const RATE_WINDOW = 60000; // 1 minute
const RATE_MAX_SEND = 20;  // max 20 sends per minute

function checkRateLimit(key, max = RATE_MAX_SEND) {
  const now = Date.now();
  if (!rateLimits[key]) rateLimits[key] = [];
  rateLimits[key] = rateLimits[key].filter(t => now - t < RATE_WINDOW);
  if (rateLimits[key].length >= max) return false;
  rateLimits[key].push(now);
  return true;
}

// ──────────────────────────────────────────────
// STRUCTURED LOGGING
// ──────────────────────────────────────────────
// ──────────────────────────────────────────────
// TELEPHONE VALIDATOR & NORMALIZER (PREVENTS ERRO 131026)
// ──────────────────────────────────────────────
function validateAndCleanPhone(phone) {
  if (!phone) return { valid: false, error: 'Telefone ausente', num: '' };
  let cleaned = String(phone).replace(/\D/g, '');
  if (cleaned.startsWith('550')) {
    cleaned = '55' + cleaned.substring(3);
  }
  if (cleaned.length === 10 || cleaned.length === 11) {
    cleaned = '55' + cleaned;
  }
  if (cleaned.startsWith('55') && cleaned.length === 12) {
    const firstDig = cleaned.charAt(4);
    if (['9', '8', '7'].includes(firstDig)) {
      cleaned = cleaned.substring(0, 4) + '9' + cleaned.substring(4);
    }
  }
  if (cleaned.length !== 12 && cleaned.length !== 13) {
    return { valid: false, error: 'Tamanho invalido (' + cleaned.length + ' digitos)', num: cleaned };
  }
  if (cleaned.startsWith('55') && cleaned.length === 12) {
    const firstDig = cleaned.charAt(4);
    if (['2', '3', '4', '5'].includes(firstDig)) {
      return { valid: false, error: 'Telefone Fixo (Sem WhatsApp ativo)', num: cleaned };
    }
  }
  return { valid: true, num: cleaned };
}

function log(level, msg, data = {}) {
  const entry = {
    ts: new Date().toISOString(),
    level,
    msg,
    ...data
  };
  console.log(JSON.stringify(entry));
}

// ──────────────────────────────────────────────
// REDIS
// ──────────────────────────────────────────────
const redis = createClient({ url: process.env.REDIS_URL || 'redis://localhost:6379' });
redis.connect().then(() => log('info', 'Redis conectado'));
redis.on('error', e => log('error', 'Redis error', { error: e.message }));

// Helpers Redis
const KEY_STATUS   = (id) => `agenda:status:${id}`;
const KEY_MSGS     = (phone) => `agenda:msgs:${phone}`;
const KEY_PHONE_ID = (phone) => `agenda:phone2id:${phone}`;
const KEY_TEMPLATES = 'agenda:templates';
const KEY_CAMPAIGNS = 'agenda:campaigns';
const KEY_UNREAD   = (phone) => `agenda:unread:${phone}`;

// SCAN helper — substitui redis.keys() que é O(N) e bloqueia
async function scanKeys(pattern, count = 200) {
  const keys = [];
  let cursor = '0';
  do {
    const result = await redis.scan(cursor, { MATCH: pattern, COUNT: count });
    cursor = result.cursor.toString();
    keys.push(...result.keys);
  } while (cursor !== '0');
  return keys;
}

// In-memory cache simples (para /conversations)
const cache = {};
function cached(key, ttlMs, fn) {
  return async (...args) => {
    const now = Date.now();
    if (cache[key] && now - cache[key].ts < ttlMs) return cache[key].data;
    const data = await fn(...args);
    cache[key] = { data, ts: now };
    return data;
  };
}

async function setStatus(clientId, status, obs = '') {
  await redis.set(KEY_STATUS(clientId), JSON.stringify({ status, obs, updatedAt: new Date().toISOString() }));
  
  // --- SHADOW WRITE ---
  try {
    if (process.env.DATABASE_URL) {
      await pgPool.query(
        'UPDATE clientes SET status_atual = $1, obs_status = $2, atualizado_em = CURRENT_TIMESTAMP WHERE id = $3', 
        [status, obs, clientId]
      );
    }
  } catch(e) { log('error', 'PG setStatus Error', {error: e.message}); }
}

async function getStatus(clientId) {
  try {
    if (process.env.DATABASE_URL) {
      const { rows } = await pgPool.query('SELECT status_atual, obs_status, atualizado_em FROM clientes WHERE id = $1', [clientId]);
      if (rows.length > 0) return { status: rows[0].status_atual, obs: rows[0].obs_status || '', updatedAt: rows[0].atualizado_em };
    }
  } catch(e) {}
  const v = await redis.get(KEY_STATUS(clientId));
  return v ? JSON.parse(v) : { status: 'pendente', obs: '', updatedAt: null };
}

async function appendMsg(phone, msg) {
  const raw = await redis.get(KEY_MSGS(phone));
  const msgs = raw ? JSON.parse(raw) : [];
  
  // Evitar duplicação: se a última mensagem for idêntica (mesmo remetente e texto) e muito recente
  if (msgs.length > 0) {
    const lastMsg = msgs[msgs.length - 1];
    if (lastMsg.from === msg.from && lastMsg.text === msg.text) {
      if (Math.abs(lastMsg.ts - msg.ts) < 10000) return; // ignora duplicata de 10 seg
    }
  }

  msgs.push(msg);
  // mantém últimas 200 mensagens
  if (msgs.length > 200) msgs.splice(0, msgs.length - 200);
  await redis.set(KEY_MSGS(phone), JSON.stringify(msgs));

  // --- SHADOW WRITE ---
  try {
    if (process.env.DATABASE_URL) {
      await pgPool.query(
        'INSERT INTO mensagens (telefone, remetente, texto, timestamp, instancia, is_auto) VALUES ($1, $2, $3, $4, $5, $6)', 
        [phone, msg.from, msg.text, msg.ts, msg.instance || null, msg.auto || false]
      );
    }
  } catch(e) { log('error', 'PG appendMsg Error', {error: e.message}); }
}

async function getMsgs(phone) {
  try {
    if (process.env.DATABASE_URL) {
      const { rows } = await pgPool.query('SELECT * FROM mensagens WHERE telefone = $1 ORDER BY timestamp ASC', [phone]);
      if (rows.length > 0) {
        return rows.map(r => ({ from: r.remetente, text: r.texto, ts: Number(r.timestamp), instance: r.instancia, auto: r.is_auto }));
      }
    }
  } catch(e) {}
  const raw = await redis.get(KEY_MSGS(phone));
  return raw ? JSON.parse(raw) : [];
}

// ──────────────────────────────────────────────
// META CLOUD API CLIENT
// ──────────────────────────────────────────────
const META_VERIFY_TOKEN = process.env.META_VERIFY_TOKEN || 'svoboda-webhook-2025';

async function getMetaConfig() {
  const token = await redis.get('agenda:meta_token') || process.env.META_ACCESS_TOKEN;
  const phoneId = await redis.get('agenda:meta_phone_id') || process.env.META_PHONE_ID;
  return { token, phoneId };
}

function getMetaClient(token) {
  return axios.create({
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    timeout: 15000
  });
}

async function withRetry(fn, retries = 3, delayMs = 2000) {
  for (let i = 0; i < retries; i++) {
    try { return await fn(); } 
    catch (e) {
      if (i === retries - 1) throw e;
      log('warn', `Retry ${i + 1}/${retries}`, { error: e.message });
      await new Promise(r => setTimeout(r, delayMs * (i + 1)));
    }
  }
}

function extractTemplateParams(templateText, clientData, remetente) {
  const matches = [...templateText.matchAll(/\{\{([^}]+)\}\}/g)];
  const parameters = [];

  // Mapeamento numérico: {{1}}→nome, {{2}}→data, {{3}}→cidade, etc.
  const numericFields = [
    clientData.nome || '',
    clientData.data || '',
    clientData.cidade || '',
    clientData.horario || '',
    clientData.endereco || '',
    clientData.tipo || '',
    remetente || ''
  ];

  for (const match of matches) {
    const varName = match[1].toLowerCase().trim();
    let textValue = '';

    // Variáveis numéricas: {{1}}, {{2}}, {{3}}...
    const numIdx = parseInt(varName);
    if (!isNaN(numIdx) && numIdx >= 1 && numIdx <= numericFields.length) {
      textValue = numericFields[numIdx - 1];
    }
    // Variáveis nomeadas: {{nome}}, {{data}}, etc.
    else if (varName === 'nome') textValue = clientData.nome || '';
    else if (varName === 'data') textValue = clientData.data || '';
    else if (varName === 'cidade') textValue = clientData.cidade || '';
    else if (varName === 'horario') textValue = clientData.horario || '';
    else if (varName === 'endereco') textValue = clientData.endereco || '';
    else if (varName === 'tipo') textValue = clientData.tipo || '';
    else if (varName === 'remetente') textValue = remetente || '';

    parameters.push({ type: "text", text: textValue || ' ' });
  }
  return parameters;
}

// Envio de Template
async function sendTemplate(phone, templateName, components, lang = 'pt_BR') {
  const conf = await getMetaConfig();
  if (!conf.token || !conf.phoneId) {
    throw new Error('Meta API credentials missing. Check your Dashboard configs.');
  }
  const META_API_URL = `https://graph.facebook.com/v19.0/${conf.phoneId}/messages`;
  const meta = getMetaClient(conf.token);

  let number = phone.replace(/\D/g, '');
  if (!number.startsWith('55')) number = '55' + number;

  const payload = {
    messaging_product: "whatsapp",
    to: number,
    type: "template",
    template: {
      name: templateName,
      language: { code: lang },
      components: components
    }
  };

  const res = await withRetry(() => meta.post(META_API_URL, payload));
  log('info', 'Template enviado (Meta API)', { phone: number, template: templateName, lang });
  return res.data;
}

// Envio de Texto Livre (apenas se houver janela 24h aberta)
async function sendText(phoneInput, text) {
  const conf = await getMetaConfig();
  if (!conf.token || !conf.phoneId) {
    throw new Error('Meta API credentials missing. Check your Dashboard configs.');
  }
  const META_API_URL = `https://graph.facebook.com/v19.0/${conf.phoneId}/messages`;
  const meta = getMetaClient(conf.token);

  let cleaned = String(phoneInput).replace(/\D/g, '');
  if (!cleaned.startsWith('55')) cleaned = '55' + cleaned;

  const payload = {
    messaging_product: "whatsapp",
    recipient_type: "individual",
    to: cleaned,
    type: "text",
    text: { preview_url: false, body: text }
  };

  const result = await withRetry(() => meta.post(META_API_URL, payload));
  log('info', 'Mensagem enviada (Meta API)', { phone: cleaned });
  return result.data;
}

// ──────────────────────────────────────────────
// META API MANAGEMENT (Stubs para frontend)
// ──────────────────────────────────────────────
app.get('/wa/status', async (req, res) => {
  res.json({ instance: { state: "open", status: "Meta API Oficial conectada" } });
});

app.get('/wa/qr', async (req, res) => {
  res.json({ error: "API Oficial não requer QR Code. Use o painel da Meta." });
});

app.delete('/wa/logout', async (req, res) => res.json({ ok: true }));
app.post('/wa/logout', async (req, res) => {
  await redis.del('agenda:meta_token');
  await redis.del('agenda:meta_phone_id');
  res.json({ ok: true });
});

app.get('/wa/instances', async (req, res) => {
  const conf = await getMetaConfig();
  if (conf.token && conf.phoneId) {
    res.json(['Meta_API_Oficial']);
  } else {
    res.json([]);
  }
});

// Endpoint para salvar as credenciais da Meta via Painel
app.post('/meta-config', async (req, res) => {
  try {
    const { token, phoneId, wabaId } = req.body;
    if (token) await redis.set('agenda:meta_token', token);
    if (phoneId) await redis.set('agenda:meta_phone_id', phoneId);
    if (wabaId) await redis.set('agenda:meta_waba_id', wabaId);
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// GET /meta-config — retorna credenciais salvas (mascaradas)
app.get('/meta-config', async (req, res) => {
  try {
    const token = await redis.get('agenda:meta_token') || '';
    const phoneId = await redis.get('agenda:meta_phone_id') || '';
    const wabaId = await redis.get('agenda:meta_waba_id') || '';
    res.json({
      token: token ? '***' + token.slice(-8) : '',
      phoneId,
      wabaId,
      configured: !!(token && phoneId && wabaId)
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ──────────────────────────────────────────────
// META TEMPLATE MANAGEMENT (Graph API)
// ──────────────────────────────────────────────

// GET /meta/templates — lista templates da WABA na Meta
app.get('/meta/templates', async (req, res) => {
  try {
    const token = await redis.get('agenda:meta_token') || process.env.META_ACCESS_TOKEN;
    const wabaId = await redis.get('agenda:meta_waba_id') || process.env.META_WABA_ID;
    if (!token || !wabaId) {
      return res.status(400).json({ error: 'Configure Token e WABA ID primeiro' });
    }
    const url = `https://graph.facebook.com/v19.0/${wabaId}/message_templates?limit=100`;
    const resp = await axios.get(url, {
      headers: { Authorization: `Bearer ${token}` },
      timeout: 15000
    });
    const templates = (resp.data.data || []).map(t => ({
      id: t.id,
      name: t.name,
      status: t.status,
      category: t.category,
      language: t.language,
      components: t.components || [],
      quality_score: t.quality_score
    }));
    res.json({ templates, total: templates.length });
  } catch (e) {
    const errMsg = e.response?.data?.error?.message || e.message;
    log('error', 'Erro ao listar templates Meta', { error: errMsg });
    res.status(500).json({ error: errMsg });
  }
});

// POST /meta/templates — cria novo template na Meta
app.post('/meta/templates', async (req, res) => {
  try {
    const token = await redis.get('agenda:meta_token') || process.env.META_ACCESS_TOKEN;
    const wabaId = await redis.get('agenda:meta_waba_id') || process.env.META_WABA_ID;
    if (!token || !wabaId) {
      return res.status(400).json({ error: 'Configure Token e WABA ID primeiro' });
    }
    const { name, category, language, body_text } = req.body;
    if (!name || !body_text) {
      return res.status(400).json({ error: 'name e body_text obrigatórios' });
    }
    const url = `https://graph.facebook.com/v19.0/${wabaId}/message_templates`;
    const payload = {
      name: name.toLowerCase().replace(/[^a-z0-9_]/g, '_'),
      category: category || 'UTILITY',
      language: language || 'pt_BR',
      components: [{
        type: 'BODY',
        text: body_text,
        example: { body_text: [Array.from({length: (body_text.match(/\{\{[0-9]+\}\}/g) || ['x']).length}, (_, i) => 'exemplo' + (i + 1))] }
      }]
    };
    const resp = await axios.post(url, payload, {
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      timeout: 15000
    });
    log('info', 'Template criado na Meta', { name: payload.name, id: resp.data.id });
    res.json({ ok: true, id: resp.data.id, status: resp.data.status });
  } catch (e) {
    const errMsg = e.response?.data?.error?.message || e.message;
    log('error', 'Erro ao criar template Meta', { error: errMsg });
    res.status(500).json({ error: errMsg });
  }
});

// DELETE /meta/templates/:name — exclui template na Meta
app.delete('/meta/templates/:name', async (req, res) => {
  try {
    const token = await redis.get('agenda:meta_token') || process.env.META_ACCESS_TOKEN;
    const wabaId = await redis.get('agenda:meta_waba_id') || process.env.META_WABA_ID;
    if (!token || !wabaId) {
      return res.status(400).json({ error: 'Configure Token e WABA ID primeiro' });
    }
    const url = `https://graph.facebook.com/v19.0/${wabaId}/message_templates?name=${req.params.name}`;
    await axios.delete(url, {
      headers: { Authorization: `Bearer ${token}` },
      timeout: 15000
    });
    log('info', 'Template excluído na Meta', { name: req.params.name });
    res.json({ ok: true });
  } catch (e) {
    const errMsg = e.response?.data?.error?.message || e.message;
    log('error', 'Erro ao excluir template Meta', { error: errMsg });
    res.status(500).json({ error: errMsg });
  }
});

// ──────────────────────────────────────────────
// DETECÇÃO AUTOMÁTICA DE STATUS POR PALAVRAS-CHAVE
// Carregado dinamicamente do PostgreSQL (tabela configuracoes)
// ──────────────────────────────────────────────
let KEYWORDS = {
  'nao-atendido': ['nao posso', 'impossivel', 'ocupado', 'nao vou', 'cancelar', 'cancela', 'desmarcar', 'nao'],
  reagendado: ['remarcar', 'reagendar', 'outro dia', 'outra data', 'mudar data', 'mudar horario', 'pode ser amanha', 'outra hora', 'diferente', 'semana que vem'],
  confirmado: ['sim', 'confirmo', 'confirmado', 'ok', 'pode vir', 'pode sim', 'pode confirmar', 'certo', 'perfeito', 'ta bom', 'tudo bem', 'estarei', 'combinado', 'show', 'vou estar', 'otimo', 'beleza', 'claro', 'com certeza', 'positivo']
};
let BTN_STATUS_MAP_DYNAMIC = null;

async function loadDynamicConfig() {
  try {
    if (!process.env.DATABASE_URL) return;
    const { rows } = await pgPool.query('SELECT chave, valor FROM configuracoes');
    for (const row of rows) {
      if (row.chave === 'keywords_status') KEYWORDS = row.valor;
      if (row.chave === 'btn_status_map') BTN_STATUS_MAP_DYNAMIC = row.valor;
    }
    log('info', 'Configurações dinâmicas carregadas do PostgreSQL');
  } catch(e) {
    log('error', 'Erro ao carregar configurações dinâmicas', { error: e.message });
  }
}
// Carrega na inicialização e recarrega a cada 60s
loadDynamicConfig();
setInterval(loadDynamicConfig, 60000);

function detectStatus(text) {
  const t = text.toLowerCase().trim();
  
  const checkWords = (words) => words.some(w => {
    // Para palavras curtas, força a busca como palavra inteira
    if (['não', 'nao', 'ok', 'sim'].includes(w)) {
      const regex = new RegExp(`(?:^|\\s|[.,!?])${w}(?:\\s|$|[.,!?])`, 'i');
      return regex.test(t);
    }
    return t.includes(w);
  });

  // Prioridade 1: Cancelamentos e recusas
  if (checkWords(KEYWORDS['nao-atendido'])) return 'nao-atendido';
  
  // Prioridade 2: Reagendamentos
  if (checkWords(KEYWORDS.reagendado)) return 'reagendado';
  
  // Prioridade 3: Confirmações
  if (checkWords(KEYWORDS.confirmado)) return 'confirmado';

  return null;
}

// ──────────────────────────────────────────────
// ROUTES
// ──────────────────────────────────────────────

// GET /status/:clientId — retorna status salvo
app.get('/status/:clientId', async (req, res) => {
  try {
    const s = await getStatus(req.params.clientId);
    res.json(s);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// POST /status/:clientId — salva status manualmente
app.post('/status/:clientId', async (req, res) => {
  try {
    const { status, obs } = req.body;
    await setStatus(req.params.clientId, status, obs);
    
    // Sincronizacao automatica com a Blacklist baseada estritamente no Numero
    let phone = '';
    const match = req.params.clientId.match(/^wa_(\d+)_/);
    if (match) {
      phone = match[1];
    } else {
      phone = req.params.clientId.replace(/\D/g, '');
    }
    
    if (phone) {
      if (!phone.startsWith('55') && phone.length >= 10) {
        phone = '55' + phone;
      }
      if (status === 'numero-nao-pertence') {
        await redis.sAdd('agenda:blacklist', phone);
        log('info', 'Numero adicionado a Blacklist manualmente pelo Painel', { phone, status });
      } else {
        await redis.sRem('agenda:blacklist', phone);
        log('info', 'Numero removido da Blacklist manualmente pelo Painel', { phone, status });
      }
    }
    
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// GET /msgs/:phone — histórico de mensagens do número
app.get('/msgs/:phone', async (req, res) => {
  try {
    const msgs = await getMsgs(req.params.phone);
    res.json(msgs);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// POST /send — envia mensagem para 1 cliente
app.post('/send', async (req, res) => {
  try {
    if (!checkRateLimit('send')) {
      return res.status(429).json({ error: 'Rate limit: máx 20 envios/min' });
    }

    const { phone, text, clientId } = req.body;
    if (!phone || !text) return res.status(400).json({ error: 'phone e text obrigatórios' });

    // 1. Limpeza e Validacao de Formato
    const val = validateAndCleanPhone(phone);
    if (!val.valid) {
      return res.status(400).json({ error: `Numero Invalido: ${val.error}` });
    }
    const number = val.num;

    // 2. Checagem de Blacklist
    const isBlacklisted = await redis.sIsMember('agenda:blacklist', number);
    if (isBlacklisted) {
      return res.status(400).json({ error: 'Este numero esta bloqueado na Blacklist devido a falhas anteriores.' });
    }

    const instance = 'Meta_API_Oficial';
    const result = await sendText(number, text);

    // Salva número → clientId pra cruzar no webhook
    if (clientId) {
      let number = phone.replace(/\D/g, '');
      if (!number.startsWith('55')) number = '55' + number;
      await redis.set(KEY_PHONE_ID(number), clientId);
    }

    // Registra mensagem enviada
    const msg = { from: 'me', text, ts: Date.now(), instance };
    await appendMsg(number, msg);

    if (clientId) {
      await setStatus(clientId, 'entregue', 'Mensagem enviada via painel');
    }

    res.json({ ok: true, result });
  } catch (e) {
    log('error', 'Erro ao enviar', { error: e.response?.data || e.message });
    res.status(500).json({ error: e.response?.data || e.message });
  }
});

// POST /send-bulk — disparo em massa com delay entre envios
// Suporta: templates[] (rodízio) + windowMs (janela aleatória)
// Backward compat: template (string única) + delayMs ainda funcionam
app.post('/send-bulk', async (req, res) => {
  try {
    const { clients, template, templates: tplArray, delayMs = 3000, windowMs, remetente, metaTemplateName, metaTemplateLang, metaTemplateParamCount } = req.body;
    const instance = 'Meta_API_Oficial';

    // Monta array de templates: aceita tanto "template" (string) quanto "templates" (array)
    let tpls = [];
    if (Array.isArray(tplArray) && tplArray.length) {
      tpls = tplArray;
    } else if (template) {
      tpls = [template];
    }

    if (!clients?.length || !tpls.length) {
      return res.status(400).json({ error: 'clients e template/templates obrigatórios' });
    }

    // Salvar campanha
    const campaignId = `camp_${Date.now()}`;
    const campaign = {
      id: campaignId,
      total: clients.length,
      template: tpls.length === 1 ? tpls[0] : `[${tpls.length} templates em rodízio]`,
      startedAt: new Date().toISOString(),
      success: 0,
      failed: 0,
      status: 'running',
      instance,
      mode: windowMs ? `janela ${Math.round(windowMs/60000)}min` : `fixo ${delayMs}ms`
    };
    await redis.set(`agenda:campaign:${campaignId}`, JSON.stringify(campaign));

    res.json({ ok: true, total: clients.length, campaignId, message: 'Disparo iniciado em background' });

    // Calcula delays entre envios
    let delays = [];
    if (windowMs && windowMs > 0 && clients.length > 1) {
      // Gera pontos aleatórios dentro da janela, ordena e calcula intervalos
      const points = [0];
      for (let i = 1; i < clients.length; i++) {
        points.push(Math.random() * windowMs);
      }
      points.sort((a, b) => a - b);
      for (let i = 0; i < points.length; i++) {
        delays.push(i === 0 ? points[0] : points[i] - points[i - 1]);
      }
    } else {
      // Modo fixo (compatibilidade)
      delays = clients.map(() => delayMs);
    }

    // Dispara em background
    (async () => {
      let success = 0, failed = 0;
      for (let idx = 0; idx < clients.length; idx++) {
        const c = clients[idx];
        const rawPhone = c.phone || c.tel1 || c.tel2 || '';
        let number = String(rawPhone).replace(/\D/g, '');
        if (!number.startsWith('55') && number.length >= 10) number = '55' + number;
        
        // Rodízio de templates
        const chosenTpl = tpls[idx % tpls.length];
        try {
          // 1. Validacao de formato
          const val = validateAndCleanPhone(rawPhone);
          if (!val.valid) {
            throw new Error(`Validacao de formato: ${val.error}`);
          }
          number = val.num;

          // 2. Checagem de Blacklist
          const isBlacklisted = await redis.sIsMember('agenda:blacklist', number);
          if (isBlacklisted) {
            throw new Error('Bloqueado pela Blacklist (Falhas anteriores)');
          }
          // Se o frontend enviou metaTemplateName, usa direto (prioridade)
          // Senão, tenta buscar pelo texto no Redis (fallback antigo)
          let templateName = metaTemplateName || '';
          if (!templateName) {
            templateName = '';
            const rawTemplates = await redis.get('agenda:templates');
            if (rawTemplates) {
              const parsed = JSON.parse(rawTemplates);
              const found = parsed.find(t => t.text.trim() === chosenTpl.trim());
              if (found && found.name) {
                templateName = found.name.toLowerCase().replace(/[^a-z0-9_]/g, '_');
              }
            }
          }
          
          // Se veio meta_name do template individual, prioriza sobre o global
          if (chosenTpl.meta_name && chosenTpl.meta_name !== 'template_padrao') {
            templateName = chosenTpl.meta_name;
          }

          // Se ainda não tem templateName válido, pula este cliente
          if (!templateName || templateName === 'template_padrao') {
            log('warn', 'Template nao definido, pulando cliente', { nome: c.nome, phone: number });
            await setStatus(c.id, 'entregue', 'Pulado: template Meta nao configurado');
            failed++;
            continue;
          }

          let params = extractTemplateParams(typeof chosenTpl === 'string' ? chosenTpl : (chosenTpl.text || chosenTpl), c, remetente);

          // Fallback: se é um template Meta e nenhum param foi detectado no texto,
          // envia campos do cliente como parâmetros na ordem:
          // {{1}}=nome, {{2}}=data, {{3}}=cidade, {{4}}=horario, {{5}}=endereco, {{6}}=tipo, {{7}}=remetente
          if (params.length === 0 && metaTemplateName) {
            const fallbackFields = [
              c.nome || ' ',
              c.data || ' ',
              c.cidade || ' ',
              c.horario || ' ',
              c.endereco || ' ',
              c.tipo || ' ',
              remetente || ' '
            ];
            // Usa exatamente a qtd de params que o template espera
            const count = metaTemplateParamCount || 1;
            params = fallbackFields.slice(0, count).map(v => ({ type: "text", text: v }));
          }

          const components = params.length > 0 ? [{ type: "body", parameters: params }] : [];

          await sendTemplate(number, templateName, components, metaTemplateLang || 'pt_BR');

          const tplText = typeof chosenTpl === 'string' ? chosenTpl : (chosenTpl.text || '');
          const text = tplText
            // Chave dupla {{nome}}
            .replace(/\{\{nome\}\}/gi, c.nome || '')
            .replace(/\{\{data\}\}/gi, c.data || '')
            .replace(/\{\{cidade\}\}/gi, c.cidade || '')
            .replace(/\{\{horario\}\}/gi, c.horario || '')
            .replace(/\{\{endereco\}\}/gi, c.endereco || '')
            .replace(/\{\{tipo\}\}/gi, c.tipo || '')
            .replace(/\{\{remetente\}\}/gi, remetente || '')
            // Chave simples {nome}
            .replace(/\{nome\}/gi, c.nome || '')
            .replace(/\{data\}/gi, c.data || '')
            .replace(/\{cidade\}/gi, c.cidade || '')
            .replace(/\{horario\}/gi, c.horario || '')
            .replace(/\{endereco\}/gi, c.endereco || '')
            .replace(/\{tipo\}/gi, c.tipo || '')
            .replace(/\{remetente\}/gi, remetente || '')
            // Numéricas {{1}}, {{2}}, etc.
            .replace(/\{\{1\}\}/g, c.nome || '')
            .replace(/\{\{2\}\}/g, c.data || '')
            .replace(/\{\{3\}\}/g, c.cidade || '')
            .replace(/\{\{4\}\}/g, c.horario || '')
            .replace(/\{\{5\}\}/g, c.endereco || '')
            .replace(/\{\{6\}\}/g, c.tipo || '')
            .replace(/\{\{7\}\}/g, remetente || '');

          // number já está definido e validado acima (val.num)
          await redis.set(KEY_PHONE_ID(number), c.id);

          const msg = { from: 'me', text, ts: Date.now(), instance };
          await appendMsg(number, msg);

          await setStatus(c.id, 'entregue', 'Disparo em massa realizado');

          success++;
          log('info', 'Enviado', { nome: c.nome, phone: number, instance, tplIdx: idx % tpls.length });
        } catch (e) {
          failed++;
          log('error', 'Falha envio', { nome: c.nome, phone: number, error: e.response?.data || e.message });
          
          const isBlacklistError = e.message.includes('Blacklist');
          const isValidationError = e.message.includes('Validacao');
          const statusText = 'numero-nao-pertence';
          
          let obsText = 'Falha envio: ' + (e.response?.data?.error?.message || e.message);
          if (isBlacklistError) obsText = 'Bloqueado: Lista Negra (Falhas anteriores)';
          if (isValidationError) obsText = 'Bloqueado pelo sistema: ' + e.message;
          
          await setStatus(c.id, statusText, obsText);
          
          // DYNAMIC BLACKLIST: Adiciona automaticamente a blacklist se for erro real
          const isMetaInvalidUser = e.response?.data?.error?.code === 131026 || 
                                    (e.response?.data?.error?.message && e.response.data.error.message.includes('valid'));
          
          if (isValidationError || isMetaInvalidUser) {
            if (number && number.length >= 10) {
              await redis.sAdd('agenda:blacklist', number);
              log('info', 'Numero adicionado a Blacklist automaticamente devido a falha real', { number, error: e.message });
            }
          }
        }

        // Aguarda delay (fixo ou aleatório conforme modo)
        if (idx < clients.length - 1) {
          await new Promise(r => setTimeout(r, delays[idx + 1] || delayMs));
        }
      }

      // Atualiza campanha
      campaign.success = success;
      campaign.failed = failed;
      campaign.status = 'done';
      campaign.finishedAt = new Date().toISOString();
      await redis.set(`agenda:campaign:${campaignId}`, JSON.stringify(campaign));

      log('info', 'Disparo concluído', { success, failed, campaignId, instance });
    })();

  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// POST /send-reply — envia resposta manual pelo painel
app.post('/send-reply', async (req, res) => {
  try {
    if (!checkRateLimit('reply')) {
      return res.status(429).json({ error: 'Rate limit atingido' });
    }
    const { phone, text } = req.body;
    const instance = 'Meta_API_Oficial';
    let number = String(phone).replace(/\D/g, '');
    if (!number.startsWith('55')) number = '55' + number;
    await sendText(number, text);
    const msg = { from: 'me', text, ts: Date.now(), instance };
    await appendMsg(number, msg);
    // Clear unread counter
    await redis.del(KEY_UNREAD(number));
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// GET /all-status — retorna todos os status salvos (para sync do frontend)
app.get('/all-status', async (req, res) => {
  try {
    const keys = await scanKeys('agenda:status:*');
    const result = {};
    // Batch com pipeline para não fazer N gets sequenciais
    if (keys.length > 0) {
      const values = await Promise.all(keys.map(k => redis.get(k)));
      for (let i = 0; i < keys.length; i++) {
        const id = keys[i].replace('agenda:status:', '');
        result[id] = values[i] ? JSON.parse(values[i]) : null;
      }
    }
    res.json(result);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// GET /unread — retorna contadores de não lidas
app.get('/unread', async (req, res) => {
  try {
    const keys = await scanKeys('agenda:unread:*');
    const result = {};
    if (keys.length > 0) {
      const values = await Promise.all(keys.map(k => redis.get(k)));
      for (let i = 0; i < keys.length; i++) {
        const phone = keys[i].replace('agenda:unread:', '');
        const count = values[i] ? parseInt(values[i]) : 0;
        if (count > 0) result[phone] = count;
      }
    }
    res.json(result);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ──────────────────────────────────────────────
// CLIENTS (GLOBAL AGENDA)
// ──────────────────────────────────────────────
const KEY_CLIENTS = 'agenda:clients';


// ──────────────────────────────────────────────
// BLACKLIST ENDPOINTS
// ──────────────────────────────────────────────
app.get('/agenda/blacklist', async (req, res) => {
  try {
    const list = await redis.sMembers('agenda:blacklist');
    res.json(list || []);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/agenda/blacklist', async (req, res) => {
  try {
    const { phone, action } = req.body;
    if (!phone) return res.status(400).json({ error: 'phone obrigatorio' });
    let number = String(phone).replace(/\D/g, '');
    if (!number.startsWith('55') && number.length >= 10) number = '55' + number;
    
    if (action === 'add') {
      await redis.sAdd('agenda:blacklist', number);
      log('info', 'Numero adicionado a Blacklist via API', { number });
      res.json({ ok: true, msg: 'Numero adicionado' });
    } else if (action === 'remove') {
      await redis.sRem('agenda:blacklist', number);
      log('info', 'Numero removido da Blacklist via API', { number });
      res.json({ ok: true, msg: 'Numero removido' });
    } else {
      res.status(400).json({ error: 'action deve ser add ou remove' });
    }
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/agenda/clients', async (req, res) => {
  try {
    if (process.env.DATABASE_URL) {
      const { rows } = await pgPool.query('SELECT * FROM clientes');
      const format = rows.map(r => ({
        id: r.id, nome: r.nome, telefone: r.telefone, data: r.data, cidade: r.cidade, 
        horario: r.horario, endereco: r.endereco, tipo: r.tipo, fase: r.fase, 
        status: r.status_atual !== 'pendente' ? r.status_atual : (r.status_ofs || 'Pendente')
      }));
      return res.json(format);
    }
    const raw = await redis.get(KEY_CLIENTS);
    res.json(raw ? JSON.parse(raw) : []);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/agenda/clients', async (req, res) => {
  try {
    const newClients = req.body.clients || [];
    if (!Array.isArray(newClients)) return res.status(400).json({ error: 'clients deve ser array' });
    
    const raw = await redis.get(KEY_CLIENTS);
    const existing = raw ? JSON.parse(raw) : [];
    
    const map = new Map();
    existing.forEach(c => map.set(c.id, c));
    newClients.forEach(c => map.set(c.id, c));
    
    const merged = Array.from(map.values());
    await redis.set(KEY_CLIENTS, JSON.stringify(merged));
    
    // --- SHADOW WRITE: Inserir no PostgreSQL ---
    try {
      if (process.env.DATABASE_URL) {
        const client = await pgPool.connect();
        try {
          await client.query('BEGIN');
          for (const c of newClients) {
            const query = `
              INSERT INTO clientes (id, nome, telefone, data, cidade, horario, endereco, tipo, fase, status_ofs, status_atual)
              VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
              ON CONFLICT (id) DO UPDATE SET
                nome = EXCLUDED.nome,
                telefone = EXCLUDED.telefone,
                data = EXCLUDED.data,
                cidade = EXCLUDED.cidade,
                horario = EXCLUDED.horario,
                endereco = EXCLUDED.endereco,
                tipo = EXCLUDED.tipo,
                fase = EXCLUDED.fase,
                status_ofs = EXCLUDED.status_ofs,
                atualizado_em = CURRENT_TIMESTAMP;
            `;
            const values = [
              c.id, c.nome, c.telefone, c.data, c.cidade, c.horario, c.endereco, c.tipo, c.fase, c.status || 'Pendente', 'pendente'
            ];
            await client.query(query, values);
          }
          await client.query('COMMIT');
          log('info', `Shadow Write PostgreSQL: ${newClients.length} clientes inseridos.`);
        } catch (e) {
          await client.query('ROLLBACK');
          log('error', 'Shadow Write PG Error', { error: e.message });
        } finally {
          client.release();
        }
      }
    } catch (e) {
      log('error', 'Shadow Write Pool Connection Error', { error: e.message });
    }
    // -------------------------------------------

    res.json({ ok: true, count: merged.length });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/agenda/clear', async (req, res) => {
  try {
    await redis.del(KEY_CLIENTS);
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ──────────────────────────────────────────────
// TEMPLATES (salvar e listar)
// ──────────────────────────────────────────────
app.get('/templates', async (req, res) => {
  try {
    const raw = await redis.get(KEY_TEMPLATES);
    res.json(raw ? JSON.parse(raw) : []);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/templates', async (req, res) => {
  try {
    const { name, text } = req.body;
    if (!name || !text) return res.status(400).json({ error: 'name e text obrigatórios' });
    const raw = await redis.get(KEY_TEMPLATES);
    const templates = raw ? JSON.parse(raw) : [];
    templates.push({ id: `tpl_${Date.now()}`, name, text, createdAt: new Date().toISOString() });
    await redis.set(KEY_TEMPLATES, JSON.stringify(templates));
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.delete('/templates/:id', async (req, res) => {
  try {
    const raw = await redis.get(KEY_TEMPLATES);
    const templates = raw ? JSON.parse(raw) : [];
    const filtered = templates.filter(t => t.id !== req.params.id);
    await redis.set(KEY_TEMPLATES, JSON.stringify(filtered));
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ──────────────────────────────────────────────
// CAMPAIGNS HISTORY
// ──────────────────────────────────────────────
app.get('/campaigns', async (req, res) => {
  try {
    const keys = await scanKeys('agenda:campaign:*');
    const campaigns = [];
    if (keys.length > 0) {
      const values = await Promise.all(keys.map(k => redis.get(k)));
      for (const v of values) {
        if (v) campaigns.push(JSON.parse(v));
      }
    }
    campaigns.sort((a, b) => new Date(b.startedAt) - new Date(a.startedAt));
    res.json(campaigns.slice(0, 20));
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ──────────────────────────────────────────────
// EXPORT CSV — relatório consolidado
// ──────────────────────────────────────────────
app.get('/export-csv', async (req, res) => {
  try {
    const keys = await scanKeys('agenda:status:*');
    let csv = 'ClienteID,Status,Observação,Atualizado Em\n';
    if (keys.length > 0) {
      const values = await Promise.all(keys.map(k => redis.get(k)));
      for (let i = 0; i < keys.length; i++) {
        const id = keys[i].replace('agenda:status:', '');
        const v = values[i];
        if (v) {
          const d = JSON.parse(v);
          csv += `"${id}","${d.status}","${(d.obs || '').replace(/"/g, '""')}","${d.updatedAt || ''}"\n`;
        }
      }
    }
    res.setHeader('Content-Type', 'text/csv; charset=utf-8');
    res.setHeader('Content-Disposition', `attachment; filename=agenda_report_${new Date().toISOString().split('T')[0]}.csv`);
    res.send('\ufeff' + csv);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ──────────────────────────────────────────────
// DASHBOARD SUMMARY — dados para a aba do Dashboard
// ──────────────────────────────────────────────
app.get('/dashboard-summary', async (req, res) => {
  try {
    const keys = await scanKeys('agenda:status:*');
    const summary = { total: 0, confirmado: 0, pendente: 0, 'nao-atendido': 0, reagendado: 0 };
    if (keys.length > 0) {
      const values = await Promise.all(keys.map(k => redis.get(k)));
      for (const v of values) {
        if (v) {
          const d = JSON.parse(v);
          summary.total++;
          summary[d.status] = (summary[d.status] || 0) + 1;
        }
      }
    }
    summary.taxa_confirmacao = summary.total > 0
      ? Math.round(summary.confirmado / summary.total * 1000) / 10
      : 0;
    res.json(summary);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ──────────────────────────────────────────────
// CONFIGURAÇÕES DINÂMICAS — API REST
// ──────────────────────────────────────────────
app.get('/config', async (req, res) => {
  try {
    if (process.env.DATABASE_URL) {
      const { rows } = await pgPool.query('SELECT chave, valor, descricao, atualizado_em FROM configuracoes');
      const config = {};
      rows.forEach(r => config[r.chave] = { valor: r.valor, descricao: r.descricao, atualizado_em: r.atualizado_em });
      return res.json(config);
    }
    res.json({});
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.get('/config/:chave', async (req, res) => {
  try {
    if (process.env.DATABASE_URL) {
      const { rows } = await pgPool.query('SELECT valor, descricao, atualizado_em FROM configuracoes WHERE chave = $1', [req.params.chave]);
      if (rows.length) return res.json(rows[0]);
    }
    res.status(404).json({ error: 'Configuração não encontrada' });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.post('/config/:chave', async (req, res) => {
  try {
    if (!process.env.DATABASE_URL) return res.status(500).json({ error: 'DATABASE_URL não configurada' });
    const { valor, descricao } = req.body;
    await pgPool.query(
      `INSERT INTO configuracoes (chave, valor, descricao) VALUES ($1, $2::jsonb, $3)
       ON CONFLICT (chave) DO UPDATE SET valor = $2::jsonb, descricao = COALESCE($3, configuracoes.descricao), atualizado_em = CURRENT_TIMESTAMP`,
      [req.params.chave, JSON.stringify(valor), descricao || null]
    );
    await loadDynamicConfig(); // Recarrega imediatamente
    log('info', 'Configuração atualizada', { chave: req.params.chave });
    res.json({ ok: true });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ──────────────────────────────────────────────
// BUTTON CONFIG — respostas automáticas por botão
// ──────────────────────────────────────────────
const KEY_BTN_CFG = 'agenda:button-config';

// Mapeamento botão → status (fallback hardcoded, sobrescrito pelo PostgreSQL)
const BTN_STATUS_MAP = BTN_STATUS_MAP_DYNAMIC || {
  'sim, confirmo':         'confirmado',
  'preciso reagendar':     'reagendado',
  'cancelar':              'nao-atendido',
  'agendar':               'agendado',
  'ja devolvi':            'resolvido',
  'sim, tudo certo':       'confirmado',
  'nao, tenho problema':   'problema-aberto',
  'quero falar com alguem':'problema-aberto',
  'sim, pode vir':         'agendado',
  'não, preciso reagendar':'reagendado',
  'nao, preciso reagendar':'reagendado'
};

app.get('/button-config', async (req, res) => {
  try {
    const raw = await redis.get(KEY_BTN_CFG);
    res.json(raw ? JSON.parse(raw) : {});
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/button-config', async (req, res) => {
  try {
    await redis.set(KEY_BTN_CFG, JSON.stringify(req.body));
    log('info', 'Button config salvo', { keys: Object.keys(req.body) });
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ──────────────────────────────────────────────
// FLOW API — gestão de fluxos automáticos
// ──────────────────────────────────────────────
const KEY_FLOW_CFG = 'agenda:flow-config';
const KEY_FLOWS    = 'agenda:flows';

app.get('/api/flow/flow-config', async (req, res) => {
  try {
    const raw = await redis.get(KEY_FLOW_CFG);
    res.json(raw ? JSON.parse(raw) : { ativo: false, delay_segundos: 10 });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/api/flow/flow-config', async (req, res) => {
  try {
    const existing = await redis.get(KEY_FLOW_CFG);
    const merged = Object.assign(existing ? JSON.parse(existing) : {}, req.body);
    await redis.set(KEY_FLOW_CFG, JSON.stringify(merged));
    log('info', 'Flow config salvo', { ativo: merged.ativo });
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/api/flow/flows', async (req, res) => {
  try {
    const raw = await redis.get(KEY_FLOWS);
    res.json(raw ? JSON.parse(raw) : []);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/api/flow/flows', async (req, res) => {
  try {
    const newFlows = Array.isArray(req.body) ? req.body : [];
    const raw = await redis.get(KEY_FLOWS);
    const existing = raw ? JSON.parse(raw) : [];
    const toAdd = newFlows.map(f => ({
      id: `flow_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      phone: (f.phone || '').replace(/\D/g, ''),
      nome: f.nome || '',
      enviado_em: f.enviado_em || new Date().toISOString(),
      status: 'aguardando',
      resposta_recebida: null,
      classificacao: null
    }));
    const merged = existing.concat(toAdd);
    await redis.set(KEY_FLOWS, JSON.stringify(merged));
    log('info', 'Fluxos registrados', { count: toAdd.length });
    res.json({ ok: true, added: toAdd.length });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.delete('/api/flow/flows/:id', async (req, res) => {
  try {
    const raw = await redis.get(KEY_FLOWS);
    const flows = raw ? JSON.parse(raw) : [];
    const updated = flows.map(f => f.id === req.params.id ? Object.assign(f, { status: 'cancelado' }) : f);
    await redis.set(KEY_FLOWS, JSON.stringify(updated));
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.delete('/api/flow/flows', async (req, res) => {
  try {
    const raw = await redis.get(KEY_FLOWS);
    const flows = raw ? JSON.parse(raw) : [];
    const active = flows.filter(f => f.status === 'aguardando');
    await redis.set(KEY_FLOWS, JSON.stringify(active));
    res.json({ ok: true, remaining: active.length });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/api/flow/status', async (req, res) => {
  try {
    const raw = await redis.get(KEY_FLOWS);
    const flows = raw ? JSON.parse(raw) : [];
    const counts = { aguardando: 0, respondidos: 0, cancelados: 0 };
    flows.forEach(f => {
      if (f.status === 'aguardando') counts.aguardando++;
      else if (f.status === 'respondido') counts.respondidos++;
      else if (f.status === 'cancelado') counts.cancelados++;
    });
    res.json(counts);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Helper: atualiza fluxo quando cliente responde
async function flowMarkResponded(phone, text, classificacao) {
  try {
    const raw = await redis.get(KEY_FLOWS);
    if (!raw) return;
    const flows = JSON.parse(raw);
    const cleanPhone = phone.replace(/\D/g, '').slice(-8);
    let changed = false;
    flows.forEach(f => {
      if (f.status === 'aguardando' && f.phone.slice(-8) === cleanPhone) {
        f.status = 'respondido';
        f.resposta_recebida = text.slice(0, 100);
        f.classificacao = classificacao;
        f.respondido_em = new Date().toISOString();
        changed = true;
      }
    });
    if (changed) await redis.set(KEY_FLOWS, JSON.stringify(flows));
  } catch (e) {
    log('warn', 'Erro ao marcar fluxo respondido', { error: e.message });
  }
}

// ──────────────────────────────────────────────
// WEBHOOK — recebe mensagens da Meta API
// ──────────────────────────────────────────────

app.get('/webhook', (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];
  if (mode === 'subscribe' && token === META_VERIFY_TOKEN) {
    res.status(200).send(challenge);
  } else {
    res.sendStatus(403);
  }
});

// ──────────────────────────────────────────────
// JARVIS IA — Debounce para não sobrecarregar
// ──────────────────────────────────────────────
const jarvisDebounce = {};
const JARVIS_COOLDOWN = 30000; // 30 segundos entre chamadas pro mesmo número

function shouldCallJarvis(phone) {
  const now = Date.now();
  if (jarvisDebounce[phone] && now - jarvisDebounce[phone] < JARVIS_COOLDOWN) {
    return false;
  }
  jarvisDebounce[phone] = now;
  return true;
}

// Verifica se o cliente foi disparado hoje a partir das 16h
async function isEligibleForJarvis(clientId) {
  try {
    const statusRaw = await redis.get(KEY_STATUS(clientId));
    if (!statusRaw) return false;
    const statusData = JSON.parse(statusRaw);
    // Precisa ter sido "entregue" (disparado)
    if (!statusData.status || !statusData.status.startsWith('entregue')) return false;
    if (!statusData.updatedAt) return false;
    const updatedAt = new Date(statusData.updatedAt);
    const now = new Date();
    // Mesmo dia
    if (updatedAt.toDateString() !== now.toDateString()) return false;
    // A partir das 16h (19h UTC = 16h BRT)
    const cutoffToday = new Date(now);
    cutoffToday.setUTCHours(19, 0, 0, 0); // 16h BRT = 19h UTC
    return updatedAt >= cutoffToday;
  } catch (e) {
    log('warn', 'Erro ao verificar elegibilidade Jarvis', { error: e.message });
    return false;
  }
}

app.post('/webhook', async (req, res) => {
  res.sendStatus(200);
  try {
    const body = req.body;
    if (body.object === 'whatsapp_business_account') {
      for (const entry of body.entry) {
        for (const change of entry.changes) {
          if (change.value.messages && change.value.messages.length > 0) {
            const msg = change.value.messages[0];
            let phone = msg.from;
            if (!phone.startsWith('55')) phone = '55' + phone;

            const text = msg.text ? msg.text.body : (msg.button ? msg.button.text : '');
            if (!text) continue;

            const instance = 'Meta API Oficial';

            log('info', 'Msg webhook', { phone, type: msg.type || 'text', text: text.slice(0, 60) });

            await appendMsg(phone, { from: 'client', text, ts: Date.now(), instance });
            await redis.incr(KEY_UNREAD(phone));

            // ── AUTO-REPLY POR BOTÃO (sem Jarvis) ──────
            const clientId = await redis.get(KEY_PHONE_ID(phone));
            let autoReplied = false;

            try {
              const btnCfgRaw = await redis.get(KEY_BTN_CFG);
              const btnCfg = btnCfgRaw ? JSON.parse(btnCfgRaw) : {};
              const btnKey = text.toLowerCase().trim();
              const replyTemplate = btnCfg[btnKey];
              const newStatus = BTN_STATUS_MAP[btnKey];

              if (replyTemplate && clientId) {
                // Buscar nome do cliente
                const clientRaw = await redis.get(KEY_CLIENTS);
                const clients = clientRaw ? JSON.parse(clientRaw) : [];
                const client = clients.find(c => c.id === clientId) || {};
                const firstName = (client.nome || 'Cliente').split(' ')[0];
                const firstName2 = firstName.charAt(0).toUpperCase() + firstName.slice(1).toLowerCase();

                // Substituir NOME pelo primeiro nome
                const replyText = replyTemplate.replace(/NOME/g, firstName2);

                // Enviar resposta automática
                await sendText(phone, replyText);
                await appendMsg(phone, { from: 'me', text: replyText, ts: Date.now(), instance: 'Auto_Flow', auto: true });
                log('info', 'Auto-reply enviado', { phone, button: btnKey, status: newStatus });

                // Atualizar status
                if (newStatus) {
                  await setStatus(clientId, newStatus, `Auto-flow: botão "${text.slice(0, 40)}"`);
                }

                // Marcar fluxo como respondido
                const classificacao = ['confirmado', 'agendado', 'resolvido'].includes(newStatus) ? 'sim' : 'nao';
                await flowMarkResponded(phone, text, classificacao);

                autoReplied = true;
              } else if (replyTemplate && !clientId) {
                // Tem config do botão mas não tem clientId — tenta responder mesmo assim
                const replyText = replyTemplate.replace(/NOME/g, 'Cliente');
                await sendText(phone, replyText);
                await appendMsg(phone, { from: 'me', text: replyText, ts: Date.now(), instance: 'Auto_Flow', auto: true });
                await flowMarkResponded(phone, text, 'sim');
                log('info', 'Auto-reply enviado (sem clientId)', { phone, button: btnKey });
                autoReplied = true;
              }
            } catch (btnErr) {
              log('warn', 'Erro no auto-reply por botão', { phone, error: btnErr.message });
            }

            // ── JARVIS IA — DESATIVADO ──
            // Motivo: Jarvis offline (404) e vazava raciocínio interno no painel.
            // O fluxo agora é: auto-reply por botão → fallback por keywords.
            const jarvisHandled = false;

            // Fallback: keywords antigas (se nem auto-reply nem Jarvis processaram)
            if (!autoReplied && !jarvisHandled && clientId) {
              const detected = detectStatus(text);
              if (detected) {
                const obs = `Auto-kw: "${text.slice(0, 60)}"`;
                await setStatus(clientId, detected, obs);
                await flowMarkResponded(phone, text, detected === 'confirmado' ? 'sim' : 'nao');
              }
            }

          } else if (change.value.statuses && change.value.statuses.length > 0) {
            // Pode processar status de entrega futuramente
          }
        }
      }
    }
  } catch (e) {
    log('error', 'Meta Webhook error', { error: e.message });
  }
});

// ──────────────────────────────────────────────
// CONVERSATIONS — lista conversas para a aba Chat
// ──────────────────────────────────────────────
// Função interna para construir lista de conversas (com cache de 30s)
const buildConversations = cached('conversations', 30000, async () => {
  const msgKeys = await scanKeys('agenda:msgs:*');
  const conversations = [];

  // Batch: busca msgs e unreads em paralelo (não sequencial)
  const batchSize = 50;
  for (let i = 0; i < msgKeys.length; i += batchSize) {
    const batch = msgKeys.slice(i, i + batchSize);
    const phones = batch.map(k => k.replace('agenda:msgs:', ''));
    const [msgValues, unreadValues] = await Promise.all([
      Promise.all(batch.map(k => redis.get(k))),
      Promise.all(phones.map(p => redis.get(KEY_UNREAD(p))))
    ]);

    for (let j = 0; j < batch.length; j++) {
      const raw = msgValues[j];
      if (!raw) continue;
      const msgs = JSON.parse(raw);
      if (!msgs.length) continue;
      const lastMsg = msgs[msgs.length - 1];
      conversations.push({
        phone: phones[j],
        lastMessage: (lastMsg.text || '').substring(0, 100),
        lastTs: lastMsg.ts,
        lastFrom: lastMsg.from,
        unread: unreadValues[j] ? parseInt(unreadValues[j]) : 0
      });
    }
  }

  conversations.sort((a, b) => (b.lastTs || 0) - (a.lastTs || 0));
  return conversations;
});

app.get('/conversations', async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = Math.min(parseInt(req.query.limit) || 50, 100);

    const conversations = await buildConversations();
    const total = conversations.length;
    const pages = Math.ceil(total / limit) || 1;
    const start = (page - 1) * limit;
    const sliced = conversations.slice(start, start + limit);

    res.json({ conversations: sliced, page, pages, total });
  } catch (e) {
    log('error', 'Erro ao listar conversas', { error: e.message });
    res.status(500).json({ error: e.message });
  }
});

// ──────────────────────────────────────────────
// HEALTH
// ──────────────────────────────────────────────
app.get('/health', (_, res) => res.json({ ok: true, ts: new Date().toISOString() }));
app.get('/', (_, res) => res.json({ service: 'WhatsApp Agenda API', version: '2.0', status: 'online' }));

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => log('info', `Backend rodando na porta ${PORT}`));
