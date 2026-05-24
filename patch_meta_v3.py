#!/usr/bin/env python3
"""
patch_meta_v3.py - Insere gerenciador de templates Meta de forma segura.
O JS e salvo em arquivo separado para evitar problemas com f-strings.
"""
import sys, os

ARQUIVO = '/docker/dashboard/whatsapp_agenda_gen.py'

# ── Le o arquivo ──────────────────────────────────────────────────────────────
with open(ARQUIVO, 'r', encoding='utf-8') as f:
    lines = f.readlines()

content = ''.join(lines)

# ── Verifica se ja foi aplicado ───────────────────────────────────────────────
if 'GERENCIADOR DE TEMPLATES META' in content:
    print('[INFO] Patch ja aplicado. Nada a fazer.')
    sys.exit(0)

# ── Ancora: o </div> que fecha wa-config vem imediatamente antes de <!-- SUB: Chat -->
# Exemplo no arquivo:
#       </div>      <- fecha chart-card credenciais
#     </div>        <- fecha grid-2
#   </div>          <- fecha wa-sub wa-config
#                   <- linha vazia
#   <!-- SUB: Chat -->

ANCHOR = '  <!-- SUB: Chat -->'
if ANCHOR not in content:
    print('[ERRO] Ancora nao encontrada.')
    sys.exit(1)

# ── HTML a inserir (puro, sem f-string, sem {{ }}) ─────────────────────────────
HTML = r"""    <!-- GERENCIADOR DE TEMPLATES META -->
    <div class="chart-card" style="margin-top:20px">
      <div class="chart-title">📋 Templates de Mensagens (Meta)</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:12px">
        <div>
          <div style="font-size:12px;color:#94a3b8;font-weight:600;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.5px">Criar Novo Template</div>
          <div style="display:flex;flex-direction:column;gap:10px">
            <input class="wa-cfg-input" id="tpl-name" placeholder="Nome (ex: confirmacao_visita)" style="font-family:monospace">
            <select class="wa-cfg-input" id="tpl-category" style="cursor:pointer">
              <option value="UTILITY">📦 Utility (Notificação/Aviso)</option>
              <option value="MARKETING">📢 Marketing (Promoção)</option>
              <option value="AUTHENTICATION">🔐 Authentication (Código)</option>
            </select>
            <textarea class="wa-cfg-input" id="tpl-body" rows="4" placeholder="Corpo da mensagem. Use {1}, {2} para variáveis." style="resize:vertical;font-size:13px;line-height:1.5"></textarea>
            <div style="font-size:11px;color:#475569">
              Variáveis: <code style="background:#1a1e28;padding:2px 5px;border-radius:4px;color:#a78bfa">{1}</code>
              <code style="background:#1a1e28;padding:2px 5px;border-radius:4px;color:#a78bfa">{2}</code> etc.
            </div>
            <button class="wa-cfg-btn" onclick="tplCreate()" id="tpl-create-btn" style="padding:12px;font-size:14px">
              🚀 Enviar para Aprovação da Meta
            </button>
          </div>
          <div style="margin-top:16px">
            <div style="font-size:12px;color:#94a3b8;font-weight:600;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px">Preview</div>
            <div style="background:#0b141a;border-radius:12px;padding:16px">
              <div style="background:#005c4b;color:white;padding:10px 14px;border-radius:10px 10px 2px 10px;font-size:13px;line-height:1.6;max-width:280px;word-wrap:break-word" id="tpl-preview">
                <span style="color:#8696a0;font-style:italic">Sua mensagem aparecerá aqui...</span>
              </div>
              <div style="text-align:right;font-size:10px;color:#667781;margin-top:4px">12:00 ✓✓</div>
            </div>
          </div>
        </div>
        <div>
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <div style="font-size:12px;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.5px">Templates Cadastrados</div>
            <button class="wa-cfg-btn" onclick="tplLoad()" style="padding:5px 12px;font-size:11px">🔄 Atualizar</button>
          </div>
          <div id="tpl-table-wrap" style="max-height:420px;overflow-y:auto">
            <table class="data-table" style="font-size:12px">
              <thead><tr>
                <th style="padding:8px 10px">Nome</th>
                <th style="padding:8px 10px">Categoria</th>
                <th style="padding:8px 10px">Status</th>
                <th style="padding:8px 10px;text-align:right">Ação</th>
              </tr></thead>
              <tbody id="tpl-tbody">
                <tr><td colspan="4" style="text-align:center;color:#64748b;padding:24px">Clique em "Atualizar" para carregar os templates</td></tr>
              </tbody>
            </table>
          </div>
          <div id="tpl-msg" style="font-size:12px;margin-top:8px;color:#64748b"></div>
        </div>
      </div>
    </div>
    <!-- FIM GERENCIADOR DE TEMPLATES META -->
"""

