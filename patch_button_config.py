"""
patch_button_config.py — Adiciona:
1. Rotas GET/POST /button-config no backend
2. Modifica BUTTON_FLOWS para ler mensagens do Redis (editáveis pela UI)
3. Injeta seção de edição no HTML do dashboard (VPS)
"""
import paramiko, os, sys, time, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

ts = time.strftime('%Y%m%d_%H%M%S')

# ══════════════════════════════════════════════════
# BACKUP
# ══════════════════════════════════════════════════
print(f'[1/5] Backup...')
i, o, e = c.exec_command(f'docker cp backend-agenda:/app/index.js /docker/backup_index_{ts}_pre_config.js')
time.sleep(2)
i, o, e = c.exec_command(f'cp /docker/dashboard/html/index.html /docker/backup_dashboard_{ts}.html')
time.sleep(1)
print('    OK')

# ══════════════════════════════════════════════════
# PATCH BACKEND: Adicionar /button-config + BUTTON_FLOWS dinâmico
# ══════════════════════════════════════════════════
patch_js = r'''
const fs = require('fs');
let code = fs.readFileSync('/app/index.js', 'utf8');

// ─────────────────────────────────────────────
// PARTE 1: Adicionar rotas /button-config
// ─────────────────────────────────────────────
if (!code.includes('/button-config')) {
  const healthAnchor = "app.get('/health'";
  if (!code.includes(healthAnchor)) {
    console.log('[!] Âncora /health não encontrada!');
    process.exit(1);
  }

  const configRoutes = `
// ──────────────────────────────────────────────
// BUTTON CONFIG — Mensagens editáveis dos botões
// ──────────────────────────────────────────────
const KEY_BUTTON_CONFIG = 'agenda:button-config';

const DEFAULT_BUTTON_CONFIG = {
  'sim, confirmo':          'Perfeito, NOME! Seu atendimento está confirmado. Nossa equipe estará no local conforme agendado. Obrigado!',
  'preciso reagendar':      'Sem problemas, NOME! Por favor, nos informe uma nova data e horário de sua preferência.',
  'cancelar':               'Entendido, NOME. Seu atendimento foi cancelado. Caso precise, entre em contato conosco.',
  'agendar':                'Certo, NOME! Por favor, nos informe uma data e horário para agendarmos a retirada do equipamento.',
  'ja devolvi':             'Obrigado pela informação, NOME! Vamos verificar e atualizar nosso sistema.',
  'sim, tudo certo':        'Que bom saber, NOME! Ficamos felizes que está tudo funcionando. Qualquer dúvida, estamos à disposição!',
  'nao, tenho problema':    'Lamentamos, NOME. Nossa equipe de suporte será acionada para resolver o quanto antes.',
  'quero falar com alguem': 'Certo, NOME! Um de nossos atendentes entrará em contato em breve.'
};

app.get('/button-config', async (req, res) => {
  try {
    const raw = await redis.get(KEY_BUTTON_CONFIG);
    res.json(raw ? JSON.parse(raw) : DEFAULT_BUTTON_CONFIG);
  } catch (e) { res.status(500).json({ error: e.message }); }
});

app.post('/button-config', async (req, res) => {
  try {
    const existing = await redis.get(KEY_BUTTON_CONFIG);
    const current = existing ? JSON.parse(existing) : DEFAULT_BUTTON_CONFIG;
    const merged = { ...current, ...req.body };
    await redis.set(KEY_BUTTON_CONFIG, JSON.stringify(merged));
    res.json({ ok: true, config: merged });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

`;

  code = code.replace(healthAnchor, configRoutes + '\n' + healthAnchor);
  console.log('[+] Rotas /button-config adicionadas');
} else {
  console.log('[=] Rotas /button-config já existem');
}

// ─────────────────────────────────────────────
// PARTE 2: Modificar BUTTON_FLOWS para ler do Redis
// ─────────────────────────────────────────────
// Substituir o bloco hardcoded por leitura dinâmica
const oldFlowBlock = `const BUTTON_FLOWS = {
              // Fluxo A: Confirmação de visita
              'sim, confirmo':          { status: 'confirmado',      msg: 'Perfeito, NOME! Seu atendimento está confirmado. Nossa equipe estará no local conforme agendado. Obrigado!' },
              'preciso reagendar':      { status: 'reagendado',      msg: 'Sem problemas, NOME! Por favor, nos informe uma nova data e horário de sua preferência.' },
              'cancelar':               { status: 'nao-atendido',    msg: 'Entendido, NOME. Seu atendimento foi cancelado. Caso precise, entre em contato conosco.' },
              // Fluxo B: Recolhimento de equipamento
              'agendar':                { status: 'agendado',        msg: 'Certo, NOME! Por favor, nos informe uma data e horário para agendarmos a retirada do equipamento.' },
              'já devolvi':             { status: 'resolvido',       msg: 'Obrigado pela informação, NOME! Vamos verificar e atualizar nosso sistema.' },
              'ja devolvi':             { status: 'resolvido',       msg: 'Obrigado pela informação, NOME! Vamos verificar e atualizar nosso sistema.' },
              // Fluxo C: Pesquisa de qualidade
              'sim, tudo certo':        { status: 'satisfeito',      msg: 'Que bom saber, NOME! Ficamos felizes que está tudo funcionando. Qualquer dúvida, estamos à disposição!' },
              'não, tenho problema':    { status: 'problema-aberto', msg: 'Lamentamos, NOME. Nossa equipe de suporte será acionada para resolver o quanto antes.' },
              'nao, tenho problema':    { status: 'problema-aberto', msg: 'Lamentamos, NOME. Nossa equipe de suporte será acionada para resolver o quanto antes.' },
              'quero falar com alguém': { status: 'problema-aberto', msg: 'Certo, NOME! Um de nossos atendentes entrará em contato em breve.' },
              'quero falar com alguem': { status: 'problema-aberto', msg: 'Certo, NOME! Um de nossos atendentes entrará em contato em breve.' },
            };`;

const newFlowBlock = `// Mapa de botão → status (fixo) — mensagens vêm do Redis
            const BUTTON_STATUS = {
              'sim, confirmo': 'confirmado', 'preciso reagendar': 'reagendado', 'cancelar': 'nao-atendido',
              'agendar': 'agendado', 'já devolvi': 'resolvido', 'ja devolvi': 'resolvido',
              'sim, tudo certo': 'satisfeito',
              'não, tenho problema': 'problema-aberto', 'nao, tenho problema': 'problema-aberto',
              'quero falar com alguém': 'problema-aberto', 'quero falar com alguem': 'problema-aberto',
            };
            // Ler mensagens editáveis do Redis
            let btnMsgs = null;
            try {
              const cfgRaw = await redis.get('agenda:button-config');
              btnMsgs = cfgRaw ? JSON.parse(cfgRaw) : null;
            } catch(e) {}
            if (!btnMsgs) {
              btnMsgs = {
                'sim, confirmo': 'Perfeito, NOME! Seu atendimento está confirmado. Nossa equipe estará no local conforme agendado. Obrigado!',
                'preciso reagendar': 'Sem problemas, NOME! Por favor, nos informe uma nova data e horário de sua preferência.',
                'cancelar': 'Entendido, NOME. Seu atendimento foi cancelado. Caso precise, entre em contato conosco.',
                'agendar': 'Certo, NOME! Por favor, nos informe uma data e horário para agendarmos a retirada do equipamento.',
                'ja devolvi': 'Obrigado pela informação, NOME! Vamos verificar e atualizar nosso sistema.',
                'sim, tudo certo': 'Que bom saber, NOME! Ficamos felizes que está tudo funcionando. Qualquer dúvida, estamos à disposição!',
                'nao, tenho problema': 'Lamentamos, NOME. Nossa equipe de suporte será acionada para resolver o quanto antes.',
                'quero falar com alguem': 'Certo, NOME! Um de nossos atendentes entrará em contato em breve.'
              };
            }
            const BUTTON_FLOWS = {};
            for (const [btn, st] of Object.entries(BUTTON_STATUS)) {
              const normalKey = btn.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
              BUTTON_FLOWS[btn] = { status: st, msg: btnMsgs[btn] || btnMsgs[normalKey] || 'Obrigado pelo retorno!' };
            }`;

if (code.includes(oldFlowBlock)) {
  code = code.replace(oldFlowBlock, newFlowBlock);
  console.log('[+] BUTTON_FLOWS atualizado para ler do Redis');
} else if (code.includes('BUTTON_FLOWS') && !code.includes('BUTTON_STATUS')) {
  console.log('[!] BUTTON_FLOWS encontrado mas formato diferente. Tentando patch alternativo...');
  // Fallback: substituir a partir do início do bloco
  const startMarker = "const BUTTON_FLOWS = {";
  const endMarker = "};";
  const startIdx = code.indexOf(startMarker);
  if (startIdx !== -1) {
    // Encontrar o fechamento correto (depois dos 8+ itens)
    let endIdx = startIdx;
    let braceCount = 0;
    for (let i = startIdx; i < code.length; i++) {
      if (code[i] === '{') braceCount++;
      if (code[i] === '}') { braceCount--; if (braceCount === 0) { endIdx = i + 2; break; } }
    }
    code = code.substring(0, startIdx) + newFlowBlock + code.substring(endIdx);
    console.log('[+] BUTTON_FLOWS substituído (método alternativo)');
  }
} else {
  console.log('[=] BUTTON_FLOWS já usa Redis ou não encontrado');
}

// ── Salvar ──
fs.writeFileSync('/app/index.js', code);
console.log('[+] index.js salvo (' + code.split('\n').length + ' linhas)');

// Verificação
const v = fs.readFileSync('/app/index.js', 'utf8');
console.log('[✓] /button-config:', v.includes('/button-config'));
console.log('[✓] BUTTON_STATUS:', v.includes('BUTTON_STATUS'));
console.log('[✓] agenda:button-config:', v.includes('agenda:button-config'));
'''

