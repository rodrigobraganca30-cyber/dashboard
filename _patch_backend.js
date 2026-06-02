#!/usr/bin/env node
// Patch index.js para adicionar normalizePhone e aplicar em todos os pontos
const fs = require('fs');
const path = '/docker/whatsapp-agenda/backend/index.js';

let code = fs.readFileSync(path, 'utf8');
const orig = code;

// 1. Adicionar normalizePhone depois de validateAndCleanPhone
const normalizeFunc = `
// Normaliza telefone BR para 13 digitos (55+DDD+9+8dig)
function normalizePhone(raw) {
  let n = String(raw).replace(/\\D/g, '');
  if (!n.startsWith('55')) n = '55' + n;
  if (n.length === 12) n = n.slice(0, 4) + '9' + n.slice(4);
  return n;
}
`;

if (!code.includes('function normalizePhone')) {
  code = code.replace(
    /function validateAndCleanPhone\(raw\)/,
    normalizeFunc + '\nfunction validateAndCleanPhone(raw)'
  );
  console.log('[OK] normalizePhone adicionada');
} else {
  console.log('[SKIP] normalizePhone ja existe');
}

// 2. appendMsg: normalizar phone
code = code.replace(
  /async function appendMsg\(phone, msg\) \{\n\s*const raw = await redis\.get\(KEY_MSGS\(phone\)\);/,
  `async function appendMsg(phone, msg) {\n  phone = normalizePhone(phone);\n  const raw = await redis.get(KEY_MSGS(phone));`
);
console.log('[OK] appendMsg normalizado');

// 3. getMsgs: normalizar phone
code = code.replace(
  /async function getMsgs\(phone\) \{\n\s*const raw = await redis\.get\(KEY_MSGS\(phone\)\);/,
  `async function getMsgs(phone) {\n  phone = normalizePhone(phone);\n  const raw = await redis.get(KEY_MSGS(phone));`
);
console.log('[OK] getMsgs normalizado');

// 4. Webhook: normalizar phone apos startsWith check
code = code.replace(
  /let phone = msg\.from;\n\s*if \(!phone\.startsWith\('55'\)\) phone = '55' \+ phone;/,
  `let phone = msg.from;\n            if (!phone.startsWith('55')) phone = '55' + phone;\n            phone = normalizePhone(phone);`
);
console.log('[OK] webhook normalizado');

// 5. /send: normalizar no appendMsg call
code = code.replace(
  /await appendMsg\(phone\.replace\(\/\\D\/g, ''\), msg\);/,
  `await appendMsg(normalizePhone(phone), msg);`
);
console.log('[OK] /send normalizado');

// 6. KEY_PHONE_ID no /send: normalizar
code = code.replace(
  /await redis\.set\(KEY_PHONE_ID\(number\), clientId\);/,
  `await redis.set(KEY_PHONE_ID(normalizePhone(number)), clientId);`
);
console.log('[OK] KEY_PHONE_ID no /send normalizado');

// 7. KEY_UNREAD no webhook: normalizar
code = code.replace(
  /await redis\.incr\(KEY_UNREAD\(phone\)\);/,
  `await redis.incr(KEY_UNREAD(normalizePhone(phone)));`
);
console.log('[OK] KEY_UNREAD normalizado');

if (code === orig) {
  console.log('\n[AVISO] Nenhuma mudanca feita!');
} else {
  fs.writeFileSync(path, code);
  console.log('\n[SUCESSO] index.js atualizado!');
  console.log(`[INFO] ${orig.length} -> ${code.length} bytes`);
}
