# -*- coding: utf-8 -*-
"""Patch para injetar modal de importacao no HTML live da VPS"""
import re

html = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()
changes = 0

# 1. EXPAND accept
old_accept = 'accept=".csv,.xlsx,.xls"'
new_accept = 'accept=".csv,.xlsx,.xls,.xlsb,.ods,.tsv,.txt"'
if old_accept in html:
    html = html.replace(old_accept, new_accept)
    print('[+] 1/3 accept expandido')
    changes += 1
elif new_accept in html:
    print('[=] 1/3 accept ja expandido')
else:
    print('[!] 1/3 accept nao encontrado')

# 2. MODAL HTML
if 'wa-import-modal' not in html:
    modal_html = (
        '\n<!-- MODAL DE IMPORTACAO -->\n'
        '<div id="wa-import-modal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);z-index:10000;align-items:center;justify-content:center">\n'
        '<div style="background:#0d1117;border:1px solid #1c2237;border-radius:16px;width:560px;max-width:95%;max-height:90vh;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 25px 60px rgba(0,0,0,0.6)">\n'
        '<div style="padding:20px 24px;border-bottom:1px solid #1c2237;display:flex;justify-content:space-between;align-items:center;background:linear-gradient(135deg,#0d1117,#111520)">\n'
        '<div style="display:flex;align-items:center;gap:12px">\n'
        '<span style="font-size:24px">\U0001f4ca</span>\n'
        '<div>\n'
        '<div style="font-weight:800;font-size:16px;color:#e2e8f0">Resultado da Importa\u00e7\u00e3o</div>\n'
        '<div style="font-size:11px;color:#64748b;font-family:var(--font-mono)" id="wa-imp-filename">arquivo.csv</div>\n'
        '</div></div>\n'
        '<button onclick="waCloseImportModal()" style="background:transparent;border:none;color:#94a3b8;cursor:pointer;font-size:18px">\u2716</button>\n'
        '</div>\n'
        '<div style="padding:20px 24px;overflow-y:auto;flex:1" id="wa-imp-body">\n'
        '<div style="font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px">Mapeamento de Colunas</div>\n'
        '<div id="wa-imp-rows" style="display:flex;flex-direction:column;gap:8px"></div>\n'
        '</div>\n'
        '<div style="padding:16px 24px;border-top:1px solid #1c2237;display:flex;justify-content:space-between;align-items:center;background:#0a0d14">\n'
        '<label style="display:flex;align-items:center;gap:8px;font-size:12px;color:#94a3b8;cursor:pointer"><input type="checkbox" id="wa-imp-remember" style="accent-color:#25d366" checked> Lembrar mapeamento</label>\n'
        '<div style="display:flex;gap:10px">\n'
        '<button class="wa-cfg-btn secondary" onclick="waCloseImportModal()">Cancelar</button>\n'
        '<button class="wa-cfg-btn" onclick="waFinishImport()" id="wa-imp-confirm" style="min-width:180px">\u2705 Importar 0 linhas</button>\n'
        '</div></div></div></div>\n'
        '<!-- FIM MODAL IMPORTACAO -->\n'
    )
    idx = html.rfind('</body>')
    if idx < 0:
        idx = html.rfind('</html>')
    if idx > 0:
        html = html[:idx] + modal_html + html[idx:]
        print('[+] 2/3 Modal HTML injetado')
        changes += 1
    else:
        print('[!] 2/3 Ponto de insercao nao encontrado')
else:
    print('[=] 2/3 Modal ja existe')