print(f'\n[2/5] Aplicando patch no backend...')
sftp = c.open_sftp()
with sftp.open('/tmp/patch_config.js', 'w') as f:
    f.write(patch_js)
sftp.close()

i, o, e = c.exec_command('docker cp /tmp/patch_config.js backend-agenda:/tmp/patch_config.js')
time.sleep(1)
i, o, e = c.exec_command('docker exec backend-agenda node /tmp/patch_config.js')
time.sleep(5)
out = o.read().decode('utf-8', errors='replace').strip()
err = e.read().decode('utf-8', errors='replace').strip()
print(out)
if err:
    print(f'    STDERR: {err[:300]}')

# ══════════════════════════════════════════════════
# SEED: Salvar config default no Redis
# ══════════════════════════════════════════════════
print(f'\n[3/5] Salvando config default no Redis...')
default_config = json.dumps({
    "sim, confirmo": "Perfeito, NOME! Seu atendimento está confirmado. Nossa equipe estará no local conforme agendado. Obrigado!",
    "preciso reagendar": "Sem problemas, NOME! Por favor, nos informe uma nova data e horário de sua preferência.",
    "cancelar": "Entendido, NOME. Seu atendimento foi cancelado. Caso precise, entre em contato conosco.",
    "agendar": "Certo, NOME! Por favor, nos informe uma data e horário para agendarmos a retirada do equipamento.",
    "ja devolvi": "Obrigado pela informação, NOME! Vamos verificar e atualizar nosso sistema.",
    "sim, tudo certo": "Que bom saber, NOME! Ficamos felizes que está tudo funcionando. Qualquer dúvida, estamos à disposição!",
    "nao, tenho problema": "Lamentamos, NOME. Nossa equipe de suporte será acionada para resolver o quanto antes.",
    "quero falar com alguem": "Certo, NOME! Um de nossos atendentes entrará em contato em breve."
}, ensure_ascii=False)

