filepath = "/docker/dashboard/html/index.html"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

# 1. Ampliar accept
old_accept = 'accept=".csv,.xlsx,.xls" multiple'
new_accept = 'accept=".csv,.xlsx,.xls,.ods,.tsv" multiple'
if old_accept in content:
    content = content.replace(old_accept, new_accept)
    changes += 1
    print("1. OK - accept ampliado")

# 2. Remover filtro de status na waParseCSV
old_filter = """      if(!st) continue;
      var isConclu = st.indexOf('conclu')>=0 && st.indexOf('nao conclu')<0 && st.indexOf('n\u00e3o conclu')<0;
      if(st.indexOf('pendente')<0 && st.indexOf('agendado')<0 && st.indexOf('pending')<0 && st.indexOf('nao iniciado')<0 && !isConclu) continue;"""
new_filter = "      // Filtro de status removido - aceita todas as linhas"
if old_filter in content:
    content = content.replace(old_filter, new_filter)
    changes += 1
    print("2. OK - filtro de status removido")
else:
    print("2. SKIP - filtro nao encontrado")
    # tentar encontrar
    if "isConclu" in content:
        print("  'isConclu' existe")
    if "nao iniciado" in content:
        print("  'nao iniciado' existe")

# 3. Ampliar nomes de coluna na idx
old_nome = "var iNome=idx('nome','name','cliente');"
new_nome = "var iNome=idx('nome','name','cliente','assinante','titular','razao','contratante');"
if old_nome in content:
    content = content.replace(old_nome, new_nome)
    changes += 1
    print("3. OK - nomes de coluna ampliados")

old_tel = "var iTel=idx('telefone celular','celular','telefone','phone','tel');"
new_tel = "var iTel=idx('telefone celular','celular','telefone','phone','tel','fone','contato','whatsapp','wpp','numero');"
if old_tel in content:
    content = content.replace(old_tel, new_tel)
    changes += 1
    print("4. OK - telefone ampliado")

old_end = "var iEnd=idx('endere\u00e7o','endereco','logradouro','address');"
new_end = "var iEnd=idx('endere\u00e7o','endereco','logradouro','address','rua','local');"
if old_end in content:
    content = content.replace(old_end, new_end)
    changes += 1
    print("5. OK - endereco ampliado")

old_cid = "var iCid=idx('cidade','city');"
new_cid = "var iCid=idx('cidade','city','municipio','localidade');"
if old_cid in content:
    content = content.replace(old_cid, new_cid)
    changes += 1
    print("6. OK - cidade ampliada")

# 4. Alterar waHandleFile para mostrar modal
old_handle = "if(ext==='csv'){var r=new FileReader();r.onload=function(ev){waParseCSV(ev.target.result)};r.readAsText(file,'UTF-8')}"
new_handle = "if(ext==='csv'||ext==='tsv'){var r=new FileReader();r.onload=function(ev){window._waPendingCSV=ev.target.result;try{waShowMappingModal(ev.target.result)}catch(err){alert('Erro: '+err.message);waParseCSV(ev.target.result)}};r.readAsText(file,'UTF-8')}"
if old_handle in content:
    content = content.replace(old_handle, new_handle)
    changes += 1
    print("7. OK - CSV handler com modal")

# Para XLSX tambem adicionar modal
old_xlsx_parse = "waParseCSV(XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]))"
new_xlsx_parse = "var csv=XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]);window._waPendingCSV=csv;try{waShowMappingModal(csv)}catch(err){waParseCSV(csv)}"
count_xlsx = content.count(old_xlsx_parse)
if count_xlsx > 0:
    content = content.replace(old_xlsx_parse, new_xlsx_parse)
    changes += 1
    print(f"8. OK - XLSX handler com modal ({count_xlsx}x)")

