#!/usr/bin/env python3
"""
Adiciona ao post_inject.py:
  - inject_wa_tabs_fix       → tabs inline onclick
  - inject_wa_handle_file    → waHandleFile com loading
  - inject_wa_mapping_modal  → modal de mapeamento de colunas
"""
import re

ARQUIVO = '/docker/dashboard/post_inject.py'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    src = f.read()

# ── Verifica se já está injetado ───────────────────────────────────────────
if 'inject_wa_mapping_modal' in src:
    print('[OK] Injeções WA já presentes no post_inject.py')
    exit(0)

# ── Novo bloco de funções a inserir antes de "# MAIN" ─────────────────────
NEW_FUNCS = r'''
# 9. WA TABS INLINE FIX
def inject_wa_tabs_fix(html):
    if 'wamap-nome' in html or 'querySelectorAll' in html and 'wa-sub' in html and 'style.display' in html:
        # Verifica se os tabs já estão com inline
        if "style.display='none'" in html:
            log("[9] WA tabs fix OK"); return html
    def make_onclick(target_id):
        return (
            "document.querySelectorAll('.wa-sub').forEach(function(s){s.style.display='none'});"
            "document.querySelectorAll('.wa-tab').forEach(function(b){b.classList.remove('active')});"
            "var t=document.getElementById('" + target_id + "');if(t){t.style.display='block'};"
            "this.classList.add('active');"
            "if(typeof showWaSub==='function')showWaSub('" + target_id + "',null);"
        )
    tabs = {
        "onclick=\"showWaSub('wa-painel',this)\"": "onclick=\"" + make_onclick('wa-painel') + "\"",
        "onclick=\"showWaSub('wa-disparo',this)\"": "onclick=\"" + make_onclick('wa-disparo') + "\"",
        "onclick=\"showWaSub('wa-config',this)\"": "onclick=\"" + make_onclick('wa-config') + "\"",
        "onclick=\"showWaSub('wa-chat',this)\"": "onclick=\"" + make_onclick('wa-chat') + "\"",
    }
    changed = False
    for old, new in tabs.items():
        if old in html:
            html = html.replace(old, new, 1); changed = True
    if changed:
        log("[9] WA tabs inline INJETADO")
    else:
        log("[9] AVISO: ancoras dos wa-tabs nao encontradas")
    return html


# 10. WA HANDLE FILE (loading + CDN fallback)
def inject_wa_handle_file(html):
    if "showLoading(file.name)" in html:
        log("[10] waHandleFile OK"); return html
    old = (
        "  function waHandleFile(e){\n"
        "    var files=e.target.files;\n"
        "    if(!files||!files.length)return;\n"
        "    for(var i=0;i<files.length;i++){\n"
        "      (function(file){\n"
        "        var ext=file.name.split('.').pop().toLowerCase();\n"
        "        if(ext==='csv'){var r=new FileReader();r.onload=function(ev){waParseCSV(ev.target.result)};r.readAsText(file,'UTF-8')}"
    )
    if old not in html:
        log("[10] AVISO: ancora waHandleFile nao encontrada"); return html
    idx = html.find(old)
    end_marker = "    e.target.value='';\n  }"
    end_idx = html.find(end_marker, idx)
    if end_idx < 0:
        log("[10] AVISO: fim de waHandleFile nao encontrado"); return html
    end_idx += len(end_marker)

    new_func = (
        "  function waHandleFile(e){\n"
        "    var files=e.target.files;\n"
        "    if(!files||!files.length)return;\n"
        "    function showLoading(name) {\n"
        "      var dz = document.getElementById('wa-drop-zone');\n"
        "      if(dz) dz.innerHTML = '<div style=\"padding:20px;text-align:center;color:#25d366;font-size:14px\">\u23f3 Lendo <b>'+name+'</b>...</div>';\n"
        "    }\n"
        "    function resetDropzone() {\n"
        "      var dz = document.getElementById('wa-drop-zone');\n"
        "      if(dz) dz.innerHTML = '<div style=\"font-size:32px;margin-bottom:12px\">\u2b06\ufe0f</div><p style=\"color:#e8eaf6;font-size:14px;margin-bottom:6px\">Arraste ou clique para importar</p><p style=\"color:#25d366;font-size:12px\">CSV ou Excel da agenda OFS</p>';\n"
        "    }\n"
        "    function processCSV(csvText, filename) {\n"
        "      try { resetDropzone(); waShowMappingModal(csvText, filename); }\n"
        "      catch(err) { resetDropzone(); alert('Erro ao processar planilha: ' + err.message); }\n"
        "    }\n"
        "    function loadXLSX(cb) {\n"
        "      if(window.XLSX) return cb();\n"
        "      var sc=document.createElement('script');\n"
        "      sc.src='https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';\n"
        "      sc.onload=cb;\n"
        "      sc.onerror=function(){\n"
        "        var s2=document.createElement('script');\n"
        "        s2.src='https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js';\n"
        "        s2.onload=cb; s2.onerror=function(){resetDropzone();alert('Erro ao carregar biblioteca Excel.');};\n"
        "        document.head.appendChild(s2);\n"
        "      };\n"
        "      document.head.appendChild(sc);\n"
        "    }\n"
        "    for(var i=0;i<files.length;i++){\n"
        "      (function(file){\n"
        "        var ext=file.name.split('.').pop().toLowerCase();\n"
        "        showLoading(file.name);\n"
        "        if(ext==='csv'||ext==='tsv'){\n"
        "          var r=new FileReader();\n"
        "          r.onload=function(ev){processCSV(ev.target.result, file.name)};\n"
        "          r.onerror=function(){resetDropzone();alert('Erro ao ler CSV.')};\n"
        "          r.readAsText(file,'UTF-8');\n"
        "        } else {\n"
        "          loadXLSX(function(){\n"
        "            var r=new FileReader();\n"
        "            r.onload=function(ev){\n"
        "              try{\n"
        "                var wb=XLSX.read(new Uint8Array(ev.target.result),{type:'array'});\n"
        "                processCSV(XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]), file.name);\n"
        "              }catch(e2){resetDropzone();alert('Erro ao ler Excel: '+e2.message);}\n"
        "            };\n"
        "            r.onerror=function(){resetDropzone();alert('Erro ao ler o arquivo.')};\n"
        "            r.readAsArrayBuffer(file);\n"
        "          });\n"
        "        }\n"
        "      })(files[i]);\n"
        "    }\n"
        "    e.target.value='';\n"
        "  }"
    )
    html = html[:idx] + new_func + html[end_idx:]
    log("[10] waHandleFile INJETADO com loading e CDN fallback")
    return html


# 11. WA MAPPING MODAL
def inject_wa_mapping_modal(html):
    if 'waShowMappingModal' in html:
        log("[11] waShowMappingModal OK"); return html
    anchor = "  var waDispMode='fixed';"
    if anchor not in html:
        log("[11] AVISO: ancora waDispMode nao encontrada"); return html

    JS = r"""
  function closeWaMapModal() { var m=document.getElementById('waMapModal'); if(m)m.remove(); }

  function waShowMappingModal(csvText, filename) {
    var rows = waCSVtoRows(csvText);
    if (!rows || rows.length < 2) { alert('Planilha vazia ou sem dados.'); return; }
    var headers = rows[0];
    var preview = rows.slice(1, 4);
    window._waMappingCSV = csvText;
    var fields = [
      { key: 'nome',      label: '\ud83d\udc64 Nome *',        required: true  },
      { key: 'telefone',  label: '\ud83d\udcf1 Telefone *',     required: true  },
      { key: 'data',      label: '\ud83d\udcc5 Data',           required: false },
      { key: 'cidade',    label: '\ud83c\udfd9\ufe0f Cidade',   required: false },
      { key: 'endereco',  label: '\ud83d\udccd Endere\u00e7o',  required: false },
      { key: 'status',    label: '\ud83d\udd04 Status',         required: false },
      { key: 'intervalo', label: '\u23f0 Intervalo/Turno',      required: false },
      { key: 'tipo',      label: '\ud83d\udd27 Tipo Atividade', required: false },
    ];
    var autoMap = {};
    var hLower = headers.map(function(h){ return h.toLowerCase(); });
    fields.forEach(function(f) {
      var patterns = {
        nome:['nome','name','cliente','assinante','titular'],
        telefone:['telefone celular','celular','whatsapp','telefone','phone','tel','fone','numero','contato'],
        data:['data','date','dia','agendamento'],
        cidade:['cidade','city','municipio'],
        endereco:['endereco','address','logradouro','rua'],
        status:['status','estado','situacao'],
        intervalo:['intervalo','turno','periodo','horario','hora','slot'],
        tipo:['tipo','atividade'],
      };
      var pats = patterns[f.key] || [];
      var found = -1;
      for (var pi = 0; pi < pats.length && found < 0; pi++)
        for (var hi = 0; hi < hLower.length; hi++)
          if (hLower[hi].indexOf(pats[pi]) >= 0) { found = hi; break; }
      autoMap[f.key] = found;
    });
    var optsList = '<option value="-1">-- nao usar --</option>';
    headers.forEach(function(h, i) { optsList += '<option value="' + i + '">' + h + '</option>'; });
    var tableRows = '';
    fields.forEach(function(f) {
      var color = f.required ? '#f472b6' : '#94a3b8';
      var weight = f.required ? '600' : '400';
      var sel = '<select id="wamap-' + f.key + '" style="background:#1e293b;color:#e2e8f0;border:1px solid #334155;border-radius:6px;padding:6px 10px;font-size:13px;min-width:200px">' + optsList + '</select>';
      tableRows += '<tr><td style="padding:8px 12px;color:' + color + ';font-weight:' + weight + ';font-size:13px">' + f.label + '</td><td style="padding:8px 12px">' + sel + '</td></tr>';
    });
    var previewHtml = '<table style="width:100%;border-collapse:collapse;font-size:11px"><thead><tr>';
    headers.forEach(function(h) { previewHtml += '<th style="background:#1e293b;padding:4px 8px;border:1px solid #334155;color:#94a3b8;white-space:nowrap">' + h + '</th>'; });
    previewHtml += '</tr></thead><tbody>';
    preview.forEach(function(row) {
      previewHtml += '<tr>';
      headers.forEach(function(_, i) { previewHtml += '<td style="padding:4px 8px;border:1px solid #1e293b;color:#cbd5e1">' + ((row[i] || '').slice(0, 30)) + '</td>'; });
      previewHtml += '</tr>';
    });
    previewHtml += '</tbody></table>';
    var modal = document.createElement('div');
    modal.id = 'waMapModal';
    modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.75);z-index:99999;display:flex;align-items:center;justify-content:center;padding:16px';
    modal.innerHTML = [
      '<div style="background:#0f172a;border:1px solid #334155;border-radius:12px;padding:28px;max-width:700px;width:100%;max-height:90vh;overflow-y:auto;box-shadow:0 25px 60px rgba(0,0,0,0.8)">',
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px">',
          '<h3 style="color:#f1f5f9;font-size:18px;margin:0">\ud83d\udcca Mapear Colunas</h3>',
          '<button onclick="closeWaMapModal()" style="background:none;border:none;color:#64748b;font-size:20px;cursor:pointer">\u2715</button>',
        '</div>',
        '<p style="color:#64748b;font-size:13px;margin-bottom:12px">' + headers.length + ' colunas \u00b7 ' + (rows.length-1) + ' linhas' + (filename ? ' \u00b7 ' + filename : '') + '</p>',
        '<div style="overflow-x:auto;max-height:110px;margin-bottom:16px">' + previewHtml + '</div>',
        '<table style="width:100%">' + tableRows + '</table>',
        '<div style="display:flex;gap:12px;margin-top:20px;justify-content:flex-end">',
          '<button onclick="closeWaMapModal()" style="background:#1e293b;color:#94a3b8;border:1px solid #334155;padding:10px 20px;border-radius:8px;cursor:pointer;font-size:14px">Cancelar</button>',
          '<button onclick="waConfirmMapping()" style="background:linear-gradient(135deg,#10b981,#059669);color:#fff;border:none;padding:10px 24px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:600">\u2705 Importar</button>',
        '</div>',
      '</div>'
    ].join('');
    document.body.appendChild(modal);
    fields.forEach(function(f) {
      var sel = document.getElementById('wamap-' + f.key);
      if (sel && autoMap[f.key] >= 0) sel.value = autoMap[f.key];
    });
  }

  function waConfirmMapping() {
    var nome     = parseInt(document.getElementById('wamap-nome').value);
    var telefone = parseInt(document.getElementById('wamap-telefone').value);
    if (nome < 0 || telefone < 0) { alert('Nome e Telefone sao obrigatorios!'); return; }
    var mapping = {
      nome: nome, telefone: telefone,
      data:      parseInt(document.getElementById('wamap-data').value),
      cidade:    parseInt(document.getElementById('wamap-cidade').value),
      endereco:  parseInt(document.getElementById('wamap-endereco').value),
      status:    parseInt(document.getElementById('wamap-status').value),
      intervalo: parseInt(document.getElementById('wamap-intervalo').value),
      tipo:      parseInt(document.getElementById('wamap-tipo').value),
    };
    closeWaMapModal();
    waParseCSVMapped(window._waMappingCSV, mapping);
  }

  function waParseCSVMapped(text, map) {
    var allRows = waCSVtoRows(text);
    if (allRows.length < 2) { alert('Planilha sem dados.'); return; }
    function g(row, i) { return i >= 0 && i < row.length && row[i] ? row[i].trim() : ''; }
    var list = [];
    for (var i = 1; i < allRows.length; i++) {
      var row = allRows[i];
      var nome = g(row, map.nome) || 'Cliente';
      var tel  = g(row, map.telefone);
      if (!tel) continue;
      list.push({
        id: 'wa_' + tel.replace(/\D/g,'') + '_' + nome.replace(/ +/g,'_').slice(0,20),
        nome: nome, phone: tel,
        data: g(row, map.data), cidade: g(row, map.cidade),
        endereco: g(row, map.endereco), statusOfs: g(row, map.status),
        intervalo: g(row, map.intervalo), tipo: g(row, map.tipo),
      });
    }
    if (!list.length) { alert('Nenhum cliente com telefone encontrado.'); return; }
    waClients = waClients.concat(list);
    var unique = []; var ids = new Set();
    for (var z = waClients.length-1; z >= 0; z--)
      if (!ids.has(waClients[z].id)) { unique.unshift(waClients[z]); ids.add(waClients[z].id); }
    waClients = unique;
    waSaveClients(); _chatSaveNomesToCache(); waRefreshUI();
    if (WA_BACKEND) waSyncStatus();
  }

"""
    html = html.replace(anchor, JS + "\n  " + "var waDispMode='fixed';", 1)
    log("[11] waShowMappingModal INJETADO")
    return html

'''

# Insere antes de "# MAIN"
MAIN_MARKER = "# MAIN\nif __name__ == \"__main__\":"
if MAIN_MARKER not in src:
    print('[ERRO] Marcador # MAIN não encontrado')
    exit(1)

src = src.replace(MAIN_MARKER, NEW_FUNCS + MAIN_MARKER, 1)

# Adiciona chamadas no main()
OLD_SAVE = "    html = inject_estoque(html)\n    save(DASH, html)"
NEW_SAVE = (
    "    html = inject_estoque(html)\n"
    "    html = inject_wa_tabs_fix(html)\n"
    "    html = inject_wa_handle_file(html)\n"
    "    html = inject_wa_mapping_modal(html)\n"
    "    save(DASH, html)"
)

if OLD_SAVE in src:
    src = src.replace(OLD_SAVE, NEW_SAVE, 1)
    print('[OK] Chamadas adicionadas ao main()')
else:
    print('[AVISO] Anchor do save não encontrado — adicione manualmente')

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(src)

print('[DONE] post_inject.py atualizado com injeções WA')