escaped = default_config.replace("'", "'\"'\"'")
i, o, e = c.exec_command(f"docker exec redis-agenda redis-cli SET agenda:button-config '{escaped}'")
time.sleep(1)
print(f'    {o.read().decode().strip()}')

# ══════════════════════════════════════════════════
# RESTART
# ══════════════════════════════════════════════════
print(f'\n[4/5] Reiniciando backend-agenda...')
i, o, e = c.exec_command('docker restart backend-agenda')
time.sleep(10)
print(f'    {o.read().decode().strip()}')

# ══════════════════════════════════════════════════
# INJETAR UI NO DASHBOARD HTML (VPS)
# ══════════════════════════════════════════════════
print(f'\n[5/5] Injetando seção de edição no dashboard...')

inject_html = r'''
<!-- BOTÃO CONFIG EDITOR (injetado) -->
<style>
.btn-cfg-section{margin-top:24px;background:#0d1117;border:1px solid #1c2237;border-radius:12px;padding:20px}
.btn-cfg-title{font-size:15px;font-weight:800;color:#25d366;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.btn-cfg-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.btn-cfg-card{background:#111520;border:1px solid #1c2237;border-radius:10px;padding:14px}
.btn-cfg-label{font-size:11px;font-weight:700;margin-bottom:6px;display:flex;align-items:center;gap:6px}
.btn-cfg-label.green{color:#25d366}
.btn-cfg-label.blue{color:#60a5fa}
.btn-cfg-label.red{color:#ff4d6d}
.btn-cfg-label.purple{color:#a78bfa}
.btn-cfg-label.yellow{color:#fbbf24}
.btn-cfg-label.orange{color:#fb923c}
.btn-cfg-textarea{width:100%;background:#0d1117;border:1px solid #1c2237;border-radius:8px;padding:8px 12px;color:#e8eaf6;font-size:12px;font-family:inherit;resize:vertical;outline:none;box-sizing:border-box}
.btn-cfg-textarea:focus{border-color:#25d366}
.btn-cfg-hint{font-size:10px;color:#475569;margin-top:4px}
.btn-cfg-save{background:#25d366;color:#022c22;border:none;padding:12px 24px;border-radius:10px;font-size:14px;font-weight:700;cursor:pointer;width:100%;margin-top:16px;font-family:inherit;transition:all .2s}
.btn-cfg-save:hover{background:#128c7e;color:#fff}
.btn-cfg-status{text-align:center;font-size:12px;margin-top:8px;color:#25d366;display:none}
.btn-cfg-flow-title{font-size:13px;font-weight:700;color:#94a3b8;margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid #1c2237;grid-column:1/-1}
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

<script>
(function(){
  var BCFG_MAP = {
    'sim, confirmo':         'bcfg-sim-confirmo',
    'preciso reagendar':     'bcfg-preciso-reagendar',
    'cancelar':              'bcfg-cancelar',
    'agendar':               'bcfg-agendar',
    'ja devolvi':            'bcfg-ja-devolvi',
    'sim, tudo certo':       'bcfg-sim-tudo-certo',
    'nao, tenho problema':   'bcfg-nao-tenho-problema',
    'quero falar com alguem':'bcfg-quero-falar'
  };
  var backend = localStorage.getItem('wa_backend') || '';
  var key = localStorage.getItem('wa_key') || '';
  if(!backend) return;
  // Load
  fetch(backend+'/button-config', {headers:{'x-api-key':key}})
    .then(function(r){return r.json()})
    .then(function(cfg){
      for(var btn in BCFG_MAP){
        var el = document.getElementById(BCFG_MAP[btn]);
        if(el && cfg[btn]) el.value = cfg[btn];
      }
    }).catch(function(e){console.log('btnCfg load err:', e)});

  window.btnCfgSave = function(){
    var payload = {};
    for(var btn in BCFG_MAP){
      var el = document.getElementById(BCFG_MAP[btn]);
      if(el && el.value.trim()) payload[btn] = el.value.trim();
    }
    fetch(backend+'/button-config', {
      method:'POST',
      headers:{'Content-Type':'application/json','x-api-key':key},
      body: JSON.stringify(payload)
    }).then(function(r){return r.json()}).then(function(j){
      var st = document.getElementById('btn-cfg-status');
      if(st){st.style.display='block';st.textContent='✓ Salvo com sucesso!';setTimeout(function(){st.style.display='none'},3000)}
    }).catch(function(e){alert('Erro ao salvar: '+e.message)});
  };
})();
</script>
<!-- FIM BOTÃO CONFIG EDITOR -->
'''