# 3. JS FUNCTIONS
new_js = r'''
  var WA_COL_ALIASES = {
    nome:['nome','name','cliente','customer','assinante','subscriber','razao social','contato','nome do cliente','nome completo','responsavel','titular','beneficiario','nome_cliente','full_name'],
    phone:['telefone celular','celular','telefone','phone','tel','mobile','fone','whatsapp','contato tel','telefone de contato','cel','phone_number','num_telefone','fone_contato','cellphone','tel_cel'],
    data:['data','date','data agendamento','dt','data da atividade','data atividade','data visita','agendado para','agenda','dt_agenda','data_agendamento','scheduled','data prevista','data programada'],
    cidade:['cidade','city','municipio','localidade','regional','mun','town','regiao'],
    status:['status da atividade','status','estado','state','status ofs','status os','status_ativ','conclusao','resultado'],
    endereco:['endereco','logradouro','address','rua','local','end','endereco completo','morada','localizacao','end_completo'],
    intervalo:['intervalo de tempo','intervalo','turno','slot','horario','hora','janela','faixa horaria','janela de tempo','time slot','hora inicio','hora_ini','hora_fim','period'],
    tipo:['tipo de atividade','tipo','servico','type','categoria','atividade','tipo servico','tipo os','tipo_ativ','service','natureza']
  };
  var WA_COL_LABELS={nome:'Nome do Cliente',phone:'Telefone',data:'Data',cidade:'Cidade',status:'Status',endereco:'Endere\u00e7o',intervalo:'Intervalo/Hor\u00e1rio',tipo:'Tipo de Atividade'};
  var WA_COL_ICONS={nome:'\ud83d\udc64',phone:'\ud83d\udcf1',data:'\ud83d\udcc5',cidade:'\ud83c\udfd9\ufe0f',status:'\ud83d\udccb',endereco:'\ud83d\udccd',intervalo:'\u23f0',tipo:'\ud83d\udd27'};
  var WA_COL_REQUIRED=['nome','phone'];
  var _waImpState=null;

  function _waAutoMap(headers){
    var mapping={};var usedCols=new Set();
    var hdrKey=headers.join('|').toLowerCase();
    try{var saved=JSON.parse(localStorage.getItem('wa_col_mapping_v2')||'{}');
      if(saved._key===hdrKey&&saved.map){var allValid=true;for(var f in saved.map){if(saved.map[f]>=0&&saved.map[f]<headers.length)mapping[f]=saved.map[f];else allValid=false;}
      if(allValid&&Object.keys(mapping).length>0)return mapping;mapping={};}}catch(ex){}
    var headersLow=headers.map(function(h){return h.toLowerCase().trim()});
    var fields=Object.keys(WA_COL_ALIASES);
    for(var fi=0;fi<fields.length;fi++){var field=fields[fi];var aliases=WA_COL_ALIASES[field];var bestIdx=-1;
      for(var ai=0;ai<aliases.length;ai++){var alias=aliases[ai];
        for(var hi=0;hi<headersLow.length;hi++){if(usedCols.has(hi))continue;if(headersLow[hi]===alias){bestIdx=hi;break;}}
        if(bestIdx>=0)break;
        for(var hi2=0;hi2<headersLow.length;hi2++){if(usedCols.has(hi2))continue;if(headersLow[hi2].indexOf(alias)>=0){if(field==='tipo')bestIdx=hi2;else{bestIdx=hi2;break;}}}
        if(bestIdx>=0&&field!=='tipo')break;}
      if(bestIdx>=0){mapping[field]=bestIdx;usedCols.add(bestIdx);}}
    return mapping;}

  function waShowImportModal(){
    if(!_waImpState)return;var s=_waImpState;
    var modal=document.getElementById('wa-import-modal');
    document.getElementById('wa-imp-filename').textContent=s.filename+' ('+s.rows.length+' linhas)';
    var container=document.getElementById('wa-imp-rows');container.innerHTML='';
    var fields=Object.keys(WA_COL_ALIASES);
    for(var fi=0;fi<fields.length;fi++){var field=fields[fi];var mapped=s.mapping[field];
      var isOk=mapped!==undefined&&mapped>=0;var isReq=WA_COL_REQUIRED.indexOf(field)>=0;
      var icon=isOk?'\u2705':'\u274c';
      var row=document.createElement('div');
      row.style.cssText='display:flex;align-items:center;gap:10px;padding:10px 12px;background:#111520;border:1px solid '+(isOk?'#22d3a022':'#ff4d6d22')+';border-radius:10px;transition:all 0.2s';
      var selectOpts='<option value="-1"'+(isOk?'':'selected')+'>\u2014 N\u00e3o mapear \u2014</option>';
      for(var hi=0;hi<s.headers.length;hi++){var sel=(mapped===hi)?'selected':'';selectOpts+='<option value="'+hi+'" '+sel+'>'+s.headers[hi]+'</option>';}
      row.innerHTML='<span style="font-size:16px;width:24px;text-align:center">'+WA_COL_ICONS[field]+'</span>'+'<span style="font-size:13px;font-weight:700;color:#e2e8f0;min-width:140px">'+WA_COL_LABELS[field]+(isReq?' <span style="color:#ff4d6d">*</span>':'')+'</span>'+'<span style="font-size:14px;width:20px;text-align:center">'+icon+'</span>'+'<select class="wa-cfg-input" data-field="'+field+'" onchange="waImpFieldChange(this)" style="flex:1;font-size:12px;padding:6px 10px;height:32px;min-width:0">'+selectOpts+'</select>';
      container.appendChild(row);}
    waImpUpdateBtn();modal.style.display='flex';}

  function waImpFieldChange(sel){if(!_waImpState)return;var field=sel.getAttribute('data-field');var val=parseInt(sel.value);
    if(val<0)delete _waImpState.mapping[field];else _waImpState.mapping[field]=val;
    var row=sel.closest('div');var iconSpan=row.querySelectorAll('span')[2];
    if(val>=0){iconSpan.textContent='\u2705';row.style.borderColor='#22d3a022';}
    else{iconSpan.textContent='\u274c';row.style.borderColor='#ff4d6d22';}
    waImpUpdateBtn();}

  function waImpUpdateBtn(){if(!_waImpState)return;var m=_waImpState.mapping;
    var hasRequired=(m.nome!==undefined&&m.nome>=0)||(m.phone!==undefined&&m.phone>=0);
    var btn=document.getElementById('wa-imp-confirm');
    btn.textContent='\u2705 Importar '+_waImpState.rows.length+' linhas';
    btn.disabled=!hasRequired;btn.style.opacity=hasRequired?'1':'0.4';}

  function waCloseImportModal(){document.getElementById('wa-import-modal').style.display='none';_waImpState=null;}

  function waFinishImport(){if(!_waImpState)return;var s=_waImpState;var m=s.mapping;
    function g(row,i){return i!==undefined&&i>=0&&i<row.length&&row[i]?row[i].trim():'';}
    var list=[];
    for(var i=0;i<s.rows.length;i++){var row=s.rows[i];var nome=g(row,m.nome)||'Cliente';var tel=g(row,m.phone);
      if(!tel&&nome==='Cliente')continue;var cleanTel=(tel||'').replace(/\D/g,'');
      list.push({id:'wa_'+cleanTel+'_'+nome.replace(/ +/g,'_').slice(0,20),nome:nome,phone:tel,data:g(row,m.data),cidade:g(row,m.cidade),tipo:g(row,m.tipo),endereco:g(row,m.endereco),intervalo:g(row,m.intervalo),statusOfs:g(row,m.status)||'\u2014'});}
    if(document.getElementById('wa-imp-remember').checked){try{var hdrKey=s.headers.join('|').toLowerCase();
      localStorage.setItem('wa_col_mapping_v2',JSON.stringify({_key:hdrKey,map:m}));}catch(ex){}}
    if(!list.length){alert('Nenhuma linha encontrada');return;}
    waClients=waClients.concat(list);
    var unique=[];var ids=new Set();
    for(var z=waClients.length-1;z>=0;z--){if(!ids.has(waClients[z].id)){unique.unshift(waClients[z]);ids.add(waClients[z].id);}}
    waClients=unique;waSaveClients();
    if(typeof _chatSaveNomesToCache==='function')_chatSaveNomesToCache();
    waRefreshUI();if(WA_BACKEND)waSyncStatus();waCloseImportModal();}
'''

