const { createClient } = require('redis');
const http = require('http');

async function main() {
  const r = createClient({ url: 'redis://redis:6379' });
  await r.connect();

  // Carregar config de botões
  let btnMsgs = null;
  try {
    const cfgRaw = await r.get('agenda:button-config');
    btnMsgs = cfgRaw ? JSON.parse(cfgRaw) : null;
  } catch(e) {}
  if (!btnMsgs) {
    btnMsgs = {
      'agendar': 'Certo, NOME! Por favor, nos informe uma data e horário para agendarmos a retirada do equipamento.',
      'ja devolvi': 'Obrigado pela informação, NOME! Vamos verificar e atualizar nosso sistema.',
      'sim, confirmo': 'Perfeito, NOME! Seu atendimento está confirmado. Nossa equipe estará no local conforme agendado. Obrigado!',
    };
  }

  const BUTTON_STATUS = {
    'agendar': 'agendado',
    'já devolvi': 'resolvido', 'ja devolvi': 'resolvido',
    'sim, confirmo': 'confirmado',
    'preciso reagendar': 'reagendado',
    'cancelar': 'nao-atendido',
    'sim, tudo certo': 'satisfeito',
    'não, tenho problema': 'problema-aberto', 'nao, tenho problema': 'problema-aberto',
    'quero falar com alguém': 'problema-aberto', 'quero falar com alguem': 'problema-aberto',
  };

  // Lista dos 36 pendentes
  const pendingRaw = await r.get('_pending_reprocess');
  const pending = JSON.parse(pendingRaw);
  
  let processed = 0;
  let skipped = 0;

  for (const item of pending) {
    const { phone, text, clientId } = item;
    const btnKey = text.toLowerCase().trim();
    
    // Buscar nome do cliente
    const cRaw = await r.get('agenda:clients');
    const cList = cRaw ? JSON.parse(cRaw) : [];
    const cData = cList.find(c => c.id === clientId) || {};
    const firstName = (cData.nome || 'Cliente').split(' ')[0];
    const firstName2 = firstName.charAt(0).toUpperCase() + firstName.slice(1).toLowerCase();

    // Verificar se é botão conhecido
    const btnStatus = BUTTON_STATUS[btnKey];
    
    if (btnStatus) {
      // FLUXO BOTÃO: atualizar status + enviar resposta
      const replyTemplate = btnMsgs[btnKey] || btnMsgs['agendar'] || 'Obrigado pelo retorno!';
      const replyMsg = replyTemplate.replace(/NOME/g, firstName2);
      
      // Atualizar status
      await r.set(`agenda:status:${clientId}`, JSON.stringify({
        status: btnStatus,
        obs: `Botão reprocessado: "${text}"`,
        updatedAt: new Date().toISOString()
      }));

      // Enviar resposta via API local
      const body = JSON.stringify({ phone, text: replyMsg, clientId });
      await new Promise((resolve, reject) => {
        const req = http.request({
          hostname: 'localhost', port: 3001, path: '/send?apikey=svoboda-agenda-2025',
          method: 'POST', headers: { 'Content-Type': 'application/json' }
        }, res => {
          let data = '';
          res.on('data', c => data += c);
          res.on('end', () => { resolve(data); });
        });
        req.on('error', reject);
        req.write(body);
        req.end();
      });

      console.log(`[BOTAO] ${phone} | ${firstName2} | "${text}" -> ${btnStatus} | Resposta enviada`);
      processed++;
    } else {
      // TEXTO LIVRE: apenas atualizar status para "problema-aberto" para review manual
      // Não enviar mensagem automática para textos livres
      await r.set(`agenda:status:${clientId}`, JSON.stringify({
        status: 'problema-aberto',
        obs: `Resposta livre: "${text.slice(0, 80)}"`,
        updatedAt: new Date().toISOString()
      }));
      console.log(`[LIVRE] ${phone} | ${firstName2} | "${text.slice(0, 60)}" -> problema-aberto (review manual)`);
      skipped++;
    }

    // Delay entre envios (1.5s)
    await new Promise(res => setTimeout(res, 1500));
  }

  console.log(`\n[RESULTADO] Processados: ${processed} botões | ${skipped} texto livre (problema-aberto)`);
  await r.quit();
}

main().catch(e => { console.error(e); process.exit(1); });
