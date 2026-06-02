const {createClient}=require('redis');
(async()=>{
  const r=createClient({url:'redis://redis:6379'});
  await r.connect();
  
  // Verificar alguns status
  const ids=[
    'wa_5532998462122_GILMARA_GABRIELA_DE_',
    'wa_5532988394247_CAROLINE_MARIANO_TOM',
    'wa_5532999305665_CATIANE_LEITE_DOS_SA',
    'wa_5532998137862_GILMAR_LUCINDO_RODRI',
    'wa_5532984948674_ANGELA_MARIA_BERNARD',
    'wa_5532988049090_ADEMAR_CAMERINO'
  ];
  
  console.log('=== STATUS NO REDIS ===');
  for(const id of ids){
    const s=await r.get('agenda:status:'+id);
    console.log(`${id} => ${s}`);
  }

  // Verificar como o all-status endpoint le
  const allKeys = await r.keys('agenda:status:*');
  let agendados=0, resolvidos=0, problemas=0, entregues=0;
  for(const k of allKeys){
    const v = await r.get(k);
    if(!v) continue;
    const obj = JSON.parse(v);
    if(obj.status==='agendado') agendados++;
    else if(obj.status==='resolvido') resolvidos++;
    else if(obj.status==='problema-aberto') problemas++;
    else if(obj.status==='entregue') entregues++;
  }
  console.log(`\n=== TOTAIS ===`);
  console.log(`agendado: ${agendados}`);
  console.log(`resolvido: ${resolvidos}`);
  console.log(`problema-aberto: ${problemas}`);
  console.log(`entregue: ${entregues}`);
  console.log(`total keys: ${allKeys.length}`);

  // Verificar se o statusOfs no client list é diferente
  const cRaw = await r.get('agenda:clients');
  const clients = cRaw ? JSON.parse(cRaw) : [];
  const gilmara = clients.find(c => c.id === 'wa_5532998462122_GILMARA_GABRIELA_DE_');
  console.log(`\n=== CLIENT LIST ENTRY (Gilmara) ===`);
  console.log(JSON.stringify(gilmara, null, 2));

  await r.quit();
})();