if 'waShowImportModal' not in html:
    # Encontrar waParseCSV antiga
    idx_parse = html.find('function waParseCSV(text)')
    if idx_parse > 0:
        # Achar o fim da funcao
        brace_count = 0
        end_idx = idx_parse
        started = False
        for ci in range(idx_parse, min(idx_parse + 5000, len(html))):
            if html[ci] == '{':
                brace_count += 1
                started = True
            elif html[ci] == '}':
                brace_count -= 1
                if started and brace_count == 0:
                    end_idx = ci + 1
                    break

        new_parse = ('function waParseCSV(text, filename){\n'
                     '    var allRows=waCSVtoRows(text);\n'
                     '    if(allRows.length<2){alert("Arquivo vazio ou sem dados");return;}\n'
                     '    var headers=allRows[0];\n'
                     '    var mapping=_waAutoMap(headers);\n'
                     '    _waImpState={headers:headers,rows:allRows.slice(1),mapping:mapping,filename:filename||"arquivo"};\n'
                     '    waShowImportModal();\n'
                     '  }')

        html = html[:idx_parse] + new_parse + '\n' + new_js + html[end_idx:]
        print('[+] 3/3 waParseCSV substituida + funcoes do modal adicionadas')
        changes += 1
    else:
        # Fallback: inserir antes do ultimo </script>
        last_script = html.rfind('</script>')
        if last_script > 0:
            new_parse = ('function waParseCSV(text, filename){\n'
                         '    var allRows=waCSVtoRows(text);\n'
                         '    if(allRows.length<2){alert("Arquivo vazio");return;}\n'
                         '    var headers=allRows[0];\n'
                         '    var mapping=_waAutoMap(headers);\n'
                         '    _waImpState={headers:headers,rows:allRows.slice(1),mapping:mapping,filename:filename||"arquivo"};\n'
                         '    waShowImportModal();\n'
                         '  }\n')
            html = html[:last_script] + '\n' + new_parse + new_js + '\n' + html[last_script:]
            print('[+] 3/3 Funcoes inseridas antes de </script>')
            changes += 1
