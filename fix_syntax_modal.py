#!/usr/bin/env python3
"""
Fix definitivo: corrige o erro de sintaxe JS em waShowMappingModal
causado por aspas simples não escapadas dentro de strings JS.
"""
ARQUIVO = '/docker/dashboard/html/index.html'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

# Localiza e substitui waShowMappingModal inteira por versão correta
import re

# Encontra o início da função waShowMappingModal
start_marker = "  function waShowMappingModal(csvText) {"
end_marker = "  function waConfirmMapping() {"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx < 0 or end_idx < 0:
    print(f'[ERRO] Marcadores não encontrados: start={start_idx}, end={end_idx}')
    exit(1)

print(f'[OK] waShowMappingModal encontrado: chars {start_idx}-{end_idx}')

# Nova implementação sem problema de aspas - usa função nomeada e concatenação segura
NEW_SHOW_MAPPING = r"""  function closeWaMapModal() { var m=document.getElementById('waMapModal'); if(m)m.remove(); }

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
        nome:      ['nome','name','cliente','assinante','titular'],
        telefone:  ['telefone','celular','phone','tel','fone','whatsapp','numero','contato'],
        data:      ['data','date','dia','agendamento'],
        cidade:    ['cidade','city','municipio'],
        endereco:  ['endereco','address','logradouro','rua'],
        status:    ['status','estado','situacao'],
        intervalo: ['intervalo','turno','periodo','horario','hora','slot'],
        tipo:      ['tipo','atividade'],
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

    // Monta SELECT de colunas
    var optsList = '<option value="-1">-- nao usar --</option>';
    headers.forEach(function(h, i) {
      optsList += '<option value="' + i + '">' + h + '</option>';
    });

    // Monta linhas da tabela
    var tableRows = '';
    fields.forEach(function(f) {
      var color = f.required ? '#f472b6' : '#94a3b8';
      var weight = f.required ? '600' : '400';
      var sel = '<select id="wamap-' + f.key + '" style="background:#1e293b;color:#e2e8f0;border:1px solid #334155;border-radius:6px;padding:6px 10px;font-size:13px;min-width:200px">' + optsList + '</select>';
      tableRows += '<tr><td style="padding:8px 12px;color:' + color + ';font-weight:' + weight + ';font-size:13px">' + f.label + '</td><td style="padding:8px 12px">' + sel + '</td></tr>';
    });

    // Monta preview
    var previewHtml = '<table style="width:100%;border-collapse:collapse;font-size:11px"><thead><tr>';
    headers.forEach(function(h) {
      previewHtml += '<th style="background:#1e293b;padding:4px 8px;border:1px solid #334155;color:#94a3b8;white-space:nowrap">' + h + '</th>';
    });
    previewHtml += '</tr></thead><tbody>';
    preview.forEach(function(row) {
      previewHtml += '<tr>';
      headers.forEach(function(_, i) {
        previewHtml += '<td style="padding:4px 8px;border:1px solid #1e293b;color:#cbd5e1">' + ((row[i] || '').slice(0, 30)) + '</td>';
      });
      previewHtml += '</tr>';
    });
    previewHtml += '</tbody></table>';

    // Monta modal
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

    // Auto-detect
    fields.forEach(function(f) {
      var sel = document.getElementById('wamap-' + f.key);
      if (sel && autoMap[f.key] >= 0) sel.value = autoMap[f.key];
    });
  }

"""

# Substitui o bloco antigo pelo novo
old_block = content[start_idx:end_idx]
content = content[:start_idx] + NEW_SHOW_MAPPING + content[end_idx:]

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(content)

print('[OK] waShowMappingModal reescrita sem erros de aspas')
print('[OK] Funcao closeWaMapModal adicionada')
print('[DONE] Erro de sintaxe JS corrigido')
