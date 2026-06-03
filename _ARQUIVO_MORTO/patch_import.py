import re

filepath = "/docker/whatsapp-agenda/frontend/index.html"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

# === 1. Ampliar accept para mais formatos ===
old_accept = 'accept=".csv,.xlsx,.xls"'
new_accept = 'accept=".csv,.xlsx,.xls,.ods,.tsv"'
if old_accept in content:
    content = content.replace(old_accept, new_accept)
    changes += 1
    print("1. OK - accept ampliado (.ods, .tsv)")

# === 2. Remover filtro de status ===
old_filter = "    const st = g(row, iStatus).toLowerCase();\n    if (st && !st.includes('pendente') && !st.includes('agendado') && !st.includes('pending')) continue;"
new_filter = "    const st = g(row, iStatus).toLowerCase();\n    // Filtro de status removido - carrega todas as linhas"
if old_filter in content:
    content = content.replace(old_filter, new_filter)
    changes += 1
    print("2. OK - filtro de status removido")

# === 3. Ampliar idx() com mais variacoes de nomes ===
old_idx_block = """  const iRecurso  = idx('recurso','técnico','tecnico');
  const iData      = idx('data','date','dia');
  const iStatus    = idx('status','estado');
  const iNome      = idx('nome','name','cliente');
  const iEnd       = idx('endereço','endereco','address','logradouro');
  const iCid       = idx('cidade','city');
  const iIntervalo = idx('intervalo de tempo','intervalo','turno','período','periodo','slot','horario','hora');
  const iTel1      = idx('telefone','phone','tel','fone','celular');"""

new_idx_block = """  const iRecurso  = idx('recurso','técnico','tecnico','profissional','operador','instalador','equipe');
  const iData      = idx('data','date','dia','data_os','dt','agendamento','data agendamento');
  const iStatus    = idx('status','estado','situação','situacao','fase');
  const iNome      = idx('nome','name','cliente','assinante','titular','razão','razao','contratante');
  const iEnd       = idx('endereço','endereco','address','logradouro','rua','local','localização','localizacao');
  const iCid       = idx('cidade','city','município','municipio','localidade','uf');
  const iIntervalo = idx('intervalo de tempo','intervalo','turno','período','periodo','slot','horario','hora','janela','faixa');
  const iTel1      = idx('telefone','phone','tel','fone','celular','contato','whatsapp','wpp','numero','número');"""

if old_idx_block in content:
    content = content.replace(old_idx_block, new_idx_block)
    changes += 1
    print("3. OK - nomes de coluna ampliados")

# === 4. Alterar toast de "pendente" para generico ===
old_toast = "if (!list.length) return showToast('Nenhum agendamento pendente encontrado', 'info');"
new_toast = "if (!list.length) return showToast('Nenhum registro encontrado na planilha', 'info');"
if old_toast in content:
    content = content.replace(old_toast, new_toast)
    changes += 1
    print("4. OK - mensagem de toast atualizada")

# === 5. Adicionar modal de mapeamento de colunas ===
# Vou substituir a funcao handleFile e parseCSV inteiras por versoes com modal

old_handleFile = """function handleFile(e) {
  const file = e.target.files[0];
  if (!file) return;
  const ext = file.name.split('.').pop().toLowerCase();

  if (ext === 'csv') {
    const r = new FileReader();
    r.onload = ev => parseCSV(ev.target.result);
    r.readAsText(file, 'UTF-8');
  } else {
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
    script.onload = () => {
      const r = new FileReader();
      r.onload = ev => {
        const wb = XLSX.read(new Uint8Array(ev.target.result), { type:'array' });
        const csv = XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]);
        parseCSV(csv);
      };
      r.readAsArrayBuffer(file);
    };
    document.head.appendChild(script);
  }
  e.target.value = '';
}"""

