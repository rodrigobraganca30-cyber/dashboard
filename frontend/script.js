// ──────────────────────────────────────────────
// CONFIG — aponte para seu backend
// ──────────────────────────────────────────────
const BACKEND = 'http://187.77.240.87:3001'; // ← ALTERE AQUI

// ──────────────────────────────────────────────
// STATE
// ──────────────────────────────────────────────
let allClients   = [];
let tratativas   = {};   // clientId → { status, obs }
let waSent       = new Set(); // clientIds que já receberam mensagem
let selected     = new Set();
let activeClient = null; // cliente com chat aberto
let pollTimer    = null;

const STATUS_LABELS = { pendente:'⏳ Pendente', confirmado:'✅ Confirmado', 'nao-atendido':'📵 Não Atendeu', reagendado:'🔁 Reagendado' };
const STATUS_ORDER  = ['pendente','confirmado','nao-atendido','reagendado'];

// ──────────────────────────────────────────────
// BACKEND HEALTH + STATUS SYNC
// ──────────────────────────────────────────────
async function checkBackend() {
  try {
    await fetch(`${BACKEND}/health`);
    document.getElementById('conn-dot').classList.add('online');
    document.getElementById('conn-label').textContent = 'Backend OK';
    syncAllStatus();
  } catch {
    document.getElementById('conn-label').textContent = 'Backend offline';
  }
}

async function syncAllStatus() {
  try {
    const r = await fetch(`${BACKEND}/all-status`);
    const data = await r.json();
    let changed = false;
    for (const [id, val] of Object.entries(data)) {
      if (val && (!tratativas[id] || tratativas[id].status !== val.status)) {
        tratativas[id] = val;
        changed = true;
      }
    }
    if (changed) { updateSummary(); rerenderRows(); }
  } catch {}
}

// Polling automático a cada 8 segundos
setInterval(syncAllStatus, 8000);
checkBackend();

// ──────────────────────────────────────────────
// FILE UPLOAD
// ──────────────────────────────────────────────
function handleFile(e) {
  const file = e.target.files[0];
  if (!file) return;
  const ext = file.name.split('.').pop().toLowerCase();

  const processCSV = (csvText) => {
    window._pendingCSV = csvText;
    try { showMappingModal(csvText); } catch(err) { alert('Erro ao abrir mapeamento: ' + err.message); console.error(err); }
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
      script.onerror = () => {
        // fallback para segundo CDN
        const s2 = document.createElement('script');
        s2.src = 'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js';
        s2.onload = cb;
        s2.onerror = () => { alert('Erro ao carregar biblioteca Excel. Verifique sua conexão.'); };
        document.head.appendChild(s2);
      };
      document.head.appendChild(script);
    };
    loadXLSX(() => {
      if (!window.XLSX) {
        alert('Erro: biblioteca Excel não carregou. Verifique sua conexão e tente novamente.');
        return;
      }
      const r = new FileReader();
      r.onload = ev => {
        try {
          const wb = XLSX.read(new Uint8Array(ev.target.result), { type:'array' });
          const csv = XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]);
          processCSV(csv);
        } catch(err) {
          alert('Erro ao ler o Excel: ' + err.message);
        }
      };
      r.onerror = () => alert('Erro ao ler o arquivo.');
      r.readAsArrayBuffer(file);
    });
  }
  e.target.value = '';
}

