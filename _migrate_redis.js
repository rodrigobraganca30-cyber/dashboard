const { createClient } = require('redis');

async function migrate() {
  const r = createClient({ url: 'redis://redis:6379' });
  await r.connect();
  console.log('[OK] Redis conectado');

  // 1. Migrar agenda:msgs:*
  const msgKeys = await r.keys('agenda:msgs:*');
  let migrated = 0, merged = 0;

  for (const key of msgKeys) {
    const phone = key.replace('agenda:msgs:', '');
    const digits = phone.replace(/\D/g, '');

    if (digits.length === 12 && digits.startsWith('55')) {
      const correct = digits.slice(0, 4) + '9' + digits.slice(4);
      const correctKey = `agenda:msgs:${correct}`;

      const oldRaw = await r.get(key);
      const oldMsgs = oldRaw ? JSON.parse(oldRaw) : [];
      const existRaw = await r.get(correctKey);
      const existMsgs = existRaw ? JSON.parse(existRaw) : [];

      if (existMsgs.length > 0) {
        const all = [...existMsgs, ...oldMsgs];
        const seen = new Set();
        const unique = all.filter(m => {
          const sig = `${m.from||''}${m.text||''}${m.ts||0}`;
          if (seen.has(sig)) return false;
          seen.add(sig);
          return true;
        }).sort((a, b) => (a.ts || 0) - (b.ts || 0));
        await r.set(correctKey, JSON.stringify(unique));
        await r.del(key);
        merged++;
        console.log(`  MERGED: ${phone} -> ${correct} (${oldMsgs.length}+${existMsgs.length}=${unique.length})`);
      } else {
        await r.rename(key, correctKey);
        migrated++;
        console.log(`  RENAMED: ${phone} -> ${correct} (${oldMsgs.length} msgs)`);
      }
    }
  }
  console.log(`\n[OK] msgs: ${migrated} renomeadas, ${merged} mescladas`);

  // 2. Migrar agenda:phone2id:*
  const p2iKeys = await r.keys('agenda:phone2id:*');
  let p2i = 0;
  for (const key of p2iKeys) {
    const phone = key.replace('agenda:phone2id:', '');
    const digits = phone.replace(/\D/g, '');
    if (digits.length === 12 && digits.startsWith('55')) {
      const correct = digits.slice(0, 4) + '9' + digits.slice(4);
      const ck = `agenda:phone2id:${correct}`;
      const val = await r.get(key);
      if (!(await r.exists(ck))) {
        await r.rename(key, ck);
      } else {
        await r.del(key);
      }
      p2i++;
    }
  }
  console.log(`[OK] phone2id: ${p2i} migradas`);

  // 3. Migrar agenda:unread:*
  const urKeys = await r.keys('agenda:unread:*');
  let ur = 0;
  for (const key of urKeys) {
    const phone = key.replace('agenda:unread:', '');
    const digits = phone.replace(/\D/g, '');
    if (digits.length === 12 && digits.startsWith('55')) {
      const correct = digits.slice(0, 4) + '9' + digits.slice(4);
      const ck = `agenda:unread:${correct}`;
      const oldVal = parseInt(await r.get(key) || '0');
      const exVal = parseInt(await r.get(ck) || '0');
      await r.set(ck, String(oldVal + exVal));
      await r.del(key);
      ur++;
    }
  }
  console.log(`[OK] unread: ${ur} migradas`);

  // 4. Verificar
  const remaining = (await r.keys('agenda:msgs:55*')).filter(k => {
    const p = k.replace('agenda:msgs:', '');
    return p.length === 12;
  }).length;
  console.log(`\n[RESULTADO] Chaves orfas restantes: ${remaining}`);
  console.log('[SUCESSO] Migracao concluida!');

  await r.quit();
}

migrate().catch(e => { console.error('ERRO:', e.message); process.exit(1); });
