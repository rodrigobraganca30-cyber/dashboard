const axios = require('axios');
const { redis } = require('../config/redis');
const { log } = require('../config/logger');

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

    const numIdx = parseInt(varName);
    if (!isNaN(numIdx) && numIdx >= 1 && numIdx <= numericFields.length) {
      textValue = numericFields[numIdx - 1];
    }
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

module.exports = {
  getMetaConfig,
  getMetaClient,
  withRetry,
  extractTemplateParams,
  sendTemplate,
  sendText,
  META_VERIFY_TOKEN
};
