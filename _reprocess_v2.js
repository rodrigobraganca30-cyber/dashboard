const { createClient } = require('redis');
const http = require('http');

function sendMsg(phone, text) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ phone, text });
    const req = http.request({
      hostname: 'localhost', port: 3001, path: '/send?apikey=svoboda-agenda-2025',
      method: 'POST', headers: { 'Content-Type': 'application/json' }
    }, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => resolve(data));
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function main() {
  const r = createClient({ url: 'redis://redis:6379' });
  await r.connect();

  let btnMsgs = null;
  try {
    const cfgRaw = await r.get('agenda:button-config');
    btnMsgs = cfgRaw ? JSON.parse(cfgRaw) : null;
  } catch(e) {}
  if (!btnMsgs) {
    btnMsgs = {
      'agendar': 'Certo, NOME! Por favor, nos informe uma data e horário para agendarmos a retirada do equipamento.',
      'ja devolvi': 'Obrigado pela informação, NOME! Vamos verificar e atualizar nosso sistema.',
    };
  }

  const BUTTON_STATUS = {
    'agendar': 'agendado',
    'já devolvi': 'resolvido', 'ja devolvi': 'resolvido',
  };

  const pendingRaw = await r.get('_pending_reprocess');
  const pending = JSON.parse(pendingRaw);
  
  let processed = 0, skipped = 0;

  for (const item of pending) {
    const { phone, text, clientId } = item;
    const btnKey = text.toLowerCase().trim();
    
    const cRaw = await r.get('agenda:clients');
    const cList = cRaw ? JSON.parse(cRaw) : [];
    const cData = cList.find(c => c.id === clientId) || {};
    const firstName = (cData.nome || 'Cliente').split(' ')[0];
    const firstName2 = firstName.charAt(0).toUpperCase() + firstName.slice(1).toLowerCase();

    const btnStatus = BUTTON_STATUS[btnKey];
    
    if (btnStatus) {
      // 1. Enviar resposta PRIMEIRO (sem clientId para não sobrescrever status)
      const replyTemplate = btnMsgs[btnKey] || 'Obrigado pelo retorno!';
      const replyMsg = replyTemplate.replace(/NOME/g, firstName2);
      await sendMsg(phone, replyMsg);
      
      // 2. DEPOIS setar o status correto (sobrescreve o "entregue" do /send)
      await r.set(`agenda:status:${clientId}`, JSON.stringify({
        status: btnStatus,
        obs: `Botão: "${text}"`,
        updatedAt: new Date().toISOString()
      }));

      console.log(`[BOTAO] ${phone} | ${firstName2} | "${text}" -> ${btnStatus}`);
      processed++;
    } else {
      // Texto livre - setar problema-aberto
      await r.set(`agenda:status:${clientId}`, JSON.stringify({
        status: 'problema-aberto',
        obs: `Resposta livre: "${text.slice(0, 80)}"`,
        updatedAt: new Date().toISOString()
      }));
      console.log(`[LIVRE] ${phone} | ${firstName2} | "${text.slice(0, 60)}" -> problema-aberto`);
      skipped++;
    }

    await new Promise(res => setTimeout(res, 1500));
  }

  console.log(`\n[RESULTADO] ${processed} botoes + ${skipped} texto livre`);
  
  // Verificar
  let ag=0, re=0, pa=0;
  for (const item of pending) {
    const s = await r.get(`agenda:status:${item.clientId}`);
    const obj = s ? JSON.parse(s) : {};
    if(obj.status==='agendado') ag++;
    else if(obj.status==='resolvido') re++;
    else if(obj.status==='problema-aberto') pa++;
  }
  console.log(`[CHECK] agendado=${ag} resolvido=${re} problema-aberto=${pa}`);

  await r.quit();
}

main().catch(e => { console.error(e); process.exit(1); });