else:
    print('[=] 3/3 Funcoes do modal ja existem')

# Atualizar chamadas para passar filename
if 'waParseCSV(ev.target.result)}' in html:
    html = html.replace('waParseCSV(ev.target.result)}', 'waParseCSV(ev.target.result,file.name)}')
    print('[+] Chamada CSV atualizada com filename')
if 'sheet_to_csv(wb.Sheets[wb.SheetNames[0]]))' in html and 'file.name)' not in html.split('sheet_to_csv')[1][:50]:
    html = html.replace(
        'waParseCSV(XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]))',
        'waParseCSV(XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]),file.name)'
    )
    print('[+] Chamada XLSX atualizada com filename')

open('/docker/dashboard/html/index.html', 'w', encoding='utf-8').write(html)
print('\n[OK] HTML salvo (%d bytes, %d mudancas)' % (len(html), changes))
print('[v] wa-import-modal: %s' % ('SIM' if 'wa-import-modal' in html else 'NAO'))
print('[v] waShowImportModal: %s' % ('SIM' if 'waShowImportModal' in html else 'NAO'))
print('[v] waFinishImport: %s' % ('SIM' if 'waFinishImport' in html else 'NAO'))
print('[v] WA_COL_ALIASES: %s' % ('SIM' if 'WA_COL_ALIASES' in html else 'NAO'))
print('[v] accept expandido: %s' % ('SIM' if '.xlsb,.ods,.tsv,.txt' in html else 'NAO'))
