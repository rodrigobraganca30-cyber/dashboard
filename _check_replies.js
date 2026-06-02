const { createClient } = require('redis');

async function main() {
  const r = createClient({ url: 'redis://redis:6379' });
  await r.connect();

  const phones = [
    "5532988049090","5532984008276","5532998140110","5532998462122",
    "5532988810434","5532988394247","5532988085574","5532988635314",
    "5532998689219","5532984124871","5532998021996","5532987032505",
    "5532991000462","5532998826446","5532988472203","5532999203519",
    "5532998411778","5532988740858","5532988038656","5532998620599",
    "5531992158907","5532998808831","5532999993131","5532998476852",
    "5532998826508","5532998076473","5532988234375","5532999741813",
    "5532998195448","5532999960645","5532999305665","5532999266350",
    "5532984519514","5532998137862","5532999323878","5532998006698",
    "5532998028873","5532984948674"
  ];

  let needsProcessing = [];

  for (const phone of phones) {
    const raw = await r.get(`agenda:msgs:${phone}`);
    const msgs = raw ? JSON.parse(raw) : [];
    
    // Pegar ultima mensagem do cliente
    const clientMsgs = msgs.filter(m => m.from === 'client');
    if (clientMsgs.length === 0) continue;
    
    const lastClient = clientMsgs[clientMsgs.length - 1];
    
    // Verificar se o bot ja respondeu apos a ultima msg do cliente
    const lastClientIdx = msgs.lastIndexOf(lastClient);
    const afterMsgs = msgs.slice(lastClientIdx + 1);
    const botReplied = afterMsgs.some(m => m.from === 'me');
    
    // Buscar clientId
    const clientId = await r.get(`agenda:phone2id:${phone}`);
    
    // Buscar status atual
    const statusRaw = await r.get(`agenda:status:${clientId || ''}`);
    const status = statusRaw ? JSON.parse(statusRaw) : {};
    
    console.log(`${phone} | "${lastClient.text}" | botReplied=${botReplied} | clientId=${clientId || 'N/A'} | status=${status.status || '?'}`);
    
    if (!botReplied && clientId) {
      needsProcessing.push({ phone, text: lastClient.text, clientId });
    }
  }

  console.log(`\n--- PRECISAM PROCESSAMENTO: ${needsProcessing.length} ---`);
  for (const p of needsProcessing) {
    console.log(`  ${p.phone}: "${p.text}" (${p.clientId})`);
  }

  // Salvar lista para processamento
  await r.set('_pending_reprocess', JSON.stringify(needsProcessing));
  
  await r.quit();
}

main().catch(e => { console.error(e); process.exit(1); });
