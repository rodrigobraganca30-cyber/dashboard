#!/usr/bin/env python3
"""
Adiciona modal de mapeamento de colunas no dashboard (svoboda.rtflowapp.com)
- Remove debug alerts
- Mostra modal após upload com dropdowns para mapear colunas
- Nome e Telefone obrigatórios, resto opcional
"""
ARQUIVO = '/docker/dashboard/html/index.html'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── 1. Remove debug alerts ───────────────────────────────────────────────
OLD_DEBUG = "    if(!list.length){alert('DEBUG: Planilha lida - '+allRows.length+' linhas, mas 0 clientes encontrados. Colunas detectadas: nome='+iNome+' tel='+iTel);return}\n    alert('DEBUG: '+list.length+' clientes carregados!');"
NEW_DEBUG = "    if(!list.length){var msg='Nenhum cliente encontrado nesta planilha ('+allRows.length+' linhas lidas).';alert(msg);return}"

if OLD_DEBUG in content:
    content = content.replace(OLD_DEBUG, NEW_DEBUG, 1)
    changes += 1
    print('[OK] Debug alerts removidos')
else:
    print('[AVISO] Debug alerts não encontrados, continuando...')

# ── 2. Modifica waHandleFile para chamar modal em vez de waParseCSV diretamente ─
OLD_HANDLE = "  function waHandleFile(e){\n    var files=e.target.files;\n    if(!files||!files.length)return;\n    for(var i=0;i<files.length;i++){\n      (function(file){\n        var ext=file.name.split('.').pop().toLowerCase();\n        if(ext==='csv'){var r=new FileReader();r.onload=function(ev){waParseCSV(ev.target.result)};r.readAsText(file,'UTF-8')}"

NEW_HANDLE = "  function waHandleFile(e){\n    var files=e.target.files;\n    if(!files||!files.length)return;\n    for(var i=0;i<files.length;i++){\n      (function(file){\n        var ext=file.name.split('.').pop().toLowerCase();\n        if(ext==='csv'){var r=new FileReader();r.onload=function(ev){waShowMappingModal(ev.target.result)};r.readAsText(file,'UTF-8')}"

if OLD_HANDLE in content:
    content = content.replace(OLD_HANDLE, NEW_HANDLE, 1)
    changes += 1
    print('[OK] waHandleFile modificado para chamar modal')
else:
    print('[AVISO] waHandleFile csv anchor não encontrado')

# Modifica também o branch Excel para chamar modal
OLD_XLSX_CALL = "waParseCSV(XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]))}catch(e2){alert('Erro ao ler Excel: '+e2.message)}};r.onerror=function(){alert('Erro ao ler o arquivo.')};r.readAsArrayBuffer(file)};"
NEW_XLSX_CALL = "waShowMappingModal(XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]))}catch(e2){alert('Erro ao ler Excel: '+e2.message)}};r.onerror=function(){alert('Erro ao ler o arquivo.')};r.readAsArrayBuffer(file)};"

if OLD_XLSX_CALL in content:
    content = content.replace(OLD_XLSX_CALL, NEW_XLSX_CALL, 1)
    changes += 1
    print('[OK] waHandleFile Excel modificado para chamar modal')
else:
    print('[AVISO] XLSX call anchor não encontrado')

# Modifica branch XLSX já carregado
OLD_XLSX_LOADED = "r.readAsArrayBuffer(file);\n          }\n        }\n      })(files[i]);\n    }\n    e.target.value='';\n  }"
NEW_XLSX_LOADED = "r.readAsArrayBuffer(file);\n          }\n        }\n      })(files[i]);\n    }\n    e.target.value='';\n  }"

# O branch do else (XLSX já carregado) também precisa ser atualizado
OLD_ELSE_BRANCH = "            var r=new FileReader();r.onload=function(ev){var wb=XLSX.read(new Uint8Array(ev.target.result),{type:'array'});waParseCSV(XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]))};r.readAsArrayBuffer(file);"
NEW_ELSE_BRANCH = "            var r=new FileReader();r.onload=function(ev){var wb=XLSX.read(new Uint8Array(ev.target.result),{type:'array'});waShowMappingModal(XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]))};r.readAsArrayBuffer(file);"

if OLD_ELSE_BRANCH in content:
    content = content.replace(OLD_ELSE_BRANCH, NEW_ELSE_BRANCH, 1)
    changes += 1
    print('[OK] XLSX else branch modificado')