new_handleFile = """function handleFile(e) {
  const file = e.target.files[0];
  if (!file) return;
  const ext = file.name.split('.').pop().toLowerCase();

  const processCSV = (csvText) => {
    window._pendingCSV = csvText;
    showMappingModal(csvText);
  };

  if (ext === 'csv' || ext === 'tsv') {
    const r = new FileReader();
    r.onload = ev => processCSV(ev.target.result);
    r.readAsText(file, 'UTF-8');
  } else {
    const loadXLSX = (cb) => {
      if (window.XLSX) return cb();
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
      script.onload = cb;
      document.head.appendChild(script);
    };
    loadXLSX(() => {
      const r = new FileReader();
      r.onload = ev => {
        const wb = XLSX.read(new Uint8Array(ev.target.result), { type:'array' });
        const csv = XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]);
        processCSV(csv);
      };
      r.readAsArrayBuffer(file);
    });
  }
  e.target.value = '';
}

// ──────────────────────────────────────────────
// MODAL DE MAPEAMENTO DE COLUNAS
// ──────────────────────────────────────────────
function showMappingModal(csvText) {
  const lines = csvText.split(/\\r?\\n/).filter(l => l.trim());
  if (lines.length < 2) return showToast('Arquivo vazio', 'info');
  const delim = lines[0].includes(';') ? ';' : (lines[0].includes('\\t') ? '\\t' : ',');
  const headers = lines[0].split(delim).map(h => h.replace(/"/g,'').trim());
  const headersLower = headers.map(h => h.toLowerCase());

  // Auto-detect
  const idx = (...names) => {
    for (const n of names) { const i = headersLower.findIndex(h => h.includes(n)); if(i>=0) return i; }
    return -1;
  };

  const fields = [
    { key:'nome',      label:'👤 Nome/Cliente',  auto: idx('nome','name','cliente','assinante','titular','razão','razao','contratante'), required:true },
    { key:'phone',     label:'📱 Telefone',       auto: idx('telefone','phone','tel','fone','celular','contato','whatsapp','wpp','numero','número'), required:true },
    { key:'cidade',    label:'🏙 Cidade',         auto: idx('cidade','city','município','municipio','localidade','uf') },
    { key:'data',      label:'📅 Data',           auto: idx('data','date','dia','data_os','dt','agendamento') },
    { key:'endereco',  label:'📍 Endereço',       auto: idx('endereço','endereco','address','logradouro','rua','local') },
    { key:'recurso',   label:'👷 Técnico',        auto: idx('recurso','técnico','tecnico','profissional','operador','instalador','equipe') },
    { key:'intervalo', label:'🕐 Turno/Horário',  auto: idx('intervalo de tempo','intervalo','turno','período','periodo','slot','horario','hora','janela') },
    { key:'status',    label:'📊 Status',         auto: idx('status','estado','situação','situacao','fase') },
  ];

  // Preview: 5 primeiras linhas
  const previewRows = [];
  for (let i = 1; i < Math.min(lines.length, 6); i++) {
    previewRows.push(lines[i].split(delim).map(c => c.replace(/"/g,'').trim()));
  }

  // Gerar options
  const opts = (sel) => '<option value="-1">(não mapear)</option>' +
    headers.map((h, i) => `<option value="${i}" ${i===sel?'selected':''}>${h}</option>`).join('');

  // Gerar preview table
  const previewHTML = () => {
    const mapped = fields.filter(f => f.required || document.getElementById('map-'+f.key)?.value >= 0);
    if (!mapped.length) return '';
    let html = '<table style="width:100%;font-size:11px;border-collapse:collapse;margin-top:10px"><thead><tr>';
    mapped.forEach(f => { html += `<th style="padding:4px 6px;border-bottom:1px solid var(--border);text-align:left;color:var(--text3)">${f.label.split(' ').pop()}</th>`; });
    html += '</tr></thead><tbody>';
    previewRows.forEach(row => {
      html += '<tr>';
      mapped.forEach(f => {
        const ci = document.getElementById('map-'+f.key)?.value ?? f.auto;
        const val = ci >= 0 && row[ci] ? row[ci].slice(0, 25) : '—';
        html += `<td style="padding:3px 6px;border-bottom:1px solid var(--border);color:var(--text2)">${val}</td>`;
      });
      html += '</tr>';
    });
    html += '</tbody></table>';
    return html;
  };

  // Criar modal
  let modal = document.getElementById('mapping-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'mapping-modal';
    document.body.appendChild(modal);
  }

  modal.className = 'modal-overlay';
  modal.innerHTML = `
    <div class="modal" style="max-width:620px;max-height:90vh;overflow-y:auto">
      <div class="modal-title">📋 Mapeamento de Colunas</div>
      <div class="modal-sub">A planilha tem ${headers.length} colunas e ${lines.length-1} linhas. Confirme o mapeamento:</div>
      <div id="mapping-fields" style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        ${fields.map(f => `
          <div class="form-row" style="margin-bottom:6px">
            <div class="form-label">${f.label} ${f.required?'<span style="color:var(--red)">*</span>':''}</div>
            <select id="map-${f.key}" class="form-ctrl" style="padding:6px 8px;font-size:12px" onchange="document.getElementById('map-preview').innerHTML=window._updatePreview?.()??''">
              ${opts(f.auto)}
            </select>
          </div>
        `).join('')}
      </div>
      <div style="margin-top:12px;font-size:11px;color:var(--text3);font-family:'DM Mono',monospace">Preview (${Math.min(previewRows.length,5)} linhas)</div>
      <div id="map-preview" style="overflow-x:auto">${previewHTML()}</div>
      <div style="display:flex;gap:10px;margin-top:16px">
        <button class="btn-primary" style="flex:1;padding:10px" onclick="applyMapping()">✅ Importar ${lines.length-1} registros</button>
        <button class="btn-outline" style="padding:10px 18px" onclick="document.getElementById('mapping-modal').className='modal-overlay hidden'">Cancelar</button>
      </div>
    </div>`;

  window._updatePreview = previewHTML;
  // Trigger initial preview
  setTimeout(() => { document.getElementById('map-preview').innerHTML = previewHTML(); }, 50);
}

function applyMapping() {
  const csvText = window._pendingCSV;
  if (!csvText) return;

  // Ler mapeamento do modal
  const mapping = {};
  ['nome','phone','cidade','data','endereco','recurso','intervalo','status'].forEach(k => {
    const sel = document.getElementById('map-'+k);
    mapping[k] = sel ? parseInt(sel.value) : -1;
  });

  // Validar obrigatorios
  if (mapping.nome < 0 && mapping.phone < 0) {
    return showToast('Mapeie pelo menos Nome ou Telefone', 'info');
  }

  // Fechar modal
  document.getElementById('mapping-modal').className = 'modal-overlay hidden';

  // Parsear com mapeamento manual
  parseCSVWithMapping(csvText, mapping);
}

function parseCSVWithMapping(text, mapping) {
  const lines = text.split(/\\r?\\n/).filter(l => l.trim());
  if (lines.length < 2) return showToast('Arquivo vazio', 'info');
  const delim = lines[0].includes(';') ? ';' : (lines[0].includes('\\t') ? '\\t' : ',');

  const g = (row, i) => i >= 0 && row[i] ? row[i].replace(/"/g,'').trim() : '';

  const list = [];
  for (let i = 1; i < lines.length; i++) {
    const row = lines[i].split(delim);
    if (row.length < 2) continue;
    const nome = g(row, mapping.nome);
    const tel1 = g(row, mapping.phone);
    const tel2 = '';
    list.push({
      id: `c${i}-${nome}-${g(row,mapping.data)}`.replace(/\\s+/g,'_').slice(0,60),
      recurso: g(row, mapping.recurso),
      data: g(row, mapping.data),
      nome: nome || g(row, mapping.recurso) || 'Cliente',
      endereco: g(row, mapping.endereco),
      cidade: g(row, mapping.cidade),
      intervalo: g(row, mapping.intervalo),
      tel1, tel2,
      phone: tel1 || tel2,
    });
  }

  if (!list.length) return showToast('Nenhum registro encontrado na planilha', 'info');
  allClients = list;

  const cities = [...new Set(list.map(c => c.cidade).filter(Boolean))].sort();
  const selCity = document.getElementById('f-city');
  selCity.innerHTML = '<option value="">Todas cidades</option>' + cities.map(c => `<option value="${c}">${c}</option>`).join('');

  const intervalos = [...new Set(list.map(c => c.intervalo).filter(Boolean))].sort();
  const selInt = document.getElementById('f-intervalo');
  selInt.innerHTML = '<option value="">Todos turnos</option>' + intervalos.map(v => `<option value="${v}">${v}</option>`).join('');

  document.getElementById('empty-state').style.display = 'none';
  document.getElementById('client-table').style.display = 'table';
  document.getElementById('summary').style.display = 'grid';
  document.getElementById('controls').style.display = 'flex';

  syncAllStatus();
  render();
  showToast(`✅ ${list.length} registros carregados`, 'success');
}"""

if old_handleFile in content:
    content = content.replace(old_handleFile, new_handleFile)
    changes += 1
    print("5. OK - handleFile + modal de mapeamento adicionado")
else:
    print("5. ERRO - handleFile nao encontrado")
    # Debug
    if "function handleFile" in content:
        print("  handleFile existe mas texto nao bate exatamente")

# === 6. Manter parseCSV original (para compatibilidade) mas atualizar ===
# O parseCSV original continua existendo para ser chamado diretamente se necessario

# Salva
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nTOTAL: {changes} mudancas aplicadas")