function parseCSV(text) {
  const lines = text.split(/\r?\n/).filter(l => l.trim());
  if (lines.length < 2) return showToast('Arquivo vazio', 'info');
  const delim = lines[0].includes(';') ? ';' : ',';
  const headers = lines[0].split(delim).map(h => h.replace(/"/g,'').trim().toLowerCase());

  const idx = (...names) => {
    for (const n of names) { const i = headers.findIndex(h => h.includes(n)); if(i>=0) return i; }
    return -1;
  };

  const iRecurso  = idx('recurso','técnico','tecnico','profissional','operador','instalador','equipe');
  const iData      = idx('data','date','dia','data_os','dt','agendamento');
  const iStatus    = idx('status','estado','situação','situacao','fase');
  const iNome      = idx('nome','name','cliente','assinante','titular','razão','razao','contratante');
  const iEnd       = idx('endereço','endereco','address','logradouro','rua','local');
  const iCid       = idx('cidade','city','município','municipio','localidade');
  const iIntervalo = idx('intervalo de tempo','intervalo','turno','período','periodo','slot','horario','hora','janela','faixa');
  const iTel1      = idx('telefone','phone','tel','fone','celular','contato','whatsapp','wpp','numero','número');
  const iTel2      = iTel1>=0 ? headers.findIndex((h,i)=>i>iTel1&&(h.includes('telefone')||h.includes('phone')||h.includes('tel'))) : -1;

  const g = (row, i) => i>=0 && row[i] ? row[i].replace(/"/g,'').trim() : '';

  const list = [];
  for (let i=1; i<lines.length; i++) {
    const row = lines[i].split(delim);
    if (row.length < 3) continue;
    const st = g(row, iStatus).toLowerCase();
    const tel1 = g(row, iTel1);
    const tel2 = iTel2>=0 ? g(row, iTel2) : '';
    list.push({
      id: `c${i}-${g(row,iNome)}-${g(row,iData)}`.replace(/\s+/g,'_').slice(0,60),
      recurso: g(row,iRecurso), data: g(row,iData), nome: g(row,iNome)||g(row,iRecurso)||'Cliente',
      endereco: g(row,iEnd), cidade: g(row,iCid), intervalo: g(row,iIntervalo), tel1, tel2,
      phone: tel1 || tel2,
    });
  }

  if (!list.length) return showToast('Nenhum registro encontrado na planilha', 'info');
  allClients = list;

  const cities = [...new Set(list.map(c=>c.cidade).filter(Boolean))].sort();
  const selCity = document.getElementById('f-city');
  selCity.innerHTML = '<option value="">Todas cidades</option>' + cities.map(c=>`<option value="${c}">${c}</option>`).join('');

  const intervalos = [...new Set(list.map(c=>c.intervalo).filter(Boolean))].sort();
  const selInt = document.getElementById('f-intervalo');
  selInt.innerHTML = '<option value="">Todos turnos</option>' + intervalos.map(v=>`<option value="${v}">${v}</option>`).join('');

  document.getElementById('empty-state').style.display = 'none';
  document.getElementById('client-table').style.display = 'table';
  document.getElementById('summary').style.display = 'grid';
  document.getElementById('controls').style.display = 'flex';

  syncAllStatus();
  render();
  showToast(`✅ ${list.length} agendamentos carregados`, 'success');
}

// ──────────────────────────────────────────────
// MODAL DE MAPEAMENTO DE COLUNAS
// ──────────────────────────────────────────────
function showMappingModal(csvText) {
  var lines = csvText.split(/\r?\n/).filter(function(l){return l.trim();});
  if (lines.length < 2) return showToast('Arquivo vazio', 'info');
  var delim = lines[0].indexOf(';')>=0 ? ';' : (lines[0].indexOf('\t')>=0 ? '\t' : ',');
  var headers = lines[0].split(delim).map(function(h){return h.replace(/"/g,'').trim();});
  var headersLower = headers.map(function(h){return h.toLowerCase();});

  var idxF = function() {
    var names = Array.prototype.slice.call(arguments);
    for (var n=0; n<names.length; n++) {
      for (var hi=0; hi<headersLower.length; hi++) {
        if (headersLower[hi].indexOf(names[n])>=0) return hi;
      }
    }
    return -1;
  };

  var fields = [
    {key:'nome',label:'Nome/Cliente',auto:idxF('nome','name','cliente','assinante','titular'),req:true},
    {key:'phone',label:'Telefone',auto:idxF('telefone','phone','tel','fone','celular','contato','whatsapp','wpp','numero'),req:true},
    {key:'cidade',label:'Cidade',auto:idxF('cidade','city','municipio','localidade')},
    {key:'data',label:'Data',auto:idxF('data','date','dia','data_os','agendamento')},
    {key:'endereco',label:'Endereco',auto:idxF('endereco','address','logradouro','rua')},
    {key:'recurso',label:'Tecnico',auto:idxF('recurso','tecnico','profissional','operador')},
    {key:'intervalo',label:'Turno',auto:idxF('intervalo','turno','periodo','horario','janela')},
    {key:'status',label:'Status',auto:idxF('status','estado','situacao')}
  ];

  var previewRows = [];
  for (var i=1; i<Math.min(lines.length,6); i++) {
    previewRows.push(lines[i].split(delim).map(function(c){return c.replace(/"/g,'').trim();}));
  }

  var modal = document.getElementById('mapping-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'mapping-modal';
    document.body.appendChild(modal);
  }

  var fieldsHTML = '';
  for (var f=0; f<fields.length; f++) {
    var fl = fields[f];
    var optsHTML = '<option value="-1">(nao mapear)</option>';
    for (var j=0; j<headers.length; j++) {
      optsHTML += '<option value="'+j+'"'+(j===fl.auto?' selected':'')+'>'+headers[j]+'</option>';
    }
    fieldsHTML += '<div style="margin-bottom:6px">';
    fieldsHTML += '<div class="form-label">' + fl.label + (fl.req?' <b style="color:var(--red)">*</b>':'') + '</div>';
    fieldsHTML += '<select id="map-'+fl.key+'" class="form-ctrl" style="padding:6px 8px;font-size:12px">' + optsHTML + '</select>';
    fieldsHTML += '</div>';
  }

  var previewHTML = '<table style="width:100%;font-size:11px;border-collapse:collapse;margin-top:8px"><thead><tr>';
  previewHTML += '<th style="padding:4px 6px;border-bottom:1px solid var(--border);text-align:left;color:var(--text3)">#</th>';
  for (var h=0; h<Math.min(headers.length,8); h++) {
    previewHTML += '<th style="padding:4px 6px;border-bottom:1px solid var(--border);text-align:left;color:var(--text3)">'+headers[h].substring(0,15)+'</th>';
  }
  previewHTML += '</tr></thead><tbody>';
  for (var p=0; p<previewRows.length; p++) {
    previewHTML += '<tr><td style="padding:3px 6px;border-bottom:1px solid var(--border);color:var(--text3)">'+(p+1)+'</td>';
    for (var c=0; c<Math.min(previewRows[p].length,8); c++) {
      previewHTML += '<td style="padding:3px 6px;border-bottom:1px solid var(--border);color:var(--text2)">'+previewRows[p][c].substring(0,20)+'</td>';
    }
    previewHTML += '</tr>';
  }
  previewHTML += '</tbody></table>';

  modal.className = 'modal-overlay';
  modal.style.zIndex = '999';
  modal.innerHTML = '<div class="modal" style="max-width:700px;max-height:90vh;overflow-y:auto">'
    + '<div class="modal-title">Mapeamento de Colunas</div>'
    + '<div class="modal-sub">A planilha tem ' + headers.length + ' colunas e ' + (lines.length-1) + ' linhas. Confirme o mapeamento:</div>'
    + '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">' + fieldsHTML + '</div>'
    + '<div style="margin-top:12px;font-size:11px;color:var(--text3);font-family:monospace">Preview (' + previewRows.length + ' linhas)</div>'
    + '<div style="overflow-x:auto">' + previewHTML + '</div>'
    + '<div style="display:flex;gap:10px;margin-top:16px">'
    + '<button class="btn-primary" style="flex:1;padding:10px" onclick="applyMapping()">Importar ' + (lines.length-1) + ' registros</button>'
    + '<button class="btn-cancel" style="padding:10px 18px" onclick="closeMappingModal()">Cancelar</button>'
    + '</div></div>';
}

function closeMappingModal() {
  var m = document.getElementById('mapping-modal');
  if (m) m.className = 'modal-overlay hidden';
}

function applyMapping() {
  var csvText = window._pendingCSV;
  if (!csvText) return;

  var mapping = {};
  var keys = ['nome','phone','cidade','data','endereco','recurso','intervalo','status'];
  for (var k=0; k<keys.length; k++) {
    var sel = document.getElementById('map-'+keys[k]);
    mapping[keys[k]] = sel ? parseInt(sel.value) : -1;
  }

  if (mapping.nome < 0 && mapping.phone < 0) {
    return showToast('Mapeie pelo menos Nome ou Telefone', 'info');
  }

  closeMappingModal();

  var lines = csvText.split(/\r?\n/).filter(function(l){return l.trim();});
  var delim = lines[0].indexOf(';')>=0 ? ';' : (lines[0].indexOf('\t')>=0 ? '\t' : ',');
  var g = function(row, i) { return i>=0 && row[i] ? row[i].replace(/"/g,'').trim() : ''; };

  var list = [];
  for (var i=1; i<lines.length; i++) {
    var row = lines[i].split(delim);
    if (row.length < 2) continue;
    var nome = g(row, mapping.nome);
    var tel1 = g(row, mapping.phone);
    list.push({
      id: ('c'+i+'-'+nome+'-'+g(row,mapping.data)).replace(/\s+/g,'_').slice(0,60),
      recurso: g(row, mapping.recurso),
      data: g(row, mapping.data),
      nome: nome || g(row, mapping.recurso) || 'Cliente',
      endereco: g(row, mapping.endereco),
      cidade: g(row, mapping.cidade),
      intervalo: g(row, mapping.intervalo),
      tel1: tel1, tel2: '',
      phone: tel1,
    });
  }

  if (!list.length) return showToast('Nenhum registro encontrado', 'info');
  allClients = list;

  var cities = []; var citySet = {};
  list.forEach(function(c){ if(c.cidade && !citySet[c.cidade]){cities.push(c.cidade);citySet[c.cidade]=1;} });
  cities.sort();
  document.getElementById('f-city').innerHTML = '<option value="">Todas cidades</option>' + cities.map(function(c){return '<option value="'+c+'">'+c+'</option>';}).join('');

  var intervalos = []; var intSet = {};
  list.forEach(function(c){ if(c.intervalo && !intSet[c.intervalo]){intervalos.push(c.intervalo);intSet[c.intervalo]=1;} });
  intervalos.sort();
  document.getElementById('f-intervalo').innerHTML = '<option value="">Todos turnos</option>' + intervalos.map(function(v){return '<option value="'+v+'">'+v+'</option>';}).join('');

  document.getElementById('empty-state').style.display = 'none';
  document.getElementById('client-table').style.display = 'table';
  document.getElementById('summary').style.display = 'grid';
  document.getElementById('controls').style.display = 'flex';

  syncAllStatus();
  render();
  showToast(list.length + ' registros carregados', 'success');
}

// ──────────────────────────────────────────────
// STATUS HELPERS
// ──────────────────────────────────────────────
function getStatus(c) { return (tratativas[c.id]||{}).status || 'pendente'; }

async function saveStatus(clientId, status, obs='') {
  tratativas[clientId] = { status, obs, updatedAt: new Date().toISOString() };
  updateSummary();
  rerenderRows();
  // persiste no backend
  try { await fetch(`${BACKEND}/status/${clientId}`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({status,obs}) }); }
  catch {}
}

// ──────────────────────────────────────────────
// RENDER TABLE
// ──────────────────────────────────────────────
function filtered() {
  const city      = document.getElementById('f-city').value;
  const intervalo = document.getElementById('f-intervalo').value;
  const status    = document.getElementById('f-status').value;
  const q         = document.getElementById('search').value.toLowerCase();
  return allClients.filter(c => {
    if (city      && c.cidade !== city) return false;
    if (intervalo && c.intervalo !== intervalo) return false;
    if (status    && getStatus(c) !== status) return false;
    if (q && !c.nome.toLowerCase().includes(q) && !(c.phone||'').includes(q) && !(c.cidade||'').toLowerCase().includes(q) && !(c.intervalo||'').toLowerCase().includes(q)) return false;
    return true;
  });
}

function render() {
  updateSummary();
  const list = filtered();
  const tbody = document.getElementById('tbody');
  tbody.innerHTML = list.map(c => rowHTML(c)).join('');
  document.getElementById('sel-count').textContent = `${selected.size} selecionados`;
}

function rerenderRows() {
  const list = filtered();
  const tbody = document.getElementById('tbody');
  if (!tbody.children.length) return;
  list.forEach(c => {
    const row = tbody.querySelector(`tr[data-id="${c.id}"]`);
    if (!row) return;
    const st = getStatus(c);
    row.querySelector('.sbadge').className = `sbadge ${st}`;
    row.querySelector('.sbadge').innerHTML = `<span class="dot"></span>${STATUS_LABELS[st]}`;
  });
  updateSummary();
}

function rowHTML(c) {
  const st    = getStatus(c);
  const isSel = selected.has(c.id);
  const isAct = activeClient?.id === c.id;
  const sent  = waSent.has(c.id);

  return `<tr data-id="${c.id}" onclick="openChat('${c.id}')" class="${isSel?'selected':''} ${isAct?'active-chat':''}">
    <td class="check-col" onclick="event.stopPropagation()">
      <input type="checkbox" ${isSel?'checked':''} onchange="toggleSel('${c.id}',this)">
    </td>
    <td><div class="cname" title="${c.nome}">${c.nome}</div></td>
    <td><span class="cphone">${c.phone||'—'}</span></td>
    <td><span class="cdate">${c.data||'—'}</span></td>
    <td>${c.intervalo?`<span class="cintervalo">${c.intervalo}</span>`:'—'}</td>
    <td><span class="cend" title="${c.endereco||''}">${c.endereco||'—'}</span></td>
    <td><span class="ctag">${c.cidade||'—'}</span></td>
    <td><button class="sbadge ${st}" onclick="event.stopPropagation();cycleStatusClient('${c.id}')"><span class="dot"></span>${STATUS_LABELS[st]}</button></td>
    <td>${sent?`<span class="wa-sent">✓ Enviado</span>`:'<span style="font-size:11px;color:var(--text3)">—</span>'}</td>
  </tr>`;
}

function updateSummary() {
  const counts = { pendente:0, confirmado:0, 'nao-atendido':0, reagendado:0 };
  allClients.forEach(c => counts[getStatus(c)]++);
  document.getElementById('s-total').textContent = allClients.length;
  document.getElementById('s-pend').textContent  = counts.pendente;
  document.getElementById('s-conf').textContent  = counts.confirmado;
  document.getElementById('s-nao').textContent   = counts['nao-atendido'];
  document.getElementById('s-reag').textContent  = counts.reagendado;
}

// ──────────────────────────────────────────────
// SELECTION
// ──────────────────────────────────────────────
function toggleSel(id, cb) {
  cb.checked ? selected.add(id) : selected.delete(id);
  document.getElementById('sel-count').textContent = `${selected.size} selecionados`;
  const row = document.querySelector(`tr[data-id="${id}"]`);
  if (row) row.classList.toggle('selected', cb.checked);
}

function toggleAll(cb) {
  filtered().forEach(c => {
    cb.checked ? selected.add(c.id) : selected.delete(c.id);
  });
  render();
}

function selectAll()  { selected.clear(); filtered().forEach(c => selected.add(c.id)); render(); }
function selectNone() { selected.clear(); render(); }
function filterChanged() {
  selected.clear();
  const chkAll = document.getElementById('check-all');
  if (chkAll) chkAll.checked = false;
  render();
}

function cycleStatusClient(id) {
  const cur = (tratativas[id]||{}).status || 'pendente';
  const next = STATUS_ORDER[(STATUS_ORDER.indexOf(cur)+1) % STATUS_ORDER.length];
  saveStatus(id, next);
}

// ──────────────────────────────────────────────
// CHAT
// ──────────────────────────────────────────────
async function openChat(id) {
  const c = allClients.find(x => x.id === id);
  if (!c) return;
  activeClient = c;

  document.getElementById('no-chat').style.display = 'none';
  const cp = document.getElementById('chat-panel');
  cp.style.display = 'flex';

  document.getElementById('chat-name').textContent  = c.nome;
  document.getElementById('chat-phone').textContent = c.phone || '—';
  document.getElementById('chat-intervalo').textContent = c.intervalo ? '🕐 ' + c.intervalo : '';
  document.getElementById('chat-endereco').textContent  = c.endereco  ? '📍 ' + c.endereco  : '';

  updateChatStatusBadge();
  await loadMessages();

  // highlight row
  document.querySelectorAll('tr[data-id]').forEach(r => r.classList.remove('active-chat'));
  const row = document.querySelector(`tr[data-id="${id}"]`);
  if (row) row.classList.add('active-chat');

  // poll mensagens a cada 5s
  clearInterval(pollTimer);
  pollTimer = setInterval(loadMessages, 5000);
}

function updateChatStatusBadge() {
  if (!activeClient) return;
  const st = getStatus(activeClient);
  const badge = document.getElementById('chat-status-badge');
  badge.className = `sbadge ${st}`;
  badge.innerHTML = `<span class="dot"></span><span id="chat-status-label">${STATUS_LABELS[st]}</span>`;
}

async function loadMessages() {
  if (!activeClient) return;
  const phone = (activeClient.phone||'').replace(/\D/g,'');
  if (!phone) return;

  try {
    const r = await fetch(`${BACKEND}/msgs/${phone}`);
    const msgs = await r.json();
    renderMessages(msgs);

    // Verifica se status mudou automaticamente
    const sr = await fetch(`${BACKEND}/status/${activeClient.id}`);
    const sv = await sr.json();
    if (sv.status && sv.status !== getStatus(activeClient)) {
      tratativas[activeClient.id] = sv;
      updateChatStatusBadge();
      updateSummary();
      rerenderRows();
    }
  } catch {}
}

function renderMessages(msgs) {
  const el = document.getElementById('messages');
  if (!msgs.length) {
    el.innerHTML = '<div style="text-align:center;padding:20px;font-size:12px;color:var(--text3)">Nenhuma mensagem ainda</div>';
    return;
  }

  el.innerHTML = msgs.map(m => {
    const ts = m.ts ? new Date(m.ts).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}) : '';
    const isMe = m.from === 'me';
    return `<div class="msg-wrap ${isMe?'me':'client'}">
      <div class="msg-bubble">${escHtml(m.text)}</div>
      <div class="msg-ts">${ts}${m.auto?'<span class="msg-auto-tag">auto</span>':''}</div>
    </div>`;
  }).join('');

  el.scrollTop = el.scrollHeight;
}

async function sendReply() {
  if (!activeClient) return;
  const input = document.getElementById('reply-input');
  const text  = input.value.trim();
  if (!text) return;

  input.value = '';
  input.style.height = 'auto';

  try {
    await fetch(`${BACKEND}/send-reply`, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ phone: activeClient.phone, text })
    });
    await loadMessages();
    showToast('Mensagem enviada', 'wa');
  } catch { showToast('Erro ao enviar', 'info'); }
}

function setActiveStatus(status) {
  if (!activeClient) return;
  saveStatus(activeClient.id, status);
  updateChatStatusBadge();
}

function cycleStatus() {
  if (!activeClient) return;
  const cur = getStatus(activeClient);
  const next = STATUS_ORDER[(STATUS_ORDER.indexOf(cur)+1) % STATUS_ORDER.length];
  saveStatus(activeClient.id, next);
  updateChatStatusBadge();
}

// ──────────────────────────────────────────────
// DISPARO EM MASSA
// ──────────────────────────────────────────────
function openDisparo() {
  if (!selected.size) return showToast('Selecione pelo menos 1 cliente', 'info');

  const selClients = allClients.filter(c => selected.has(c.id));
  document.getElementById('disparo-sub').textContent = `${selClients.length} clientes selecionados`;
  document.getElementById('fire-count').textContent  = selClients.length;

  // template padrão
  const tmpl = document.getElementById('template-input');
  if (!tmpl.value) {
    tmpl.value = `Olá {{nome}}! 👋\n\nPassando para confirmar seu agendamento de instalação de internet no dia *{{data}}* em {{cidade}}.\n\nVocê confirma a presença? Responda *SIM* para confirmar ou *NÃO* caso precise reagendar. 😊`;
  }
  updatePreview();
  document.getElementById('modal-disparo').classList.remove('hidden');
}

function closeDisparo() {
  document.getElementById('modal-disparo').classList.add('hidden');
  document.getElementById('progress-wrap').style.display = 'none';
  document.getElementById('btn-fire').disabled = false;
}

function updatePreview() {
  const tmpl = document.getElementById('template-input').value;
  const selClients = allClients.filter(c => selected.has(c.id));
  const c = selClients[0];
  if (!c) { document.getElementById('preview-box').textContent = '—'; return; }

  document.getElementById('preview-box').textContent = tmpl
    .replace(/\{\{nome\}\}/gi, c.nome)
    .replace(/\{\{data\}\}/gi, c.data||'—')
    .replace(/\{\{cidade\}\}/gi, c.cidade||'—')
    .replace(/\{\{horario\}\}/gi, c.horario||'—')
    .replace(/\{\{intervalo\}\}/gi, c.intervalo||'—')
    .replace(/\{\{endereco\}\}/gi, c.endereco||'—');
}

async function fireDisparo() {
  const template = document.getElementById('template-input').value.trim();
  if (!template) return showToast('Preencha o template', 'info');

  const selClients = allClients.filter(c => selected.has(c.id) && (c.phone||c.tel1));
  if (!selClients.length) return showToast('Nenhum cliente com telefone', 'info');

  const delayMs = parseInt(document.getElementById('delay-input').value) * 1000 || 5000;

  document.getElementById('btn-fire').disabled = true;
  document.getElementById('progress-wrap').style.display = 'block';
  document.getElementById('progress-txt').textContent = `Enviando 0/${selClients.length}...`;
  document.getElementById('progress-fill').style.width = '0%';

  try {
    // Dispara no backend (bulk)
    fetch(`${BACKEND}/send-bulk`, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ clients: selClients, template, delayMs })
    });

    // Simula progresso no front (backend processa em background)
    let sent = 0;
    const interval = setInterval(() => {
      sent++;
      const pct = Math.round(sent/selClients.length*100);
      document.getElementById('progress-fill').style.width = `${pct}%`;
      document.getElementById('progress-txt').textContent = `Enviando ${sent}/${selClients.length}...`;

      selClients[sent-1] && waSent.add(selClients[sent-1].id);

      if (sent >= selClients.length) {
        clearInterval(interval);
        document.getElementById('progress-txt').textContent = `✅ Disparo concluído! ${selClients.length} mensagens enviadas.`;
        rerenderRows();
        showToast(`🚀 ${selClients.length} mensagens disparadas`, 'wa');
        setTimeout(closeDisparo, 2000);
      }
    }, delayMs);

  } catch(e) {
    showToast('Erro ao disparar: ' + e.message, 'info');
    document.getElementById('btn-fire').disabled = false;
  }
}

// ──────────────────────────────────────────────
// UTILS
// ──────────────────────────────────────────────
function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>');
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

function showToast(msg, type='info') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `toast ${type} show`;
  setTimeout(() => t.classList.remove('show'), 3200);
}

document.getElementById('modal-disparo').addEventListener('click', e => {
  if (e.target === document.getElementById('modal-disparo')) closeDisparo();
});

// Garante que paste e drop no campo de busca usem filterChanged
document.getElementById('search').addEventListener('paste', function() {
  setTimeout(filterChanged, 100);
});
document.getElementById('search').addEventListener('drop', function() {
  setTimeout(filterChanged, 100);
});