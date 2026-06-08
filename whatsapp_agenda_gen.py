"""Gera HTML da aba WhatsApp Agenda para o Dashboard SVOBODA."""

def gerar_whatsapp_agenda_html(backend_url="https://svoboda.rtflowapp.com/api/agenda", api_key="svoboda-agenda-2025"):
    return f"""
<style>
.wa-tabs{{display:flex;gap:8px;margin-bottom:24px}}
.wa-tab{{background:#111520;border:1px solid #1c2237;border-radius:8px;padding:10px 20px;font-size:13px;color:#94a3b8;cursor:pointer;font-family:var(--font-head);font-weight:600;transition:all .2s}}
.wa-tab:hover{{border-color:#25d366;color:#6ee7b7}}
.wa-tab.active{{background:#25d366;border-color:#25d366;color:#022c22;box-shadow:0 4px 15px rgba(37,211,102,.3)}}
.wa-sub{{display:none}}.wa-sub.active{{display:block}}
.wa-cfg-row{{display:flex;gap:12px;margin-bottom:16px;align-items:center}}
.wa-cfg-input{{background:#111520;border:1px solid #1c2237;border-radius:8px;padding:8px 14px;color:#e8eaf6;font-size:13px;font-family:var(--font-mono);outline:none;flex:1}}
.wa-cfg-input:focus{{border-color:#25d366}}
.wa-cfg-btn{{background:#25d366;color:#022c22;border:none;padding:8px 18px;border-radius:8px;font-size:13px;font-weight:700;cursor:pointer;font-family:var(--font-head);transition:all .2s}}
.wa-cfg-btn:hover{{background:#128c7e;color:#fff}}
.wa-cfg-btn.secondary{{background:transparent;border:1px solid #1c2237;color:#94a3b8}}
.wa-cfg-btn.secondary:hover{{border-color:#25d366;color:#25d366}}
.wa-status-dot{{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:6px}}
.wa-status-dot.online{{background:#25d366;box-shadow:0 0 8px #25d366}}
.wa-status-dot.offline{{background:#ff4d6d}}
.wa-chat-area{{display:grid;grid-template-columns:1fr 360px;gap:20px;min-height:500px}}
.wa-msg-list{{background:#111520;border:1px solid #1c2237;border-radius:12px;padding:16px;max-height:450px;overflow-y:auto;display:flex;flex-direction:column;gap:6px}}
.wa-msg{{padding:8px 12px;border-radius:10px;font-size:12px;max-width:80%;word-break:break-word}}
.wa-msg.me{{background:linear-gradient(135deg,#128c7e,#25d366);color:#fff;align-self:flex-end;border-bottom-right-radius:2px}}
.wa-msg.client{{background:#1a1e28;color:#e8eaf6;align-self:flex-start;border-bottom-left-radius:2px}}
.wa-badge{{font-size:10px;padding:3px 8px;border-radius:20px;font-weight:600;display:inline-flex;align-items:center;gap:4px}}
.wa-badge.pendente{{background:rgba(251,191,36,.15);color:#fbbf24}}
.wa-badge.confirmado{{background:rgba(37,211,102,.15);color:#25d366}}
.wa-badge.nao-atendido{{background:rgba(255,77,109,.15);color:#ff4d6d}}
.wa-badge.reagendado{{background:rgba(124,58,237,.15);color:#7c3aed}}
.wa-badge.entregue{{background:rgba(59,130,246,.15);color:#60a5fa}}
.wa-badge.conveniente{{background:rgba(249,115,22,.15);color:#f97316}}
.wa-badge.entregue-d1{{background:rgba(59,130,246,.18);color:#60a5fa;border:1px solid rgba(59,130,246,.3)}}
.wa-badge.entregue-d0{{background:rgba(234,179,8,.18);color:#eab308;border:1px solid rgba(234,179,8,.3)}}
.wa-badge.entregue-pos{{background:rgba(249,115,22,.18);color:#fb923c;border:1px solid rgba(249,115,22,.3)}}
.wa-badge.satisfeito{{background:rgba(34,197,94,.15);color:#22c55e}}
.wa-badge.insatisfeito{{background:rgba(239,68,68,.15);color:#ef4444}}
.wa-badge.problema-aberto{{background:rgba(251,146,60,.15);color:#fb923c}}
.wa-badge.elogio{{background:rgba(234,179,8,.15);color:#fbbf24}}
.wa-badge.bloqueado{{background:rgba(239,68,68,.2);color:#ef4444;border:1px solid rgba(239,68,68,.3)}}
.wa-file-drop{{border:2px dashed #1c2237;border-radius:12px;padding:40px;text-align:center;cursor:pointer;transition:all .2s;background:#0d1117}}
.wa-file-drop:hover{{border-color:#25d366;background:#0a1510}}
.wa-tbl-wrap{{max-height:400px;overflow-y:auto}}
.wa-dd-wrap{{position:relative;display:inline-block}}
.wa-dd-btn{{background:#111520;border:1px solid #1c2237;border-radius:8px;padding:6px 12px;color:#e8eaf6;font-size:12px;cursor:pointer;min-width:140px;display:flex;justify-content:space-between;align-items:center}}
.wa-dd-btn:hover{{border-color:#25d366}}
.wa-dd-menu{{position:absolute;top:calc(100% + 4px);left:0;background:#111520;border:1px solid #1c2237;border-radius:8px;padding:8px;min-width:180px;max-height:250px;overflow-y:auto;z-index:100;display:none;box-shadow:0 10px 25px rgba(0,0,0,0.5)}}
.wa-dd-menu.active{{display:block}}
.wa-dd-item{{display:flex;align-items:center;gap:8px;padding:6px 8px;cursor:pointer;font-size:12px;color:#e8eaf6;border-radius:4px;white-space:nowrap}}
.wa-dd-item:hover{{background:#1a1e28}}
.wa-dd-item input{{accent-color:#25d366;cursor:pointer}}
</style>
<div class="page" id="whatsapp-agenda">
  <div class="wa-tabs">
    <div class="wa-tab active" onclick="showWaSub('wa-painel',this)">📱 Painel</div>
    <div class="wa-tab" onclick="showWaSub('wa-disparo',this)">🚀 Disparo</div>
    <div class="wa-tab" onclick="showWaSub('wa-config',this)">⚙️ Configuração</div>
    <div class="wa-tab" onclick="showWaSub('wa-chat',this)">💬 Chat</div>
  </div>

  <!-- SUB: Painel -->
  <div class="wa-sub active" id="wa-painel">
    <div class="kpi-grid" style="grid-template-columns:repeat(8,1fr);margin-bottom:24px" id="wa-kpis">
      <div class="kpi-card" style="border-color:#25d36633">
        <div class="kpi-label">Total Agenda</div>
        <div class="kpi-value blue" id="wa-total">0</div>
        <div class="kpi-sub">agendamentos</div>
      </div>
      <div class="kpi-card green">
        <div class="kpi-label">Confirmados</div>
        <div class="kpi-value green" id="wa-conf">0</div>
        <div class="kpi-sub" id="wa-conf-pct">0%</div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-label">Não Atendeu</div>
        <div class="kpi-value red" id="wa-nao">0</div>
        <div class="kpi-sub" id="wa-nao-pct">0%</div>
      </div>
      <div class="kpi-card" style="border-color:#7c3aed33">
        <div class="kpi-label">Reagendados</div>
        <div class="kpi-value" style="color:#7c3aed" id="wa-reag">0</div>
        <div class="kpi-sub" id="wa-reag-pct">0%</div>
      </div>
      <div class="kpi-card yellow">
        <div class="kpi-label">Pendentes</div>
        <div class="kpi-value yellow" id="wa-pend">0</div>
        <div class="kpi-sub" id="wa-pend-pct">0%</div>
      </div>
      <div class="kpi-card" style="border-color:#60a5fa33">
        <div class="kpi-label">Entregues</div>
        <div class="kpi-value" style="color:#60a5fa" id="wa-entr">0</div>
        <div class="kpi-sub" id="wa-entr-pct">0%</div>
      </div>
      <div class="kpi-card" style="border-color:#f9731633">
        <div class="kpi-label">Conveniente</div>
        <div class="kpi-value" style="color:#f97316" id="wa-conv">0</div>
        <div class="kpi-sub" id="wa-conv-pct">0%</div>
      </div>
      <div class="kpi-card" style="border-color:#25d36633">
        <div class="kpi-label">Taxa Confirmação</div>
        <div class="kpi-value green" id="wa-taxa">0%</div>
        <div class="kpi-sub">confirmados/total</div>
      </div>
    </div>

    <div class="section-title">📋 Clientes da Agenda</div>
    <div class="wa-cfg-row" style="flex-wrap:wrap">
      <input class="wa-cfg-input" id="wa-search" placeholder="🔍 Buscar cliente..." oninput="waFilterTable()" style="max-width:200px">
      <div style="display:flex;align-items:center;gap:6px;background:#111520;border:1px solid #1c2237;border-radius:8px;padding:4px 10px;">
        <span style="font-size:11px;color:#64748b">De:</span><input type="date" id="wa-f-d1" onchange="waFilterTable()" style="background:transparent;border:none;color:#e8eaf6;font-size:11px;outline:none;font-family:var(--font-mono)">
        <span style="font-size:11px;color:#64748b">Ate:</span><input type="date" id="wa-f-d2" onchange="waFilterTable()" style="background:transparent;border:none;color:#e8eaf6;font-size:11px;outline:none;font-family:var(--font-mono)">
      </div>
      <div class="wa-dd-wrap">
        <div class="wa-dd-btn" onclick="waToggleDD('dd-status', event)"><span id="lbl-status">Todos Status</span> <span style="font-size:10px">▼</span></div>
        <div class="wa-dd-menu" id="dd-status">
          <label class="wa-dd-item"><input type="checkbox" value="cancelamento-do-contrato" onchange="waFilterTable()"> ❌ Cancelado</label>
          <label class="wa-dd-item"><input type="checkbox" value="pendente" onchange="waFilterTable()"> ⏳ Pendente</label>
          <label class="wa-dd-item"><input type="checkbox" value="confirmado" onchange="waFilterTable()"> ✅ Confirmado</label>
          <label class="wa-dd-item"><input type="checkbox" value="nao-atendido" onchange="waFilterTable()"> 📵 Não Atendeu</label>
          <label class="wa-dd-item"><input type="checkbox" value="reagendado" onchange="waFilterTable()"> 🔁 Reagendado</label>
          <label class="wa-dd-item"><input type="checkbox" value="entregue" onchange="waFilterTable()"> 📤 Entregue</label>
          <label class="wa-dd-item"><input type="checkbox" value="entregue-d1" onchange="waFilterTable()"> 📥 Entregue D-1</label>
          <label class="wa-dd-item"><input type="checkbox" value="entregue-d0" onchange="waFilterTable()"> 📨 Entregue D-0</label>
          <label class="wa-dd-item"><input type="checkbox" value="entregue-pos" onchange="waFilterTable()"> 📤 Entregue Pós</label>
          <label class="wa-dd-item"><input type="checkbox" value="conveniente" onchange="waFilterTable()"> 🟡 Conveniente</label>
          <label class="wa-dd-item"><input type="checkbox" value="normalizado" onchange="waFilterTable()"> NORMALIZADO</label>
          <label class="wa-dd-item"><input type="checkbox" value="sem-contato" onchange="waFilterTable()"> SEM CONTATO</label>
          <label class="wa-dd-item"><input type="checkbox" value="resolvido" onchange="waFilterTable()"> RESOLVIDO</label>
          <label class="wa-dd-item"><input type="checkbox" value="aberto-reparo" onchange="waFilterTable()"> ABERTO REPARO</label>
          <label class="wa-dd-item"><input type="checkbox" value="problema-na-rede" onchange="waFilterTable()"> PROBLEMA NA REDE</label>
          <label class="wa-dd-item"><input type="checkbox" value="central" onchange="waFilterTable()"> CENTRAL</label>
          <label class="wa-dd-item"><input type="checkbox" value="cancelamento-do-contrato" onchange="waFilterTable()"> CANCELAMENTO DO CONTRATO</label>
          <label class="wa-dd-item"><input type="checkbox" value="agendado" onchange="waFilterTable()"> AGENDADO</label>
          <label class="wa-dd-item"><input type="checkbox" value="suspenso-por-debito" onchange="waFilterTable()"> SUSPENSO POR DÉBITO</label>
          <label class="wa-dd-item"><input type="checkbox" value="sem-retorno-supervisao" onchange="waFilterTable()"> SEM RETORNO SUPERVISÃO</label>
          <label class="wa-dd-item"><input type="checkbox" value="numero-nao-pertence" onchange="waFilterTable()"> NÚMERO NÃO PERTENCE</label>
          <label class="wa-dd-item"><input type="checkbox" value="area-de-risco" onchange="waFilterTable()"> ÁREA DE RISCO</label>
          <label class="wa-dd-item"><input type="checkbox" value="nao-se-encontra" onchange="waFilterTable()"> NÃO SE ENCONTRA</label>
          <label class="wa-dd-item"><input type="checkbox" value="solicitou-upgrade" onchange="waFilterTable()"> SOLICITOU UPGRADE</label>
          <label class="wa-dd-item"><input type="checkbox" value="bloqueado" onchange="waFilterTable()"> 🚫 Bloqueado</label>
        </div>
      </div>
      <div class="wa-dd-wrap">
        <div class="wa-dd-btn" onclick="waToggleDD('dd-city', event)"><span id="lbl-city">Todas Cidades</span> <span style="font-size:10px">▼</span></div>
        <div class="wa-dd-menu" id="dd-city"></div>
      </div>
      <div class="wa-dd-wrap">
        <div class="wa-dd-btn" onclick="waToggleDD('dd-tipo', event)"><span id="lbl-tipo">Todos Tipos</span> <span style="font-size:10px">▼</span></div>
        <div class="wa-dd-menu" id="dd-tipo"></div>
      </div>
      <div class="wa-dd-wrap">
        <div class="wa-dd-btn" onclick="waToggleDD('dd-statusofs', event)"><span id="lbl-statusofs">Status OFS</span> <span style="font-size:10px">▼</span></div>
        <div class="wa-dd-menu" id="dd-statusofs"></div>
      </div>
      <div class="wa-dd-wrap">
        <div class="wa-dd-btn" onclick="waToggleDD('dd-fase', event)"><span id="lbl-fase">Fase</span> <span style="font-size:10px">▼</span></div>
        <div class="wa-dd-menu" id="dd-fase">
          <label class="wa-dd-item"><input type="checkbox" value="d1" onchange="waFilterTable()"> 🔵 D-1 (Amanhã)</label>
          <label class="wa-dd-item"><input type="checkbox" value="d0" onchange="waFilterTable()"> 🟡 D-0 (Hoje)</label>
          <label class="wa-dd-item"><input type="checkbox" value="pos" onchange="waFilterTable()"> 🟠 Pós (Concluído)</label>
        </div>
      </div>
      <button class="wa-cfg-btn" onclick="waSelectAll()" style="font-size:11px;padding:6px 12px">✅ Selecionar Todos</button>
      <button class="wa-cfg-btn secondary" onclick="waSelectNone()" style="font-size:11px;padding:6px 12px">❌ Limpar</button>
      <button class="wa-cfg-btn secondary" onclick="waExportCSV()">📥 Exportar CSV</button>
      <button class="wa-cfg-btn secondary" onclick="waExportFull()" style="background:rgba(37,211,102,.1);border-color:#25d36650;color:#25d366">📊 Exportar Completo</button>
    </div>
    <div class="chart-card wa-tbl-wrap">
      <table class="data-table" id="wa-client-table">
        <thead><tr>
          <th style="width:36px;text-align:center" onclick="event.stopPropagation()"><input type="checkbox" id="wa-chk-all" onclick="waToggleAll(this)" style="accent-color:#25d366;cursor:pointer;width:14px;height:14px"></th>
          <th class="sortable" onclick="waSortTable('nome')">Cliente</th>
          <th class="sortable" onclick="waSortTable('phone')">Telefone</th>
          <th class="sortable" onclick="waSortTable('data')">Data</th>
          <th class="sortable" onclick="waSortTable('intervalo')">Intervalo</th>
          <th class="sortable" onclick="waSortTable('endereco')">Endereço</th>
          <th class="sortable" onclick="waSortTable('cidade')">Cidade</th>
          <th class="sortable" onclick="waSortTable('tipo')">Tipo Atividade</th>
          <th>Fase</th>
          <th class="sortable" onclick="waSortTable('statusOfs')">Status OFS</th>
          <th class="sortable" onclick="waSortTable('status')">Status Atual</th>
          <th>WhatsApp</th>
        </tr></thead>
        <tbody id="wa-tbody"></tbody>
      </table>
    </div>
    <div id="wa-empty" style="text-align:center;padding:40px;color:#64748b">
      <div style="font-size:40px;margin-bottom:12px">📅</div>
      <div style="font-size:16px;font-weight:700;margin-bottom:6px">Nenhuma agenda carregada</div>
      <div style="font-size:13px">Importe CSV/Excel na aba Disparo ou conecte ao backend</div>
    </div>
  </div>

  <!-- SUB: Disparo -->
  <div class="wa-sub" id="wa-disparo">
    <div class="grid-2">
      <div>
        <div class="section-title">📁 Importar Agenda</div>
        <div class="chart-card">
          <div class="wa-file-drop" onclick="document.getElementById('wa-csv-input').click()" id="wa-drop-zone">
            <div style="font-size:32px;margin-bottom:8px">⬆️</div>
            <div style="font-size:14px;font-weight:600;margin-bottom:4px">Arraste ou clique para importar</div>
            <div style="font-size:12px;color:#64748b;margin-bottom:4px">CSV, Excel, ODS, TSV — qualquer formato</div>
            <div style="font-size:11px;color:#f97316;background:rgba(249,115,22,.08);border:1px solid rgba(249,115,22,.2);border-radius:6px;padding:4px 10px;display:inline-block">💡 Para múltiplas planilhas: selecione todas juntas com Ctrl+Click</div>
          </div>
          <input type="file" id="wa-csv-input" accept=".csv,.xlsx,.xls,.xlsb,.ods,.tsv,.txt" multiple style="display:none" onchange="waHandleFile(event)">
          <button class="wa-cfg-btn secondary" onclick="waClearAgenda()" style="width:100%;margin-top:12px;color:#ff4d6d;border-color:#ff4d6d33">
            🗑️ Limpar Toda a Agenda
          </button>
        </div>
        <div class="section-title" style="margin-top:20px">📝 Templates de Mensagem <span id="wa-tpl-count" style="color:#25d366;font-weight:600;font-size:12px"></span></div>
        <div class="chart-card">
          <!-- SELETOR DE TEMPLATE META -->
          <div id="wa-meta-tpl-wrapper" style="margin-bottom:14px;background:rgba(37,211,102,.06);border:1px solid rgba(37,211,102,.18);border-radius:8px;padding:12px 14px">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
              <span style="font-size:13px;font-weight:700;color:#25d366">✅ Usar Template Meta Aprovado</span>
              <button class="wa-cfg-btn" onclick="waLoadMetaTemplates()" style="font-size:11px;padding:4px 12px;height:auto;background:#25d366;border:none;color:#fff;border-radius:6px;cursor:pointer">🔄 Carregar Templates</button>
            </div>
            <select class="wa-cfg-input" id="wa-meta-tpl-select" onchange="waApplyMetaTemplate()" style="width:100%;margin-bottom:6px;font-size:12px;cursor:pointer;background:#111520;color:#e2e8f0;border:1px solid #1c2237;border-radius:6px;padding:8px 12px">
              <option value="">— Digitar mensagem manualmente —</option>
            </select>
            <div id="wa-meta-tpl-preview-box" style="display:none;background:rgba(37,211,102,.08);border-radius:6px;padding:8px 10px;font-size:11px;color:#e2e8f0;white-space:pre-wrap;max-height:120px;overflow-y:auto;border:1px solid rgba(37,211,102,.12)"></div>
          </div>
          <!-- FIM SELETOR DE TEMPLATE META -->
          <div style="font-size:11px;color:#64748b;margin-bottom:8px;font-family:var(--font-mono)">
            Variáveis: <span style="color:#25d366">{{nome}}</span> <span style="color:#25d366">{{data}}</span> <span style="color:#25d366">{{cidade}}</span> <span style="color:#25d366">{{horario}}</span> <span style="color:#25d366">{{intervalo}}</span> <span style="color:#25d366">{{tipo}}</span> <span style="color:#60a5fa">{{remetente}}</span>
          </div>

          <div id="wa-tpl-boxes">
            <div class="wa-tpl-box" style="margin-bottom:10px">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">
                <span style="font-size:11px;font-weight:700;color:#25d366">Mensagem 1 (obrigatória)</span>
                <input class="wa-cfg-input" id="wa-tpl-name-1" placeholder="Nome Meta (ex: msg_1)" style="font-size:10px;padding:2px 6px;height:22px;width:120px">
              </div>
              <textarea class="wa-cfg-input wa-tpl" id="wa-template-1" rows="4" style="width:100%;resize:vertical" oninput="waUpdatePreview()" placeholder="Olá {{nome}}! 👋"></textarea>
            </div>

          </div>
          <div style="margin-top:6px;font-size:11px;color:#64748b">Prévia (Mensagem 1):</div>
          <div id="wa-preview" style="background:rgba(37,211,102,.05);border:1px solid rgba(37,211,102,.2);border-radius:8px;padding:12px;font-size:12px;color:#94a3b8;margin-top:4px;white-space:pre-wrap">—</div>
        </div>
      </div>
      <div>
        <div class="section-title">🚀 Controle de Envio</div>
        <div class="chart-card">
          <div style="font-size:13px;margin-bottom:12px"><strong id="wa-sel-count">0</strong> clientes selecionados</div>
          <div style="margin-bottom:12px">
            <div style="font-size:11px;color:#64748b;margin-bottom:6px">Modo de Envio:</div>
            <div style="display:flex;gap:0;border:1px solid #1c2237;border-radius:8px;overflow:hidden">
              <button class="wa-cfg-btn" id="wa-mode-fixed" onclick="waSetMode('fixed')" style="flex:1;border-radius:0;font-size:11px;padding:8px">⏱️ Intervalo Fixo</button>
              <button class="wa-cfg-btn secondary" id="wa-mode-window" onclick="waSetMode('window')" style="flex:1;border-radius:0;border:none;font-size:11px;padding:8px">🎲 Janela Aleatória</button>
            </div>
          </div>
          <div id="wa-ctrl-fixed" class="wa-cfg-row">
            <span style="font-size:12px;color:#64748b">Intervalo (seg):</span>
            <input class="wa-cfg-input" type="number" id="wa-delay" value="5" min="3" max="30" style="width:80px">
          </div>
          <div id="wa-ctrl-window" class="wa-cfg-row" style="display:none">
            <span style="font-size:12px;color:#64748b">Janela (min):</span>
            <input class="wa-cfg-input" type="number" id="wa-window" value="20" min="1" max="120" style="width:80px">
            <span style="font-size:10px;color:#94a3b8">mensagens saem em horários aleatórios dentro desse tempo</span>
          </div>
          <div style="margin-bottom:12px;margin-top:16px">
            <div style="font-size:11px;color:#64748b;margin-bottom:6px">WhatsApp Remetente:</div>
            <select class="wa-cfg-input" id="wa-active-instance" style="width:100%;margin-bottom:8px"><option value="">Carregando...</option></select>
          </div>
          <div style="margin-bottom:12px">
            <div style="font-size:11px;color:#64748b;margin-bottom:6px">Nome do Remetente <span style="color:#60a5fa">(variável {{remetente}})</span>:</div>
            <input class="wa-cfg-input" type="text" id="wa-sender-name" value="" placeholder="Ex: Rodrigo, Equipe Svoboda..." style="width:100%" oninput="waUpdatePreview()">
          </div>
          <button class="wa-cfg-btn" onclick="waFireDisparo()" id="wa-fire-btn" style="width:100%;padding:14px;font-size:15px">
            🚀 Disparar WhatsApp
          </button>
          <div id="wa-progress" style="display:none;margin-top:16px">
            <div style="font-size:12px;color:#64748b;font-family:var(--font-mono)" id="wa-prog-txt">0/0</div>
            <div style="background:#1c2237;border-radius:4px;height:8px;margin-top:6px;overflow:hidden">
              <div id="wa-prog-fill" style="height:100%;background:linear-gradient(90deg,#128c7e,#25d366);width:0%;transition:width .3s;border-radius:4px"></div>
            </div>
          </div>
        </div>
        <div class="section-title" style="margin-top:20px">📊 Histórico de Campanhas</div>
        <div class="chart-card" id="wa-campaigns" style="max-height:200px;overflow-y:auto">
          <div style="text-align:center;color:#64748b;font-size:12px;padding:20px">Nenhuma campanha ainda</div>
        </div>
      </div>
    </div>

    <!-- SEÇÃO: Fluxo Automático de Respostas -->
    <div style="margin-top:24px">
      <div class="section-title">🤖 Fluxo Automático de Respostas</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">

        <!-- Card Configuração -->
        <div class="chart-card">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
            <span style="font-size:13px;font-weight:700;color:#25d366">Configurar Fluxo</span>
            <label style="display:flex;align-items:center;gap:8px;cursor:pointer">
              <span style="font-size:11px;color:#64748b">Ativo:</span>
              <input type="checkbox" id="fluxo-ativo" onchange="waFluxoToggle(this.checked)" style="width:16px;height:16px;accent-color:#25d366;cursor:pointer">
            </label>
          </div>

          <div style="margin-bottom:10px">
            <div style="font-size:11px;color:#64748b;margin-bottom:4px">⏱️ Aguardar (segundos) antes de responder:</div>
            <input class="wa-cfg-input" type="number" id="fluxo-delay" value="10" min="0" max="300" style="width:100px">
          </div>

          <div style="margin-bottom:10px">
            <div style="font-size:11px;color:#25d366;font-weight:600;margin-bottom:4px">✅ Mensagem quando cliente responder SIM:</div>
            <textarea class="wa-cfg-input" id="fluxo-msg-sim" rows="3" style="width:100%;resize:vertical;font-size:12px" placeholder="Que ótimo! Ficamos felizes que tudo correu bem. 😊">Que ótimo! Ficamos felizes que tudo correu bem. 😊 Qualquer dúvida, estamos à disposição!</textarea>
          </div>

          <div style="margin-bottom:10px">
            <div style="font-size:11px;color:#ff4d6d;font-weight:600;margin-bottom:4px">❌ Mensagem quando cliente responder NÃO:</div>
            <textarea class="wa-cfg-input" id="fluxo-msg-nao" rows="3" style="width:100%;resize:vertical;font-size:12px" placeholder="Lamentamos o ocorrido!">Lamentamos o ocorrido! Nossa equipe de suporte será acionada para resolver o problema. ⚙️</textarea>
          </div>

          <div style="margin-bottom:14px">
            <div style="font-size:11px;color:#94a3b8;font-weight:600;margin-bottom:4px">💬 Mensagem para qualquer outra resposta:</div>
            <textarea class="wa-cfg-input" id="fluxo-msg-outro" rows="3" style="width:100%;resize:vertical;font-size:12px" placeholder="Obrigado pelo retorno!">Obrigado pelo retorno! Em breve um de nossos atendentes entrará em contato. 🙏</textarea>
          </div>

          <button class="wa-cfg-btn" onclick="waFluxoSaveConfig()" style="width:100%">
            💾 Salvar Configuração de Fluxo
          </button>
          <div id="fluxo-save-msg" style="font-size:11px;color:#25d366;margin-top:6px;text-align:center;display:none">✓ Configuração salva!</div>

          <div style="margin-top:10px;font-size:10px;color:#64748b;background:rgba(37,211,102,.04);border:1px solid rgba(37,211,102,.1);border-radius:6px;padding:8px">
            <strong>Como funciona:</strong> Ao disparar com fluxo ativo, o servidor monitora respostas 24/7 e envia a mensagem certa automaticamente.
          </div>
        </div>

        <!-- Card Fluxos Ativos -->
        <div class="chart-card">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
            <span style="font-size:13px;font-weight:700;color:#25d366">Fluxos Ativos</span>
            <div style="display:flex;gap:8px">
              <button class="wa-cfg-btn secondary" onclick="waFluxoLoadAtivos()" style="font-size:11px;padding:4px 10px;height:auto">🔄</button>
              <button class="wa-cfg-btn secondary" onclick="waFluxoLimpar()" style="font-size:11px;padding:4px 10px;height:auto;color:#ff4d6d;border-color:#ff4d6d33">🗑️ Limpar concluídos</button>
            </div>
          </div>
          <div id="fluxo-status-bar" style="display:flex;gap:12px;margin-bottom:10px;font-size:11px">
            <span>⏳ <strong id="fluxo-cnt-aguardando">0</strong> aguardando</span>
            <span style="color:#25d366">✅ <strong id="fluxo-cnt-respondidos">0</strong> respondidos</span>
            <span style="color:#64748b">🚫 <strong id="fluxo-cnt-cancelados">0</strong> cancelados</span>
          </div>
          <div id="fluxo-table-wrap" style="max-height:320px;overflow-y:auto">
            <div style="text-align:center;color:#64748b;font-size:12px;padding:30px" id="fluxo-empty">
              Nenhum fluxo ativo. Dispare com o fluxo ativado para começar.
            </div>
            <table id="fluxo-table" style="width:100%;border-collapse:collapse;font-size:11px;display:none">
              <thead>
                <tr style="color:#64748b;border-bottom:1px solid #1c2237">
                  <th style="text-align:left;padding:4px 6px;font-weight:600">Cliente</th>
                  <th style="text-align:left;padding:4px 6px;font-weight:600">Status</th>
                  <th style="text-align:left;padding:4px 6px;font-weight:600">Resposta</th>
                  <th style="text-align:center;padding:4px 6px;font-weight:600">Ação</th>
                </tr>
              </thead>
              <tbody id="fluxo-tbody"></tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
    <!-- FIM SEÇÃO FLUXO -->

    <!-- SEÇÃO: Respostas Automáticas dos Botões Meta (editável) -->
    <div style="margin-top:24px">
      <style>
      .btn-cfg-section{{background:#0d1117;border:1px solid #1c2237;border-radius:12px;padding:20px}}
      .btn-cfg-title{{font-size:15px;font-weight:800;color:#25d366;margin-bottom:16px;display:flex;align-items:center;gap:8px}}
      .btn-cfg-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
      .btn-cfg-card{{background:#111520;border:1px solid #1c2237;border-radius:10px;padding:14px}}
      .btn-cfg-label{{font-size:11px;font-weight:700;margin-bottom:6px;display:flex;align-items:center;gap:6px}}
      .btn-cfg-label.green{{color:#25d366}}
      .btn-cfg-label.blue{{color:#60a5fa}}
      .btn-cfg-label.red{{color:#ff4d6d}}
      .btn-cfg-label.purple{{color:#a78bfa}}
      .btn-cfg-label.orange{{color:#fb923c}}
      .btn-cfg-textarea{{width:100%;background:#0d1117;border:1px solid #1c2237;border-radius:8px;padding:8px 12px;color:#e8eaf6;font-size:12px;font-family:inherit;resize:vertical;outline:none;box-sizing:border-box}}
      .btn-cfg-textarea:focus{{border-color:#25d366}}
      .btn-cfg-save{{background:#25d366;color:#022c22;border:none;padding:12px 24px;border-radius:10px;font-size:14px;font-weight:700;cursor:pointer;width:100%;margin-top:16px;font-family:inherit;transition:all .2s}}
      .btn-cfg-save:hover{{background:#128c7e;color:#fff}}
      .btn-cfg-status{{text-align:center;font-size:12px;margin-top:8px;color:#25d366;display:none}}
      .btn-cfg-flow-title{{font-size:13px;font-weight:700;color:#94a3b8;margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid #1c2237;grid-column:1/-1}}
      </style>
      <div class="btn-cfg-section" id="btn-cfg-section">
        <div class="btn-cfg-title">🤖 Respostas Automáticas dos Botões <span style="font-size:11px;color:#64748b;font-weight:400">(editável — use NOME para inserir o primeiro nome do cliente)</span></div>
        <div class="btn-cfg-grid">
          <div class="btn-cfg-flow-title">🔵 Fluxo A — Confirmação de Visita</div>
          <div class="btn-cfg-card">
            <div class="btn-cfg-label green">✅ Botão: "SIM, confirmo" → confirmado</div>
            <textarea class="btn-cfg-textarea" id="bcfg-sim-confirmo" rows="3"></textarea>
          </div>
          <div class="btn-cfg-card">
            <div class="btn-cfg-label purple">🔄 Botão: "Preciso reagendar" → reagendado</div>
            <textarea class="btn-cfg-textarea" id="bcfg-preciso-reagendar" rows="3"></textarea>
          </div>
          <div class="btn-cfg-card">
            <div class="btn-cfg-label red">❌ Botão: "Cancelar" → não atendido</div>
            <textarea class="btn-cfg-textarea" id="bcfg-cancelar" rows="3"></textarea>
          </div>
          <div class="btn-cfg-flow-title">🟠 Fluxo B — Recolhimento de Equipamento</div>
          <div class="btn-cfg-card">
            <div class="btn-cfg-label blue">📅 Botão: "Agendar" → agendado</div>
            <textarea class="btn-cfg-textarea" id="bcfg-agendar" rows="3"></textarea>
          </div>
          <div class="btn-cfg-card">
            <div class="btn-cfg-label green">✅ Botão: "Já devolvi" → resolvido</div>
            <textarea class="btn-cfg-textarea" id="bcfg-ja-devolvi" rows="3"></textarea>
          </div>
          <div class="btn-cfg-flow-title">🟢 Fluxo C — Pesquisa de Qualidade</div>
          <div class="btn-cfg-card">
            <div class="btn-cfg-label green">😊 Botão: "SIM, tudo certo" → satisfeito</div>
            <textarea class="btn-cfg-textarea" id="bcfg-sim-tudo-certo" rows="3"></textarea>
          </div>
          <div class="btn-cfg-card">
            <div class="btn-cfg-label red">😟 Botão: "NÃO, tenho problema" → problema aberto</div>
            <textarea class="btn-cfg-textarea" id="bcfg-nao-tenho-problema" rows="3"></textarea>
          </div>
          <div class="btn-cfg-card">
            <div class="btn-cfg-label orange">🗣️ Botão: "Quero falar com alguém" → problema aberto</div>
            <textarea class="btn-cfg-textarea" id="bcfg-quero-falar" rows="3"></textarea>
          </div>
        </div>
        <button class="btn-cfg-save" onclick="btnCfgSave()">💾 Salvar Respostas Automáticas</button>
        <div class="btn-cfg-status" id="btn-cfg-status">✓ Salvo com sucesso!</div>
      </div>
    </div>
    <!-- FIM SEÇÃO BOTÕES -->

  </div>

  <!-- SUB: Configuração -->
  <div class="wa-sub" id="wa-config">
    <div class="grid-2">
      <div class="chart-card">
        <div class="chart-title">🔗 Conexão com Backend</div>
        <div class="wa-cfg-row">
          <input class="wa-cfg-input" id="wa-backend-url" placeholder="https://svoboda.rtflowapp.com/api/agenda" value="{backend_url}">
          <input class="wa-cfg-input" id="wa-api-key" placeholder="API Key" value="{api_key}" style="max-width:200px">
          <input class="wa-cfg-input" id="wa-instance-name" placeholder="Perfil (ex: operador1)" value="svoboda" style="max-width:150px">
          <button class="wa-cfg-btn" onclick="waTestConnection()">Testar</button>
        </div>
        <div id="wa-conn-status" style="font-size:12px;color:#64748b;margin-top:8px">
          <span class="wa-status-dot offline"></span> Não conectado
        </div>
        <div style="margin-top:16px;font-size:11px;color:#475569">
          Configure o IP do VPS onde o backend WhatsApp está rodando.<br>
          A API Key é definida na variável AGENDA_API_KEY do backend.
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-title">🔐 Credenciais da API Oficial (Meta)</div>
        <div style="display:flex;flex-direction:column;gap:8px;margin-top:12px">
          <input class="wa-cfg-input" id="wa-meta-token" type="password" placeholder="Token de Acesso Permanente (Meta)">
          <input class="wa-cfg-input" id="wa-meta-phone" placeholder="Phone Number ID (Meta)">
          <button class="wa-cfg-btn" onclick="waSaveMetaConfig()">Salvar Credenciais da API</button>
        </div>
        <div id="wa-whatsapp-status" style="text-align:center;padding:12px;color:#64748b;margin-top:10px">
          <span class="wa-status-dot offline"></span> Conecte o backend primeiro
        </div>
      </div>
    </div>
  </div>

  <!-- SUB: Chat -->
  <style>
  .chat-layout{{display:grid;grid-template-columns:320px 1fr;flex:1;min-height:0;border:1px solid #1c2237;border-radius:12px;overflow:hidden;background:#0d1117}}
  .chat-sidebar{{display:flex;flex-direction:column;border-right:1px solid #1c2237;background:#111520}}
  .chat-sidebar-header{{padding:14px 16px;border-bottom:1px solid #1c2237;display:flex;align-items:center;gap:10px}}
  .chat-sidebar-header input{{flex:1;background:#1a1e28;border:1px solid #2d3748;border-radius:8px;padding:8px 12px;color:#e2e8f0;font-size:12px;outline:none;font-family:inherit}}
  .chat-sidebar-header input::placeholder{{color:#475569}}
  .chat-sidebar-header input:focus{{border-color:#25d366}}
  .chat-contact-list{{flex:1;overflow-y:auto}}
  .chat-contact{{display:flex;align-items:center;gap:12px;padding:12px 16px;cursor:pointer;border-bottom:1px solid rgba(28,34,55,.4);transition:background .15s}}
  .chat-contact:hover{{background:rgba(255,255,255,.03)}}
  .chat-contact.active{{background:rgba(37,211,102,.08);border-left:3px solid #25d366}}
  .chat-contact-avatar{{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#25d366,#128c7e);display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;color:#fff;font-weight:700}}
  .chat-contact-info{{flex:1;min-width:0}}
  .chat-contact-name{{font-size:13px;font-weight:600;color:#e2e8f0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
  .chat-contact-preview{{font-size:11px;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px}}
  .chat-contact-meta{{display:flex;flex-direction:column;align-items:flex-end;gap:4px;flex-shrink:0}}
  .chat-contact-time{{font-size:10px;color:#475569;font-family:'DM Mono',monospace}}
  .chat-unread-badge{{background:#25d366;color:#022c22;font-size:10px;font-weight:700;padding:2px 7px;border-radius:20px;min-width:20px;text-align:center}}
  .chat-main{{display:flex;flex-direction:column;background:#0a0d14;overflow:hidden;min-height:0;height:100%}}
  .chat-main-header{{padding:14px 20px;border-bottom:1px solid #1c2237;display:flex;align-items:center;gap:12px;background:#111520;flex-shrink:0}}
  .chat-main-avatar{{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#25d366,#128c7e);display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;color:#fff;font-weight:700}}
  .chat-main-name{{font-size:14px;font-weight:700;color:#e2e8f0}}
  .chat-main-phone{{font-size:11px;color:#94a3b8;font-family:'DM Mono',monospace}}
  .chat-main-client{{font-size:12px;color:#25d366;font-weight:600;margin-top:1px}}
  .chat-contact-phone{{font-size:10px;color:#475569;font-family:'DM Mono',monospace;margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
  .chat-messages{{overflow-y:auto;padding:16px 20px;display:flex;flex-direction:column;gap:6px;min-height:0}}
  .chat-msg{{display:flex;align-items:flex-end;gap:6px}}
  .chat-msg.sent{{flex-direction:row-reverse}}
  .chat-msg-bubble{{max-width:75%;padding:8px 14px;border-radius:12px;font-size:13px;line-height:1.5;word-break:break-word}}
  .chat-msg.received .chat-msg-bubble{{background:#1a1e28;border-bottom-left-radius:2px;color:#e2e8f0}}
  .chat-msg.sent .chat-msg-bubble{{background:linear-gradient(135deg,#128c7e,#25d366);color:#fff;border-bottom-right-radius:2px}}
  .chat-msg-time{{font-size:10px;color:#475569;font-family:'DM Mono',monospace;white-space:nowrap}}
  .chat-date-divider{{text-align:center;font-size:10px;color:#475569;padding:8px 0;font-family:'DM Mono',monospace}}
  .chat-date-divider span{{background:#1a1e28;padding:3px 12px;border-radius:6px}}
  .chat-main-active-panel{{display:none;grid-template-rows:auto 1fr auto;height:100%;overflow:hidden}}
  .chat-reply-area{{padding:14px 20px;border-top:1px solid #1c2237;display:flex;gap:10px;align-items:flex-end;background:#111520;flex-shrink:0}}
  .chat-reply-input{{flex:1;background:#1a1e28;border:1px solid #2d3748;border-radius:10px;padding:10px 14px;color:#e2e8f0;font-size:13px;font-family:inherit;outline:none;resize:none;min-height:40px;max-height:120px}}
  .chat-reply-input:focus{{border-color:#25d366}}
  .chat-reply-input::placeholder{{color:#475569}}
  .chat-reply-btn{{padding:10px 16px;background:#25d366;color:#fff;border:none;border-radius:10px;cursor:pointer;font-size:16px;flex-shrink:0;transition:background .15s}}
  .chat-reply-btn:hover{{background:#128c7e}}
  .chat-empty-main{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;opacity:.4}}
  .chat-sidebar-count{{font-size:10px;color:#475569;padding:6px 16px;border-bottom:1px solid rgba(28,34,55,.4);font-family:'DM Mono',monospace}}
  @media(max-width:900px){{.chat-layout{{grid-template-columns:1fr;min-height:400px}}.chat-sidebar{{max-height:300px}}}}
  body.chat-mode{{overflow:hidden!important;height:100vh!important}}
  body.chat-mode .filter-bar{{display:none!important}}
  body.chat-mode .nav{{display:none!important}}
  body.chat-mode .footer{{display:none!important}}
  body.chat-mode #whatsapp-agenda{{padding:0!important;margin:0!important;height:calc(100vh - 66px)!important;max-height:calc(100vh - 66px)!important;display:flex!important;flex-direction:column;overflow:hidden!important}}
  body.chat-mode .wa-tabs{{flex-shrink:0;padding:8px 16px;margin-bottom:0}}
  body.chat-mode #wa-chat.active{{flex:1!important;display:flex!important;flex-direction:column;min-height:0!important;max-height:100%!important;overflow:hidden!important}}
  body.chat-mode .chat-layout{{flex:1!important;min-height:0!important;max-height:100%!important;overflow:hidden!important}}
  body.chat-mode .chat-main{{max-height:100%!important;overflow:hidden!important}}
  body.chat-mode .chat-main-active-panel{{max-height:100%!important;overflow:hidden!important}}
  body.chat-mode .chat-messages{{flex:1!important;min-height:0!important;overflow-y:auto!important}}
  body.chat-mode .chat-reply-area{{flex-shrink:0!important}}
  body.chat-mode .chat-sidebar{{max-height:100%!important;overflow:hidden!important}}
  body.chat-mode .chat-contact-list{{overflow-y:auto!important}}
  .chat-msg-image{{max-width:250px;border-radius:8px;cursor:pointer;transition:transform .2s}}
  .chat-msg-image:hover{{transform:scale(1.05)}}
  .chat-msg-audio{{width:220px;height:32px;border-radius:4px}}
  .chat-msg-location{{display:inline-flex;align-items:center;gap:6px;padding:4px 8px;background:rgba(37,211,102,.1);border-radius:6px;text-decoration:none;color:#25d366;font-size:12px;font-weight:600}}
  .chat-msg-location:hover{{background:rgba(37,211,102,.2)}}
  .chat-mic-btn{{padding:10px 14px;background:transparent;color:#94a3b8;border:1px solid #2d3748;border-radius:10px;cursor:pointer;font-size:16px;flex-shrink:0;transition:all .2s}}
  .chat-mic-btn:hover{{background:rgba(37,211,102,.1);color:#25d366;border-color:#25d366}}
  .chat-mic-btn.recording{{background:rgba(239,68,68,.15);color:#ef4444;border-color:#ef4444;animation:pulse-rec 1s infinite}}
  @keyframes pulse-rec{{0%,100%{{opacity:1}}50%{{opacity:.5}}}}
  .chat-audio-timer{{font-size:11px;color:#ef4444;font-family:'DM Mono',monospace;min-width:40px;text-align:center;display:none}}
  .chat-audio-timer.active{{display:block}}
  </style>
  <div class="wa-sub" id="wa-chat">
    <div class="chat-layout">
      <div class="chat-sidebar">
        <div class="chat-sidebar-header">
          <input type="text" id="chat-search-input" placeholder="Buscar número ou nome..." oninput="chatFilterContacts()">
          <button onclick="chatShowNewMsg()" style="width:34px;height:34px;border-radius:8px;background:#25d366;border:none;color:#fff;font-size:18px;cursor:pointer;flex-shrink:0;display:flex;align-items:center;justify-content:center;transition:background .15s" onmouseover="this.style.background='#128c7e'" onmouseout="this.style.background='#25d366'" title="Nova conversa">✏️</button>
        </div>
        <!-- Modal Nova Conversa (inline) -->
        <div id="chat-new-msg-panel" style="display:none;padding:12px 16px;border-bottom:1px solid #1c2237;background:#141824">
          <div style="font-size:11px;color:#94a3b8;margin-bottom:8px;font-weight:600">NOVA CONVERSA</div>
          <input type="text" id="chat-new-phone" placeholder="Número com DDD (ex: 5521999999999)" style="width:100%;background:#1a1e28;border:1px solid #2d3748;border-radius:8px;padding:8px 12px;color:#e2e8f0;font-size:12px;outline:none;font-family:inherit;margin-bottom:8px;box-sizing:border-box" onfocus="this.style.borderColor='#25d366'" onblur="this.style.borderColor='#2d3748'">
          <textarea id="chat-new-text" placeholder="Digite sua mensagem..." rows="2" style="width:100%;background:#1a1e28;border:1px solid #2d3748;border-radius:8px;padding:8px 12px;color:#e2e8f0;font-size:12px;outline:none;font-family:inherit;resize:none;margin-bottom:8px;box-sizing:border-box" onfocus="this.style.borderColor='#25d366'" onblur="this.style.borderColor='#2d3748'"></textarea>
          <div style="display:flex;gap:8px">
            <button onclick="chatSendNewMsg()" style="flex:1;padding:8px;background:#25d366;color:#fff;border:none;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit;transition:background .15s" onmouseover="this.style.background='#128c7e'" onmouseout="this.style.background='#25d366'">📤 Enviar</button>
            <button onclick="chatHideNewMsg()" style="padding:8px 12px;background:#1a1e28;color:#94a3b8;border:1px solid #2d3748;border-radius:8px;font-size:12px;cursor:pointer;font-family:inherit;transition:background .15s" onmouseover="this.style.background='#2d3748'" onmouseout="this.style.background='#1a1e28'">Cancelar</button>
          </div>
        </div>
        <div class="chat-sidebar-count" id="chat-sidebar-count">Carregando conversas...</div>
        <div class="chat-contact-list" id="chat-contact-list"></div>
      </div>
      <div class="chat-main">
        <div class="chat-empty-main" id="chat-empty-main">
          <div style="font-size:48px">💬</div>
          <div style="font-size:14px;color:#475569;text-align:center;max-width:240px;line-height:1.6">Selecione uma conversa para ver o histórico de mensagens</div>
        </div>
        <div id="chat-main-active" class="chat-main-active-panel">
          <div class="chat-main-header">
            <div class="chat-main-avatar" id="chat-main-avatar">📱</div>
            <div>
              <div class="chat-main-name" id="chat-main-name">—</div>
              <div class="chat-main-client" id="chat-main-client"></div>
              <div class="chat-main-phone" id="chat-main-phone">—</div>
            </div>
          </div>
          <div class="chat-messages" id="chat-messages-area"></div>
          <div class="chat-reply-area">
            <textarea class="chat-reply-input" id="chat-reply-text" placeholder="Responder via WhatsApp..." rows="1" onkeydown="if(event.key==='Enter'&&!event.shiftKey){{event.preventDefault();chatSendReply()}}" oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,120)+'px'"></textarea>
            <span class="chat-audio-timer" id="chat-audio-timer">0:00</span>
            <button class="chat-mic-btn" id="chat-mic-btn" onclick="chatToggleRecording()" title="Gravar audio">&#127908;</button>
            <button class="chat-reply-btn" onclick="chatSendReply()">➤</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  
  <!-- MODAL DE IMPORTAÇÃO (mapeamento de colunas) -->
  <div id="wa-import-modal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);z-index:10000;align-items:center;justify-content:center">
    <div style="background:#0d1117;border:1px solid #1c2237;border-radius:16px;width:560px;max-width:95%;max-height:90vh;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 25px 60px rgba(0,0,0,0.6)">
      <div style="padding:20px 24px;border-bottom:1px solid #1c2237;display:flex;justify-content:space-between;align-items:center;background:linear-gradient(135deg,#0d1117,#111520)">
        <div style="display:flex;align-items:center;gap:12px">
          <span style="font-size:24px">📊</span>
          <div>
            <div style="font-weight:800;font-size:16px;color:#e2e8f0">Resultado da Importação</div>
            <div style="font-size:11px;color:#64748b;font-family:var(--font-mono)" id="wa-imp-filename">arquivo.csv</div>
          </div>
        </div>
        <button onclick="waCloseImportModal()" style="background:transparent;border:none;color:#94a3b8;cursor:pointer;font-size:18px">✖</button>
      </div>
      <div style="padding:20px 24px;overflow-y:auto;flex:1" id="wa-imp-body">
        <div style="font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px">Mapeamento de Colunas</div>
        <div id="wa-imp-rows" style="display:flex;flex-direction:column;gap:8px"></div>
      </div>
      <div style="padding:16px 24px;border-top:1px solid #1c2237;display:flex;justify-content:space-between;align-items:center;background:#0a0d14">
        <label style="display:flex;align-items:center;gap:8px;font-size:12px;color:#94a3b8;cursor:pointer"><input type="checkbox" id="wa-imp-remember" style="accent-color:#25d366" checked> Lembrar mapeamento</label>
        <div style="display:flex;gap:10px">
          <button class="wa-cfg-btn secondary" onclick="waCloseImportModal()">Cancelar</button>
          <button class="wa-cfg-btn" onclick="waFinishImport()" id="wa-imp-confirm" style="min-width:180px">✅ Importar 0 linhas</button>
        </div>
      </div>
    </div>
  </div>

  <!-- MODAL DE CHAT -->
  <div id="wa-chat-modal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:9999;align-items:center;justify-content:center">
    <div style="background:#0d1117;border:1px solid #1c2237;border-radius:12px;width:400px;max-width:90%;display:flex;flex-direction:column;height:500px">
      <div style="padding:16px;border-bottom:1px solid #1c2237;display:flex;justify-content:space-between;align-items:center">
        <div style="display:flex;align-items:center;gap:12px">
          <div style="font-weight:700;font-size:16px" id="wa-chat-title">Cliente</div>
          <select id="wa-chat-status" class="wa-cfg-input" style="padding:4px 8px;font-size:11px;height:26px;width:150px;background:#1a1e28;border-color:#2d3748" onchange="waChangeStatusManually(this.value)">
            <option value="pendente">⏳ Pendente</option>
          </select>
        </div>
        <button onclick="document.getElementById('wa-chat-modal').style.display='none'" style="background:transparent;border:none;color:#94a3b8;cursor:pointer;font-size:16px">✖</button>
      </div>
      <div id="wa-chat-msgs" class="wa-msg-list" style="flex:1;border:none;border-radius:0;background:transparent"></div>
      <div style="padding:16px;border-top:1px solid #1c2237;display:flex;gap:8px">
        <select class="wa-cfg-input" id="wa-chat-instance" style="max-width:120px"><option value="">...</option></select>
        <input class="wa-cfg-input" id="wa-chat-input" placeholder="Digite uma mensagem..." onkeypress="if(event.key==='Enter')waSendReply()">
        <button class="wa-cfg-btn" onclick="waSendReply()">Enviar</button>
      </div>
    </div>
  </div>

  <script>
  // ── WhatsApp Agenda State ──
  var waClients=[], waSelected=new Set(), waTratativas={{}}, waSort={{col:'nome',dir:'asc'}};
  var WA_BACKEND='', WA_KEY='', WA_INSTANCE='';
  var WA_STATUS_LABELS={{pendente:'⏳ Pendente',confirmado:'✅ Confirmado','nao-atendido':'📵 Não Atendeu',reagendado:'🔁 Reagendado',entregue:'📤 Entregue',conveniente:'🟡 Conveniente','entregue-d1':'📥 Entregue D-1','entregue-d0':'📨 Entregue D-0','entregue-pos':'📤 Entregue Pós',satisfeito:'😊 Satisfeito',insatisfeito:'😤 Insatisfeito','problema-aberto':'🔧 Problema Aberto',elogio:'⭐ Elogio',normalizado:'NORMALIZADO','sem-contato':'SEM CONTATO',resolvido:'RESOLVIDO','aberto-reparo':'ABERTO REPARO','problema-na-rede':'PROBLEMA NA REDE',central:'CENTRAL','cancelamento-do-contrato':'CANCELAMENTO DO CONTRATO',agendado:'AGENDADO','suspenso-por-debito':'SUSPENSO POR DÉBITO','sem-retorno-supervisao':'SEM RETORNO SUPERVISÃO','numero-nao-pertence':'NÚMERO NÃO PERTENCE','area-de-risco':'ÁREA DE RISCO','nao-se-encontra':'NÃO SE ENCONTRA','solicitou-upgrade':'SOLICITOU UPGRADE',bloqueado:'🚫 Bloqueado'}};

  function showWaSub(id,btn){{
    document.querySelectorAll('.wa-sub').forEach(function(s){{s.classList.remove('active')}});
    document.querySelectorAll('.wa-tab').forEach(function(b){{b.classList.remove('active')}});
    document.getElementById(id).classList.add('active');
    if(btn)btn.classList.add('active');
  }}

  function waGetFase(c){{
    if(!c.data)return 'pos';
    var p=c.data.split('/');
    if(p.length!==3)return 'pos';
    var y=p[2].length===2?'20'+p[2]:p[2];
    var cDate=new Date(parseInt(y),parseInt(p[1])-1,parseInt(p[0]));
    var today=new Date();today.setHours(0,0,0,0);cDate.setHours(0,0,0,0);
    var diff=Math.round((cDate-today)/86400000);
    if(diff>=1)return 'd1';
    if(diff===0)return 'd0';
    return 'pos';
  }}
  function waGetStatus(c){{return(waTratativas[c.id]||{{}}).status||'pendente'}}

  function waUpdateKPIs(list){{
    list=list||waClients;
    var counts={{pendente:0,confirmado:0,'nao-atendido':0,reagendado:0,entregue:0,conveniente:0,'entregue-d1':0,'entregue-d0':0,'entregue-pos':0,satisfeito:0,insatisfeito:0,'problema-aberto':0,elogio:0}};
    list.forEach(function(c){{counts[waGetStatus(c)]++}});
    var t=list.length;
    var tot=waClients.length;
    document.getElementById('wa-total').textContent=t+(t!==tot?' / '+tot:'');
    document.getElementById('wa-conf').textContent=counts.confirmado;
    document.getElementById('wa-nao').textContent=counts['nao-atendido'];
    document.getElementById('wa-reag').textContent=counts.reagendado;
    document.getElementById('wa-pend').textContent=counts.pendente;
    document.getElementById('wa-entr').textContent=counts.entregue;
    document.getElementById('wa-taxa').textContent=t>0?Math.round(counts.confirmado/t*1000)/10+'%':'0%';
    document.getElementById('wa-conf-pct').textContent=t>0?Math.round(counts.confirmado/t*100)+'%':'0%';
    document.getElementById('wa-nao-pct').textContent=t>0?Math.round(counts['nao-atendido']/t*100)+'%':'0%';
    document.getElementById('wa-reag-pct').textContent=t>0?Math.round(counts.reagendado/t*100)+'%':'0%';
    document.getElementById('wa-pend-pct').textContent=t>0?Math.round(counts.pendente/t*100)+'%':'0%';
    document.getElementById('wa-entr-pct').textContent=t>0?Math.round(counts.entregue/t*100)+'%':'0%';
    document.getElementById('wa-conv').textContent=counts.conveniente;
    document.getElementById('wa-conv-pct').textContent=t>0?Math.round(counts.conveniente/t*100)+'%':'0%';
  }}

  function waGetChecked(id) {{
    var els=document.querySelectorAll('#'+id+' input:checked');
    var vals=[]; for(var i=0;i<els.length;i++)vals.push(els[i].value);
    return vals;
  }}
  function waUpdateDDLabel(id, labelId, emptyText) {{
    var els = document.querySelectorAll('#'+id+' input:checked');
    if(els.length===0) document.getElementById(labelId).textContent = emptyText;
    else if(els.length===1) document.getElementById(labelId).textContent = els[0].parentNode.textContent.trim().substring(0,15);
    else document.getElementById(labelId).textContent = els.length + ' selecionados';
  }}
  function waToggleDD(id, e) {{
    e.stopPropagation();
    document.querySelectorAll('.wa-dd-menu').forEach(function(m){{if(m.id!==id)m.classList.remove('active')}});
    document.getElementById(id).classList.toggle('active');
  }}
  document.addEventListener('click', function(e){{
    if(!e.target.closest('.wa-dd-wrap')){{
      document.querySelectorAll('.wa-dd-menu').forEach(function(m){{m.classList.remove('active')}});
    }}
  }});

  function waRenderTable(){{
    var q=document.getElementById('wa-search').value.toLowerCase();
    var fs=waGetChecked('dd-status');
    var fc=waGetChecked('dd-city');
    var ft=waGetChecked('dd-tipo');
    var d1=document.getElementById('wa-f-d1').value;
    var d2=document.getElementById('wa-f-d2').value;

    var fso=waGetChecked('dd-statusofs');
    var ffase=waGetChecked('dd-fase');

    waUpdateDDLabel('dd-status', 'lbl-status', 'Todos Status');
    waUpdateDDLabel('dd-city', 'lbl-city', 'Todas Cidades');
    waUpdateDDLabel('dd-tipo', 'lbl-tipo', 'Todos Tipos');
    waUpdateDDLabel('dd-statusofs', 'lbl-statusofs', 'Status OFS');
    waUpdateDDLabel('dd-fase', 'lbl-fase', 'Fase');

    function pDate(d){{
      if(!d)return'';
      var p=d.split('/');
      if(p.length===3) {{
        var y=p[2].length===2?'20'+p[2]:p[2];
        return y+'-'+(p[1].length<2?'0':'')+p[1]+'-'+(p[0].length<2?'0':'')+p[0];
      }}
      if(p.length===2) return new Date().getFullYear()+'-'+(p[1].length<2?'0':'')+p[1]+'-'+(p[0].length<2?'0':'')+p[0];
      return d; // fallback
    }}

    var list=waClients.filter(function(c){{
      // Filtro de GAVETA (fila)
      if(waFilaAtiva && waFilaAtiva!=='TUDO' && waFilaAtiva!=='NAO_LIDO'){{
        var cFila=(c.fila||'CONFIRMACAO').toUpperCase();
        if(cFila!==waFilaAtiva) return false;
      }}
      if(fs.length && fs.indexOf(waGetStatus(c))<0) return false;
      if(fc.length && fc.indexOf(c.cidade)<0) return false;
      if(ft.length && ft.indexOf(c.tipo)<0) return false;
      if(fso.length && fso.indexOf(c.statusOfs)<0) return false;
      if(ffase.length && ffase.indexOf(waGetFase(c))<0) return false;
      if(d1 || d2) {{
         var cd = pDate(c.data);
         if(!cd) return false;
         if(d1 && cd < d1) return false;
         if(d2 && cd > d2) return false;
      }}
      if(q&&c.nome.toLowerCase().indexOf(q)<0&&(c.phone||'').indexOf(q)<0)return false;
      return true;
    }});
    list.sort(function(a,b){{
      var va=a[waSort.col]||'',vb=b[waSort.col]||'';
      if(waSort.col==='status'){{va=waGetStatus(a);vb=waGetStatus(b)}}
      return waSort.dir==='asc'?String(va).localeCompare(String(vb)):String(vb).localeCompare(String(va));
    }});
    var tbody=document.getElementById('wa-tbody');
    tbody.innerHTML=list.map(function(c){{
      var st=waGetStatus(c);
      var sel=waSelected.has(c.id);
      var fase=waGetFase(c);
      var faseLabel=fase==='d1'?'🔵 D-1':fase==='d0'?'🟡 D-0':'🟠 Pós';
      var faseBg=fase==='d1'?'rgba(59,130,246,.12)':fase==='d0'?'rgba(234,179,8,.12)':'rgba(249,115,22,.12)';
      var faseColor=fase==='d1'?'#60a5fa':fase==='d0'?'#eab308':'#fb923c';
      var safeNome=(c.nome||'').replace(/'/g, "\\\\'");
      return '<tr style="'+(sel?'background:rgba(37,211,102,.08);outline:1px solid rgba(37,211,102,.2)':'')+'" onclick="waToggleSel(\\''+c.id+'\\')">'+
        '<td style="width:36px;text-align:center" onclick="event.stopPropagation()"><input type="checkbox" '+(sel?'checked':'')+' onchange="waToggleSel(\\''+c.id+'\\')" style="accent-color:#25d366;cursor:pointer;width:14px;height:14px"></td>'+
        '<td style="font-weight:600">'+c.nome+'</td>'+
        '<td style="font-family:var(--font-mono);font-size:12px;color:#00e5ff">'+c.phone+'</td>'+
        '<td style="font-family:var(--font-mono);font-size:12px;color:#64748b">'+(c.data||'—')+'</td>'+
        '<td><span style="font-size:11px;background:rgba(99,102,241,.15);color:#a5b4fc;padding:2px 8px;border-radius:4px;white-space:nowrap">'+(c.intervalo||'—')+'</span></td>'+
        '<td><span style="font-size:11px;color:#94a3b8;max-width:160px;display:inline-block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="'+(c.endereco||'')+'">'+(c.endereco||'—')+'</span></td>'+
        '<td><span style="font-size:11px;background:#1a1e28;padding:2px 8px;border-radius:4px">'+(c.cidade||'—')+'</span></td>'+
        '<td><span style="font-size:11px;background:#0d1520;border:1px solid #1c2237;padding:2px 8px;border-radius:4px;color:#60a5fa">'+(c.tipo||'—')+'</span></td>'+
        '<td><span style="font-size:11px;font-weight:600;padding:2px 8px;border-radius:4px;white-space:nowrap;background:'+faseBg+';color:'+faseColor+'">'+faseLabel+'</span></td>'+
        '<td><span style="font-size:11px;background:rgba(251,191,36,.12);color:#fbbf24;padding:2px 8px;border-radius:4px;white-space:nowrap;border:1px solid rgba(251,191,36,.2)">'+(c.statusOfs||'—')+'</span></td>'+
        '<td><span class="wa-badge '+st+'">'+WA_STATUS_LABELS[st]+'</span></td>'+
        '<td><button class="wa-cfg-btn secondary" style="padding:4px 8px;font-size:11px" onclick="waOpenChat(\\''+c.phone+'\\',\\''+safeNome+'\\',\\''+c.id+'\\');event.stopPropagation()">💬 Chat</button></td>'+
      '</tr>';
    }}).join('');
    document.getElementById('wa-empty').style.display=waClients.length?'none':'block';
    document.getElementById('wa-client-table').style.display=waClients.length?'table':'none';
    var chkAll=document.getElementById('wa-chk-all');
    if(chkAll){{var allVis=list.length>0&&list.every(function(c){{return waSelected.has(c.id)}});chkAll.checked=allVis;chkAll.indeterminate=!allVis&&waSelected.size>0;}}
    document.getElementById('wa-sel-count').textContent=waSelected.size;
    waUpdateKPIs(list);
  }}

  function waToggleSel(id){{if(waSelected.has(id))waSelected.delete(id);else waSelected.add(id);waRenderTable()}}
  function waToggleAll(cb){{if(cb.checked){{waSelectAll()}}else{{waSelectNone()}}}}
  function waSortTable(col){{if(waSort.col===col)waSort.dir=waSort.dir==='asc'?'desc':'asc';else{{waSort.col=col;waSort.dir='asc'}};waRenderTable()}}
  function waFilterTable(){{waSelected.clear();waRenderTable()}}
  function waSelectAll(){{
    var q=document.getElementById('wa-search').value.toLowerCase();
    var fs=waGetChecked('dd-status'),fc=waGetChecked('dd-city'),ft=waGetChecked('dd-tipo');
    var d1=document.getElementById('wa-f-d1').value,d2=document.getElementById('wa-f-d2').value;
    function pDate(d){{if(!d)return'';var p=d.split('/');if(p.length===3){{var y=p[2].length===2?'20'+p[2]:p[2];return y+'-'+(p[1].length<2?'0':'')+p[1]+'-'+(p[0].length<2?'0':'')+p[0]}}return d}}
    waClients.filter(function(c){{
      // Filtro de GAVETA (fila) — só seleciona clientes da gaveta ativa
      if(waFilaAtiva && waFilaAtiva!=='TUDO' && waFilaAtiva!=='NAO_LIDO'){{
        var cFila=(c.fila||'CONFIRMACAO').toUpperCase();
        if(cFila!==waFilaAtiva) return false;
      }}
      if(fs.length&&fs.indexOf(waGetStatus(c))<0)return false;
      if(fc.length&&fc.indexOf(c.cidade)<0)return false;
      if(ft.length&&ft.indexOf(c.tipo)<0)return false;
      var fso2=waGetChecked('dd-statusofs');if(fso2.length&&fso2.indexOf(c.statusOfs)<0)return false;
      var ffase2=waGetChecked('dd-fase');if(ffase2.length&&ffase2.indexOf(waGetFase(c))<0)return false;
      if(d1||d2){{var cd=pDate(c.data);if(!cd)return false;if(d1&&cd<d1)return false;if(d2&&cd>d2)return false}}
      if(q&&c.nome.toLowerCase().indexOf(q)<0&&(c.phone||'').indexOf(q)<0)return false;
      return true;
    }}).forEach(function(c){{waSelected.add(c.id)}});
    waRenderTable();
  }}
  function waSelectNone(){{waSelected.clear();waRenderTable()}}

  function waSyncClients(){{
    if(!WA_BACKEND) return;
    var h={{}};if(WA_KEY)h['x-api-key']=WA_KEY;
    fetch(WA_BACKEND+'/agenda/clients?apikey='+(WA_KEY||''),{{headers:h}}).then(function(r){{return r.json()}}).then(function(data){{
      if(Array.isArray(data)){{ waClients = data; waRefreshUI(); _chatSaveNomesToCache(); }}
    }}).catch(function(){{}});
  }}
  function waSaveClients(){{
    if(!WA_BACKEND) return;
    var h={{'Content-Type':'application/json'}};if(WA_KEY)h['x-api-key']=WA_KEY;
    fetch(WA_BACKEND+'/agenda/clients?apikey='+(WA_KEY||''),{{method:'POST',headers:h,body:JSON.stringify({{clients:waClients}})}})
      .catch(function(){{}});
  }}
  function waClearAgenda(){{
    if(confirm('Tem certeza que deseja limpar toda a agenda do SERVIDOR?')){{
      waClients=[];waSelected.clear();
      if(!WA_BACKEND) return waRefreshUI();
      var h={{'Content-Type':'application/json'}};if(WA_KEY)h['x-api-key']=WA_KEY;
      fetch(WA_BACKEND+'/agenda/clear?apikey='+(WA_KEY||''),{{method:'POST',headers:h}}).then(function(){{waRefreshUI()}}).catch(function(){{waRefreshUI()}});
    }}
  }}
  function waRefreshUI(){{
    var cities=[...new Set(waClients.map(function(c){{return c.cidade}}).filter(Boolean))].sort();
    var sC=''; cities.forEach(function(c){{ sC+='<label class="wa-dd-item"><input type="checkbox" value="'+c+'" onchange="waFilterTable()"> '+c+'</label>'; }});
    document.getElementById('dd-city').innerHTML=sC;

    var tipos=[...new Set(waClients.map(function(c){{return c.tipo}}).filter(Boolean))].sort();
    var sT=''; tipos.forEach(function(t){{ sT+='<label class="wa-dd-item"><input type="checkbox" value="'+t+'" onchange="waFilterTable()"> '+t+'</label>'; }});
    document.getElementById('dd-tipo').innerHTML=sT;

    var statusOfsVals=[...new Set(waClients.map(function(c){{return c.statusOfs}}).filter(Boolean))].sort();
    var sOfs=''; statusOfsVals.forEach(function(v){{ sOfs+='<label class="wa-dd-item"><input type="checkbox" value="'+v+'" onchange="waFilterTable()"> '+v+'</label>'; }});
    document.getElementById('dd-statusofs').innerHTML=sOfs||'<span style="font-size:11px;color:#64748b;padding:8px">Sem dados OFS</span>';

    if(waClients.length){{document.getElementById('wa-drop-zone').innerHTML='<div style="font-size:32px;margin-bottom:8px">✅</div><div style="font-size:14px;font-weight:700;color:#25d366;margin-bottom:4px">'+waClients.length+' clientes carregados</div><div style="font-size:11px;color:#94a3b8;margin-bottom:6px">'+cities.length+' cidades · '+tipos.length+' tipos</div><div style="font-size:11px;color:#f97316;background:rgba(249,115,22,.08);border:1px solid rgba(249,115,22,.2);border-radius:6px;padding:3px 10px">💡 Adicionar mais? Clique e selecione com Ctrl+Click</div>';}}
    else{{document.getElementById('wa-drop-zone').innerHTML='<div style="font-size:32px;margin-bottom:8px">⬆️</div><div style="font-size:14px;font-weight:600;margin-bottom:4px">Arraste ou clique para importar</div><div style="font-size:12px;color:#64748b">CSV, Excel, ODS, TSV \u2014 qualquer formato</div><div style="font-size:11px;color:#94a3b8;margin-top:6px">💡 Dica: Múltiplos arquivos com Ctrl+Click</div>'}}
    waRenderTable();
  }}

  function waHandleFile(e){{
    var files=e.target.files;
    if(!files||!files.length)return;
    for(var i=0;i<files.length;i++){{
      (function(file){{
        var ext=file.name.split('.').pop().toLowerCase();
        if(ext==='csv'||ext==='tsv'||ext==='txt'){{
          var r=new FileReader();r.onload=function(ev){{waParseCSV(ev.target.result,file.name)}};r.readAsText(file,'UTF-8');
        }} else {{
          var doRead=function(){{
            var r=new FileReader();r.onload=function(ev){{
              var wb=XLSX.read(new Uint8Array(ev.target.result),{{type:'array'}});
              waParseCSV(XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]),file.name);
            }};r.readAsArrayBuffer(file);
          }};
          if(!window.XLSX){{
            var sc=document.createElement('script');sc.src='https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
            sc.onload=doRead;document.head.appendChild(sc);
          }} else {{ doRead(); }}
        }}
      }})(files[i]);
    }}
    e.target.value='';
  }}

  /* RFC4180 CSV parser — lida com campos quoted que contêm vírgulas e tabs */
  function waCSVtoRows(text){{
    var rows=[],row=[],field='',inQ=false;
    /* Detecta delimitador: tab, ponto-e-vírgula ou vírgula */
    var firstLine=text.split(/[\\r\\n]/)[0]||'';
    var delim=',';
    if(firstLine.indexOf('\\t')>=0 && firstLine.split('\\t').length>3) delim='\\t';
    else if(firstLine.indexOf(';')>=0 && firstLine.split(';').length>firstLine.split(',').length) delim=';';
    for(var i=0;i<text.length;i++){{
      var c=text[i],n=text[i+1];
      if(inQ){{if(c==='"'&&n==='"'){{field+='"';i++}}else if(c==='"'){{inQ=false}}else{{field+=c}}}}
      else{{if(c==='"'){{inQ=true}}else if(c===delim||((delim===','||delim===';')&&(c===','||c===';'))){{row.push(field.trim());field=''}}
      else if(c.charCodeAt(0)===13){{continue}}else if(c.charCodeAt(0)===10){{row.push(field.trim());if(row.length>1)rows.push(row);row=[];field=''}}
      else{{field+=c}}}}
    }}
    if(field||row.length){{row.push(field.trim());if(row.length>1)rows.push(row)}}
    return rows;
  }}

  /* ── ALIASES expandidos para auto-match de colunas ── */
  var WA_COL_ALIASES = {{
    nome:['nome','name','cliente','customer','assinante','subscriber','razao social','razão social','contato','nome do cliente','nome completo','responsavel','responsável','titular','beneficiario','beneficiário','nome_cliente','full_name'],
    phone:['telefone celular','celular','telefone','phone','tel','mobile','fone','número','numero','ddd+telefone','whatsapp','contato tel','telefone de contato','cel','phone_number','num_telefone','fone_contato','cellphone','tel_cel'],
    data:['data','date','data agendamento','dt','data da atividade','data atividade','data visita','agendado para','agenda','dt_agenda','data_agendamento','scheduled','data prevista','data programada','previsao','previsão'],
    cidade:['cidade','city','municipio','município','localidade','regional','uf/cidade','mun','town','regiao','região'],
    status:['status da atividade','status','estado','situação','situacao','state','status ofs','status os','status_ativ','conclusao','conclusão','resultado'],
    endereco:['endereço','endereco','logradouro','address','rua','local','end','endereco completo','endereço completo','morada','localizacao','localização','end_completo'],
    intervalo:['intervalo de tempo','intervalo','turno','período','periodo','slot','horario','horário','hora','janela','faixa horária','faixa horaria','janela de tempo','time slot','hora inicio','hora início','hora_ini','hora_fim','period'],
    tipo:['tipo de atividade','tipo','servico','serviço','type','categoria','atividade','tipo serviço','tipo servico','tipo os','tipo_ativ','service','natureza']
  }};
  var WA_COL_LABELS = {{nome:'Nome do Cliente',phone:'Telefone',data:'Data',cidade:'Cidade',status:'Status',endereco:'Endereço',intervalo:'Intervalo/Horário',tipo:'Tipo de Atividade'}};
  var WA_COL_ICONS = {{nome:'👤',phone:'📱',data:'📅',cidade:'🏙️',status:'📋',endereco:'📍',intervalo:'⏰',tipo:'🔧'}};
  var WA_COL_REQUIRED = ['nome','phone']; /* Pelo menos 1 dos 2 */

  /* Estado temporário da importação em andamento */
  var _waImpState = null;

  function _waAutoMap(headers){{
    var mapping = {{}};
    var usedCols = new Set();
    /* Tenta match salvo no localStorage primeiro */
    var hdrKey = headers.join('|').toLowerCase();
    try {{
      var saved = JSON.parse(localStorage.getItem('wa_col_mapping_v2')||'{{}}');
      if(saved._key===hdrKey && saved.map) {{
        var allValid = true;
        for(var f in saved.map) {{
          if(saved.map[f]>=0 && saved.map[f]<headers.length) mapping[f]=saved.map[f];
          else allValid=false;
        }}
        if(allValid && Object.keys(mapping).length>0) return mapping;
        mapping = {{}};
      }}
    }} catch(ex){{}}
    /* Fuzzy match */
    var headersLow = headers.map(function(h){{return h.toLowerCase().trim()}});
    var fields = Object.keys(WA_COL_ALIASES);
    /* Para 'tipo': preferir a ÚLTIMA coluna que dê match (OFS tem 2) */
    for(var fi=0;fi<fields.length;fi++){{
      var field = fields[fi];
      var aliases = WA_COL_ALIASES[field];
      var bestIdx = -1;
      for(var ai=0;ai<aliases.length;ai++){{
        var alias = aliases[ai];
        for(var hi=0;hi<headersLow.length;hi++){{
          if(usedCols.has(hi)) continue;
          /* Match exato primeiro */
          if(headersLow[hi]===alias){{ bestIdx=hi; break; }}
        }}
        if(bestIdx>=0) break;
        /* Match parcial (contains) */
        for(var hi2=0;hi2<headersLow.length;hi2++){{
          if(usedCols.has(hi2)) continue;
          if(headersLow[hi2].indexOf(alias)>=0){{ if(field==='tipo')bestIdx=hi2; else {{bestIdx=hi2;break;}} }}
        }}
        if(bestIdx>=0 && field!=='tipo') break;
      }}
      if(bestIdx>=0){{ mapping[field]=bestIdx; usedCols.add(bestIdx); }}
    }}
    return mapping;
  }}

  function waParseCSV(text, filename){{
    var allRows=waCSVtoRows(text);
    if(allRows.length<2){{alert('Arquivo vazio ou sem dados');return;}}
    var headers=allRows[0];
    var mapping=_waAutoMap(headers);
    /* Salva estado para o modal */
    _waImpState = {{headers:headers, rows:allRows.slice(1), mapping:mapping, filename:filename||'arquivo'}};
    waShowImportModal();
  }}

  function waShowImportModal(){{
    if(!_waImpState)return;
    var s=_waImpState;
    var modal=document.getElementById('wa-import-modal');
    document.getElementById('wa-imp-filename').textContent=s.filename+' ('+s.rows.length+' linhas)';
    var container=document.getElementById('wa-imp-rows');
    container.innerHTML='';
    var fields=Object.keys(WA_COL_ALIASES);
    for(var fi=0;fi<fields.length;fi++){{
      var field=fields[fi];
      var mapped=s.mapping[field];
      var isOk=mapped!==undefined && mapped>=0;
      var isReq=WA_COL_REQUIRED.indexOf(field)>=0;
      var icon=isOk?'✅':'❌';
      var detectedText=isOk?(' ← "'+s.headers[mapped]+'"'):' ← (não encontrado)';
      var row=document.createElement('div');
      row.style.cssText='display:flex;align-items:center;gap:10px;padding:10px 12px;background:#111520;border:1px solid '+(isOk?'#22d3a022':'#ff4d6d22')+';border-radius:10px;transition:all 0.2s';
      var selectOpts='<option value="-1"'+(isOk?'':'selected')+'>— Não mapear —</option>';
      for(var hi=0;hi<s.headers.length;hi++){{
        var sel=(mapped===hi)?'selected':'';
        selectOpts+='<option value="'+hi+'" '+sel+'>'+s.headers[hi]+'</option>';
      }}
      row.innerHTML=
        '<span style="font-size:16px;width:24px;text-align:center">'+WA_COL_ICONS[field]+'</span>'+
        '<span style="font-size:13px;font-weight:700;color:#e2e8f0;min-width:140px">'+WA_COL_LABELS[field]+(isReq?' <span style="color:#ff4d6d">*</span>':'')+'</span>'+
        '<span style="font-size:14px;width:20px;text-align:center">'+icon+'</span>'+
        '<select class="wa-cfg-input" data-field="'+field+'" onchange="waImpFieldChange(this)" style="flex:1;font-size:12px;padding:6px 10px;height:32px;min-width:0">'+selectOpts+'</select>';
      container.appendChild(row);
    }}
    /* Atualizar botão */
    waImpUpdateBtn();
    modal.style.display='flex';
  }}

  function waImpFieldChange(sel){{
    if(!_waImpState)return;
    var field=sel.getAttribute('data-field');
    var val=parseInt(sel.value);
    if(val<0) delete _waImpState.mapping[field];
    else _waImpState.mapping[field]=val;
    /* Atualizar ícones */
    var row=sel.closest('div');
    var iconSpan=row.querySelectorAll('span')[2];
    if(val>=0){{ iconSpan.textContent='✅'; row.style.borderColor='#22d3a022'; }}
    else{{ iconSpan.textContent='❌'; row.style.borderColor='#ff4d6d22'; }}
    waImpUpdateBtn();
  }}

  function waImpUpdateBtn(){{
    if(!_waImpState)return;
    var m=_waImpState.mapping;
    var hasRequired=(m.nome!==undefined && m.nome>=0)||(m.phone!==undefined && m.phone>=0);
    var btn=document.getElementById('wa-imp-confirm');
    btn.textContent='✅ Importar '+_waImpState.rows.length+' linhas';
    btn.disabled=!hasRequired;
    btn.style.opacity=hasRequired?'1':'0.4';
  }}

  function waCloseImportModal(){{
    document.getElementById('wa-import-modal').style.display='none';
    _waImpState=null;
  }}

  function waFinishImport(){{
    if(!_waImpState)return;
    var s=_waImpState;
    var m=s.mapping;
    function g(row,i){{return i!==undefined && i>=0 && i<row.length && row[i]?row[i].trim():''}}
    var list=[];
    for(var i=0;i<s.rows.length;i++){{
      var row=s.rows[i];
      var nome=g(row,m.nome)||'Cliente';
      var tel=g(row,m.phone);
      /* Pular linhas totalmente vazias (sem nome E sem telefone) */
      if(!tel && nome==='Cliente') continue;
      var cleanTel=(tel||'').replace(/\\D/g,'');
      list.push({{id:'wa_'+cleanTel+'_'+nome.replace(/ +/g,'_').slice(0,20),nome:nome,phone:tel,data:g(row,m.data),cidade:g(row,m.cidade),tipo:g(row,m.tipo),endereco:g(row,m.endereco),intervalo:g(row,m.intervalo),statusOfs:g(row,m.status)||'—'}});
    }}
    /* Salvar mapeamento no localStorage se checkbox marcado */
    if(document.getElementById('wa-imp-remember').checked){{
      try{{
        var hdrKey=s.headers.join('|').toLowerCase();
        localStorage.setItem('wa_col_mapping_v2',JSON.stringify({{_key:hdrKey,map:m}}));
      }}catch(ex){{}}
    }}
    if(!list.length){{alert('Nenhuma linha válida encontrada (todas sem nome e telefone)');return;}}
    waClients=waClients.concat(list);
    /* Remove duplicates based on ID */
    var unique=[]; var ids=new Set();
    for(var z=waClients.length-1;z>=0;z--){{if(!ids.has(waClients[z].id)){{unique.unshift(waClients[z]);ids.add(waClients[z].id)}}}}
    waClients=unique;
    waSaveClients();
    _chatSaveNomesToCache();
    waRefreshUI();
    if(WA_BACKEND)waSyncStatus();
    waCloseImportModal();
  }}

  var waDispMode='fixed';
  function waSetMode(m){{
    waDispMode=m;
    document.getElementById('wa-ctrl-fixed').style.display=m==='fixed'?'flex':'none';
    document.getElementById('wa-ctrl-window').style.display=m==='window'?'flex':'none';
    document.getElementById('wa-mode-fixed').className=m==='fixed'?'wa-cfg-btn':'wa-cfg-btn secondary';
    document.getElementById('wa-mode-window').className=m==='window'?'wa-cfg-btn':'wa-cfg-btn secondary';
  }}

  function waToggleTpl(n){{
    var el=document.getElementById('wa-template-'+n);
    var arr=document.getElementById('wa-tpl-arrow-'+n);
    var nameEl=document.getElementById('wa-tpl-name-'+n);
    if(el.style.display==='none'){{el.style.display='';nameEl.style.display='';arr.textContent='▲'}}else{{el.style.display='none';nameEl.style.display='none';arr.textContent='▼'}}
  }}
  function waGetTemplates(){{
    var tpls=[];
    for(var i=1;i<=5;i++){{
      var el=document.getElementById('wa-template-'+i);
      var ne=document.getElementById('wa-tpl-name-'+i);
      if(!el)continue;
      var v=(el.value||'').trim();
      var n=(ne?ne.value||'':'').trim();
      if(v)tpls.push({{text:v,meta_name:n||'template_padrao'}});
    }}
    return tpls;
  }}
  function waUpdatePreview(){{
    var tpls=waGetTemplates();
    var c=waClients[0]||{{nome:'João Silva',data:'05/05',cidade:'Macaé'}};
    var countEl=document.getElementById('wa-tpl-count');
    if(tpls.length>1)countEl.textContent='— '+tpls.length+' mensagens em rodízio';else countEl.textContent='';
    var first=tpls.length ? tpls[0].text : '';
    var out=first.split('{{{{nome}}}}').join(c.nome).split('{{{{data}}}}').join(c.data||'—').split('{{{{cidade}}}}').join(c.cidade||'—').split('{{{{horario}}}}').join(c.intervalo||'—').split('{{{{intervalo}}}}').join(c.intervalo||'—').split('{{{{tipo}}}}').join(c.tipo||'—').split('{{{{remetente}}}}').join(document.getElementById('wa-sender-name').value||'Remetente');
    document.getElementById('wa-preview').textContent=out;
  }}

  function waTestConnection(){{
    WA_BACKEND=document.getElementById('wa-backend-url').value.replace(/\\/$/,'');
    WA_KEY=document.getElementById('wa-api-key').value;
    WA_INSTANCE=document.getElementById('wa-instance-name').value||'svoboda';
    var el=document.getElementById('wa-conn-status');
    fetch(WA_BACKEND+'/health').then(function(r){{return r.json()}}).then(function(){{
      el.innerHTML='<span class="wa-status-dot online"></span> Backend conectado!';
      localStorage.setItem('wa_backend',WA_BACKEND);
      localStorage.setItem('wa_key',WA_KEY);
      localStorage.setItem('wa_instance',WA_INSTANCE);
      waCheckEvo();
      waFetchInstances();
      if(waClients.length)waSyncStatus();
    }}).catch(function(){{el.innerHTML='<span class="wa-status-dot offline"></span> Falha na conexão'}});
  }}

  function waCheckEvo(){{
    var el=document.getElementById('wa-whatsapp-status');
    var h={{}};if(WA_KEY)h['x-api-key']=WA_KEY;if(WA_INSTANCE)h['x-wa-instance']=WA_INSTANCE;
    fetch(WA_BACKEND+'/wa/status',{{headers:h}}).then(function(r){{return r.json()}}).then(function(d){{
      if(d.instance&&d.instance.state==='open'){{
        el.innerHTML='<div style="font-size:40px;margin-bottom:10px">✅</div><div style="color:#25d366;font-weight:700">API Oficial Conectada</div>'+
        '<button class="wa-cfg-btn secondary" style="margin-top:16px" onclick="waLogout()">Limpar Credenciais</button>';
      }}else{{
        el.innerHTML='<span class="wa-status-dot offline"></span> Configure as credenciais acima para conectar à API Oficial.';
      }}
    }}).catch(function(){{ el.innerHTML='<span class="wa-status-dot offline"></span> Configure as credenciais acima para conectar à API Oficial.'; }});
  }}

  function waSaveMetaConfig() {{
    var t = document.getElementById('wa-meta-token').value.trim();
    var p = document.getElementById('wa-meta-phone').value.trim();
    if(!WA_BACKEND) return alert("Conecte o backend primeiro na aba Configuração");
    var h = {{'Content-Type': 'application/json'}};
    if (WA_KEY) h['x-api-key'] = WA_KEY;
    fetch(WA_BACKEND+'/meta-config', {{
      method: 'POST',
      headers: h,
      body: JSON.stringify({{ token: t, phoneId: p }})
    }}).then(function(){{
      alert("Credenciais salvas com sucesso no backend!");
      waCheckEvo();
      waFetchInstances();
    }}).catch(function(){{ alert("Erro ao salvar credenciais"); }});
  }}

  function waLogout(){{
    var h={{}};if(WA_KEY)h['x-api-key']=WA_KEY;if(WA_INSTANCE)h['x-wa-instance']=WA_INSTANCE;
    fetch(WA_BACKEND+'/wa/logout',{{method:'POST',headers:h}}).then(function(){{waCheckEvo()}});
  }}

  function waFetchInstances(){{
    if(!WA_BACKEND)return;
    var h={{}};if(WA_KEY)h['x-api-key']=WA_KEY;
    fetch(WA_BACKEND+'/wa/instances',{{headers:h}}).then(function(r){{return r.json()}}).then(function(insts){{
      if(!Array.isArray(insts))return;
      var opts=insts.length?insts.map(function(i){{return '<option value="'+i+'">'+i+'</option>'}}).join(''):'<option value="">Nenhum WhatsApp online</option>';
      document.getElementById('wa-active-instance').innerHTML=opts;
      document.getElementById('wa-chat-instance').innerHTML=opts;
      var s=document.getElementById('wa-instance-name').value;
      if(insts.includes(s)){{document.getElementById('wa-active-instance').value=s;document.getElementById('wa-chat-instance').value=s;}}
    }}).catch(function(){{}});
  }}

  var currentChatPhone='';
  var currentChatId='';
  function waOpenChat(phone,nome,id){{
    currentChatPhone=phone.replace(/\\D/g,'');
    currentChatId=id;
    if(!currentChatPhone.startsWith('55'))currentChatPhone='55'+currentChatPhone;
    document.getElementById('wa-chat-title').textContent = nome;
    
    // Populate status dropdown based on client fase
    var c = waClients.find(function(cl){{return cl.id===id}});
    if(c){{
      var fase=waGetFase(c);
      var sel=document.getElementById('wa-chat-status');
      if(fase==='pos'){{
        sel.innerHTML='<option value="pendente">⏳ Pendente</option><option value="confirmado">✅ Confirmado</option><option value="nao-atendido">🚫 Não Atendeu</option><option value="reagendado">🔄 Reagendado</option><option value="conveniente">🟢 Conveniente</option><option value="cancelamento-do-contrato">❌ Cancelado</option><option value="entregue">📬 Entregue</option><option value="entregue-d1">📬 Entregue D-1</option><option value="entregue-d0">📬 Entregue D-0</option><option value="entregue-pos">📬 Entregue Pós</option><option value="normalizado">✅ Normalizado</option><option value="resolvido">✅ Resolvido</option><option value="aberto-reparo">🔧 Aberto Reparo</option><option value="problema-na-rede">🌐 Problema na Rede</option><option value="central">🏢 Central</option><option value="agendado">📅 Agendado</option><option value="suspenso-por-debito">💰 Suspenso por Débito</option><option value="numero-nao-pertence">❓ Número Não Pertence</option><option value="area-de-risco">⚠️ Área de Risco</option><option value="nao-se-encontra">🏠 Não se Encontra</option><option value="solicitou-upgrade">⬆️ Solicitou Upgrade</option><option value="sem-contato">📴 Sem Contato</option><option value="sem-retorno-supervisao">⏳ Sem Retorno Supervisão</option><option value="bloqueado">🚫 Bloqueado</option>';
      }}else{{
        sel.innerHTML='<option value="pendente">⏳ Pendente</option><option value="confirmado">✅ Confirmado</option><option value="nao-atendido">🚫 Não Atendeu</option><option value="reagendado">🔄 Reagendado</option><option value="conveniente">🟢 Conveniente</option><option value="cancelamento-do-contrato">❌ Cancelado</option><option value="entregue">📬 Entregue</option><option value="entregue-d1">📬 Entregue D-1</option><option value="entregue-d0">📬 Entregue D-0</option><option value="entregue-pos">📬 Entregue Pós</option><option value="normalizado">✅ Normalizado</option><option value="resolvido">✅ Resolvido</option><option value="aberto-reparo">🔧 Aberto Reparo</option><option value="problema-na-rede">🌐 Problema na Rede</option><option value="central">🏢 Central</option><option value="agendado">📅 Agendado</option><option value="suspenso-por-debito">💰 Suspenso por Débito</option><option value="numero-nao-pertence">❓ Número Não Pertence</option><option value="area-de-risco">⚠️ Área de Risco</option><option value="nao-se-encontra">🏠 Não se Encontra</option><option value="solicitou-upgrade">⬆️ Solicitou Upgrade</option><option value="sem-contato">📴 Sem Contato</option><option value="sem-retorno-supervisao">⏳ Sem Retorno Supervisão</option><option value="bloqueado">🚫 Bloqueado</option>';
      }}
      sel.value=waGetStatus(c);
    }}

    document.getElementById('wa-chat-msgs').innerHTML='<div style="text-align:center;color:#64748b;font-size:12px">Carregando...</div>';
    document.getElementById('wa-chat-modal').style.display='flex';
    var h={{}};if(WA_KEY)h['x-api-key']=WA_KEY;if(WA_INSTANCE)h['x-wa-instance']=WA_INSTANCE;
    fetch(WA_BACKEND+'/msgs/'+currentChatPhone,{{headers:h}}).then(function(r){{return r.json()}}).then(function(msgs){{
      if(!msgs||!msgs.length){{document.getElementById('wa-chat-msgs').innerHTML='<div style="text-align:center;color:#64748b;font-size:12px">Nenhuma mensagem ainda</div>';return}}
      document.getElementById('wa-chat-msgs').innerHTML=msgs.map(function(m){{
        var cls=m.from==='me'?'me':'client';
        var t=new Date(m.ts).toLocaleTimeString([],{{hour:'2-digit',minute:'2-digit'}});
        return '<div class="wa-msg '+cls+'">'+m.text+'<div style="font-size:9px;opacity:0.7;margin-top:2px;text-align:right">'+t+'</div></div>';
      }}).join('');
      var box=document.getElementById('wa-chat-msgs');
      box.scrollTop=box.scrollHeight;
    }});
  }}

  function waSendReply(){{
    var inp=document.getElementById('wa-chat-input');
    var txt=inp.value.trim();
    if(!txt||!currentChatPhone)return;
    var inst=document.getElementById('wa-chat-instance').value;
    if(!inst){{alert('Selecione o WhatsApp remetente primeiro!');return;}}
    inp.value='';
    var h={{'Content-Type':'application/json'}};if(WA_KEY)h['x-api-key']=WA_KEY;h['x-wa-instance']=inst;
    fetch(WA_BACKEND+'/send-reply',{{method:'POST',headers:h,body:JSON.stringify({{phone:currentChatPhone,text:txt}})}}).then(function(){{
      setTimeout(function(){{waOpenChat(currentChatPhone,document.getElementById('wa-chat-title').textContent, currentChatId)}},500);
    }});
  }}

  function waChangeStatusManually(newStatus){{
    if(!currentChatId || !WA_BACKEND) return;
    var h={{'Content-Type':'application/json'}};if(WA_KEY)h['x-api-key']=WA_KEY;
    fetch(WA_BACKEND+'/status/'+currentChatId,{{method:'POST',headers:h,body:JSON.stringify({{status:newStatus,obs:'Alterado manualmente pelo operador'}})}}).then(function(){{
       if(waTratativas[currentChatId]) waTratativas[currentChatId].status = newStatus;
       else waTratativas[currentChatId] = {{status:newStatus}};
       waRenderTable();
    }});
  }}

  function waSyncStatus(){{
    if(!WA_BACKEND)return;
    var h={{}};if(WA_KEY)h['x-api-key']=WA_KEY;if(WA_INSTANCE)h['x-wa-instance']=WA_INSTANCE;
    fetch(WA_BACKEND+'/all-status?apikey='+(WA_KEY||''),{{headers:h}}).then(function(r){{return r.json()}}).then(function(data){{
      for(var id in data)if(data[id])waTratativas[id]=data[id];
      waRenderTable();
    }}).catch(function(){{}});
  }}


  // ========== FLUXO AUTOMÁTICO DE RESPOSTAS ==========
  var FLOW_API = '/api/flow';
  var _fluxoAtivos = [];
  var _fluxoPollTimer = null;

  function waFluxoLoadConfig() {{
    fetch(FLOW_API + '/flow-config').then(function(r){{return r.json()}}).then(function(cfg){{
      var chk = document.getElementById('fluxo-ativo');
      if (chk) chk.checked = !!cfg.ativo;
      if (cfg.msg_sim)   document.getElementById('fluxo-msg-sim').value  = cfg.msg_sim;
      if (cfg.msg_nao)   document.getElementById('fluxo-msg-nao').value  = cfg.msg_nao;
      if (cfg.msg_outro) document.getElementById('fluxo-msg-outro').value = cfg.msg_outro;
      if (cfg.delay_segundos !== undefined) document.getElementById('fluxo-delay').value = cfg.delay_segundos;
    }}).catch(function(){{}});
    waFluxoLoadAtivos();
  }}

  function waFluxoToggle(ativo) {{
    var cfg = {{ ativo: ativo }};
    fetch(FLOW_API + '/flow-config', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify(cfg)}}).catch(function(){{}});
  }}

  function waFluxoSaveConfig() {{
    if (!WA_BACKEND) {{ alert('Configure o backend na aba Configuração primeiro'); return; }}
    var cfg = {{
      ativo:          document.getElementById('fluxo-ativo').checked,
      delay_segundos: parseInt(document.getElementById('fluxo-delay').value) || 10,
      wa_backend:     WA_BACKEND,
      wa_key:         WA_KEY || '',
      msg_sim:        document.getElementById('fluxo-msg-sim').value.trim(),
      msg_nao:        document.getElementById('fluxo-msg-nao').value.trim(),
      msg_outro:      document.getElementById('fluxo-msg-outro').value.trim()
    }};
    fetch(FLOW_API + '/flow-config', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify(cfg)
    }}).then(function(r){{return r.json()}}).then(function(d){{
      if (d.ok) {{
        var m = document.getElementById('fluxo-save-msg');
        if (m) {{ m.style.display = 'block'; setTimeout(function(){{m.style.display='none'}}, 2500); }}
      }}
    }}).catch(function(e){{ alert('Erro ao salvar: ' + e.message); }});
  }}

  function waFluxoLoadAtivos() {{
    fetch(FLOW_API + '/flows').then(function(r){{return r.json()}}).then(function(flows){{
      _fluxoAtivos = flows;
      waFluxoRenderTabela(flows);
    }}).catch(function(){{}});
    fetch(FLOW_API + '/status').then(function(r){{return r.json()}}).then(function(s){{
      document.getElementById('fluxo-cnt-aguardando').textContent  = s.aguardando  || 0;
      document.getElementById('fluxo-cnt-respondidos').textContent = s.respondidos || 0;
      document.getElementById('fluxo-cnt-cancelados').textContent  = s.cancelados  || 0;
    }}).catch(function(){{}});
  }}

  function waFluxoRenderTabela(flows) {{
    var tbody = document.getElementById('fluxo-tbody');
    var tabela = document.getElementById('fluxo-table');
    var empty  = document.getElementById('fluxo-empty');
    if (!tbody) return;
    if (!flows || flows.length === 0) {{
      if (tabela) tabela.style.display = 'none';
      if (empty)  empty.style.display  = 'block';
      return;
    }}
    if (tabela) tabela.style.display = 'table';
    if (empty)  empty.style.display  = 'none';

    var BADGE = {{
      'aguardando':  '<span style="background:rgba(251,191,36,.15);color:#fbbf24;border:1px solid rgba(251,191,36,.3);border-radius:4px;padding:2px 7px;font-size:10px">⏳ Aguardando</span>',
      'respondido':  '<span style="background:rgba(37,211,102,.15);color:#25d366;border:1px solid rgba(37,211,102,.3);border-radius:4px;padding:2px 7px;font-size:10px">✅ Respondido</span>',
      'cancelado':   '<span style="background:rgba(100,116,139,.15);color:#94a3b8;border:1px solid rgba(100,116,139,.3);border-radius:4px;padding:2px 7px;font-size:10px">🚫 Cancelado</span>'
    }};
    var html = '';
    var recentes = flows.slice().reverse().slice(0, 100);
    recentes.forEach(function(fl) {{
      var badge  = BADGE[fl.status] || fl.status;
      var nome   = fl.nome || fl.phone || '';
      var resp   = fl.resposta_recebida ? ('"' + fl.resposta_recebida.substring(0, 30) + '"') : '—';
      var cls    = fl.classificacao === 'sim' ? '#25d366' : fl.classificacao === 'nao' ? '#ff4d6d' : '#94a3b8';
      html += '<tr style="border-bottom:1px solid rgba(28,34,55,.5)">';
      html += '<td style="padding:5px 6px;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="' + nome + '">' + nome + '</td>';
      html += '<td style="padding:5px 6px">' + badge + '</td>';
      html += '<td style="padding:5px 6px;color:' + cls + '">' + resp + '</td>';
      html += '<td style="padding:5px 6px;text-align:center">';
      if (fl.status === 'aguardando') {{
        html += '<button onclick="waFluxoCancelar(\\\'' + fl.id + '\\\')" style="background:none;border:1px solid #ff4d6d33;color:#ff4d6d;border-radius:4px;padding:2px 8px;font-size:10px;cursor:pointer">Cancelar</button>';
      }}
      html += '</td>';
      html += '</tr>';
    }});
    tbody.innerHTML = html;
  }}

  function waFluxoCancelar(id) {{
    fetch(FLOW_API + '/flows/' + id, {{method:'DELETE'}}).then(function(){{
      waFluxoLoadAtivos();
    }}).catch(function(){{}});
  }}

  function waFluxoLimpar() {{
    if (!confirm('Remover todos os fluxos concluídos e cancelados?')) return;
    fetch(FLOW_API + '/flows', {{method:'DELETE'}}).then(function(){{
      waFluxoLoadAtivos();
    }}).catch(function(){{}});
  }}

  function waFluxoRegistrar(clientes) {{
    // Registra fluxos no servidor após disparo
    var ativo = document.getElementById('fluxo-ativo');
    if (!ativo || !ativo.checked) return;
    var agora = new Date().toISOString();
    var payload = clientes.map(function(c) {{
      return {{ phone: c.phone, nome: c.nome || '', enviado_em: agora }};
    }});
    fetch(FLOW_API + '/flows', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify(payload)
    }}).then(function(){{
      setTimeout(waFluxoLoadAtivos, 1000);
    }}).catch(function(){{}});
  }}

  function waFireDisparo(){{
    var tpls=waGetTemplates();
    if(!tpls.length){{alert('Preencha pelo menos a Mensagem 1');return}}
    var selC=waClients.filter(function(c){{return waSelected.has(c.id)&&c.phone}});
    if(!selC.length){{alert('Selecione clientes com telefone');return}}
    if(!WA_BACKEND){{alert('Configure o backend na aba Configuração');return}}
    var inst=document.getElementById('wa-active-instance').value;
    if(!inst){{alert('Selecione o WhatsApp remetente!');return;}}

    var senderName=document.getElementById('wa-sender-name').value.trim();
    // Detectar template Meta selecionado (do dropdown ou campo nome)
    var metaTplName='';
    var metaTplLang='pt_BR';
    var metaTplParamCount=0;
    var selMeta=document.getElementById('wa-meta-tpl-select');
    if(selMeta&&selMeta.value!==''){{
      var metaIdx=parseInt(selMeta.value);
      var metaTpl=waMetaTemplatesCache[metaIdx];
      if(metaTpl){{
        metaTplName=metaTpl.name;
        metaTplLang=metaTpl.language||'pt_BR';
        var bodyComp=(metaTpl.components||[]).find(function(c){{return c.type==='BODY'}});
        if(bodyComp&&bodyComp.text){{metaTplParamCount=(bodyComp.text.match(/\{{\{{\d+\}}\}}/g)||[]).length;}}
      }}
    }}
    // Fallback: pegar do campo nome do template 1
    if(!metaTplName){{
      var n1=document.getElementById('wa-tpl-name-1');
      if(n1&&n1.value.trim()&&n1.value.trim()!=='template_padrao')metaTplName=n1.value.trim();
    }}
    var body={{clients:selC,templates:tpls,remetente:senderName}};
    if(metaTplName){{body.metaTemplateName=metaTplName;body.metaTemplateLang=metaTplLang;body.metaTemplateParamCount=metaTplParamCount;}}
    else if(inst==='Meta_API_Oficial'){{
      alert('Template Meta nao configurado!\\n\\nSelecione um template aprovado no dropdown ou preencha o campo Nome Meta ao lado da mensagem.');
      return;
    }}
    var visualDelay;
    if(waDispMode==='window'){{
      var winMin=parseInt(document.getElementById('wa-window').value)||20;
      body.windowMs=winMin*60000;
      visualDelay=Math.round(body.windowMs/selC.length);
    }}else{{
      var delay=parseInt(document.getElementById('wa-delay').value)*1000||5000;
      body.delayMs=delay;
      visualDelay=delay;
    }}

    document.getElementById('wa-fire-btn').disabled=true;
    document.getElementById('wa-progress').style.display='block';
    var h={{'Content-Type':'application/json'}};if(WA_KEY)h['x-api-key']=WA_KEY;h['x-wa-instance']=inst;
    fetch(WA_BACKEND+'/send-bulk?apikey='+(WA_KEY||''),{{method:'POST',headers:h,body:JSON.stringify(body)}}).then(function(){{
      waFluxoRegistrar(selC);
    }}).catch(function(){{}});
    var sent=0;
    var iv=setInterval(function(){{
      sent++;
      document.getElementById('wa-prog-fill').style.width=Math.round(sent/selC.length*100)+'%';
      document.getElementById('wa-prog-txt').textContent=sent+'/'+selC.length+' enviados';
      if(sent>=selC.length){{
        clearInterval(iv);
        document.getElementById('wa-fire-btn').disabled=false;
        /* Opção B: gravar entregue-pos explicitamente para clientes Pós */
        var hP={{'Content-Type':'application/json'}};if(WA_KEY)hP['x-api-key']=WA_KEY;
        selC.forEach(function(c){{
          if(waGetFase(c)==='pos'){{
            fetch(WA_BACKEND+'/status/'+c.id,{{method:'POST',headers:hP,body:JSON.stringify({{status:'entregue-pos',obs:'Pós-serviço disparado'}})}}).then(function(){{
              waTratativas[c.id]=waTratativas[c.id]||{{}};
              waTratativas[c.id].status='entregue-pos';
            }}).catch(function(){{}});
          }}
        }});
        setTimeout(function(){{waSyncStatus()}},3000);
      }}
    }},visualDelay);
  }}

  function waExportCSV(){{
    var csv='Nome,Telefone,Data,Cidade,Tipo de Atividade,Status\\n';
    waClients.forEach(function(c){{csv+='"'+c.nome+'","'+c.phone+'","'+(c.data||'')+'","'+(c.cidade||'')+'","'+(c.tipo||'')+'","'+waGetStatus(c)+'"\\n'}});
    var blob = new Blob(['\\ufeff'+csv], {{type: 'text/csv;charset=utf-8;'}});
    if (navigator.msSaveBlob) {{
      navigator.msSaveBlob(blob, 'agenda.csv');
      return;
    }}
    var link = document.createElement('a');
    var url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'agenda.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }}

  // ========== META TEMPLATE SELECTOR ==========
  var waMetaTemplatesCache=[];
  function waLoadMetaTemplates(){{
    if(!WA_BACKEND){{alert('Configure o backend primeiro na aba Configuração');return;}}
    var sel=document.getElementById('wa-meta-tpl-select');
    if(!sel)return;
    sel.innerHTML='<option value="">Carregando templates...</option>';
    var h={{}};if(WA_KEY)h['x-api-key']=WA_KEY;
    fetch(WA_BACKEND+'/meta/templates',{{headers:h}}).then(function(r){{return r.json()}}).then(function(data){{
      var tpls=(data.templates||data.data||[]).filter(function(t){{return t.status==='APPROVED'}});
      waMetaTemplatesCache=tpls;
      sel.innerHTML='<option value="">— Digitar manualmente ('+tpls.length+' aprovado(s)) —</option>';
      if(!tpls.length){{sel.innerHTML+='<option value="" disabled>Nenhum template aprovado encontrado</option>';return;}}
      tpls.forEach(function(t,i){{
        var bodyComp=(t.components||[]).find(function(c){{return c.type==='BODY'}});
        var bodyText=bodyComp?bodyComp.text.substring(0,60)+(bodyComp.text.length>60?'...':''):'';
        var cat=t.category==='MARKETING'?'📢':t.category==='UTILITY'?'🔧':'📋';
        var opt=document.createElement('option');
        opt.value=String(i);
        opt.textContent=cat+' '+t.name+' ('+t.language+') - '+bodyText;
        sel.appendChild(opt);
      }});
    }}).catch(function(e){{sel.innerHTML='<option value="">Erro: '+e.message+'</option>'}});
  }}
  function waApplyMetaTemplate(){{
    var sel=document.getElementById('wa-meta-tpl-select');
    var previewBox=document.getElementById('wa-meta-tpl-preview-box');
    if(!sel||sel.value===''){{if(previewBox)previewBox.style.display='none';return;}}
    var idx=parseInt(sel.value);
    var tpl=waMetaTemplatesCache[idx];
    if(!tpl)return;
    var headerComp=(tpl.components||[]).find(function(c){{return c.type==='HEADER'}});
    var bodyComp=(tpl.components||[]).find(function(c){{return c.type==='BODY'}});
    var footerComp=(tpl.components||[]).find(function(c){{return c.type==='FOOTER'}});
    var btnComp=(tpl.components||[]).find(function(c){{return c.type==='BUTTONS'}});
    var fullText='';
    if(headerComp&&headerComp.text)fullText+=headerComp.text+'\\n\\n';
    if(bodyComp&&bodyComp.text)fullText+=bodyComp.text;
    if(footerComp&&footerComp.text)fullText+='\\n\\n'+footerComp.text;
    fullText=fullText.split('{{{{1}}}}').join('{{{{nome}}}}').split('{{{{2}}}}').join('{{{{data}}}}').split('{{{{3}}}}').join('{{{{cidade}}}}').split('{{{{4}}}}').join('{{{{horario}}}}').split('{{{{5}}}}').join('{{{{tipo}}}}');
    var msg1=document.getElementById('wa-template-1');
    var name1=document.getElementById('wa-tpl-name-1');
    if(msg1)msg1.value=fullText;
    if(name1)name1.value=tpl.name;
    if(previewBox){{
      var ph='<div style="margin-bottom:6px"><strong style="color:#25d366">'+tpl.name+'</strong> <span style="color:#64748b;font-size:10px">('+tpl.category+' | '+tpl.language+')</span></div>';
      ph+=fullText.replace(/\\n/g,'<br>');
      if(btnComp&&btnComp.buttons){{
        ph+='<div style="margin-top:8px;border-top:1px solid rgba(255,255,255,.1);padding-top:6px"><strong style="color:#60a5fa;font-size:10px">Botões:</strong><br>';
        btnComp.buttons.forEach(function(b){{ph+='<span style="display:inline-block;background:rgba(96,165,250,.15);border:1px solid rgba(96,165,250,.3);border-radius:4px;padding:2px 8px;margin:2px 4px 2px 0;font-size:10px;color:#60a5fa">'+b.text+'</span>'}});
        ph+='</div>';
      }}
      previewBox.innerHTML=ph;
      previewBox.style.display='block';
    }}
    if(typeof waUpdatePreview==='function')waUpdatePreview();
  }}
  setTimeout(function(){{
    var sel=document.getElementById('wa-meta-tpl-select');
    if(sel&&sel.options.length<=1&&WA_BACKEND)waLoadMetaTemplates();
  }},2000);
  // ========== FIM META TEMPLATE SELECTOR ==========

  // Auto-load saved config
  (function(){{
    var u=localStorage.getItem('wa_backend')||document.getElementById('wa-backend-url').value;
    var k=localStorage.getItem('wa_key')||document.getElementById('wa-api-key').value;
    var inst=localStorage.getItem('wa_instance')||'svoboda';
    document.getElementById('wa-backend-url').value=u;
    document.getElementById('wa-api-key').value=k;
    document.getElementById('wa-instance-name').value=inst;
    if(u){{WA_BACKEND=u;WA_KEY=k;WA_INSTANCE=inst;waTestConnection();waSyncClients();}}
    var tmpl=document.getElementById('wa-template-1');
    if(!tmpl.value)tmpl.value='Olá {{{{nome}}}}! 👋\\\\nPassando para confirmar seu agendamento no dia *{{{{data}}}}* em {{{{cidade}}}}.\\\\nResponda *SIM* para confirmar ou *NÃO* caso precise reagendar. 😊';
    waUpdatePreview();
  }})();
  setInterval(function(){{if(WA_BACKEND&&waClients.length){{waSyncStatus();}}}},10000);
  // ── CHAT TAB ──
  var _chatConversations = [];
  var _chatActivePhone = null;
  var _chatPollTimer = null;
  var _chatListPollTimer = null;
  var _chatCurrentPage = 1;
  var _chatTotalPages = 1;

  function _chatFormatPhone(p) {{
    if (!p) return '';
    p = p.replace(/\D/g, '');
    if (p.startsWith('55') && p.length >= 12) {{
      var ddd = p.substring(2, 4);
      var num = p.substring(4);
      if (num.length === 9) return '(' + ddd + ') ' + num.substring(0,5) + '-' + num.substring(5);
      if (num.length === 8) return '(' + ddd + ') ' + num.substring(0,4) + '-' + num.substring(4);
    }}
    return p;
  }}

  function _chatEnsureBackend() {{
    if (!WA_BACKEND) {{
      WA_BACKEND = localStorage.getItem('wa_backend') || '';
      WA_KEY = localStorage.getItem('wa_key') || '';
      WA_INSTANCE = localStorage.getItem('wa_instance') || 'svoboda';
    }}
    return !!WA_BACKEND;
  }}

  var _chatLoadingMore = false;
  var _chatAllConversations = [];

  async function chatLoadConversations(page, append) {{
    if (!_chatEnsureBackend()) {{
      document.getElementById('chat-sidebar-count').textContent = '⚠️ Configure o backend na aba Configuração';
      return;
    }}
    page = page || 1;
    if (!append) document.getElementById('chat-sidebar-count').textContent = '⏳ Carregando...';
    try {{
      var r = await fetch(WA_BACKEND + '/conversations?apikey=' + WA_KEY + '&page=' + page + '&limit=50');
      var data = await r.json();
      if (Array.isArray(data)) {{
        _chatConversations = data;
        _chatCurrentPage = 1;
        _chatTotalPages = 1;
      }} else {{
        _chatConversations = data.conversations || [];
        _chatCurrentPage = data.page || 1;
        _chatTotalPages = data.pages || 1;
      }}
      if (append && page > 1) {{
        _chatAllConversations = _chatAllConversations.concat(_chatConversations);
      }} else {{
        _chatAllConversations = _chatConversations.slice();
      }}
      // Só renderiza a lista se não houver busca sintética ativa
      var _sq2 = (document.getElementById('chat-search-input') || {{}}).value || '';
      if (_sq2.trim() && _chatSyntheticList) {{
        _chatRenderSynthetic(_chatSyntheticList, _sq2.trim().toLowerCase());
      }} else {{
        chatRenderContacts(_chatAllConversations);
      }}
      _chatLoadingMore = false;
    }} catch(e) {{
      document.getElementById('chat-sidebar-count').textContent = 'Erro ao carregar';
      console.error('Chat load error:', e);
      _chatLoadingMore = false;
    }}
  }}

  
  // -- Cache de nomes no localStorage --
  function _chatSaveNomesToCache() {{
    var cache = JSON.parse(localStorage.getItem('wa_nome_cache') || '{{}}');
    waClients.forEach(function(c) {{
      if (c.nome && c.nome !== 'Cliente') {{
        var clean = (c.phone || '').replace(/\\D/g, '');
        if (clean) cache[clean.slice(-8)] = c.nome;
      }}
    }});
    localStorage.setItem('wa_nome_cache', JSON.stringify(cache));
  }}

  // â”€â”€ Helper: busca nome do cliente pelo telefone (waClients) â”€â”€
  function _chatGetNomeByPhone(phone) {{
    if (!phone) return '';
    var clean = phone.replace(/\D/g, '');
    // 1. Buscar em waClients (agenda ativa)
    if (typeof waClients !== 'undefined') {{
      for (var i = 0; i < waClients.length; i++) {{
        var cp = (waClients[i].phone || '').replace(/\D/g, '');
        if (cp && (cp === clean || cp.slice(-8) === clean.slice(-8))) {{
          return waClients[i].nome || '';
        }}
      }}
    }}
    // 2. Fallback: cache localStorage
    var cache = JSON.parse(localStorage.getItem('wa_nome_cache') || '{{}}');
    return cache[clean.slice(-8)] || '';
  }}
  // Busca phones em waClients e cache pelo nome (abordagem inversa: nome → phone → conversa)
  function _chatFindPhonesByName(query) {{
    var phones = new Set();
    if (typeof waClients !== 'undefined') {{
      for (var i = 0; i < waClients.length; i++) {{
        if ((waClients[i].nome || '').toLowerCase().includes(query)) {{
          var p = (waClients[i].phone || '').replace(/\D/g, '');
          if (p) phones.add(p.slice(-8));
        }}
      }}
    }}
    try {{
      var cache = JSON.parse(localStorage.getItem('wa_nome_cache') || '{{}}');
      Object.keys(cache).forEach(function(k) {{
        if ((cache[k] || '').toLowerCase().includes(query)) phones.add(k);
      }});
    }} catch(e) {{}}
    return phones;
  }}
  function chatRenderContacts(list) {{
    var q = (document.getElementById('chat-search-input') || {{}}).value || '';
    q = q.trim().toLowerCase();
    var qDigits = q.replace(/\D/g, '');
    var filtered = list;
    // Busca por nome: primeiro acha os phones em waClients/cache, depois filtra conversas
    var _namePhones = (q && !qDigits) ? _chatFindPhonesByName(q) : new Set();
    if (q) filtered = list.filter(function(c) {{
      var phoneClean = (c.phone || '').replace(/\D/g, '');
      // 1. Match pelo index nome→phone (busca inversa, mais confiável)
      if (_namePhones.size > 0 && _namePhones.has(phoneClean.slice(-8))) return true;
      // 2. Match pelo nome resolvido da conversa
      var nome = (_chatGetNomeByPhone(c.phone) || '').toLowerCase();
      if (nome && nome.includes(q)) return true;
      // 3. Match por número digitado
      if (qDigits && phoneClean.includes(qDigits)) return true;
      // 4. Match pela última mensagem
      if ((c.lastMessage || '').toLowerCase().includes(q)) return true;
      return false;
    }});

    var countText = filtered.length + ' conversa(s)';
    if (_chatTotalPages > 1) countText += ' • carregadas ' + _chatCurrentPage + '/' + _chatTotalPages + ' pág';
    document.getElementById('chat-sidebar-count').textContent = countText;

    var html = '';
    for (var i = 0; i < filtered.length; i++) {{
      var c = filtered[i];
      var isActive = _chatActivePhone === c.phone;
      var ts = c.lastTs ? new Date(c.lastTs).toLocaleTimeString('pt-BR',{{hour:'2-digit',minute:'2-digit'}}) : '';
      var preview = c.lastMessage || '';
      var fromIcon = c.lastFrom === 'me' ? '↩ ' : '';
      var unreadHtml = c.unread > 0 ? '<div class="chat-unread-badge">' + c.unread + '</div>' : '';
      var initials = c.phone.slice(-2);
      html += '<div class="chat-contact' + (isActive ? ' active' : '') + '" onclick="chatOpenConversation(\\'' + c.phone + '\\')">';
      html += '<div class="chat-contact-avatar">' + initials + '</div>';
      html += '<div class="chat-contact-info">';
      var _cn = _chatGetNomeByPhone(c.phone);
      html += '<div class="chat-contact-name">' + (_cn || _chatFormatPhone(c.phone)) + '</div>';
      if (_cn) html += '<div class="chat-contact-phone">' + _chatFormatPhone(c.phone) + '</div>';
      html += '<div class="chat-contact-preview">' + fromIcon + preview.replace(/</g,'&lt;').substring(0, 50) + '</div>';
      html += '</div>';
      html += '<div class="chat-contact-meta">';
      html += '<div class="chat-contact-time">' + ts + '</div>';
      html += unreadHtml;
      html += '</div></div>';
    }}
    // Indicador de carregamento (scroll infinito)
    if (_chatCurrentPage < _chatTotalPages) {{
      html += '<div id="chat-load-more" style="text-align:center;padding:12px;font-size:11px;color:#475569">⬇ Scroll para carregar mais</div>';
    }}
    var _emptyMsg = q
      ? '<div style="text-align:center;padding:30px;color:#475569;font-size:12px">🔍 Nenhum resultado para "' + q + '"</div>'
      : '<div style="text-align:center;padding:30px;color:#475569;font-size:12px">Nenhuma conversa encontrada</div>';
    document.getElementById('chat-contact-list').innerHTML = html || _emptyMsg;

    // Scroll infinito — carregar mais conversas ao chegar no final
    var contactList = document.getElementById('chat-contact-list');
    contactList.onscroll = function() {{
      if (this.scrollTop + this.clientHeight >= this.scrollHeight - 60) {{
        if (_chatCurrentPage < _chatTotalPages && !_chatLoadingMore) {{
          _chatLoadingMore = true;
          chatLoadConversations(_chatCurrentPage + 1, true);
        }}
      }}
    }};
  }}

  var _chatSearchDebounce = null;
  var _chatSyntheticList = null;
  var _chatExportCache = null;
  var _chatExportCacheTs = 0;

  function chatFilterContacts() {{
    var q = (document.getElementById('chat-search-input') || {{}}).value || '';
    q = q.trim();
    if (!q) {{
      _chatSyntheticList = null;
      chatRenderContacts(_chatAllConversations);
      return;
    }}
    // 1. Filtro imediato nos dados já carregados
    chatRenderContacts(_chatAllConversations);
    // 2. Debounce: busca no export-full para cobrir TODAS as páginas
    clearTimeout(_chatSearchDebounce);
    _chatSearchDebounce = setTimeout(async function() {{
      if (!_chatEnsureBackend()) return;
      var qL = q.toLowerCase();
      var qDigitsAll = qL.replace(/\D/g, '');
      var el = document.getElementById('chat-sidebar-count');
      try {{
        el.textContent = '🔍 Buscando...';

        // ── Busca por nome: usa export-full (tem TODOS os clientes) ──────────
        if (!qDigitsAll) {{
          var now = Date.now();
          if (!_chatExportCache || (now - _chatExportCacheTs) > 300000) {{
            try {{
              var expR = await fetch(WA_BACKEND + '/export-full?apikey=' + (WA_KEY || ''));
              _chatExportCache = await expR.json();
              _chatExportCacheTs = now;
            }} catch(e2) {{ _chatExportCache = []; }}
          }}

          // Acha clientes que batem com o nome
          var matchClients = [];
          if (Array.isArray(_chatExportCache)) {{
            _chatExportCache.forEach(function(c) {{
              if ((c.nome || '').toLowerCase().includes(qL)) matchClients.push(c);
            }});
          }}
          // Também adiciona do waClients local
          if (typeof waClients !== 'undefined') {{
            waClients.forEach(function(c) {{
              if ((c.nome || '').toLowerCase().includes(qL)) {{
                var jaEsta = matchClients.some(function(mc) {{
                  return (mc.phone||'').replace(/\D/g,'').slice(-8) === (c.phone||'').replace(/\D/g,'').slice(-8);
                }});
                if (!jaEsta) matchClients.push(c);
              }}
            }});
          }}

          // Verifica cache localStorage (wa_nome_cache): chave=ultimos8, valor=nome
          try {{
            var noCache = JSON.parse(localStorage.getItem('wa_nome_cache') || '{{}}');
            Object.keys(noCache).forEach(function(k8) {{
              if ((noCache[k8] || '').toLowerCase().includes(qL)) {{
                var jaEsta2 = matchClients.some(function(mc) {{
                  return (mc.phone||'').replace(/\\D/g,'').slice(-8) === k8;
                }});
                if (!jaEsta2) matchClients.push({{ nome: noCache[k8], phone: k8, status: '', _fromCache: true }});
              }}
            }});
          }} catch(ec) {{}}

          if (matchClients.length === 0) {{
            el.textContent = '🔍 Nenhum resultado para "' + q + '"';
            document.getElementById('chat-contact-list').innerHTML =
              '<div style="text-align:center;padding:30px;color:#475569;font-size:12px">🔍 Nenhum cliente encontrado com esse nome.<br><span style="font-size:11px;margin-top:4px;display:block">Tente buscar pelo número de telefone.</span></div>';
            return;
          }}

          // Cria entradas sintéticas para mostrar na sidebar
          // (independe de qual página da conversa eles estão)
          var syntheticConvs = matchClients.map(function(c) {{
            var phone = (c.phone || '').replace(/\D/g, '');
            if (phone && !phone.startsWith('55') && phone.length <= 11) phone = '55' + phone;
            return {{
              phone: phone,
              lastMessage: c.status ? '📋 Status: ' + c.status : '📋 Clique para abrir conversa',
              lastTs: null,
              unread: 0,
              lastFrom: '',
              _synthetic: true,
              _nome: c.nome
            }};
          }});

          el.textContent = matchClients.length + ' cliente(s) encontrado(s)';
          // Renderiza as entradas sintéticas diretamente
          _chatRenderSynthetic(syntheticConvs, qL);
          return;
        }}

        // ── Busca por número: filtra nas conversas carregadas ────────────────
        var convR = await fetch(WA_BACKEND + '/conversations?apikey=' + WA_KEY + '&page=1&limit=2000');
        var convData = await convR.json();
        var allConvs = convData.conversations || convData || [];
        // Filtra manualmente para detectar 0 resultados
        var matched = allConvs.filter(function(c) {{
          return (c.phone || '').replace(/\D/g, '').includes(qDigitsAll);
        }});
        if (matched.length === 0 && qDigitsAll.length >= 8) {{
          // Não encontrado nas conversas carregadas (pode estar em outra página)
          // Cria acesso direto pelo número digitado
          var dPhone = qDigitsAll;
          if (!dPhone.startsWith('55') && dPhone.length <= 11) dPhone = '55' + dPhone;
          var synth = [{{
            phone: dPhone,
            lastMessage: '📞 Clique para abrir conversa diretamente',
            lastTs: null, unread: 0, lastFrom: '', _synthetic: true,
            _nome: _chatFormatPhone(dPhone)
          }}];
          el.textContent = '1 resultado - acesso direto pelo número';
          _chatRenderSynthetic(synth, qL);
        }} else {{
          chatRenderContacts(allConvs);
        }}

      }} catch(e) {{
        chatRenderContacts(_chatAllConversations);
      }}
    }}, 500);
  }}

  function _chatRenderSynthetic(list, q) {{
    _chatSyntheticList = list;
    var html = '';
    for (var i = 0; i < list.length; i++) {{
      var c = list[i];
      var nome = c._nome || _chatGetNomeByPhone(c.phone) || _chatFormatPhone(c.phone);
      var preview = c.lastMessage || '';
      var initials = (c.phone || '').slice(-2);
      html += '<div class="chat-contact" onclick="chatOpenConversation(\\'' + c.phone + '\\')">';
      html += '<div class="chat-contact-avatar">' + initials + '</div>';
      html += '<div class="chat-contact-info">';
      html += '<div class="chat-contact-name">' + nome + '</div>';
      html += '<div class="chat-contact-phone">' + _chatFormatPhone(c.phone) + '</div>';
      html += '<div class="chat-contact-preview">' + preview.replace(/</g,'&lt;').substring(0,50) + '</div>';
      html += '</div>';
      html += '<div class="chat-contact-meta"><div class="chat-contact-time">→</div></div>';
      html += '</div>';
    }}
    document.getElementById('chat-contact-list').innerHTML = html ||
      '<div style="text-align:center;padding:30px;color:#475569;font-size:12px">Nenhuma conversa encontrada</div>';
  }}

  async function chatOpenConversation(phone) {{
    _chatActivePhone = phone;
    document.getElementById('chat-empty-main').style.display = 'none';
    var panel = document.getElementById('chat-main-active');
    panel.style.display = 'grid';
    var n=_chatFormatPhone(phone);
    var nome = _chatGetNomeByPhone(phone);
    if(nome) n = nome;
    document.getElementById('chat-main-name').textContent = n;
    document.getElementById('chat-main-client').textContent = nome ? _chatFormatPhone(phone) : '';
    document.getElementById('chat-main-phone').textContent = nome ? '' : phone;
    document.getElementById('chat-main-avatar').textContent = phone.slice(-2);

    // Se há busca ativa com lista sintética, mantém a sidebar correta
    var _sq = (document.getElementById('chat-search-input') || {{}}).value || '';
    if (_sq.trim() && _chatSyntheticList) {{
      _chatRenderSynthetic(_chatSyntheticList, _sq.trim().toLowerCase());
    }} else {{
      chatRenderContacts(_chatConversations);
    }}
    await chatLoadMessages();

    clearInterval(_chatPollTimer);
    _chatPollTimer = setInterval(chatLoadMessages, 5000);

    // Clear unread for this phone on backend
    try {{ await fetch(WA_BACKEND + '/msgs/' + phone + '?apikey=' + WA_KEY); }} catch(e) {{}}
  }}

  async function chatLoadMessages() {{
    if (!_chatActivePhone || !_chatEnsureBackend()) return;
    try {{
      var r = await fetch(WA_BACKEND + '/msgs/' + _chatActivePhone + '?apikey=' + WA_KEY);
      var msgs = await r.json();
      chatRenderMessages(msgs);
    }} catch(e) {{}}
  }}

  function chatRenderMessages(msgs) {{
    var el = document.getElementById('chat-messages-area');
    if (!msgs.length) {{
      el.innerHTML = '<div style="text-align:center;padding:30px;font-size:12px;color:#475569">Nenhuma mensagem ainda</div>';
      return;
    }}
    var html = '';
    var lastDate = '';
    for (var i = 0; i < msgs.length; i++) {{
      var m = msgs[i];
      var d = m.ts ? new Date(m.ts) : null;
      var dateStr = d ? d.toLocaleDateString('pt-BR') : '';
      var timeStr = d ? d.toLocaleTimeString('pt-BR',{{hour:'2-digit',minute:'2-digit'}}) : '';
      if (dateStr && dateStr !== lastDate) {{
        html += '<div class="chat-date-divider"><span>' + dateStr + '</span></div>';
        lastDate = dateStr;
      }}
      var isSent = m.from === 'me';
      var text = (m.text || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\n/g,'<br>');
      html += '<div class="chat-msg ' + (isSent ? 'sent' : 'received') + '">';
      var bubbleContent = text;
      if (m.type === 'image' && m.mediaId) {{
        bubbleContent = '<img class="chat-msg-image" src="' + WA_BACKEND + '/media-proxy/' + m.mediaId + '?apikey=' + WA_KEY + '" alt="Foto" onclick="window.open(this.src)" loading="lazy">';
        if (m.text && m.text.indexOf('Foto') < 0) bubbleContent += '<div style="margin-top:4px;font-size:12px">' + text + '</div>';
      }} else if (m.type === 'audio' && m.mediaId) {{
        bubbleContent = '<audio class="chat-msg-audio" controls preload="none"><source src="' + WA_BACKEND + '/media-proxy/' + m.mediaId + '?apikey=' + WA_KEY + '"></audio>';
      }} else if (m.type === 'video' && m.mediaId) {{
        bubbleContent = '<video style="max-width:250px;border-radius:8px" controls preload="none"><source src="' + WA_BACKEND + '/media-proxy/' + m.mediaId + '?apikey=' + WA_KEY + '"></video>';
      }} else if (m.type === 'location' && m.latitude) {{
        bubbleContent = '<a class="chat-msg-location" href="https://www.google.com/maps?q=' + m.latitude + ',' + m.longitude + '" target="_blank">&#128205; Ver no Mapa (' + Number(m.latitude).toFixed(4) + ', ' + Number(m.longitude).toFixed(4) + ')</a>';
      }}
      html += '<div class="chat-msg-bubble">' + bubbleContent + '</div>';
      html += '<div class="chat-msg-time">' + timeStr + '</div>';
      html += '</div>';
    }}
    el.innerHTML = html;
    el.scrollTop = el.scrollHeight;
  }}

  async function chatSendReply() {{
    if (!_chatActivePhone || !_chatEnsureBackend()) return;
    var input = document.getElementById('chat-reply-text');
    var text = input.value.trim();
    if (!text) return;
    input.value = '';
    input.style.height = 'auto';
    try {{
      await fetch(WA_BACKEND + '/send-reply?apikey=' + WA_KEY, {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{ phone: _chatActivePhone, text: text }})
      }});
      await chatLoadMessages();
    }} catch(e) {{ alert('Erro ao enviar: ' + e.message); }}
  }}

  function chatShowNewMsg() {{
    var panel = document.getElementById('chat-new-msg-panel');
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    if (panel.style.display === 'block') document.getElementById('chat-new-phone').focus();
  }}
  function chatHideNewMsg() {{
    document.getElementById('chat-new-msg-panel').style.display = 'none';
    document.getElementById('chat-new-phone').value = '';
    document.getElementById('chat-new-text').value = '';
  }}
  async function chatSendNewMsg() {{
    if (!_chatEnsureBackend()) return alert('Configure o backend na aba Configuração');
    var phone = document.getElementById('chat-new-phone').value.replace(/\D/g, '');
    var text = document.getElementById('chat-new-text').value.trim();
    if (!phone || phone.length < 10) return alert('Digite um número válido com DDD');
    if (!text) return alert('Digite uma mensagem');
    try {{
      var r = await fetch(WA_BACKEND + '/send-reply?apikey=' + WA_KEY, {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{ phone: phone, text: text }})
      }});
      var data = await r.json();
      if (data.error) throw new Error(data.error);
      chatHideNewMsg();
      await chatLoadConversations(1);
      chatOpenConversation(phone);
    }} catch(e) {{ alert('Erro ao enviar: ' + e.message); }}
  }}


  // -- Audio Recording --
  var _chatMediaRecorder = null;
  var _chatAudioChunks = [];
  var _chatRecordingTimer = null;
  var _chatRecordingSeconds = 0;

  function chatToggleRecording() {{
    if (_chatMediaRecorder && _chatMediaRecorder.state === 'recording') {{
      _chatMediaRecorder.stop();
      return;
    }}
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {{
      alert('Seu navegador nao suporta gravacao de audio');
      return;
    }}
    navigator.mediaDevices.getUserMedia({{ audio: true }}).then(function(stream) {{
      _chatAudioChunks = [];
      _chatRecordingSeconds = 0;
      var options = {{ mimeType: 'audio/webm;codecs=opus' }};
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {{
        options = {{ mimeType: 'audio/webm' }};
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {{
          options = {{}};
        }}
      }}
      _chatMediaRecorder = new MediaRecorder(stream, options);
      _chatMediaRecorder.ondataavailable = function(e) {{
        if (e.data.size > 0) _chatAudioChunks.push(e.data);
      }};
      _chatMediaRecorder.onstop = function() {{
        stream.getTracks().forEach(function(t) {{ t.stop(); }});
        clearInterval(_chatRecordingTimer);
        document.getElementById('chat-mic-btn').classList.remove('recording');
        document.getElementById('chat-audio-timer').classList.remove('active');
        if (_chatAudioChunks.length === 0) return;
        var blob = new Blob(_chatAudioChunks, {{ type: _chatMediaRecorder.mimeType || 'audio/webm' }});
        chatSendAudioBlob(blob);
      }};
      _chatMediaRecorder.start(250);
      document.getElementById('chat-mic-btn').classList.add('recording');
      document.getElementById('chat-audio-timer').classList.add('active');
      _chatRecordingTimer = setInterval(function() {{
        _chatRecordingSeconds++;
        var m = Math.floor(_chatRecordingSeconds / 60);
        var s = _chatRecordingSeconds % 60;
        document.getElementById('chat-audio-timer').textContent = m + ':' + (s < 10 ? '0' : '') + s;
      }}, 1000);
    }}).catch(function(err) {{
      alert('Permissao de microfone negada: ' + err.message);
    }});
  }}

  async function chatSendAudioBlob(blob) {{
    if (!_chatActivePhone || !_chatEnsureBackend()) return;
    var btn = document.getElementById('chat-mic-btn');
    btn.disabled = true;
    btn.textContent = '...';
    try {{
      var base64 = await new Promise(function(resolve, reject) {{
        var reader = new FileReader();
        reader.onloadend = function() {{ resolve(reader.result.split(',')[1]); }};
        reader.onerror = function() {{ reject(new Error('Erro ao ler audio')); }};
        reader.readAsDataURL(blob);
      }});
      var h = {{'Content-Type': 'application/json'}};
      if (WA_KEY) h['x-api-key'] = WA_KEY;
      var r = await fetch(WA_BACKEND + '/send-audio?apikey=' + WA_KEY, {{
        method: 'POST', headers: h,
        body: JSON.stringify({{ phone: _chatActivePhone, audio: base64 }})
      }});
      var data = await r.json();
      if (!r.ok) throw new Error(data.error || 'Erro ao enviar audio');
      await chatLoadMessages();
    }} catch (e) {{
      alert('Erro ao enviar audio: ' + e.message);
    }} finally {{
      btn.disabled = false;
      btn.textContent = '🎤';
    }}
  }}

    // Observa mudança de aba para iniciar/parar polling do chat
  var _origShowWaSub = showWaSub;
  showWaSub = function(id, btn) {{
    _origShowWaSub(id, btn);
    if (id === 'wa-chat') {{
      document.body.classList.add('chat-mode');
      _chatAllConversations = [];
      chatLoadConversations(1);
      clearInterval(_chatListPollTimer);
      _chatListPollTimer = setInterval(function(){{ chatLoadConversations(_chatCurrentPage); }}, 10000);
    }} else {{
      document.body.classList.remove('chat-mode');
      clearInterval(_chatPollTimer);
      clearInterval(_chatListPollTimer);
    }}
    if (id === 'wa-disparo') {{
      waFluxoLoadConfig();
      clearInterval(_fluxoPollTimer);
      _fluxoPollTimer = setInterval(waFluxoLoadAtivos, 30000);
    }} else {{
      clearInterval(_fluxoPollTimer);
    }}
    if (id === 'wa-config') {{
      // Auto-testa conexão ao abrir a aba Configuração
      setTimeout(function() {{ if(WA_BACKEND) waTestConnection(); }}, 300);
    }}
  }};


  async function tplDelete(name) {{
  if (!confirm('Excluir o template "' + name + '"?')) return;
  try {{
    var r = await fetch(WA_BACKEND + '/meta/templates/' + name + '?apikey=' + WA_KEY, {{ method: 'DELETE' }});
    var d = await r.json();
    if (d.error) throw new Error(d.error);
    tplLoad();
  }} catch(e) {{
    alert('Erro: ' + e.message);
  }}
}}

  function waExportFull(){{
    if(!WA_BACKEND){{alert('Conecte o backend primeiro na aba Configuração');return}}
    var btn=event.target;btn.textContent='⏳ Exportando...';btn.disabled=true;
    var h={{}};if(WA_KEY)h['x-api-key']=WA_KEY;
    fetch(WA_BACKEND+'/export-full?apikey='+(WA_KEY||''),{{headers:h}}).then(function(r){{return r.json()}}).then(function(data){{
      var fs=waGetChecked('dd-status');
      var fc=waGetChecked('dd-city');
      var ft=waGetChecked('dd-tipo');
      var q=(document.getElementById('wa-search').value||'').toLowerCase();
      var filtered=data.filter(function(c){{
        if(fs.length && fs.indexOf(c.status)<0) return false;
        if(fc.length && fc.indexOf(c.cidade)<0) return false;
        if(ft.length && ft.indexOf(c.tipo)<0) return false;
        if(q && c.nome.toLowerCase().indexOf(q)<0 && (c.phone||'').indexOf(q)<0) return false;
        return true;
      }});
      var sep=';';
      var csv='Nome'+sep+'Telefone'+sep+'Data'+sep+'Cidade'+sep+'Tipo Atividade'+sep+'Status'+sep+'Observacao'+sep+'Atualizado Em'+sep+'Total Msgs'+sep+'Conversas\\n';
      filtered.forEach(function(c){{
        var esc=function(v){{return '"'+String(v||'').replace(/"/g,'""')+'"'}};
        csv+=esc(c.nome)+sep+esc(c.phone)+sep+esc(c.data)+sep+esc(c.cidade)+sep+esc(c.tipo)+sep+esc(c.status)+sep+esc(c.obs)+sep+esc(c.updatedAt)+sep+esc(c.totalMsgs)+sep+esc(c.conversas)+'\\n';
      }});
      var blob=new Blob(['\\ufeff'+csv],{{type:'text/csv;charset=utf-8;'}});
      var link=document.createElement('a');
      link.href=URL.createObjectURL(blob);
      var hoje=new Date().toISOString().split('T')[0];
      link.download='agenda_completa_'+hoje+'.csv';
      link.click();
      btn.textContent='📊 Exportar Completo';btn.disabled=false;
    }}).catch(function(e){{alert('Erro: '+e.message);btn.textContent='📊 Exportar Completo';btn.disabled=false}});
  }}

  // ── BUTTON CONFIG: Load/Save das respostas dos botões ──
  (function(){{
    var BCFG_MAP = {{
      'sim, confirmo':         'bcfg-sim-confirmo',
      'preciso reagendar':     'bcfg-preciso-reagendar',
      'cancelar':              'bcfg-cancelar',
      'agendar':               'bcfg-agendar',
      'ja devolvi':            'bcfg-ja-devolvi',
      'sim, tudo certo':       'bcfg-sim-tudo-certo',
      'nao, tenho problema':   'bcfg-nao-tenho-problema',
      'quero falar com alguem':'bcfg-quero-falar'
    }};
    var backend = localStorage.getItem('wa_backend') || '';
    var key = localStorage.getItem('wa_key') || '';
    if(!backend) return;
    fetch(backend+'/button-config', {{headers:{{'x-api-key':key}}}})
      .then(function(r){{return r.json()}})
      .then(function(cfg){{
        for(var btn in BCFG_MAP){{
          var el = document.getElementById(BCFG_MAP[btn]);
          if(el && cfg[btn]) el.value = cfg[btn];
        }}
      }}).catch(function(e){{console.log('btnCfg load err:', e)}});

    window.btnCfgSave = function(){{
      var payload = {{}};
      for(var btn in BCFG_MAP){{
        var el = document.getElementById(BCFG_MAP[btn]);
        if(el && el.value.trim()) payload[btn] = el.value.trim();
      }}
      fetch(backend+'/button-config', {{
        method:'POST',
        headers:{{'Content-Type':'application/json','x-api-key':key}},
        body: JSON.stringify(payload)
      }}).then(function(r){{return r.json()}}).then(function(j){{
        var st = document.getElementById('btn-cfg-status');
        if(st){{st.style.display='block';st.textContent='✓ Salvo com sucesso!';setTimeout(function(){{st.style.display='none'}},3000)}}
      }}).catch(function(e){{alert('Erro ao salvar: '+e.message)}});
    }};
  }})();

  </script>
</div>
"""