# ── JS a inserir (salvo em arquivo separado para evitar escape) ───────────────
JS = r"""
  // -- Gerenciador de Templates Meta --
  async function tplLoad() {
    if(!WA_BACKEND) { alert('Configure o backend primeiro'); return; }
    document.getElementById('tpl-tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;padding:16px">Carregando...</td></tr>';
    try {
      var r = await fetch(WA_BACKEND + '/meta/templates?apikey=' + WA_KEY);
      var d = await r.json();
      if (d.error) throw new Error(d.error);
      var tpls = d.templates || [];
      if (!tpls.length) {
        document.getElementById('tpl-tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;color:#64748b;padding:20px">Nenhum template ainda.<br>Crie o primeiro!</td></tr>';
        document.getElementById('tpl-msg').textContent = 'Total: 0 templates';
        return;
      }
      var statusMap = {APPROVED:'🟢 Aprovado', PENDING:'🟡 Pendente', REJECTED:'🔴 Rejeitado', PAUSED:'⏸️ Pausado', DISABLED:'⛔ Desativado'};
      var catMap = {UTILITY:'📦 Utility', MARKETING:'📢 Marketing', AUTHENTICATION:'🔐 Auth'};
      var html = '';
      tpls.forEach(function(t) {
        var st = statusMap[t.status] || t.status;
        var cat = catMap[t.category] || t.category;
        html += '<tr>';
        html += '<td style="padding:8px 10px;font-family:monospace;font-size:11px">' + t.name + '</td>';
        html += '<td style="padding:8px 10px">' + cat + '</td>';
        html += '<td style="padding:8px 10px">' + st + '</td>';
        html += '<td style="padding:8px 10px;text-align:right">';
        html += '<button class="wa-cfg-btn" style="padding:4px 8px;font-size:10px;background:#1e293b" ';
        html += 'onclick="tplDelete(\'' + t.name + '\')">🗑️</button>';
        html += '</td></tr>';
      });
      document.getElementById('tpl-tbody').innerHTML = html;
      document.getElementById('tpl-msg').textContent = 'Total: ' + tpls.length + ' template(s)';
    } catch(e) {
      document.getElementById('tpl-tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;color:#ff6b81;padding:16px">' + e.message + '</td></tr>';
    }
  }

  async function tplCreate() {
    if(!WA_BACKEND) { alert('Configure o backend primeiro'); return; }
    var name = document.getElementById('tpl-name').value.trim();
    var cat = document.getElementById('tpl-category').value;
    var body = document.getElementById('tpl-body').value.trim();
    if (!name || !body) { alert('Preencha o nome e o corpo da mensagem'); return; }
    var btn = document.getElementById('tpl-create-btn');
    btn.disabled = true; btn.textContent = 'Enviando...';
    try {
      var r = await fetch(WA_BACKEND + '/meta/templates?apikey=' + WA_KEY, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ name: name, category: cat, body_text: body, language: 'pt_BR' })
      });
      var d = await r.json();
      if (d.error) throw new Error(d.error);
      btn.textContent = '✅ Enviado!'; btn.style.background = '#065f46';
      document.getElementById('tpl-name').value = '';
      document.getElementById('tpl-body').value = '';
      document.getElementById('tpl-preview').innerHTML = '<span style="color:#8696a0;font-style:italic">Sua mensagem aparecerá aqui...</span>';
      setTimeout(function() {
        btn.textContent = '🚀 Enviar para Aprovação da Meta';
        btn.style.background = ''; btn.disabled = false;
      }, 2000);
      tplLoad();
    } catch(e) {
      alert('Erro: ' + e.message);
      btn.textContent = '🚀 Enviar para Aprovação da Meta';
      btn.style.background = ''; btn.disabled = false;
    }
  }

  async function tplDelete(name) {
    if (!confirm('Excluir o template "' + name + '"?')) return;
    try {
      var r = await fetch(WA_BACKEND + '/meta/templates/' + name + '?apikey=' + WA_KEY, { method: 'DELETE' });
      var d = await r.json();
      if (d.error) throw new Error(d.error);
      tplLoad();
    } catch(e) { alert('Erro: ' + e.message); }
  }

  document.addEventListener('input', function(e) {
    if (e.target && e.target.id === 'tpl-body') {
      var preview = document.getElementById('tpl-preview');
      if (preview) {
        var txt = e.target.value || '';
        preview.innerHTML = txt
          ? txt.replace(/\n/g, '<br>')
          : '<span style="color:#8696a0;font-style:italic">Sua mensagem aparecerá aqui...</span>';
      }
    }
  });
"""

# ── Aplica patch HTML: insere dentro de wa-config, antes de <!-- SUB: Chat --> ──
# A estrutura exata antes da ancora e:
#   </div>\n  </div>\n\n  <!-- SUB: Chat -->
# onde o primeiro </div> fecha grid-2 e o segundo fecha wa-sub
# Vamos substituir apenas a linha imediatamente antes da ancora

idx = content.find('  </div>\n\n  <!-- SUB: Chat -->')
if idx == -1:
    print('[ERRO] Estrutura de fechamento do wa-config nao encontrada.')
    sys.exit(1)

# Insere o HTML antes do </div> que fecha wa-sub
INSERT_BEFORE = '  </div>\n\n  <!-- SUB: Chat -->'
content = content.replace(INSERT_BEFORE,
    HTML + '\n  </div>\n\n  <!-- SUB: Chat -->', 1)

print('[OK] Bloco HTML inserido dentro de wa-config.')

# ── Aplica patch JS: insere antes do fechamento </script> final ───────────────
JS_ANCHOR = '  </script>\n</div>'
if JS_ANCHOR not in content:
    # tenta com \r\n
    JS_ANCHOR = '  </script>\r\n</div>'

if JS_ANCHOR in content:
    content = content.replace(JS_ANCHOR, JS + '\n  </script>\n</div>', 1)
    print('[OK] Funcoes JS inseridas.')
else:
    print('[AVISO] Ancora JS nao encontrada — JS nao inserido.')

# ── Salva ─────────────────────────────────────────────────────────────────────
with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.write(content)

print('[OK] Arquivo salvo:', ARQUIVO)