else:
    print('[AVISO] XLSX else branch não encontrado')

# ── 3. Injeta CSS + HTML do modal + função waShowMappingModal antes do fechamento </script> ─
MODAL_CSS_HTML_JS = """
  /* ═══════════════ MODAL MAPEAMENTO COLUNAS ═══════════════ */
  function waShowMappingModal(csvText) {
    var rows = waCSVtoRows(csvText);
    if (!rows || rows.length < 2) { alert('Planilha vazia ou sem dados.'); return; }
    var headers = rows[0];
    var preview = rows.slice(1, 4); // 3 linhas de preview
    window._waMappingCSV = csvText;

    var fields = [
      { key: 'nome',      label: '👤 Nome *',        required: true  },
      { key: 'telefone',  label: '📱 Telefone *',     required: true  },
      { key: 'data',      label: '📅 Data',           required: false },
      { key: 'cidade',    label: '🏙️ Cidade',         required: false },
      { key: 'endereco',  label: '📍 Endereço',       required: false },
      { key: 'status',    label: '🔄 Status',         required: false },
      { key: 'intervalo', label: '⏰ Intervalo/Turno',required: false },
      { key: 'tipo',      label: '🔧 Tipo Atividade', required: false },
    ];

    // Auto-detect based on header names
    var autoMap = {};
    var hLower = headers.map(function(h){ return h.toLowerCase(); });
    fields.forEach(function(f) {
      var patterns = {
        nome:      ['nome','name','cliente','assinante','titular'],
        telefone:  ['telefone','celular','phone','tel','fone','whatsapp','numero','número','contato'],
        data:      ['data','date','dia','agendamento'],
        cidade:    ['cidade','city','município','municipio'],
        endereco:  ['endereço','endereco','address','logradouro','rua'],
        status:    ['status','estado','situação','situacao'],
        intervalo: ['intervalo','turno','período','periodo','horario','hora','slot'],
        tipo:      ['tipo','tipo de atividade','atividade'],
      };
      var pats = patterns[f.key] || [];
      var found = -1;
      for (var pi = 0; pi < pats.length && found < 0; pi++) {
        for (var hi = 0; hi < hLower.length; hi++) {
          if (hLower[hi].indexOf(pats[pi]) >= 0) { found = hi; break; }
        }
      }
      autoMap[f.key] = found;
    });

    // Build modal HTML
    var opts = '<option value="-1">-- não usar --</option>';
    headers.forEach(function(h, i) { opts += '<option value="'+i+'">'+h+'</option>'; });

    var rows_html = fields.map(function(f) {
      var sel = '<select id="wamap-'+f.key+'" style="background:#1e293b;color:#e2e8f0;border:1px solid #334155;border-radius:6px;padding:6px 10px;font-size:13px;min-width:200px">'+opts+'</select>';
      return '<tr><td style="padding:8px 12px;color:'+(f.required?'#f472b6':'#94a3b8')+';font-weight:'+(f.required?'600':'400')+';font-size:13px">'+f.label+'</td><td style="padding:8px 12px">'+sel+'</td></tr>';
    }).join('');

    var preview_html = '<table style="width:100%;border-collapse:collapse;font-size:11px;margin-top:8px"><thead><tr>'+
      headers.map(function(h){ return '<th style="background:#1e293b;padding:4px 8px;border:1px solid #334155;color:#94a3b8;white-space:nowrap">'+h+'</th>'; }).join('')+
      '</tr></thead><tbody>'+
      preview.map(function(row){ return '<tr>'+headers.map(function(_,i){ return '<td style="padding:4px 8px;border:1px solid #1e293b;color:#cbd5e1">'+((row[i]||'').slice(0,30))+'</td>'; }).join('')+'</tr>'; }).join('')+
      '</tbody></table>';

    var modal_html = '<div id="waMapModal" style="position:fixed;inset:0;background:rgba(0,0,0,0.75);z-index:99999;display:flex;align-items:center;justify-content:center;padding:16px">'+
      '<div style="background:#0f172a;border:1px solid #334155;border-radius:12px;padding:28px;max-width:700px;width:100%;max-height:90vh;overflow-y:auto;box-shadow:0 25px 60px rgba(0,0,0,0.8)">'+
      '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px">'+
      '<h3 style="color:#f1f5f9;font-size:18px;margin:0">📊 Mapear Colunas da Planilha</h3>'+
      '<button onclick="document.getElementById(\'waMapModal\').remove()" style="background:none;border:none;color:#64748b;font-size:20px;cursor:pointer">✕</button></div>'+
      '<p style="color:#64748b;font-size:13px;margin-bottom:16px">'+headers.length+' colunas detectadas · '+( rows.length-1)+' linhas</p>'+
      '<div style="overflow-x:auto;margin-bottom:20px;max-height:120px">'+preview_html+'</div>'+
      '<table style="width:100%">'+rows_html+'</table>'+
      '<div style="display:flex;gap:12px;margin-top:24px;justify-content:flex-end">'+
      '<button onclick="document.getElementById(\'waMapModal\').remove()" style="background:#1e293b;color:#94a3b8;border:1px solid #334155;padding:10px 20px;border-radius:8px;cursor:pointer;font-size:14px">Cancelar</button>'+
      '<button onclick="waConfirmMapping()" style="background:linear-gradient(135deg,#10b981,#059669);color:#fff;border:none;padding:10px 24px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:600">✅ Importar</button>'+
      '</div></div></div>';

    document.body.insertAdjacentHTML('beforeend', modal_html);

    // Set auto-detected values
    fields.forEach(function(f) {
      var sel = document.getElementById('wamap-'+f.key);
      if (sel && autoMap[f.key] >= 0) sel.value = autoMap[f.key];
    });
  }

  function waConfirmMapping() {
    var nome     = parseInt(document.getElementById('wamap-nome').value);
    var telefone = parseInt(document.getElementById('wamap-telefone').value);
    if (nome < 0 || telefone < 0) { alert('Nome e Telefone são obrigatórios!'); return; }

    var mapping = {
      nome:      nome,
      telefone:  telefone,
      data:      parseInt(document.getElementById('wamap-data').value),
      cidade:    parseInt(document.getElementById('wamap-cidade').value),
      endereco:  parseInt(document.getElementById('wamap-endereco').value),
      status:    parseInt(document.getElementById('wamap-status').value),
      intervalo: parseInt(document.getElementById('wamap-intervalo').value),
      tipo:      parseInt(document.getElementById('wamap-tipo').value),
    };
    document.getElementById('waMapModal').remove();
    waParseCSVMapped(window._waMappingCSV, mapping);
  }

  function waParseCSVMapped(text, map) {
    var allRows = waCSVtoRows(text);
    if (allRows.length < 2) { alert('Planilha sem dados.'); return; }
    function g(row, i) { return i >= 0 && i < row.length && row[i] ? row[i].trim() : ''; }
    var list = [];
    for (var i = 1; i < allRows.length; i++) {
      var row = allRows[i];
      var nome  = g(row, map.nome) || 'Cliente';
      var tel   = g(row, map.telefone);
      if (!tel) continue;
      var cleanTel = tel.replace(/\\D/g, '');
      list.push({
        id:        'wa_' + cleanTel + '_' + nome.replace(/ +/g,'_').slice(0,20),
        nome:      nome,
        phone:     tel,
        data:      g(row, map.data),
        cidade:    g(row, map.cidade),
        endereco:  g(row, map.endereco),
        statusOfs: g(row, map.status),
        intervalo: g(row, map.intervalo),
        tipo:      g(row, map.tipo),
      });
    }
    if (!list.length) { alert('Nenhum cliente com telefone encontrado na planilha.'); return; }
    waClients = waClients.concat(list);
    var unique = []; var ids = new Set();
    for (var z = waClients.length-1; z >= 0; z--) {
      if (!ids.has(waClients[z].id)) { unique.unshift(waClients[z]); ids.add(waClients[z].id); }
    }
    waClients = unique;
    waSaveClients();
    _chatSaveNomesToCache();
    waRefreshUI();
    if (WA_BACKEND) waSyncStatus();
  }
"""

# Injeta antes do fechamento do bloco de scripts da seção WA
ANCHOR = "  var waDispMode='fixed';"
if ANCHOR in content:
    content = content.replace(ANCHOR, MODAL_CSS_HTML_JS + "\n  " + "var waDispMode='fixed';", 1)
    changes += 1
    print('[OK] Modal de mapeamento injetado')
else:
    print('[ERRO] Anchor waDispMode não encontrado')

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'[DONE] Total de {changes} mudancas aplicadas')
