const fs = require('fs');
const path = '/docker/whatsapp-agenda/backend/index.js';

let code = fs.readFileSync(path, 'utf8');
let changes = 0;

// ═══════════════════════════════════════════════
// FIX 1: /send — não sobrescrever status protegidos
// ═══════════════════════════════════════════════
const oldSend = `    if (clientId) {
      await setStatus(clientId, 'entregue', 'Mensagem enviada via painel');
    }

    res.json({ ok: true, result });`;

const newSend = `    if (clientId) {
      // BLINDAGEM: só seta "entregue" se status atual não for protegido
      const _cur = await getStatus(clientId);
      const _prot = ['agendado','resolvido','confirmado','satisfeito','reagendado','problema-aberto','nao-atendido'];
      if (!_prot.includes(_cur.status)) {
        await setStatus(clientId, 'entregue', 'Mensagem enviada via painel');
      }
    }

    res.json({ ok: true, result });`;

if (code.includes(oldSend)) {
  code = code.replace(oldSend, newSend);
  changes++;
  console.log('[FIX 1] /send: status protegido ✓');
} else {
  console.log('[FIX 1] /send: padrão não encontrado (já aplicado?)');
}

// ═══════════════════════════════════════════════
// FIX 2: normalizePhone em endpoints restantes
// ═══════════════════════════════════════════════

// 2a. /send-reply — normalizar appendMsg
const oldReply = `await appendMsg(phone.replace(/\\D/g, ''),`;
const oldReplyCount = (code.match(new RegExp(oldReply.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length;
if (oldReplyCount > 0) {
  code = code.replace(new RegExp(oldReply.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), `await appendMsg(normalizePhone(phone),`);
  changes++;
  console.log(`[FIX 2a] appendMsg normalizado (${oldReplyCount} ocorrências) ✓`);
}

// 2b. KEY_UNREAD leituras — no /unread endpoint
const oldUnread = `const val = await redis.get(KEY_UNREAD(phone));`;
if (code.includes(oldUnread)) {
  code = code.replace(oldUnread, `const val = await redis.get(KEY_UNREAD(normalizePhone(phone)));`);
  changes++;
  console.log('[FIX 2b] KEY_UNREAD leitura normalizada ✓');
}

// 2c. KEY_UNREAD no conversations
const oldConvUnread = `const ur = await redis.get(KEY_UNREAD(phone))`;
if (code.includes(oldConvUnread)) {
  code = code.replace(new RegExp(oldConvUnread.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), `const ur = await redis.get(KEY_UNREAD(normalizePhone(phone)))`);
  changes++;
  console.log('[FIX 2c] KEY_UNREAD conversations normalizado ✓');
}

// 2d. KEY_PHONE_ID no /send normalizar (já pode ter sido feito)
const oldP2I = `await redis.set(KEY_PHONE_ID(number), clientId);`;
if (code.includes(oldP2I)) {
  code = code.replace(oldP2I, `await redis.set(KEY_PHONE_ID(normalizePhone(number)), clientId);`);
  changes++;
  console.log('[FIX 2d] KEY_PHONE_ID /send normalizado ✓');
}

// ═══════════════════════════════════════════════
// FIX 4: /send-bulk — proteger status existentes
// ═══════════════════════════════════════════════
const oldBulkStatus = `await setStatus(cid, 'entregue', 'Disparo em massa realizado');`;
if (code.includes(oldBulkStatus)) {
  code = code.replace(oldBulkStatus, `// BLINDAGEM: não sobrescrever status já processados
          const _bulkCur = await getStatus(cid);
          const _bulkProt = ['agendado','resolvido','confirmado','satisfeito','reagendado','problema-aberto','nao-atendido'];
          if (!_bulkProt.includes(_bulkCur.status)) {
            await setStatus(cid, 'entregue', 'Disparo em massa realizado');
          }`);
  changes++;
  console.log('[FIX 4] /send-bulk: status protegido ✓');
} else {
  // Tentar variação
  const alt = `await setStatus(cid, 'entregue'`;
  if (code.includes(alt)) {
    console.log('[FIX 4] /send-bulk: padrão alternativo encontrado, buscando...');
  } else {
    console.log('[FIX 4] /send-bulk: verificar manualmente');
  }
}

fs.writeFileSync(path, code);
console.log(`\n[RESULTADO] ${changes} fixes aplicados | ${code.length} bytes`);