# Salvar o HTML no VPS
sftp = c.open_sftp()
with sftp.open('/tmp/btn_cfg_inject.html', 'w') as f:
    f.write(inject_html)
sftp.close()

# Injetar antes do fechamento do wa-disparo (ou antes do footer)
inject_script = r'''
import sys
html = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()
if 'btn-cfg-section' in html:
    print('[=] Seção já existe no HTML')
    sys.exit(0)
inject = open('/tmp/btn_cfg_inject.html', 'r', encoding='utf-8').read()
# Inserir antes de "<!-- FIM SEÇÃO FLUXO -->" ou antes de "</div><!-- SUB: Configuração -->"
anchor = '<!-- FIM SEÇÃO FLUXO -->'
if anchor not in html:
    # Fallback: inserir antes de "SUB: Configuração"
    anchor = '<!-- SUB: Configuração -->'
    if anchor not in html:
        # Fallback 2: antes do footer
        anchor = '<footer'
        if anchor not in html:
            print('[!] Nenhum ponto de inserção encontrado!')
            sys.exit(1)
idx = html.index(anchor)
html = html[:idx] + inject + '\n' + html[idx:]
open('/docker/dashboard/html/index.html', 'w', encoding='utf-8').write(html)
print('[+] Seção injetada no HTML (' + str(len(inject)) + ' bytes)')
'''