# 5. Adicionar funcao waShowMappingModal antes de waParseCSV
modal_code = """
  // ── MODAL DE MAPEAMENTO ──
  function waShowMappingModal(csvText){
    var allRows=waCSVtoRows(csvText);
    if(allRows.length<2) return waParseCSV(csvText);
    var headers=allRows[0].map(function(h){return h.trim()});
    var headersLower=headers.map(function(h){return h.toLowerCase()});
    function idxF(){for(var i=0;i<arguments.length;i++){for(var j=0;j<headersLower.length;j++){if(headersLower[j].indexOf(arguments[i])>=0)return j}}return -1}
    var fields=[
      {key:'nome',label:'Nome/Cliente',auto:idxF('nome','name','cliente','assinante','titular'),req:1},
      {key:'phone',label:'Telefone',auto:idxF('telefone celular','celular','telefone','phone','tel','contato','whatsapp','numero'),req:1},
      {key:'cidade',label:'Cidade',auto:idxF('cidade','city','municipio','localidade')},
      {key:'data',label:'Data',auto:idxF('data','date','dia','agendamento')},
      {key:'endereco',label:'Endereco',auto:idxF('endereco','address','logradouro','rua')},
      {key:'intervalo',label:'Turno',auto:idxF('intervalo de tempo','intervalo','turno','horario','janela')},
      {key:'tipo',label:'Tipo',auto:idxF('tipo de atividade','tipo','type')},
      {key:'status',label:'Status',auto:idxF('status da atividade','status','estado','situacao')}
    ];
    var preview=[];for(var p=1;p<Math.min(allRows.length,6);p++)preview.push(allRows[p]);
    var modal=document.getElementById('wa-mapping-modal');
    if(!modal){modal=document.createElement('div');modal.id='wa-mapping-modal';document.body.appendChild(modal)}
    var fhtml='';
    for(var f=0;f<fields.length;f++){
      var fl=fields[f];var oh='<option value="-1">(nao mapear)</option>';
      for(var j=0;j<headers.length;j++)oh+='<option value="'+j+'"'+(j===fl.auto?' selected':'')+'>'+headers[j]+'</option>';
      fhtml+='<div style="margin-bottom:6px"><div style="font-size:11px;color:#94a3b8;margin-bottom:3px">'+fl.label+(fl.req?' <b style="color:#ef4444">*</b>':'')+'</div>';
      fhtml+='<select id="wamap-'+fl.key+'" style="width:100%;background:#1a1e28;border:1px solid #22273a;border-radius:6px;color:#e2e8f0;padding:6px 8px;font-size:12px">'+oh+'</select></div>';
    }
    var phtml='<table style="width:100%;font-size:10px;border-collapse:collapse;margin-top:8px"><thead><tr>';
    phtml+='<th style="padding:3px 5px;border-bottom:1px solid #22273a;color:#475569">#</th>';
    for(var h=0;h<Math.min(headers.length,7);h++)phtml+='<th style="padding:3px 5px;border-bottom:1px solid #22273a;color:#475569;text-align:left">'+headers[h].substring(0,12)+'</th>';
    phtml+='</tr></thead><tbody>';
    for(var r=0;r<preview.length;r++){
      phtml+='<tr><td style="padding:2px 5px;border-bottom:1px solid #22273a;color:#475569">'+(r+1)+'</td>';
      for(var c=0;c<Math.min(preview[r].length,7);c++)phtml+='<td style="padding:2px 5px;border-bottom:1px solid #22273a;color:#94a3b8">'+preview[r][c].substring(0,18)+'</td>';
      phtml+='</tr>';
    }
    phtml+='</tbody></table>';
    modal.style.cssText='position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:9999;display:flex;align-items:center;justify-content:center;padding:20px;backdrop-filter:blur(4px)';
    modal.innerHTML='<div style="background:#13161e;border:1px solid #22273a;border-radius:16px;padding:24px;width:100%;max-width:700px;max-height:90vh;overflow-y:auto">'
      +'<div style="font-family:Syne,sans-serif;font-weight:700;font-size:16px;margin-bottom:4px">Mapeamento de Colunas</div>'
      +'<div style="font-size:12px;color:#475569;margin-bottom:14px">'+headers.length+' colunas, '+(allRows.length-1)+' linhas. Confirme o mapeamento:</div>'
      +'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">'+fhtml+'</div>'
      +'<div style="margin-top:10px;font-size:11px;color:#475569">Preview ('+preview.length+' linhas)</div>'
      +'<div style="overflow-x:auto">'+phtml+'</div>'
      +'<div style="display:flex;gap:10px;margin-top:16px">'
      +'<button onclick="waApplyMapping()" style="flex:1;padding:10px;background:#3b82f6;color:#fff;border:none;border-radius:8px;font-size:13px;cursor:pointer">Importar '+(allRows.length-1)+' registros</button>'
      +'<button onclick="document.getElementById(\\'wa-mapping-modal\\').style.display=\\'none\\'" style="padding:10px 18px;background:transparent;border:1px solid #22273a;color:#94a3b8;border-radius:8px;font-size:13px;cursor:pointer">Cancelar</button>'
      +'</div></div>';
  }

  function waApplyMapping(){
    var csvText=window._waPendingCSV;if(!csvText)return;
    var mapping={};
    var keys=['nome','phone','cidade','data','endereco','intervalo','tipo','status'];
    for(var k=0;k<keys.length;k++){var sel=document.getElementById('wamap-'+keys[k]);mapping[keys[k]]=sel?parseInt(sel.value):-1}
    if(mapping.nome<0&&mapping.phone<0){alert('Mapeie pelo menos Nome ou Telefone');return}
    document.getElementById('wa-mapping-modal').style.display='none';
    var allRows=waCSVtoRows(csvText);
    function g(row,i){return i>=0&&i<row.length&&row[i]?row[i].trim():''}
    var list=[];
    for(var i=1;i<allRows.length;i++){
      var row=allRows[i];if(row.length<2)continue;
      var nome=g(row,mapping.nome)||'Cliente';
      var tel=g(row,mapping.phone);
      var cleanTel=(tel||'').replace(/\\D/g,'');
      list.push({id:'wa_'+cleanTel+'_'+nome.replace(/ +/g,'_').slice(0,20),nome:nome,phone:tel,data:g(row,mapping.data),cidade:g(row,mapping.cidade),tipo:g(row,mapping.tipo),endereco:g(row,mapping.endereco),intervalo:g(row,mapping.intervalo),statusOfs:g(row,mapping.status)>=0?g(row,mapping.status):''});
    }
    if(!list.length)return;
    waClients=waClients.concat(list);
    var unique=[];var ids=new Set();
    for(var z=waClients.length-1;z>=0;z--){if(!ids.has(waClients[z].id)){unique.unshift(waClients[z]);ids.add(waClients[z].id)}}
    waClients=unique;
    waSaveClients();_chatSaveNomesToCache();waRefreshUI();
    if(WA_BACKEND)waSyncStatus();
  }

"""

# Inserir antes de waParseCSV
marker = "  function waParseCSV(text){"
if marker in content:
    content = content.replace(marker, modal_code + marker)
    changes += 1
    print("9. OK - modal de mapeamento inserido")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nTOTAL: {changes} mudancas")