sftp = c.open_sftp()
with sftp.open('/tmp/inject_btn_cfg.py', 'w') as f:
    f.write(inject_script)
sftp.close()

i, o, e = c.exec_command('python3 /tmp/inject_btn_cfg.py')
time.sleep(3)
out = o.read().decode('utf-8', errors='replace').strip()
err = e.read().decode('utf-8', errors='replace').strip()
print(f'    {out}')
if err:
    print(f'    ERR: {err[:200]}')

# ══════════════════════════════════════════════════
# VERIFICAÇÃO FINAL
# ══════════════════════════════════════════════════
print(f'\n=== VERIFICAÇÃO ===')

# Container
i, o, e = c.exec_command('docker ps --filter name=backend-agenda --format "{{.Names}}: {{.Status}}"')
time.sleep(1)
print(f'Container: {o.read().decode().strip()}')

# /button-config rota existe
i, o, e = c.exec_command('docker exec backend-agenda grep -c "button-config" /app/index.js')
time.sleep(1)
print(f'/button-config: {o.read().decode().strip()} ocorrências')

# BUTTON_STATUS (dinâmico) existe
i, o, e = c.exec_command('docker exec backend-agenda grep -c "BUTTON_STATUS" /app/index.js')
time.sleep(1)
print(f'BUTTON_STATUS: {o.read().decode().strip()} ocorrências')

# Config no Redis
i, o, e = c.exec_command('docker exec redis-agenda redis-cli EXISTS agenda:button-config')
time.sleep(1)
print(f'Redis button-config: {"existe" if o.read().decode().strip() == "1" else "NÃO EXISTE"}')

# HTML atualizado
i, o, e = c.exec_command('grep -c "btn-cfg-section" /docker/dashboard/html/index.html')
time.sleep(1)
print(f'HTML seção: {o.read().decode().strip()} ocorrências')

# Health
i, o, e = c.exec_command('docker exec backend-agenda wget -q -O- http://localhost:3001/health')
time.sleep(2)
print(f'Health: {o.read().decode().strip()}')

c.close()
print(f'\n{"="*50}')
print(f'✅ CONFIG EDITOR INJETADO COM SUCESSO')
print(f'   Acesse: https://svoboda.rtflowapp.com/index.html')
print(f'   Aba: WhatsApp Agenda → 🚀 Disparo → rolar até embaixo')
print(f'{"="*50}')
